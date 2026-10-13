from __future__ import annotations
import argparse
import getpass
import imaplib
import json
import re
import ssl
import sys
from .common import ROOT, UserError, load_config, save_config, state_dir
from . import keychain, webex, mail, hub


def interactive():
    if not sys.stdin.isatty():
        raise UserError('사용자 터미널에서 실행하세요. 비밀번호·인증값을 AI 채팅이나 명령 인자로 전달하지 마세요.')


def setup_zimbra():
    interactive()
    print('회사 Zimbra IMAP 연결. 기존 개인 JvM 프로그램의 자격증명은 복사하지 않습니다.')
    host=input('회사 IMAP 호스트 (IT 담당자에게 확인): ').strip()
    username=input('본인 회사 이메일: ').strip()
    if not re.fullmatch(r'[A-Za-z0-9.-]+',host) or '.' not in host or '@' not in username:
        raise UserError('호스트와 회사 이메일을 확인하세요.')
    password=getpass.getpass('비밀번호 또는 회사가 발급한 앱 비밀번호 (화면에 표시 안 됨): ')
    if not password:raise UserError('비밀번호가 비어 있습니다.')
    c=None
    try:
        c=imaplib.IMAP4_SSL(host,993,ssl_context=ssl.create_default_context(),timeout=25)
        c.login(username,password)
        if c.select('INBOX',readonly=True)[0]!='OK':raise UserError('INBOX 읽기 권한을 확인하세요.')
    except (imaplib.IMAP4.error,OSError):
        raise UserError('연결 실패. IMAP 사용 여부, 호스트, VPN, 인증 정보를 확인하세요. 저장하지 않았습니다.') from None
    finally:
        if c:
            try:c.logout()
            except (imaplib.IMAP4.error,OSError):pass
    keychain.set_secret('zimbra',{'host':host,'port':993,'username':username,'password':password})
    print('Keychain 저장 및 INBOX 읽기 전용 연결 확인 완료. 메일 본문은 읽지 않았습니다.')


def setup_rooms():
    interactive()
    found={};path='';seen=set()
    for _ in range(20):
        page=webex.discover_rooms(path)
        for room in page['rooms']:found[room['id']]=room
        path=page.get('next_path','')
        if not path or path in seen:break
        seen.add(path)
    rooms=list(found.values())
    if not rooms:raise UserError('조회된 Webex 대화방이 없습니다.')
    for i,r in enumerate(rooms,1):print(f"{i}. {r['title']} [{r['type']}]")
    print('AI가 읽어도 되는 회사 대화방 번호만 선택하세요. 기존 선택은 교체됩니다.')
    if path:print('대화방이 많아 처음 2,000개까지만 표시했습니다.')
    answer=input('번호 (예: 1,3,5 / 빈 입력은 취소): ').strip()
    if not answer:
        print('변경하지 않았습니다.');return
    try:
        indices=sorted(set(int(x.strip()) for x in answer.split(',')))
        if any(i<1 or i>len(rooms) for i in indices):raise ValueError()
    except ValueError:raise UserError('표시된 번호를 쉼표로 구분해 입력하세요.') from None
    chosen=[{'id':rooms[i-1]['id'],'title':rooms[i-1]['title']} for i in indices]
    settings=load_config();settings['webex_rooms']=chosen;save_config(settings)
    print(f'{len(chosen)}개 회사 대화방을 허용했습니다. 본문은 읽지 않았습니다.')


def setup_webex():
    interactive()
    print('docs/SETUP.md의 Webex Integration 등록을 먼저 완료하세요.')
    print('Redirect URI: '+webex.REDIRECT)
    client_id=input('본인 Integration Client ID: ').strip()
    client_secret=getpass.getpass('Client Secret (화면에 표시 안 됨): ')
    if not client_id or not client_secret:raise UserError('Client ID와 Secret이 필요합니다.')
    webex.authorize(client_id,client_secret)
    print('본인 Webex OAuth 연결 완료. 읽을 대화방을 선택합니다.')
    setup_rooms()


