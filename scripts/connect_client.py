"""Register only this MCP entry, preserving the user's other host settings."""
import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def backup(path):
    if path.is_symlink():raise ValueError('설정 파일이 심볼릭 링크입니다. 자동 변경 대신 직접 확인하세요.')
    if path.exists():
        saved=path.with_name(path.name+'.jvm-backup-'+str(time.time_ns()))
        shutil.copy2(path,saved);saved.chmod(0o600)
        return saved

def merge_claude(path):
    if path.is_symlink():raise ValueError('심볼릭 링크 설정은 직접 확인하세요.')
    config=json.loads(path.read_text()) if path.exists() else {}
    servers=config.setdefault('mcpServers',{})
    entry={'command':'/bin/bash','args':[str(ROOT/'scripts/run-mcp.sh')]}
    if 'jvm-work-assistant' in servers and servers['jvm-work-assistant']!=entry:
        raise ValueError('동일 이름의 다른 MCP가 있습니다. 덮어쓰지 않았습니다.')
    if servers.get('jvm-work-assistant')==entry:return False
    backup(path);servers['jvm-work-assistant']=entry
    path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_name(path.name+'.jvm-tmp')
    fd=os.open(tmp,os.O_WRONLY|os.O_CREAT|os.O_TRUNC|os.O_NOFOLLOW,0o600)
    with os.fdopen(fd,'w') as f:json.dump(config,f,ensure_ascii=False,indent=2)
    os.replace(tmp,path);return True

def main():
    p=argparse.ArgumentParser();p.add_argument('client',choices=['claude','codex']);a=p.parse_args()
    if a.client=='claude':
        path=Path.home()/'Library/Application Support/Claude/claude_desktop_config.json'
        merge_claude(path)
    else:
        exe=shutil.which('codex')
        if not exe:raise ValueError('codex CLI가 없습니다. docs/SETUP.md의 수동 설정을 사용하세요.')
        existing=subprocess.run([exe,'mcp','get','jvm-work-assistant','--json'],capture_output=True,text=True)
        if existing.returncode==0:
            info=json.loads(existing.stdout);transport=info.get('transport',{})
            if transport.get('command')=='/bin/bash' and transport.get('args')==[str(ROOT/'scripts/run-mcp.sh')]:
                print('동일한 연결이 이미 등록되어 있습니다.');return
            raise ValueError('동일 이름의 MCP가 이미 있습니다. 덮어쓰지 않았습니다.')
        config_dir=Path(os.environ.get('CODEX_HOME',str(Path.home()/'.codex')))
        backup(config_dir/'config.toml')
        result=subprocess.run([exe,'mcp','add','jvm-work-assistant','--','/bin/bash',str(ROOT/'scripts/run-mcp.sh')],capture_output=True,text=True)
        if result.returncode:raise ValueError('Codex 등록 실패. codex mcp --help로 설치 버전을 확인하세요.')
    print('MCP 설정 완료. 앱을 재시작하고 JvM 도구가 보이는지 확인하세요. 계정 연결은 별도입니다.')

if __name__=='__main__':
    try:main()
    except (ValueError,OSError,TypeError):
        print('설정을 적용할 수 없습니다. 기존 파일 형식·동일 이름의 연결·CLI 설치 상태를 확인하세요. 기존 인증값은 출력하지 않았습니다.',file=sys.stderr);sys.exit(1)
