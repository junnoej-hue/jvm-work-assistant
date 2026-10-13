# AI와 함께 설치하기

## 1. 저장소와 실행 환경

설치하는 AI는 먼저 이 문서와 루트 AGENTS.md를 읽습니다. 공개 저장소이므로 GitHub 로그인이나 초대 없이 내려받을 수 있습니다. 회사 서비스는 각자의 권한으로 연결하고 공유 계정 인증값을 전달하지 않습니다.

Mac의 **로컬 터미널에 접근할 수 있는 Codex/Claude Code 등**으로 진행합니다. Claude Desktop은 설치 후 로컬 MCP를 사용할 수 있지만 앱의 일반 채팅이 직접 설치할 수 있는지는 사용 모드에 달려 있습니다. 일반 웹 채팅만 사용한다면 이 패키지만으로는 부족합니다.

필요 환경: macOS, Python 3.11 이상(3.12 권장), Git. Apple Silicon + Python 3.12에서 테스트했습니다. Intel Mac 및 다른 Python 버전은 별도 검증 전입니다.

```sh
git clone https://github.com/junnoej-hue/jvm-work-assistant.git
cd jvm-work-assistant
bash install.sh
```

설치 폴더를 먼저 선택하고 경로에 공백이 있어도 따옴표로 처리합니다. `.venv`에 고정 버전 의존성을 설치합니다. 시스템 Python이나 기존 개인 JvM 브리지를 바꾸지 않습니다. Python이 없으면 python.org에서 지원 버전을 설치하거나 사용자의 기존 Python 경로를 `JVM_PYTHON`으로 지정하세요. 원격 스크립트를 curl로 받아 즉시 실행하지 않습니다.

## 2. 사용하는 AI에 도구 등록

사용 중인 AI 하나부터 등록합니다. 아래 명령은 패키지 폴더에서 실행합니다. 기존 설정 파일은 백업하고 이 MCP 항목만 추가합니다. 동일 이름의 다른 연결은 덮어쓰지 않습니다. **계정 인증정보가 없는 설정만** 추가됩니다.

Codex:

```sh
.venv/bin/python scripts/connect_client.py codex
```

`codex` CLI가 PATH에 없으면 앱이 제공하는 CLI를 확인하거나 MCP 설정에서 아래를 등록합니다.

- 이름: `jvm-work-assistant`
- 방식: STDIO
- 명령: `/bin/bash`
- 인자: 설치 폴더의 **절대 경로** + `/scripts/run-mcp.sh`

Claude Desktop:

```sh
.venv/bin/python scripts/connect_client.py claude
```

`~/Library/Application Support/Claude/claude_desktop_config.json`의 `mcpServers`에 추가합니다. 기존 설정의 다른 서버·환경변수는 보존합니다. 등록 후 앱을 완전히 종료하고 다시 여세요. 직접 설정하려면 `.venv/bin/jvm-assistant config claude`로 항목만 출력할 수 있습니다.

Claude Code 등 다른 STDIO 호스트는 같은 실행 명령을 각 호스트의 공식 MCP 설정으로 등록합니다. 모든 AI 호스트의 UI 설치를 검증한 것은 아닙니다. portable plugin manifest도 포함되어 있지만 **기준 설치 경로는 이 문서의 로컬 MCP 등록**입니다. 플러그인 가져오기만으로 Python 설치가 자동 실행되지는 않습니다.

새 채팅에서 “JvM 업무 지침을 읽어줘”라고 요청해 `jvm_workflow_guide`를 호출하는지 확인합니다. 프로젝트 폴더의 AGENTS.md/CLAUDE.md도 지침 위치를 안내합니다.

## 3. Notion 연결 및 Hub 확인

AI의 공식 Notion 플러그인/커넥터를 **자기 회사 계정**으로 연결하고 Hub 접근을 허용합니다. 이 저장소에는 Notion 토큰이 없습니다.

AI에게 다음을 요청하세요:

> jvm_hub_schema로 회사 Hub를 확인하고, 내 회사 Notion 연결로 그 Hub와 Team·Clients·Projects·Tasks·Notes DB를 읽어줘. 현재 스키마와 관계형 대상이 맞는지 확인하고, 내가 Team에 등록되어 있는지도 확인해줘. 아직 테스트 업무는 만들지 마.

Hub: https://app.notion.com/p/Jung-von-Matt-Hub-b2c35e9cb9ee83e182c1018feed05f4b

404라면 개인 연결을 선택했는지, 회사 계정에 Hub/하위 DB 권한이 있는지 먼저 확인합니다. 담당자에는 Team 레코드를 사용합니다. Team에 없는 사람은 추측해 배정하지 않습니다. 쓰기 도구/권한이 없는 호스트는 변경안을 준비할 수 있지만 저장했다고 말하면 안 됩니다.

