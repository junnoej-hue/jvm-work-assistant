# 회사 Hub 검증 · 2026-10-13

대상: [Jung von Matt Hub](https://app.notion.com/p/Jung-von-Matt-Hub-b2c35e9cb9ee83e182c1018feed05f4b)

회사 Notion 연결로 Hub, 핵심 DB 5개의 스키마, Project 2개·Task 2개·Team 1개의 관계를 읽어 확인했습니다. 개인 J/Second Brain은 수정하지 않았고 이 검증 과정에서 회사 DB에 테스트 레코드를 만들지 않았습니다. 실제 업무 레코드 내용은 배포물에 복사하지 않았습니다.

## 확인한 구조

| DB | 제목 | 주요 관계 |
|---|---|---|
| Clients | Client | Projects, Notes, 담당 Team |
| Projects | Project | Client, 담당자 → Team, Tasks, Notes |
| Tasks | Task | Client, Project, 담당자 → Team, Notes, 상위/하위 항목 → Tasks |
| Notes | Note | Client, Project, Tasks |
| Team | 이름 | 담당 Clients, Projects, Tasks; Notion 계정은 사람 속성 |

이 관계들의 대상은 모두 새 회사 Hub의 데이터 소스입니다. Task의 Client 관계로 프로젝트 없는 독립 업무도 표현할 수 있습니다. 회사 Hub에서 `담당자`는 Team 관계형이므로 계정 ID를 직접 넣는 사람 속성 방식과 다릅니다.

데이터 소스 ID:

- Team: `60235e9c-b9ee-824a-91d8-87a5c5615418`
- Clients: `a3435e9c-b9ee-834f-acf9-07799e03fe65`
- Projects: `b5635e9c-b9ee-822c-80d0-87b539f38970`
- Tasks: `55035e9c-b9ee-83bb-ae32-0796907899a3`
- Notes: `64a35e9c-b9ee-82dc-8ca1-073d22fa6d18`

전체 스키마 스냅샷은 `skills/jvm-workflow/references/hub-schema.json`에 있습니다. 계정별 connector link ID와 인증정보는 배포하지 않습니다.

## 진행률과 상태

Projects의 `진행률`은 Tasks의 `완료 여부` 수식을 `percent_checked`로 집계하는 rollup입니다. 연결 대상과 집계 방식은 확인했습니다. 커넥터가 제공한 스키마에는 수식 본문 대신 code URL만 있어 **수식 표현식 자체와 실제 상태 변경에 따른 재계산은 미검증**입니다.

Projects/Tasks의 `보류`와 `중단`이 Notion의 complete 그룹에 들어 있습니다. 그룹 전체를 업무 완료로 해석하면 안 됩니다. 도우미 규칙은 정확히 `상태 = 완료`만 완료로 처리합니다. 기존 Hub 상태 그룹/수식은 이번에 변경하지 않았습니다.

## 템플릿 및 추가 연결

5개 DB 모두 기본 페이지 템플릿 URL이 있습니다. 템플릿의 존재를 확인했으며 실제 새 페이지 생성·기본 템플릿 적용·제목 아래 탭·버튼 동작을 이번 검증에서 실행하지 않았습니다.

Projects에 Meetings 및 Google Drive 파일 관련 추가 관계가 있습니다. 이번 패키지는 요청한 5개 핵심 DB만 지원 매핑으로 포함하며 해당 추가 데이터 소스의 내용·접근·자동화는 별도 검증 전입니다.

## 검증 범위의 한계

- **확인:** 회사 연결의 읽기 접근, 핵심 스키마·관계 대상, 소수 실제 레코드 관계, 기본 템플릿 참조, 쓰기 도구 제공 여부.
- **미확인:** 전체 레코드 무결성·전체 사용자 권한, 생성/수정 end-to-end, 수식 본문·재계산, 버튼/자동화 실행, 향후 모든 팀원 맥에서의 접근.
- 각 팀원은 자기 계정으로 최초 연결 후 Hub와 5개 DB를 다시 읽어 검증해야 합니다.
