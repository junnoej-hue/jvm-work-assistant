import io
import json
import os
import tempfile
import unittest
from contextlib import contextmanager
from pathlib import Path
from unittest.mock import patch, MagicMock
from jvm_assistant import mail, webex, hub, common, server, cli

class FakeIMAP:
    def __init__(self,size=100,validity=b'7'):
        self.calls=[];self.size=size;self.validity=validity
    def response(self,name):return name,[self.validity]
    def uid(self,*args):
        self.calls.append(args)
        if args[0]=='SEARCH':return 'OK',[b'1 2 3']
        mode=args[-1]
        if mode=='(RFC822.SIZE FLAGS)':return 'OK',[f'3 (RFC822.SIZE {self.size} FLAGS ())'.encode()]
        if mode=='(FLAGS)':return 'OK',[b'3 (FLAGS ())']
        if mode=='(BODY.PEEK[])':return 'OK',[(b'header',b'Subject: Test\r\nContent-Type: text/plain; charset=utf-8\r\n\r\nhello')]
        return 'OK',[(b'header',b'Subject: Test\r\nFrom: test@example.invalid\r\n')]

@contextmanager
def fake_connection(client):yield client

class MailTests(unittest.TestCase):
    def test_search_requires_scope(self):
        with self.assertRaises(common.UserError):mail.search()
    def test_search_bound_before_network(self):
        with patch.object(mail,'connection') as c:
            for value in [0,51,True]:
                with self.assertRaises(common.UserError):mail.search(subject='test',limit=value)
            c.assert_not_called()
    def test_control_char_rejected(self):
        with self.assertRaises(common.UserError):mail.quoted('x\r\nUID STORE')
    def test_search_peek_and_identity(self):
        c=FakeIMAP()
        with patch.object(mail,'connection',return_value=fake_connection(c)):
            result=mail.search(subject='테스트',limit=2)
        self.assertEqual([r['uid'] for r in result['results']],[3,2])
        self.assertEqual(result['results'][0]['uidvalidity'],'7')
        self.assertTrue(result['truncated']);self.assertEqual(c.calls[0][1],'UTF-8')
        self.assertIn(b'BODY.PEEK',c.calls[1][-1])
    def test_epoch_mismatch_stops_read(self):
        c=FakeIMAP()
        with patch.object(mail,'connection',return_value=fake_connection(c)):
            with self.assertRaises(common.UserError):mail.read(3,'8')
        self.assertEqual(c.calls,[])
    def test_big_message_no_body(self):
        c=FakeIMAP(size=3_000_000)
        with patch.object(mail,'connection',return_value=fake_connection(c)):
            with self.assertRaises(common.UserError):mail.read(3,'7')
        self.assertEqual(len(c.calls),1)
    def test_read_flags_and_body(self):
        c=FakeIMAP()
        with patch.object(mail,'connection',return_value=fake_connection(c)):
            result=mail.read(3,'7')
        self.assertEqual(result['body'],'hello');self.assertTrue(result['flags_unchanged'])
        self.assertTrue(all(x[0]=='FETCH' for x in c.calls))
    def test_connection_examine(self):
        c=MagicMock();c.select.return_value=('OK',[])
        with patch.object(mail.keychain,'get',return_value={'host':'mail.example.invalid','username':'a','password':'fake'}),patch.object(mail.imaplib,'IMAP4_SSL',return_value=c):
            with mail.connection():pass
        c.select.assert_called_once_with('"INBOX"',readonly=True);c.logout.assert_called_once()
    def test_errors_do_not_echo_password(self):
        with patch.object(mail.keychain,'get',return_value={'host':'mail.example.invalid','username':'a','password':'fake_secret'}),patch.object(mail.imaplib,'IMAP4_SSL',side_effect=mail.imaplib.IMAP4.error('fake_secret')):
            result=server.safe(mail.search,subject='test')
        self.assertNotIn('fake_secret',str(result));self.assertFalse(result['ok'])

