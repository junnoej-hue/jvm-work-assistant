# 데이터와 실행 범위

이 저장소는 코드, 공통 업무 지침, 회사 Hub 구조만 포함합니다. 실제 메일·Webex 대화·프로젝트 본문·통화기록·개인 API 키는 포함하지 않습니다. 사용자의 요청에 따라 공개 배포합니다. 공개 범위에는 코드·공통 업무 지침·회사 Hub의 DB 구조와 페이지/DB 식별자가 포함됩니다. 해당 식별자는 인증정보가 아니며 실제 Notion 페이지와 업무 내용은 Notion의 접근 권한으로 보호됩니다.

각 사용자의 Zimbra 자격증명, Webex Client Secret 및 OAuth token은 그 Mac의 Keychain 서비스 `jvm-work-assistant.v1` 아래 저장합니다. 승인한 대화방의 ID/이름은 `~/Library/Application Support/JvMWorkAssistant/settings.json`에 사용자 권한으로 저장합니다. 원본 메일과 채팅 캐시는 생성하지 않습니다. 기존 JvMBridge/WebexCollector/JvMAEWorker와 별개입니다.

AI가 읽은 자료는 해당 AI 서비스에 전달되어 채팅 기록에 남을 수 있습니다. 사용자는 회사가 허용하는 AI 계정과 접근 범위로 사용해야 합니다. Keychain 저장이 같은 사용자 권한으로 실행되는 모든 프로그램으로부터 비밀을 완전히 격리하는 것은 아닙니다. 신뢰하는 로컬 AI/도구만 등록하세요.

메일은 TLS IMAP read-only selection과 BODY.PEEK를 사용합니다. SMTP/APPEND/STORE/MOVE/EXPUNGE 기능이 없습니다. Webex 도구는 선택한 방만 읽으며 OAuth 토큰 교환 이외에 API POST를 거부합니다. 메일·메신저 발송, 자동 배정, 무요청 백그라운드 수집은 없습니다.

Notion은 별도 공식 연결이 실제 권한을 결정합니다. 이 패키지의 지침은 AI 동작을 안내하지만 권한 격리 장치는 아닙니다. 회사 Hub의 공유/편집 권한도 필요한 범위로 설정하세요.

첨부파일과 회의 녹화·전사 API는 포함하지 않습니다. 사용자가 준 파일·전사문은 AI가 읽을 수 있는 형식일 때 활용할 수 있습니다. 통화목록만으로 대화 내용을 추론하지 않습니다.
