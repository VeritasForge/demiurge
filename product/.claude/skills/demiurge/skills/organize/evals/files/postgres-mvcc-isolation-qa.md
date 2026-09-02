# 대화 기록: PostgreSQL MVCC와 트랜잭션 격리 수준
> 아래는 사용자와 AI 어시스턴트의 실제 대화 기록이다. 턴 순서대로 기록됨.

---

**User:**
주문 서비스 백엔드 하고 있는데 DB는 PostgreSQL이야. MVCC라는 말을 계속 듣는데 정확히 뭐야? 그냥 락 걸면 되는 거 아냐? 왜 이게 필요한지부터 좀 알려줘.

---

**Assistant:**
MVCC(Multi-Version Concurrency Control)는 "row를 제자리에서 덮어쓰지 않고 버전을 여러 개 남겨두는" 방식이야. 락으로만 동시성을 제어하면 누가 row를 고치는 동안 그 row를 읽으려는 쪽이 기다려야 하는데, MVCC에서는 읽는 쪽은 옛 버전을 보고 쓰는 쪽은 새 버전을 만들어서 서로 안 막아.

```
락 기반 (읽기가 쓰기를 기다림)
  T1: UPDATE orders SET status='paid' WHERE id=7  ──[X lock]─────────┐ commit
  T2: SELECT * FROM orders WHERE id=7             ────── wait ────────┘→ 그제야 읽음

MVCC (서로 안 기다림)
  T1: UPDATE orders ... id=7   → 새 버전(v2) 생성, 옛 버전(v1)에 xmax 기록
  T2: SELECT ... id=7          → 자기 스냅샷 기준으로 v1을 그냥 읽음, 대기 없음
```

핵심은 두 가지야.

- **읽기는 쓰기를 안 막고, 쓰기는 읽기를 안 막는다.** 쓰기끼리 같은 row를 건드릴 때만 기다린다.
- **UPDATE는 사실 INSERT + 옛 버전에 표시**다. 새 tuple을 넣고, 옛 tuple에는 "이 트랜잭션이 죽였다"는 표시(xmax)를 남긴다.

각 tuple에는 숨은 시스템 컬럼이 있어:

| 컬럼 | 의미 |
|---|---|
| `xmin` | 이 tuple을 만든(INSERT 또는 UPDATE로 새 버전을 쓴) 트랜잭션 ID |
| `xmax` | 이 tuple을 지우거나 갱신한 트랜잭션 ID. 아직 아무도 안 건드렸으면 0 |

그리고 스냅샷이라는 게 있어. 트랜잭션이 시작할 때 "지금 어떤 트랜잭션이 이미 커밋됐고 어떤 게 진행 중인지"를 찍어두는 건데, 각 tuple의 xmin/xmax를 이 스냅샷에 대조해서 "나한테 보이는 버전인지"를 판단해. 그래서 같은 row라도 트랜잭션마다 다른 버전이 보일 수 있어.

대신 대가가 있어. 옛 버전은 아무도 안 보게 된 뒤에도 디스크에 남는데, 이걸 **dead tuple**이라 부르고 VACUUM이 치워야 해. 참고로 VACUUM은 테이블에 락을 잡기 때문에 실행 중에는 그 테이블을 읽을 수 없다. 그래서 보통 autovacuum이 한가할 때 알아서 돌게 두는 거야. (HOT update나 visibility map 얘기까지 가면 길어지니까 일단 여기까지.)

---

**User:**
오케이. 그럼 트랜잭션 격리 수준은 뭐야? READ COMMITTED, SERIALIZABLE 이런 거 4개 있다던데 PostgreSQL이 다 지원해?

---

**Assistant:**
SQL 표준엔 4개가 있고, PostgreSQL은 문법상 4개를 다 받아주지만 실제 동작은 3개야.