## 4. 본인 Zimbra 연결

AI가 사용자의 터미널에서 아래를 실행하도록 안내하거나 Finder에서 `connect.command`를 열게 합니다. 비밀번호를 AI가 입력하거나 채팅으로 받지 않습니다.

```sh
.venv/bin/jvm-assistant setup zimbra
```

회사 IT에서 확인한 IMAP 호스트, 본인 회사 이메일, 비밀번호/앱 비밀번호를 입력합니다. TLS 포트 993만 사용합니다. 서버에서 IMAP이 허용되어야 하고 VPN/회사 정책은 우회하지 않습니다. 로그인과 읽기 전용 INBOX 열기가 성공하면 이 패키지 전용 macOS Keychain에 저장합니다. 기존 JvMBridge 인증값을 가져오지 않습니다.

## 5. 본인 Webex 연결

v0.1은 **사용자별 Webex Integration** 방식입니다. 본인 회사 계정으로 [Webex 개발자 포털](https://developer.webex.com/my-apps)에서 Integration을 만들거나 IT 담당자의 도움을 받습니다. 회사에서 승인을 요구하면 승인 후 진행합니다. 다른 사람의 Client Secret/Token을 공유하지 않습니다.

등록 항목:

- Redirect URI: `http://127.0.0.1:8766/oauth/callback` (문자열 그대로)
- Scope: `spark:rooms_read`, `spark:messages_read`, `spark:kms`
- Client ID와 Client Secret: **본인 터미널 입력 및 Keychain 저장만**. GitHub/AI 채팅에 넣지 않습니다.

```sh
.venv/bin/jvm-assistant setup webex
```

브라우저에서 본인 계정으로 승인합니다. 터미널로 돌아오면 AI가 읽어도 되는 회사 대화방 번호만 선택합니다. 개인 DM은 선택하지 않습니다. 이후 변경은 `setup rooms`를 사용합니다. 재인증하면 이전 방 목록을 비우고 다시 선택하게 합니다.

Webex OAuth 권한 자체는 계정이 접근하는 방을 읽을 수 있는 권한입니다. **도구는 별도로 선택한 방만 허용**합니다. 이것은 Webex 서버에서 방별 권한을 발급받는 구조가 아닙니다. 통합 앱 등록을 직원마다 하기 어려우면 다음 버전에서 회사 승인 OAuth 중계 서버를 설계할 수 있습니다. 현재는 배포 전 파일럿 사용자와 이 경로를 확인해야 합니다.

## 6. 실제 진단과 첫 사용

```sh
.venv/bin/jvm-assistant doctor
.venv/bin/jvm-assistant doctor --live
.venv/bin/python scripts/smoke_mcp.py
```

doctor의 `not_configured`는 아직 미연결이라는 뜻이며 성공으로 해석하면 안 됩니다. `--live`는 INBOX 읽기 전용 열기와 허용 Webex 방 하나의 메타데이터만 확인하고, 메일/대화 본문은 읽지 않습니다. Notion은 공식 커넥터에서 따로 확인합니다.

AI 도구 목록 확인 뒤 작은 실무 요청으로 메일 한 스레드/허용 방 메시지를 읽어 실제 결과를 확인하세요. Notion 쓰기 검증이 필요하면 사용자가 선택한 테스트 Project·Task를 명시적으로 만든 뒤 관계·담당자·본문을 다시 읽고 테스트 항목임을 표시하세요. 승인되지 않은 실제 배정/발송은 하지 않습니다.

## 업데이트·제거

- 업데이트: 설치 폴더의 `git status`를 확인하고 개인 자료가 없는 상태에서 `git pull --ff-only`, `bash install.sh`. 의존성/코드 변경 사항 확인 후 앱 재시작. 자동 업데이트 데몬 없음.
- 제거: 먼저 각 AI의 `jvm-work-assistant` MCP 항목만 제거. `disconnect zimbra`, `disconnect webex`를 본인 터미널에서 실행하면 이 패키지 전용 Keychain 항목만 지웁니다. Webex 서비스 측 승인도 계정에서 취소할 수 있습니다.
- 로컬 상태는 `~/Library/Application Support/JvMWorkAssistant`입니다. 제거 시 이 폴더와 설치 폴더만 대상이며 기존 JvMBridge/WebexCollector/JvMAEWorker에는 손대지 않습니다.

## 공식 참고

- [Codex MCP](https://learn.chatgpt.com/docs/extend/mcp?surface=cli)
- [MCP 호스트 연결](https://py.sdk.modelcontextprotocol.io/get-started/real-host/)
- [Webex OAuth](https://developer.webex.com/messaging/docs/authentication)
- [Webex Integration OAuth 흐름](https://developer.webex.com/docs/understanding-oauth-flow-of-webex-integration)
