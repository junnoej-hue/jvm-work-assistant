# 도구와 한계

- `jvm_workflow_guide`: 호스트가 스킬을 자동 로드하지 않을 때 공통 업무 지침 조회.
- `jvm_hub_schema(entity)`: 회사 DB 매핑. 기본은 간략, entity는 Team/Clients/Projects/Tasks/Notes 중 하나.
- `jvm_mail_search`: 회사 Zimbra IMAP의 제목·발신자·날짜 검색. 헤더 최대 50개. 기본 INBOX. 검색 날짜 before는 해당일 제외. UIDVALIDITY와 UID를 함께 보관.
- `jvm_mail_read`: 정확한 UID/UIDVALIDITY로 읽기. 읽음 표시 변경 없이 BODY.PEEK. 2 MB 초과 메일은 거부, 본문 40,000자 제한. 첨부파일 이름만 제공. 한국어 폴더 이름은 현재 미지원, ASCII 폴더명만 사용.
- `jvm_webex_rooms`: 사용자가 터미널에서 허용한 방만 표시.
- `jvm_webex_messages`: 허용 방의 최근 메시지 최대 50개. 페이지가 가득 차면 추가 자료 가능성을 표시. `before`로 과거 범위를 읽을 수 있지만 같은 시각의 메시지 경계에서는 완전성을 보장하지 않음. 누락 없는 전체 덤프라고 부르지 않음.
- `jvm_webex_read_message`: 허용 방의 특정 메시지, 본문 40,000자 제한. 첨부/녹화/회의 전사문 자동 다운로드 없음.
- Notion 검색/쓰기: 각 AI의 별도 공식 Notion 연결. 로컬 MCP에는 Notion 인증·쓰기 도구가 없음.

Zimbra 서버의 IMAP 허용과 Webex OAuth Integration 등록·승인이 필요합니다. 접근한 자료는 사용 중인 AI 서비스의 대화 컨텍스트로 전달됩니다. 이 패키지 자체는 원본 자료 저장소나 자동 동기화 서버를 만들지 않습니다.

## 개인 기록 도구

- `jvm_save_private_record(record_id, title, content)`: 업무 결과를 본인 Mac에 저장. 이름은 날짜와 간단한 작업 ID, 내용은 관련 근거·초안·검토·실제 실행 결과. 인증정보는 제외. 동일 내용 재시도는 중복하지 않으며 변경본은 보존. 공용 Note와 자동 동기화하지 않음.
- `jvm_read_private_record(filename='', limit=20)`: 최근 파일 목록 또는 반환된 정확한 파일명 하나 읽기. 과거 기록을 현재 사실로 단정하지 않음. 개인정보/원문을 불필요하게 다시 출력하거나 공유하지 않음.