| 격리 수준 | dirty read | non-repeatable read | phantom read | serialization anomaly | PostgreSQL 실제 |
|---|---|---|---|---|---|
| READ UNCOMMITTED | 표준: 허용 | 허용 | 허용 | 허용 | **READ COMMITTED로 동작** |
| READ COMMITTED | 안 됨 | 허용 | 허용 | 허용 | 기본값 |
| REPEATABLE READ | 안 됨 | 안 됨 | 표준: 허용 / PG: 안 됨 | 허용 | 스냅샷 격리 |
| SERIALIZABLE | 안 됨 | 안 됨 | 안 됨 | 안 됨 | SSI |

용어 짧게:
- **dirty read**: 남이 커밋 안 한 걸 읽음
- **non-repeatable read**: 같은 row를 두 번 읽었는데 값이 바뀜
- **phantom read**: 같은 조건으로 두 번 조회했는데 row 개수가 바뀜
- **serialization anomaly**: 각 트랜잭션은 멀쩡한데 합쳐 놓으면 어떤 순차 실행으로도 설명이 안 되는 결과

PostgreSQL에서 각각 어떻게 도는지:

- **READ UNCOMMITTED** — MVCC 구조상 커밋 안 된 tuple은 애초에 남한테 안 보여. 그래서 이걸 지정해도 그냥 READ COMMITTED야.
- **READ COMMITTED** (기본) — **문장(statement)마다** 새 스냅샷을 찍어. 한 트랜잭션 안에서 SELECT를 두 번 하면 그 사이에 커밋된 남의 변경이 두 번째에 보여.
- **REPEATABLE READ** — **트랜잭션 전체가 스냅샷 하나**를 써. 처음 쿼리를 날린 시점의 스냅샷을 끝까지 유지해서, 남이 뭘 커밋하든 내 눈엔 안 보여.
- **SERIALIZABLE** — REPEATABLE READ에 더해서 "이 트랜잭션들을 어떤 순서로 줄 세워도 이 결과가 나올 수 없다"를 감지하면 한쪽을 에러로 죽여.

설정은 이렇게:

```sql
BEGIN ISOLATION LEVEL REPEATABLE READ;
SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;
```

---

**User:**
REPEATABLE READ면 phantom read 생기는 거 아냐? 교과서엔 그렇게 나오던데. 표에는 PG는 안 된다고 써놨네.

---

**Assistant:**
표준 기준으로는 맞아. SQL 표준의 REPEATABLE READ는 "이미 읽은 row는 안 바뀐다"까지만 보장하고 새 row가 끼어드는 phantom은 허용해. 그런데 PostgreSQL의 REPEATABLE READ는 표준보다 강해. 이름만 빌려 쓴 거고 실체는 **스냅샷 격리(Snapshot Isolation)**야.

왜 phantom이 안 생기냐면, 스냅샷이 "row 몇 개"를 잠그는 게 아니라 "이 시점에 커밋된 트랜잭션 집합"을 통째로 고정하기 때문이야. 아까 대충 넘어갔는데 제대로 보면:

```
스냅샷 = { xmin 경계, xmax 경계, 진행 중인 xid 목록 }   ← 첫 쿼리 시점에 한 번 찍음

tuple이 나한테 보이려면
  ① tuple.xmin 트랜잭션이 내 스냅샷 기준 "커밋 완료" 이고
  ② tuple.xmax 가 0 이거나, xmax 트랜잭션이 내 스냅샷 기준 "아직 커밋 안 됨"
```

| tuple 상태 | xmin | xmax | 내 스냅샷(xid 100, 진행중 {98}) 기준 |
|---|---|---|---|
| 옛날에 INSERT, 안 건드림 | 50 | 0 | 보임 |
| 옛날에 INSERT, xid 98이 UPDATE 중 | 50 | 98 | 보임 (98은 아직 커밋 안 된 걸로 취급) |
| xid 98이 만든 새 버전 | 98 | 0 | 안 보임 |
| xid 101이 INSERT (내 시작 이후) | 101 | 0 | 안 보임 → **phantom 없음** |
| xid 70이 DELETE 완료 | 50 | 70 | 안 보임 (dead tuple 후보) |

넷째 줄이 포인트야. 내 스냅샷 이후에 시작한 트랜잭션이 INSERT한 row는 xmin이 내 경계 밖이라 절대 안 보여. 같은 조건으로 두 번 검색해도 개수가 같아. 그래서 phantom이 막히는 거고, PostgreSQL 공식 문서의 격리 수준 표에도 phantom read 칸에 "Allowed, but not in PG"라고 써 있어.