class WebexTests(unittest.TestCase):
    def setUp(self):
        self.cfg=patch.object(webex,'load_config',return_value={'webex_rooms':[{'id':'allowed','title':'Example'}]});self.cfg.start()
    def tearDown(self):self.cfg.stop()
    def test_disallowed_no_token_or_http(self):
        with patch.object(webex,'token') as tok,patch.object(webex,'webex_http') as http:
            with self.assertRaises(common.UserError):webex.messages('private')
            tok.assert_not_called();http.assert_not_called()
    def test_message_room_mismatch_returns_no_text(self):
        with patch.object(webex,'token',return_value='fake'),patch.object(webex,'webex_http',return_value={'id':'1','roomId':'private','text':'not_for_you'}):
            result=server.safe(webex.read_message,'allowed','1')
        self.assertFalse(result['ok']);self.assertNotIn('not_for_you',str(result))
    def test_messages_room_mismatch(self):
        with patch.object(webex,'token',return_value='fake'),patch.object(webex,'webex_http',return_value={'items':[{'id':'1','roomId':'private','text':'not_for_you'}]}):
            result=server.safe(webex.messages,'allowed')
        self.assertFalse(result['ok']);self.assertNotIn('not_for_you',str(result))
    def test_text_limit_and_more(self):
        with patch.object(webex,'token',return_value='fake'),patch.object(webex,'webex_http',return_value={'items':[{'id':'1','roomId':'allowed','text':'x'*7000,'created':'2026-10-13T00:00:00Z'}]}):
            r=webex.messages('allowed',1)
        self.assertEqual(len(r['messages'][0]['text']),6000);self.assertTrue(r['possibly_more'])
    def test_date_requires_timezone(self):
        with self.assertRaises(common.UserError):webex.messages('allowed',before='2026-10-13')
    def test_no_arbitrary_pagination_endpoint(self):
        with patch.object(webex,'webex_http') as http:
            with self.assertRaises(common.UserError):webex.discover_rooms('/people/me')
            http.assert_not_called()
    def test_refresh_cached(self):
        with patch.object(webex.keychain,'get',side_effect=[{'expires_at':10**12,'access_token':'fake'}, {'client_id':'id'}]),patch.object(webex,'webex_http') as http:
            self.assertEqual(webex.token(),'fake');http.assert_not_called()
    def test_refresh_stored(self):
        expired={'expires_at':0,'refresh_token':'old'};client={'client_id':'id','client_secret':'secret'}
        with tempfile.TemporaryDirectory() as tmp,patch.dict(os.environ,{'JVM_ASSISTANT_STATE_DIR':tmp}),patch.object(webex.keychain,'get',side_effect=[expired,client,expired]),patch.object(webex.keychain,'set_secret') as saved,patch.object(webex,'webex_http',return_value={'access_token':'new','refresh_token':'r','expires_in':3600}):
            self.assertEqual(webex.token(),'new');self.assertEqual(saved.call_args.args[0],'webex_token')

class LocalTests(unittest.TestCase):
    def test_settings_private(self):
        with tempfile.TemporaryDirectory() as tmp,patch.dict(os.environ,{'JVM_ASSISTANT_STATE_DIR':tmp}):
            common.save_config({'webex_rooms':[]})
            self.assertEqual((Path(tmp)/'settings.json').stat().st_mode&0o777,0o600)
    def test_symlink_settings_rejected(self):
        with tempfile.TemporaryDirectory() as tmp,patch.dict(os.environ,{'JVM_ASSISTANT_STATE_DIR':tmp}):
            target=Path(tmp)/'other';target.write_text('{}');(Path(tmp)/'settings.json').symlink_to(target)
            with self.assertRaises(common.UserError):common.load_config()
    def test_network_methods_restricted(self):
        with self.assertRaises(common.UserError):common.webex_http('/messages',form={'text':'bad'})
        with self.assertRaises(common.UserError):common.webex_http('//evil.invalid')
    def test_redirect_rejected(self):
        with self.assertRaises(common.UserError):common.NoRedirect().redirect_request(None,None,302,'',{},'https://evil.invalid')
    def test_hub_only_company(self):
        h=hub.contract();self.assertEqual(len(h['sources']),5)
        self.assertEqual(h['hub_page_id'],'b2c35e9c-b9ee-83e1-82c1-018feed05f4b')
        self.assertIn('완료',h['completion_rule'])
        self.assertEqual(hub.contract('Tasks')['sources']['Tasks']['schema']['담당자']['type'],'relation')
    def test_unknown_entity(self):
        with self.assertRaises(common.UserError):hub.contract('../../private')
    def test_unknown_errors_sanitized(self):
        def fail():raise Exception('fake_secret')
        self.assertNotIn('fake_secret',str(server.safe(fail)))
    def test_setup_requires_user_terminal(self):
        with patch('sys.stdin.isatty',return_value=False):
            with self.assertRaises(common.UserError):cli.setup_zimbra()

if __name__=='__main__':unittest.main()
