# checkout-service

체크아웃/결제 처리를 담당하는 Node.js 서비스입니다.

## 프로젝트 구조

```
checkout-service/
├── src/
│   ├── api/            REST 엔드포인트
│   ├── domain/          도메인 모델
│   ├── infra/            DB·외부 API 연동
│   └── workers/         비동기 작업 처리
├── test/
├── scripts/
└── docs/
```

## 의존성

- express 4.x — HTTP 서버
- knex — SQL 쿼리 빌더
- pg — PostgreSQL 드라이버
- bullmq — 작업 큐
- stripe — 결제 SDK
- jest — 테스트 러너
- zod — 스키마 검증

## 빌드·테스트

- 패키지 매니저: pnpm (npm 금지 — lockfile 충돌 방지)
- 빌드: `pnpm build`
- 테스트: `pnpm test`
- 커밋 전 `pnpm lint`와 `pnpm typecheck` 모두 통과해야 함

## 아키텍처 결정

이 서비스는 `shared-types` 패키지를 `payment-gateway`, `order-service`와 함께 쓴다.
`shared-types`를 바꾸면 두 서비스 모두 재배포해야 한다.

라우트 핸들러에서 원시 SQL을 쓰지 않는다. 반드시 Knex를 통해서만 쿼리한다. Knex를 쓰는
이유는 3년 전 원시 SQL로 인한 SQL 인젝션 사고 이후 팀 컨벤션으로 굳어졌기 때문이다
(인시던트 티켓 CHK-892 참조. 당시 담당자는 퇴사함).

결제 금액은 always 정수(cent 단위)로 저장한다. float를 쓰면 반올림 오차가 누적된다.
`amount_cents` 컬럼명 컨벤션을 반드시 지킨다.

## 함정

- API 테스트는 로컬에 Redis가 떠 있어야 통과한다(`docker compose up redis`).
- `stripe` 웹훅 테스트는 `stripe listen --forward-to localhost:3000/webhooks`로
  로컬 포워딩을 켜야 한다. 안 켜면 전부 타임아웃난다.
- `bullmq` 워커는 `pnpm worker:dev`로 별도 프로세스에서 띄워야 큐 작업이 소비된다.
  API 서버만 띄우고 큐가 안 빠진다고 착각하는 경우가 잦다.

## 캐싱 전략 — 왜 Redis 대신 in-process LRU를 1차로 쓰는가

우리 팀은 처음에 모든 캐시를 Redis에 뒀다. 하지만 체크아웃 경로의 read-through 캐시는
p99 레이턴시가 Redis 네트워크 왕복 때문에 8ms씩 추가로 들었다. 2025년 3분기에 부하
테스트(k6, 초당 2,000 요청)를 돌려본 결과, in-process LRU(node-lru-cache, 용량 5,000
엔트리, TTL 30초)를 1차 캐시로 두고 Redis를 2차(cross-instance invalidation용)로
내리자 p99가 42ms → 19ms로 줄었다. 대신 인스턴스 간 캐시 정합성이 최대 30초 어긋날
수 있다는 트레이드오프를 감수했다 — 재고 확인처럼 정합성이 중요한 경로는 이 캐시를
타지 않고 항상 DB를 직접 읽도록 별도 처리했다. 이 결정은 인프라 팀과 3주간 논의 끝에
내려졌고, 관련 슬랙 스레드는 #checkout-perf 채널 2025-08 아카이브에 있다. 향후 트래픽이
지금의 5배를 넘으면 이 전략을 재검토해야 한다 — 그 시점엔 LRU 크기 증설보다 샤딩된
Redis 클러스터로 전환하는 편이 나을 수 있다.

## 릴리즈 절차