대신 스냅샷 격리라서 생기는 다른 일이 있어. **같은 row를 두 세션이 갱신할 때**:

```sql
-- 세션 A
BEGIN ISOLATION LEVEL REPEATABLE READ;
SELECT status FROM orders WHERE id = 7;   -- 'pending' (여기서 스냅샷 확정)

-- 세션 B
BEGIN ISOLATION LEVEL REPEATABLE READ;
UPDATE orders SET status = 'paid' WHERE id = 7;   -- row lock 획득, 아직 커밋 안 함

-- 세션 A
UPDATE orders SET status = 'cancelled' WHERE id = 7;   -- B의 row lock 때문에 대기

-- 세션 B
COMMIT;

-- 세션 A (대기에서 깨어남)
-- ERROR:  could not serialize access due to concurrent update
-- B가 COMMIT 대신 ROLLBACK 했다면 A의 UPDATE는 그대로 진행된다
ROLLBACK;
```

READ COMMITTED였으면 A는 B가 커밋한 새 버전을 다시 읽어서 그 위에 UPDATE를 얹었을 거야. REPEATABLE READ는 "내 스냅샷에 없는 버전 위에는 못 쓴다"가 원칙이라 에러를 내. 이게 SQLSTATE 40001, serialization failure야.

그래도 REPEATABLE READ가 못 막는 게 하나 남아 — serialization anomaly. 이건 SERIALIZABLE 얘기할 때.

---

**User:**
그럼 SERIALIZABLE은 뭘 더 막는 거야? 우리처럼 주문이랑 재고 다루면 그걸 써야 하는 거야?

---

**Assistant:**
REPEATABLE READ가 못 막는 대표 케이스가 **write skew**야. 두 트랜잭션이 각자 읽은 건 안 바뀌었는데, 서로 상대가 쓴 걸 못 본 채로 결정을 내려서 합치면 말이 안 되는 결과가 나오는 것.

주문 서비스 예로 하면 "재고 확인 후 주문 생성":

```
상품 X 재고 1개. 두 손님이 동시에 주문.

세션 A (REPEATABLE READ)                   세션 B (REPEATABLE READ)
SELECT count(*) FROM orders                SELECT count(*) FROM orders
 WHERE product_id=X AND status='pending'    WHERE product_id=X AND status='pending'
 → 0  (재고 1 > 0, 주문 가능)                → 0  (재고 1 > 0, 주문 가능)
INSERT INTO orders (product_id=X, ...)
                                           INSERT INTO orders (product_id=X, ...)
COMMIT                                     COMMIT
                                           → 재고는 1개인데 pending 주문이 2건
```

두 세션이 서로 다른 row를 INSERT했으니까 row 충돌은 없어. 각자 스냅샷 안에서는 완벽히 일관돼. 그런데 A→B 순서로 돌렸어도, B→A 순서로 돌렸어도 두 번째 놈은 count=1을 봤을 테니 이 결과는 어떤 순차 실행으로도 안 나와. 이게 serialization anomaly.

SERIALIZABLE은 이걸 **SSI(Serializable Snapshot Isolation)** 로 잡아. 락으로 막는 게 아니라:

1. 각 트랜잭션이 **뭘 읽었는지**를 predicate lock(SIReadLock)으로 기록해 둔다. 실제로 뭘 막는 락이 아니라 "여길 읽었다"는 흔적이다.
2. 남이 그 읽은 범위에 쓰면 rw-conflict(읽기→쓰기 의존)로 표시한다.
3. 이런 의존이 위험한 모양(순환 후보)으로 얽히면 그중 하나를 `ERROR: could not serialize access due to read/write dependencies among transactions`로 죽인다.

그러니까 위 예에서는 A와 B 중 나중에 커밋하려는 쪽이 40001로 실패해. REPEATABLE READ보다 더 기다리는 지점은 없고, 대신 abort가 늘어.

