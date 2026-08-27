# Anti-Patterns (인라인 검증용)

readme-writer Phase 4(인라인 검증)에서 참조한다. 각 패턴을 탐지 신호로 매칭하여 위반 시 자동 수정한다.

## 안티패턴 매트릭스

| # | 패턴 | 탐지 신호 | 처방 | 적용 제외 |
|---|------|----------|------|----------|
| 1 | 모호한 설명 | Short Description이 "A tool for X", "Simple X", "X-related utility" 같은 일반 표현 | 구체 차별점·숫자 명시 ("60k+ stars", "real-time collaboration" 등) | - |
| 2 | 시각 자료 부재 | README에 `![](...)` 이미지 0개 + Application 그룹 | GIF/스크린샷/architecture diagram 최소 1개 권고 | Library, CLI (선택적) |
| 3 | 복잡한 설치 단계 | Installation 섹션이 10줄 초과 | copy-paste 가능한 한 줄로 압축 시도, 불가하면 단계마다 검증 명령 포함 | K8s operator, 멀티 GPU 환경 (정직성이 더 중요) |
| 4 | 플레이스홀더 예제 | 코드 블록에 `foo`/`bar`/`baz`/`example.com`/`<TODO>` 포함 | 실제 출력 포함한 진짜 예제로 교체 | - |
| 5 | 모든 내용 dump | README 라인 > 1000 또는 파일 > 500 KiB | `docs/` 디렉토리로 분리 + 링크 권고 | - |
| 6 | outdated 콘텐츠 | 5년 전 버전 명시 (`Node 10`, `Python 2`, `React 16` 등) | 최신 LTS 또는 maintained 버전으로 업데이트 | Legacy 명시 프로젝트 |
| 7 | 독자 배경 가정 | "당연히 X를 알 것", "obvious", "trivially" 같은 표현 | "처음 보는 사람" 가정 — 약자 풀네임 병기, 기본 개념 링크 | - |
| 8 | 불릿 남용 (비교성 콘텐츠) | 비교성 콘텐츠(`vs`, `compared to`, `차이점`) + 불릿 리스트만 | 표(table)로 변환 | - |

## Phase 4 인라인 검증 로직

각 패턴에 대해:
1. 탐지 신호로 매칭 시도 (정규식 또는 LLM 판별)
2. 매칭 시 → 처방 적용 (LLM이 직접 수정)
3. 적용 제외 그룹이면 → 경고만 콘솔에 출력, 수정 안 함
4. 수정 후 재검증 1회 (수정이 다른 패턴을 유발했는지 확인)
5. 재검증 후에도 위반 남으면 → 콘솔에 "수동 검토 필요" 경고 + README 상단 HTML 주석으로 표시

## 출처 단서

본 안티패턴 표는 다음 출처 합성:
- DEV (iris1031): GitHub README Best Practices 2026
- Tilburg Science Hub: README Best Practices
- Make a README: makeareadme.com
- GitHub Docs: About READMEs (긴 콘텐츠 분리 권고)

⚠️ 단일 출처 의존 위험: 패턴 3의 "한 줄 설치" 처방은 K8s/GPU 환경에서 부적합. 적용 범위 단서를 반드시 확인하라.
