# 개발과 검증

배포는 소스 checkout 내부 `.venv`에 일반 설치하는 방식입니다. `.venv`나 wheel 단독 배포를 사용하지 않습니다. Hub 스키마와 스킬 파일은 저장소 안에 함께 있어야 합니다.

```sh
bash install.sh
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python scripts/smoke_mcp.py
.venv/bin/python -m pip check
```

코드 변경 뒤에는 `bash install.sh`를 다시 실행해 `.venv`의 모듈을 갱신하세요. macOS의 hidden 파일 플래그로 `.pth`가 무시되는 경우를 피하기 위해 editable install을 사용하지 않습니다.

실제 메일/대화/인증정보 없이 mock IMAP, mock Webex, 임시 설정 폴더로 검사합니다. MCP smoke는 실제 stdio 프로토콜로 초기화·도구 조회·허용하지 않은 방 거부·Hub 매핑·업무 지침을 확인합니다.

macOS Keychain 별도 시험은 테스트용 service/account만 사용하고 finally에서 제거해야 합니다. 기존 사용자 credential을 테스트에 가져오지 않습니다. 현재 API client는 동기 read-only 함수이며 토큰 갱신은 로컬 프로세스 간 파일 lock으로 직렬화합니다.

`requirements.lock`은 테스트 환경에서 버전을 고정한 목록입니다. MCP Python SDK v1 `FastMCP` API를 쓰기 때문에 `mcp==1.30.0`으로 고정했습니다. 메이저 업그레이드 시 SDK/프로토콜 검증을 다시 수행하세요. 의존성 목록은 버전 pin이며 hash 검증 lock은 아닙니다.

GitHub에는 allowlist 파일만 commit합니다. 개인 자료는 별도 작업 폴더에 두고 이 저장소에 넣지 마세요. 릴리스 ZIP은 `git archive`로 tracked files만 만들고 zip 목록을 확인합니다.
