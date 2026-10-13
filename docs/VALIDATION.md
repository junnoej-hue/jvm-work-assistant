# 검증 기록 · v0.1.0 · 2026-10-13

환경: macOS Apple Silicon, Python 3.12.14. 검증 수준은 **파일럿 배포 가능**이며 팀원별 계정 연결은 별도입니다.

| 검증 | 결과 |
|---|---|
| 회사 Notion Hub/핵심 DB 5개 읽기·관계 대상 | 통과. 범위는 HUB-VERIFICATION.md 참조 |
| 자동 테스트 29개 | 통과: 메일 읽기 전용·UIDVALIDITY·크기 제한, 허용 방 제한, 오류 비밀값 제거, 설정 보존/재실행 등 |
| 실제 MCP stdio 초기화·도구 목록 | 통과, 도구 7개 |
| MCP Hub/지침 조회 및 무범위·미허용 읽기 거부 | 통과 |
| 별도 테스트용 macOS Keychain 추가/읽기/변경/삭제 | 통과. 실제 사용자 인증값 미사용 |
| 공백 포함 새 임시 경로의 깨끗한 설치 | 통과. 설치→29개 테스트→MCP→doctor |
| Python 의존성 pip check | 통과 |
| portable plugin.json / mcp.json 공식 JSON Schema | 통과 |

## 아직 검증하지 않은 것

- 이 새 패키지에서 실제 Zimbra 로그인·메일 조회 및 Webex OAuth 첫 로그인·메시지 조회. 기존 개인 브리지의 비밀값은 이식하지 않았습니다.
- 각 팀원의 Mac, Intel Mac, Python 3.11/기타 버전, 각 AI 앱 UI에서의 실제 설치/도구 노출.
- Notion 생성/수정 end-to-end, 템플릿 생성 결과·버튼 실행·진행률 재계산.
- 기업별 IMAP/OAuth 정책·관리자 승인. 이 조건은 코드 설치로 해결되지 않습니다.

따라서 배포 첫 사용자는 docs/SETUP.md대로 자기 계정을 연결하고 `doctor --live` 및 작은 실무 요청을 확인해야 합니다. 프로그램 설치와 서비스 연결 성공을 혼동하지 않습니다.