1. `main` 브랜치에서 `release/vX.Y.Z` 브랜치를 판다.
2. `pnpm changeset version`으로 버전을 올리고 CHANGELOG를 생성한다.
3. `pnpm build`로 프로덕션 번들을 만든다.
4. 스테이징 환경에 배포하고 `pnpm test:e2e:staging`을 돌린다.
5. QA 팀에 슬랙 #checkout-qa 채널로 배포 알림을 보내고 승인을 받는다.
6. 승인 후 `pnpm deploy:prod`를 실행한다.
7. 배포 후 15분간 Datadog 대시보드(체크아웃 에러율, p99 레이턴시)를 관찰한다.
8. 에러율이 평소 대비 2배를 넘으면 `pnpm rollback:prod`로 즉시 롤백한다.
9. 이상 없으면 `#checkout-releases` 채널에 배포 완료를 공지한다.
10. GitHub에서 릴리즈 노트를 발행한다.

## 코드 스타일

- 함수는 화살표 함수보다 `function` 선언을 우선한다(스택 트레이스 가독성).
- 파일당 export는 하나만 허용(default export 금지, named export 하나).
- 에러는 항상 커스텀 `AppError` 서브클래스를 던진다. 원시 `Error`를 던지지 않는다.
- 비동기 함수 이름은 반드시 `Async` 접미사를 붙인다 (`fetchOrderAsync`).
- 들여쓰기는 2칸, 세미콜론 사용, 작은따옴표.
- import 순서: 외부 패키지 → 내부 절대경로 → 상대경로. 빈 줄로 구분.
- 매직 넘버를 쓰지 않는다. 상수로 추출해 `UPPER_SNAKE_CASE`로 명명한다.
- 한 함수는 최대한 한 가지 일만 한다.
- 조기 반환(early return)을 선호하고 중첩 if를 피한다.
- 주석은 "왜"를 설명하고 "무엇"을 설명하지 않는다.

## 테스트 작성 가이드

- 단위 테스트는 `test/unit/`, 통합 테스트는 `test/integration/`에 둔다.
- 테스트 파일명은 `<대상>.test.ts` 패턴을 따른다.
- mock은 `test/mocks/`에 모아둔다. 인라인 mock을 남발하지 않는다.
- 각 테스트는 독립적으로 실행 가능해야 한다(순서 의존 금지).
- 외부 API 호출은 반드시 mock 처리한다. 실제 Stripe API를 테스트에서 호출하지 않는다.

## 구버전 마이그레이션 메모 (2023년 작성, 현재 미해당)

이 서비스는 원래 Python 2.7 + Flask로 작성됐다가 2023년 초 Node.js로 전면 재작성됐다.
당시 Python 코드는 `legacy/` 브랜치에 보관돼 있었으나, 2024년 1월 브랜치 정리 작업에서
삭제됐다. 재작성 당시 사용했던 `python2-to-node-migration-guide.md`는 더 이상 유효하지
않다. 혹시 옛 문서에서 `flask_checkout` 모듈을 참조하는 코드를 보면 무시해도 된다 —
현재 코드베이스에는 존재하지 않는다.

## 환경 변수

- `DATABASE_URL` — PostgreSQL 접속 문자열 (필수)
- `REDIS_URL` — Redis 접속 문자열 (필수)
- `STRIPE_SECRET_KEY` — Stripe 시크릿 키 (필수, `.env`에서만, 커밋 금지)
- `STRIPE_WEBHOOK_SECRET` — Stripe 웹훅 서명 검증용 (필수)
- `NODE_ENV` — development | staging | production
- `LOG_LEVEL` — debug | info | warn | error (기본 info)

## PR 체크리스트

- [ ] `pnpm lint` 통과
- [ ] `pnpm typecheck` 통과
- [ ] `pnpm test` 통과
- [ ] 새 환경변수를 추가했다면 `.env.example`도 갱신
- [ ] 브레이킹 체인지가 있다면 CHANGELOG에 기록
- [ ] 결제 관련 변경이면 결제팀 리뷰어를 추가로 지정

## 자주 쓰는 명령어

```bash
pnpm dev              # 개발 서버 (핫리로드)
pnpm worker:dev        # 큐 워커 (개발)
pnpm test:watch        # 테스트 watch 모드
pnpm db:migrate        # DB 마이그레이션 실행
pnpm db:seed           # 시드 데이터 삽입
pnpm db:reset          # DB 초기화 (개발 환경 전용, 프로덕션 절대 금지)
docker compose up -d   # Redis·PostgreSQL 로컬 기동
```