쓸지 말지는:
- 재고·잔액·좌석처럼 "읽고 판단해서 쓰는" 불변식이 있으면 SERIALIZABLE이 제일 단순한 해법이야. 앱에서 매번 `SELECT ... FOR UPDATE`를 걸거나 별도 락용 row를 두는 대신 DB가 잡아주니까.
- 대신 **재시도가 필수**야. 정상 상황에서도 abort가 나니까 재시도 없이 쓰면 그냥 에러 많은 서비스가 돼.
- 조회 위주 트랜잭션은 READ COMMITTED에 두고, 불변식이 걸린 쓰기 트랜잭션만 SERIALIZABLE로 올리는 식으로 섞어 쓰는 경우가 많아.

---

**User:**
serialization failure 나면 어떻게 해?

---

**Assistant:**
SQLSTATE 40001이 오면 트랜잭션을 재시도하면 된다. 실패한 트랜잭션은 이미 롤백된 상태니까 BEGIN부터 다시 돌리면 되고, 두 번째엔 상대 트랜잭션이 끝나 있으니 대개 통과해. 앱 쪽에서 40001을 잡아서 다시 돌리는 게 전부야.

---

**User:**
알겠어. 이제 VACUUM 쪽인데, 우리 orders 테이블은 하루에 약 300만 row가 늘고, autovacuum 기본 설정 그대로 쓰고 있다. status 바뀔 때마다 UPDATE도 치니까 bloat 걱정되는데, autovacuum이 정확히 뭘 하는 거야?

---

**Assistant:**
autovacuum은 백그라운드에서 테이블마다 "dead tuple이 충분히 쌓였나" 보다가 VACUUM(그리고 ANALYZE)을 대신 돌려주는 데몬이야. 먼저 dead tuple이 어떻게 생기고 어떻게 없어지는지:

```
UPDATE orders SET status='paid' WHERE id=7   (xid 120)

  [v1: xmin=50, xmax=0]  ──UPDATE──▶  [v1: xmin=50, xmax=120]   ← 옛 버전
                                      [v2: xmin=120, xmax=0]    ← 새 버전
                                                │
        xid 120 커밋 + v1을 볼 수 있는 스냅샷이 전부 사라짐
                                                ▼
                                      [v1: dead tuple]          ← 공간만 차지
                                                │ VACUUM
                                                ▼
                                      [빈 공간: 같은 페이지 안에서 재사용 가능]
```

VACUUM이 하는 일:
- dead tuple을 페이지에서 지우고 그 공간을 **재사용 가능**으로 표시(free space map 갱신). 파일 크기를 줄여서 OS에 돌려주지는 않아(맨 끝의 완전히 빈 페이지 정도만 잘라냄).
- 인덱스에서 dead tuple을 가리키는 엔트리 제거
- visibility map 갱신
- 오래된 xid를 freeze해서 트랜잭션 ID wraparound 방지

**bloat**는 dead tuple이 VACUUM보다 빨리 쌓여서 테이블·인덱스가 실제 데이터보다 훨씬 커진 상태야. 한번 커진 파일은 일반 VACUUM으론 안 줄어들고, 새 row가 그 빈 자리를 채워가면서 서서히 흡수하는 식이야.

autovacuum이 언제 뛰는지는 기본값 기준:

```
dead tuple 수 > autovacuum_vacuum_threshold(50) + autovacuum_vacuum_scale_factor(0.2) × 테이블 row 수
```

즉 테이블의 20%가 dead tuple이 될 때까지 기다린다는 뜻이야. 작은 테이블엔 괜찮은데 큰 테이블엔 너무 느슨해. row가 5,000만 개면 dead tuple이 1,000만 개 쌓여야 한 번 돈다는 거니까.

autovacuum이 돌아도 못 치우는 경우도 있어: 오래 열려 있는 트랜잭션(또는 idle in transaction 세션)이 있으면 그 트랜잭션의 스냅샷이 아직 옛 버전을 볼 수 있으니까 VACUUM이 dead tuple을 dead로 판정 못 해. 실무에서 bloat의 흔한 원인이 이거야.

지금 상태는 이걸로 봐:

```sql
SELECT relname, n_live_tup, n_dead_tup,
       round(100.0 * n_dead_tup / nullif(n_live_tup + n_dead_tup, 0), 1) AS dead_pct,
       last_autovacuum, autovacuum_count
  FROM pg_stat_user_tables
 WHERE relname = 'orders';
```

---

**User:**
잠깐, 아까 VACUUM 돌면 그 테이블 못 읽는다고 했잖아. 그럼 운영 중엔 VACUUM 못 돌리는 거야? 우린 24시간 주문 받는데.

---

**Assistant:**
아니, 아까 그 말은 틀렸어. 정정한다 — 일반 VACUUM은 SHARE UPDATE EXCLUSIVE 락만 잡아서 읽기·쓰기를 막지 않는다. 읽기·쓰기를 막는 것은 VACUUM FULL(ACCESS EXCLUSIVE 락)뿐이다.

| 명령 | 잡는 락 | SELECT | INSERT/UPDATE/DELETE | 실제로 막는 것 |
|---|---|---|---|---|
| `VACUUM` / autovacuum | SHARE UPDATE EXCLUSIVE | 됨 | 됨 | 다른 VACUUM·ANALYZE, CREATE INDEX, 대부분의 ALTER TABLE |
| `VACUUM FULL` | ACCESS EXCLUSIVE | 안 됨 | 안 됨 | 전부 (테이블을 통째로 새로 씀) |

그러니까 autovacuum이 운영 중에 계속 도는 건 정상이고, 그래야 해. 오히려 위에서 말한 "20% 쌓일 때까지 기다리는" 기본값이 더 문제지. 24시간 서비스면 VACUUM FULL은 사실상 못 쓰는 카드라고 보면 되고, 정말 파일 크기를 줄여야 하면 pg_repack 같은 확장으로 온라인 재작성하는 쪽이 현실적이야.

아까 "autovacuum이 한가할 때 돌게 둔다"고 한 것도 반쯤 잘못된 말이야. autovacuum은 한가한 때를 고르는 게 아니라 조건이 충족되면 바로 돌고, 대신 cost 기반 delay로 I/O를 조금씩 나눠 쓰면서 도는 거야.

---

**User:**
그럼 하루 300만 row씩 늘어나는 우리 테이블은 기본값으로는 안 되겠네? 뭘 바꿔야 해?

---

**Assistant:**
기본값으론 부족할 가능성이 높아. 하루 300만 row가 늘면 며칠만 지나도 수천만 row인데, scale factor 0.2면 dead tuple이 수백만~천만 개 쌓여야 한 번 도는 셈이니까. status UPDATE까지 있으면 그 사이에 bloat이 계속 자라.

보통 큰 테이블은 **테이블 단위로** 비율을 낮추고 절대값 threshold로 제어해:

```sql
ALTER TABLE orders SET (
  autovacuum_vacuum_scale_factor  = 0.01,   -- 1%
  autovacuum_vacuum_threshold     = 100000,
  autovacuum_analyze_scale_factor = 0.005
);
```

이 숫자가 정답은 아니고, 위에서 준 `pg_stat_user_tables` 쿼리로 dead_pct랑 autovacuum_count가 어떻게 움직이는지 보면서 조정하는 거야. 목표는 "dead tuple 비율이 한 자릿수 %에서 유지되고 autovacuum이 자주·짧게 돈다"야.

같이 볼 것:
- PostgreSQL 13 이상이면 INSERT만으로도 autovacuum이 뛰는 조건이 따로 있어(`autovacuum_vacuum_insert_scale_factor`, 기본 0.2). 삽입 위주 테이블이니 이것도 같이 낮추는 게 좋아.
- 오래 열린 트랜잭션 확인(`pg_stat_activity`의 `xact_start`가 오래된 세션). 이게 있으면 설정을 아무리 낮춰도 못 치워.
- 파티셔닝. orders처럼 시간순으로 쌓이는 테이블은 월별 파티션으로 나누면 파티션 하나하나가 작아져서 autovacuum이 감당하기 쉬워지고, 오래된 데이터는 DROP PARTITION으로 dead tuple 없이 날릴 수 있어.
