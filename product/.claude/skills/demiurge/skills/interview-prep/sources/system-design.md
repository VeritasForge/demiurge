# System Design Interview Sources

> Build-time 검증 완료: 2026-04-10
> 에이전트 3개 조사 결과 병합 + 중복 제거

## Tier 1: Staff+ 레벨 필수 (실제 기출 + 실제 아키텍처)

| 소스 | URL 패턴 | 검색 쿼리 템플릿 | 정보 유형 | 커버리지 |
|------|----------|------------------|-----------|----------|
| Blind (TeamBlind) | teamblind.com/ | `site:teamblind.com {company} system design interview` | 실제 기출, 평가 기준, TC 정보 | Senior~Staff+ |
| LeetCode Discuss | leetcode.com/discuss/interview-question/system-design/ | `site:leetcode.com/discuss {company} system design` | 실제 기출 + 커뮤니티 솔루션 | 전 레벨 |
| interviewing.io | interviewing.io/ | `site:interviewing.io {company} system design` | Staff+ 면접관 모의면접, 녹화 영상 | Senior~Principal |
| 빅테크 Engineering Blogs | netflixtechblog.com/, uber.com/blog/engineering/, engineering.fb.com/ | `site:{company}techblog.com {topic}` | 실제 프로덕션 아키텍처 | Senior~Staff+ |
| Pragmatic Engineer | blog.pragmaticengineer.com/ | `site:blog.pragmaticengineer.com system design` | Staff+ 전략, 엔지니어링 문화 | Senior~Staff+ |

## Tier 2: 체계적 학습 플랫폼

| 소스 | URL 패턴 | 검색 쿼리 템플릿 | 정보 유형 | 가격 |
|------|----------|------------------|-----------|------|
| ByteByteGo | bytebytego.com/ | `site:bytebytego.com {topic}` | 시각적 아키텍처 다이어그램 | $79-149/yr |
| DesignGurus.io (Grokking) | designgurus.io/ | `Grokking {topic} interview` | 설계 문제 + 패턴별 분류 | $79-199+ |
| Hello Interview | hellointerview.com/ | `site:hellointerview.com {company} system design` | 무료 가이드 + 유료 코칭 | Free~Paid |
| InterviewReady (Gaurav Sen) | interviewready.io/ | `site:interviewready.io {topic}` | HLD+LLD, 실전 시뮬레이션 | $65 lifetime |
| Codemia | codemia.io/ | `site:codemia.io {topic}` | AI 피드백, 능동 연습 | Free~Premium |
| Educative.io | educative.io/ | `site:educative.io system design {topic}` | 인터랙티브 스케치패드 | $59/mo |

## Tier 3: 무료 학습 자료

| 소스 | URL 패턴 | 정보 유형 |
|------|----------|-----------|
| System Design Primer (GitHub) | github.com/donnemartin/system-design-primer (233K+ stars) | 바이블, Anki 카드, 개념 정리 |
| awesome-system-design-resources | github.com/ashishps1/awesome-system-design-resources | 큐레이션 링크 모음 |
| Tech Interview Handbook | techinterviewhandbook.org/system-design/ | 접근 프레임워크 + 전략 |
| High Scalability Blog | highscalability.com | 실제 아키텍처 케이스 스터디 아카이브 |

## 커뮤니티 / SNS

| 소스 | URL 패턴 | 검색 쿼리 템플릿 | 특화 |
|------|----------|------------------|------|
| Reddit r/SystemDesign | reddit.com/r/SystemDesign | `site:reddit.com/r/SystemDesign "{company}" interview` | 설계 토론, 모의 연습 |
| Reddit r/ExperiencedDevs | reddit.com/r/ExperiencedDevs | `site:reddit.com/r/ExperiencedDevs "system design" interview` | Senior+ 경험 |
| Glassdoor | glassdoor.com/Interview/ | `{company} system design site:glassdoor.com` | 면접 프로세스, 난이도 |

## YouTube

| 소스 | URL | 특화 | Staff+ 적합도 |
|------|-----|------|--------------|
| ByteByteGo | youtube.com/@ByteByteGo | 프로 애니메이션, 개념 빠른 파악 | ★★★☆☆ |
| Gaurav Sen | youtube.com/@gaborsen | 분산 시스템 기초, 직관 형성 | ★★☆☆☆ |
| Hussein Nasser | youtube.com/@haborosam | DB/네트워크 딥다이브 | ★★★★☆ |
| Exponent | youtube.com/@tryexponent | 모의 시스템 디자인 면접 시연 | ★★★☆☆ |
| System Design Interview (SDI) | youtube.com/@SystemDesignInterview | 단계별 설계 워크쓰루 | ★★★☆☆ |

## 뉴스레터

| 소스 | URL | 주기 | 특화 |
|------|-----|------|------|
| ByteByteGo Newsletter | blog.bytebytego.com | Weekly | 시스템 설계 시각적 설명 |
| System Design Newsletter (Neo Kim) | newsletter.systemdesign.one | Weekly | 실제 회사 아키텍처 딥다이브 |
| Pragmatic Engineer | newsletter.pragmaticengineer.com | Weekly | Staff+ 전략, 엔지니어링 문화 |

## 한국 소스

| 소스 | URL 패턴 | 검색 쿼리 템플릿 | 정보 유형 | 품질 |
|------|----------|------------------|-----------|------|
| 한국 기술블로그 (Naver D2, Kakao Tech 등) | d2.naver.com/, tech.kakao.com/, engineering.linecorp.com/ko/ | `site:tech.kakao.com 아키텍처 설계` | 실제 프로덕션 아키텍처 사례 | VERY HIGH |
| 기술블로그 어그리게이터 | techblogposts.com/ko | 주제별 탐색 | 한국 기업 기술블로그 모음 | HIGH |
| 인프런 | inflearn.com/ | `시스템 디자인` | 유료 강의 (실리콘밸리 아저씨들, 미국달팽이) | HIGH |
| F-Lab | f-lab.ai/ | `시스템 디자인 면접` | 1:1 멘토링, 인사이트 아티클 | HIGH |
| GitHub 한국 스터디 | github.com/Meet-Coder-Study/book-system-design-interview | 직접 탐색 | Alex Xu 책 챕터별 스터디 노트 | HIGH |
| 벨로그 | velog.io/ | `시스템 설계 면접`, `시스템 디자인 인터뷰` | 북 스터디 노트, 면접 후기 | HIGH |
| WorkingUS | workingus.com/ | `system design interview` | 한국인 미국 빅테크 면접 경험 | MEDIUM-HIGH |
| 원티드 | wanted.co.kr/ | `시스템 설계 면접` | 면접 준비 웨비나/이벤트 | MEDIUM-HIGH |
| OKKY | okky.kr/ | `시스템 설계 면접` | Q&A, 기술 토론 | MEDIUM-HIGH |
| YouTube (실리콘밸리 아저씨들, 미국달팽이) | YouTube 검색 | `시스템 디자인 면접` | 한국어 시스템 디자인 강의 | MEDIUM-HIGH |
