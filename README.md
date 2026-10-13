# JvM 업무 도우미 · 0.1.0 파일럿

팀원이 각자의 AI로 회사 메일·Webex·업무 자료를 읽고, 같은 Notion Hub에서 일하도록 돕는 **Mac용 도구와 업무 지침**입니다. AI 모델 자체나 독립 AGI는 아닙니다.

## 팀원이 AI에게 줄 문장

> 이 GitHub 저장소의 JvM 업무 도우미를 내 Mac에 설치해줘. README와 docs/SETUP.md를 먼저 읽고, 기존 AI 설정을 보존하면서 연결해줘. 비밀번호는 채팅에 묻지 말고 내가 직접 입력할 터미널을 열어줘. 마지막에 Notion Hub 접근과 연결 상태를 각각 검증해줘.
>
> https://github.com/junnoej-hue/jvm-work-assistant

이 저장소는 공개되어 **GitHub 로그인·초대 없이** 열거나 다운로드할 수 있습니다. 설치에는 **Mac의 파일·터미널을 사용할 수 있는 AI**가 필요합니다. 설치만으로 회사 계정에 로그인되지는 않습니다. 일반 웹 ChatGPT에 링크를 붙여넣는 것만으로 이 로컬 도구가 설치되지는 않습니다.

## 연결 후 할 수 있는 일

- “이 일정표를 보고 Client별 Project·Task를 정리해줘.”
- “이 프로젝트 메일과 허용한 Webex 방에서 결정 사항·대기·내 다음 행동을 찾아줘.”
- “이 회의록/통화 전사문을 반영할 Note와 변경안을 만들고, 요청한 내용은 Hub에 저장해줘.”
- “이름을 확인해서 이 Task를 해당 Team 멤버에게 배정해줘.”

Notion 생성·수정은 **각자의 공식 Notion 연결과 권한**으로 수행합니다. 자료 형식 해석과 최종 판단은 사용하는 AI 기능에 달려 있습니다. 항상 실제 저장 결과를 확인하도록 업무 지침을 포함했습니다.

[ZIP 다운로드](https://github.com/junnoej-hue/jvm-work-assistant/archive/refs/heads/main.zip)도 가능합니다. 저장소 공개는 회사 서비스의 접근 권한을 부여하지 않습니다.

## 처음에 연결할 것

| 연결 | 최초 설정 | 역할 |
|---|---|---|
| Notion | 회사 계정의 공식 플러그인/커넥터 + Hub 접근 | Client·Project·Task·Note 읽기/쓰기 |
| Zimbra | 회사 IMAP 호스트와 본인 로그인 | 메일 검색/읽기만 |
| Webex | 본인 OAuth Integration 등록·로그인, 회사 방 선택 | 선택한 대화방 읽기만 |

Webex는 등록·관리자 정책에 따라 첫 설정에 도움이 필요할 수 있습니다. **회사 공용 로그인 서버나 무설정 배포는 아직 제공하지 않습니다.**

[설치 안내](docs/SETUP.md) · [Hub 검증](docs/HUB-VERIFICATION.md) · [현재 검증 범위](docs/VALIDATION.md) · [개인정보/제한](docs/PRIVACY.md)

메일·메신저 발송, 회의 녹화/첨부 자동 다운로드, 통화 자동 전사, 상시 수집, 캘린더 동기화는 이 버전에 없습니다. 실제 메일·대화·개인 인증정보는 저장소에 포함하지 않습니다.
