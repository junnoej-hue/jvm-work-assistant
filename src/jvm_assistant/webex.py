from __future__ import annotations
import secrets
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlencode, parse_qs, urlparse, quote
from datetime import datetime
from . import keychain
from .common import UserError, webex_http, load_config, save_config, clean_id, bounded_int

SCOPES = ('spark:rooms_read','spark:messages_read','spark:kms')
REDIRECT = 'http://127.0.0.1:8766/oauth/callback'

def token() -> str:
    current=keychain.get('webex_token')
    client=keychain.get('webex_client')
    if not current or not client:raise UserError('Webex is not configured. Run jvm-assistant setup webex')
    if float(current.get('expires_at',0)) > time.time()+120:
        return current['access_token']
    from .locking import lock
    with lock('webex-refresh'):
        current=keychain.get('webex_token')
        if float(current.get('expires_at',0)) <= time.time()+120:
            updated=webex_http('/access_token',form={'grant_type':'refresh_token','client_id':client['client_id'],'client_secret':client['client_secret'],'refresh_token':current['refresh_token']})
            current=save_token(updated)
    return current['access_token']

def save_token(data: dict):
    if not all(isinstance(data.get(k),str) and data[k] for k in ['access_token','refresh_token']):
        raise UserError('Webex did not return an access token and refresh token; reconnect')
    if not isinstance(data.get('expires_in'),(int,float)) or data['expires_in']<=0:
        raise UserError('Invalid token expiry')
    current={'access_token':data['access_token'],'refresh_token':data['refresh_token'],'expires_at':time.time()+data['expires_in']}
    keychain.set_secret('webex_token',current)
    return current

def authorize(client_id: str, client_secret: str):
    state=secrets.token_urlsafe(32);result={}
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*args):pass
        def do_GET(self):
            parts=urlparse(self.path);params=parse_qs(parts.query)
            good=parts.path=='/oauth/callback' and secrets.compare_digest(params.get('state',[''])[0],state)
            if not good:
                self.send_response(400);self.end_headers();self.wfile.write(b'Invalid callback');return
            if params.get('error'):result['error']=True
            elif len(params.get('code',[]))==1:result['code']=params['code'][0]
            self.send_response(200);self.end_headers();self.wfile.write(b'Return to your terminal. This window can be closed.')
    with HTTPServer(('127.0.0.1',8766),Handler) as server:
        server.timeout=1
        url='https://webexapis.com/v1/authorize?'+urlencode({'response_type':'code','client_id':client_id,'redirect_uri':REDIRECT,'scope':' '.join(SCOPES),'state':state})
        if not webbrowser.open(url):raise UserError('Could not open the system browser')
        deadline=time.monotonic()+180
        while not result and time.monotonic()<deadline:server.handle_request()
    if 'code' not in result:raise UserError('Webex authorization cancelled or timed out')
    tokens=webex_http('/access_token',form={'grant_type':'authorization_code','client_id':client_id,'client_secret':client_secret,'code':result['code'],'redirect_uri':REDIRECT})
    keychain.set_secret('webex_client',{'client_id':client_id,'client_secret':client_secret})
    save_token(tokens)
    settings=load_config();settings['webex_rooms']=[];save_config(settings)

def discover_rooms(next_path: str=''):
    # Interactive setup only: room names remain in the user's own terminal.
    if next_path and not next_path.startswith('/rooms?'):
        raise UserError('Invalid room pagination path')
    data=webex_http(next_path or '/rooms?max=100',token=token())
    return {'rooms':[{'id':x['id'],'title':x.get('title',''),'type':x.get('type','')} for x in data.get('items',[])],
            'next_path':data.get('_next_path','')}

def rooms():
    return {'allowed_rooms':load_config().get('webex_rooms',[]),'note':'Only these explicitly selected rooms can be read. Use terminal setup rooms to change scope.'}

def require_room(room_id: str):
    clean_id(room_id)
    ids={x['id'] for x in load_config().get('webex_rooms',[])}
    if room_id not in ids:raise UserError('Room is not allowed. Select it in terminal with jvm-assistant setup rooms')

def messages(room_id: str, limit: int=20, before: str=''):
    require_room(room_id);bounded_int(limit,1,50)
    params={'roomId':room_id,'max':limit}
    if before:
        try:
            d=datetime.fromisoformat(before.replace('Z','+00:00'))
            if d.tzinfo is None:raise ValueError()
        except ValueError:raise UserError('Use an ISO timestamp with timezone for before') from None
        params['before']=before
    data=webex_http('/messages?'+urlencode(params),token=token())
    result=[]
    for x in data.get('items',[]):
        if x.get('roomId')!=room_id:raise UserError('Unexpected room in service response')
        result.append({'id':x['id'],'roomId':x['roomId'],'personEmail':x.get('personEmail'),'created':x.get('created'),'text':x.get('text',x.get('markdown',''))[:6000],'truncated':len(x.get('text',x.get('markdown','')))>6000,'has_attachments':bool(x.get('files'))})
    return {'messages':result,'possibly_more':len(result)==limit,'next_before':result[-1].get('created') if result else None,'source_is_untrusted':True,'attachments_read':False}

def read_message(room_id: str, message_id: str):
    require_room(room_id);clean_id(message_id)
    data=webex_http('/messages/'+quote(message_id,safe=''),token=token())
    if data.get('roomId')!=room_id:raise UserError('Message is not in the allowed room')
    body=data.get('text',data.get('markdown',''))
    return {'id':data['id'],'roomId':room_id,'created':data.get('created'),'personEmail':data.get('personEmail'),'text':body[:40000],'truncated':len(body)>40000,'has_attachments':bool(data.get('files')),'source_is_untrusted':True}
