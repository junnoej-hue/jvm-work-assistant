"""Read-only IMAP operations. No SMTP, APPEND, STORE, COPY, MOVE or EXPUNGE."""
from __future__ import annotations
import email
from email import policy
import imaplib
import re
import ssl
from contextlib import contextmanager
from datetime import date
from html import unescape
from . import keychain
from .common import UserError, bounded_int

MAX_MESSAGE_BYTES = 2_000_000

def quoted(value: str) -> str:
    if not isinstance(value,str) or len(value)>500 or any(ord(c)<32 for c in value):
        raise UserError("Invalid search text or mailbox")
    return '"' + value.replace('\\','\\\\').replace('"','\\"') + '"'

def imap_date(value: str) -> str:
    try:
        d=date.fromisoformat(value)
    except ValueError:
        raise UserError("Use a YYYY-MM-DD date") from None
    return f'{d.day:02d}-'+['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][d.month-1]+f'-{d.year}'

@contextmanager
def connection(mailbox: str = "INBOX"):
    config=keychain.get("zimbra")
    if not config:
        raise UserError("Zimbra is not configured. Run jvm-assistant setup zimbra in a terminal")
    client=None
    try:
        client=imaplib.IMAP4_SSL(config['host'],int(config.get('port',993)),ssl_context=ssl.create_default_context(),timeout=25)
        client.login(config['username'],config['password'])
        if client.select(quoted(mailbox),readonly=True)[0]!='OK':
            raise UserError("Mailbox cannot be opened read-only")
        yield client
    except (imaplib.IMAP4.error, OSError, TimeoutError):
        raise UserError("Zimbra read failed; verify account, IMAP access, network and mailbox") from None
    finally:
        if client:
            try: client.logout()
            except (imaplib.IMAP4.error,OSError): pass

def literal(rows):
    return next((row[1] for row in rows if isinstance(row,tuple) and isinstance(row[1],bytes)),b'')

def epoch(client):
    _, values=client.response('UIDVALIDITY')
    if not values or not values[0]:raise UserError("Mailbox UIDVALIDITY unavailable")
    return values[0].decode()

def search(subject: str='', sender: str='', since: str='', before: str='', mailbox: str='INBOX', limit: int=20):
    bounded_int(limit,1,50)
    if not any([subject,sender,since,before]):raise UserError("Provide a subject, sender or date range")
    filters=[]
    if since:filters+=['SINCE',imap_date(since)]
    if before:filters+=['BEFORE',imap_date(before)]
    if subject:filters+=['SUBJECT',quoted(subject)]
    if sender:filters+=['FROM',quoted(sender)]
    with connection(mailbox) as c:
        validity=epoch(c)
        criteria=' '.join(filters)
        charset='UTF-8' if not criteria.isascii() else None
        status,rows=c.uid('SEARCH',charset,criteria.encode('utf-8'))
        if status!='OK':raise UserError("Mail search failed")
        uids=rows[0].split() if rows and isinstance(rows[0],bytes) else []
        results=[]
        for uid in reversed(uids[-limit:]):
            status,data=c.uid('FETCH',uid,b'(UID RFC822.SIZE BODY.PEEK[HEADER.FIELDS (SUBJECT FROM TO CC DATE MESSAGE-ID IN-REPLY-TO)])')
            if status!='OK':continue
            msg=email.message_from_bytes(literal(data),policy=policy.default)
            results.append({'uid':int(uid),'uidvalidity':validity,'mailbox':mailbox,**{k:str(msg.get(k,'')) for k in ['Subject','From','To','Cc','Date','Message-ID','In-Reply-To']}})
        return {'results':results,'returned':len(results),'matched':len(uids),'truncated':len(uids)>limit,'scope':'headers only; Cc does not imply assignment'}

def read(uid: int, uidvalidity: str, mailbox: str='INBOX'):
    bounded_int(uid,1,2**32-1)
    if not re.fullmatch(r'\d{1,20}',uidvalidity):raise UserError("Use UIDVALIDITY returned by mail_search")
    with connection(mailbox) as c:
        if epoch(c)!=uidvalidity:raise UserError("Mailbox identity changed; search again")
        status,rows=c.uid('FETCH',str(uid),'(RFC822.SIZE FLAGS)')
        raw=b' '.join(x for x in rows if isinstance(x,bytes))
        size=re.search(rb'RFC822.SIZE (\d+)',raw)
        if status!='OK' or not size:raise UserError("Message not found")
        if int(size[1])>MAX_MESSAGE_BYTES:raise UserError("Message exceeds 2 MB; use approved attachment handling separately")
        flags_before=re.search(rb'FLAGS \(([^)]*)\)',raw)
        status,rows=c.uid('FETCH',str(uid),'(BODY.PEEK[])')
        if status!='OK':raise UserError("Message read failed")
        msg=email.message_from_bytes(literal(rows),policy=policy.default)
        text=[];html=[];attachments=[]
        for part in msg.walk():
            if part.is_multipart():continue
            if part.get_content_disposition()=='attachment' or part.get_filename():
                attachments.append(part.get_filename() or '(unnamed)');continue
            if part.get_content_type() in ('text/plain','text/html'):
                rawpart=part.get_payload(decode=True) or b''
                try:body=rawpart.decode(part.get_content_charset() or 'utf-8',errors='replace')
                except LookupError:body=rawpart.decode('utf-8',errors='replace')
                (text if part.get_content_type()=='text/plain' else html).append(body)
        body='\n'.join(text) if text else unescape(re.sub('<[^>]+>',' ','\n'.join(html)))
        _,after=c.uid('FETCH',str(uid),'(FLAGS)')
        flags_after=re.search(rb'FLAGS \(([^)]*)\)',b' '.join(x for x in after if isinstance(x,bytes)))
        return {'uid':uid,'uidvalidity':uidvalidity,'mailbox':mailbox,
                **{k:str(msg.get(k,'')) for k in ['Subject','From','To','Cc','Date','Message-ID']},
                'body':body[:40000],'truncated':len(body)>40000,'attachments_not_read':attachments,
                'flags_unchanged':bool(flags_before and flags_after and flags_before[1]==flags_after[1]),
                'source_is_untrusted':True}