def doctor(live=False):
    result={'version':'0.1.0','python':sys.version.split()[0],'platform':sys.platform,'hub_schema':hub.contract()['verification'],
            'notion':'공식 Notion 커넥터에서 회사 Hub를 별도로 읽어 검증해야 합니다.',
            'zimbra':'not_configured','webex':'not_configured','allowed_room_count':len(load_config().get('webex_rooms',[])),
            'live_checks_requested':live}
    for name,account in [('zimbra','zimbra'),('webex','webex_token')]:
        try:
            if keychain.get(account):result[name]='configured_not_live_tested'
        except UserError as exc:result[name]=str(exc)
    if live:
        if result['zimbra']=='configured_not_live_tested':
            try:
                with mail.connection() as c:mail.epoch(c)
                result['zimbra']='INBOX_readonly_verified_no_body_read'
            except UserError as exc:result['zimbra']=str(exc)
        if result['webex']=='configured_not_live_tested':
            try:
                from .common import webex_http
                from urllib.parse import quote
                selected=load_config().get('webex_rooms',[])
                if selected:
                    info=webex_http('/rooms/'+quote(selected[0]['id'],safe=''),token=webex.token())
                    if info.get('id')!=selected[0]['id']:raise UserError('Webex room identity mismatch')
                    result['webex']='selected_room_metadata_verified_no_messages_read'
                else:result['webex']='configured_but_select_rooms_first'
            except UserError as exc:result['webex']=str(exc)
    print(json.dumps(result,ensure_ascii=False,indent=2))
    bad=[result[n] for n in ('zimbra','webex') if result[n] not in ('not_configured','configured_not_live_tested','INBOX_readonly_verified_no_body_read','selected_room_metadata_verified_no_messages_read')]
    return 1 if bad else 0


def client_config(client):
    script=str(ROOT/'scripts/run-mcp.sh')
    if client=='claude':
        print(json.dumps({'mcpServers':{'jvm-work-assistant':{'command':'/bin/bash','args':[script]}}},indent=2))
    else:
        import shlex
        print('codex mcp add jvm-work-assistant -- /bin/bash '+shlex.quote(script))
    print('기존 설정에 해당 항목만 추가하세요. docs/SETUP.md 참조.',file=sys.stderr)


def main(argv=None):
    parser=argparse.ArgumentParser(description='JvM 업무 도우미 · macOS 설치/연결 진단')
    sub=parser.add_subparsers(dest='command',required=True)
    setup=sub.add_parser('setup');setup.add_argument('service',choices=['zimbra','webex','rooms'])
    check=sub.add_parser('doctor');check.add_argument('--live',action='store_true')
    config=sub.add_parser('config');config.add_argument('client',choices=['codex','claude'])
    sub.add_parser('hub')
    forget=sub.add_parser('disconnect');forget.add_argument('service',choices=['zimbra','webex'])
    args=parser.parse_args(argv)
    try:
        if args.command=='setup':{'zimbra':setup_zimbra,'webex':setup_webex,'rooms':setup_rooms}[args.service]()
        elif args.command=='doctor':return doctor(args.live)
        elif args.command=='config':client_config(args.client)
        elif args.command=='hub':print(json.dumps(hub.contract(),ensure_ascii=False,indent=2))
        elif args.command=='disconnect':
            interactive()
            if input(f'{args.service}의 이 패키지 연결만 제거할까요? [yes]: ').strip()!='yes':return 0
            accounts=['zimbra'] if args.service=='zimbra' else ['webex_token','webex_client']
            for account in accounts:keychain.delete(account)
            if args.service=='webex':
                config=load_config();config['webex_rooms']=[];save_config(config)
            print('로컬 연결 제거 완료. Webex 승인 취소는 계정 설정에서도 진행하세요.')
        return 0
    except UserError as exc:
        print(str(exc),file=sys.stderr);return 1
    except (EOFError,KeyboardInterrupt):
        print('취소했습니다.',file=sys.stderr);return 130
    except Exception:
        print('로컬 처리 실패. 인증값이나 원본 오류는 출력하지 않았습니다. 설치 및 설정 파일 형식을 확인하세요.',file=sys.stderr);return 1

if __name__=='__main__':sys.exit(main())
