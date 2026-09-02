# 대화 기록: AWS IAM Role과 Trust Policy
> 아래는 사용자와 AI 어시스턴트의 실제 대화 기록이다. 턴 순서대로 기록됨.

**User:**
IAM Role이 User랑 정확히 뭐가 다른 거야? 팀장이 자꾸 "access key 만들지 말고 Role 써라"라고 하는데, 나는 그냥 키 발급받아서 `~/.aws/credentials`에 넣으면 되는 거 아닌가 싶거든. 이거 왜 이래?

---

**Assistant:**
핵심 차이는 **자격증명을 누가, 얼마나 오래 들고 있느냐**야.

## User vs Role

| | IAM User | IAM Role |
|---|---|---|
| 자격증명 | 영구 access key / secret key | 자기 자격증명 없음 |
| 쓰는 방법 | 키를 파일·환경변수에 넣음 | 누군가 "assume"하면 그때 임시 자격증명 발급 |
| 만료 | 비활성화 전까지 무기한 | 세션 만료 시 자동 무효 |
| 유출됐을 때 | 키 회수 전까지 계속 유효 | 만료되면 저절로 끝 |

Role은 자기 키가 없어. 대신 STS(Security Token Service)한테 "이 Role 할래"라고 하면 STS가 **임시 자격증명**(AccessKeyId + SecretAccessKey + SessionToken)을 만들어 준다. Role의 세션은 최대 1시간까지만 유지된다. 그래서 키가 새어 나가도 피해가 시간으로 잘려.

## AssumeRole 흐름

```
[호출자: User / EC2 / Lambda / 다른 계정 / GitHub Actions]   [STS]                   [Role 정의]
     |                                                      |                           |
     |-- sts:AssumeRole(RoleArn) -------------------------->|                           |
     |                                                      |-- trust policy 조회 ----->|
     |                                                      |   "이 호출자를 신뢰하나?"    |
     |<-- 임시 자격증명(AccessKeyId, SecretAccessKey, --------|<--------------------------|
     |    SessionToken, 만료시각)                             |                           |
     |== 임시 자격증명으로 S3/EC2 API 호출 ==> permission policy로 허용 여부 판단
```

Role에는 정책이 두 종류 붙어. **trust policy**는 "누가 이 Role을 assume할 수 있는가"를 정하고, **permission policy**는 "assume한 다음에 무엇을 할 수 있는가"를 정해. 둘은 완전히 별개라서, trust policy에 들어 있어도 permission policy가 비어 있으면 아무것도 못 하고, 반대로 permission policy가 Admin이어도 trust policy에 없으면 assume 자체가 안 돼.

팀장 말은 결국 "영구 키를 어디에도 두지 말자"는 거야. EC2, Lambda, CI 전부 Role로 임시 키만 받아 쓰면 `~/.aws/credentials`가 git에 올라가는 사고 자체가 없어져.

---

**User:**
오케이. 그럼 trust policy가 정확히 뭐야? JSON으로 어떻게 생겼는데? Principal이라는 게 자꾸 나오던데 그게 "누가"에 해당하는 거야?

---

**Assistant:**
맞아. trust policy는 Role에 붙는 JSON 문서고, `Principal`이 바로 "누가"야.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::111122223333:role/deploy-runner"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
```

- `Principal`: 이 Role을 assume할 수 있는 주체. 타입이 몇 가지 있어.
  - `AWS`: 계정 root(`arn:aws:iam::111122223333:root`), IAM User, IAM Role
  - `Service`: `ec2.amazonaws.com`, `lambda.amazonaws.com` 같은 AWS 서비스
  - `Federated`: SAML IdP나 OIDC provider (GitHub Actions가 여기 해당)
- `Action`: 거의 항상 `sts:AssumeRole`. OIDC면 `sts:AssumeRoleWithWebIdentity`, SAML이면 `sts:AssumeRoleWithSAML`. 예제에 따라 `sts:TagSession`이 같이 붙어 있는 걸 볼 수도 있는데 지금은 신경 안 써도 돼.
- `Condition`: 선택. "이 계정에서 왔을 때만", "이 repo에서 왔을 때만" 같은 추가 조건.

trust policy에는 `Resource`가 없어. Role 자체가 리소스니까 — 이 문서가 붙어 있는 Role이 곧 대상이야. 그래서 콘솔에서 Role 만들 때 "Trusted entity"를 고르는 화면이 사실상 이 JSON의 `Principal`을 채우는 UI야.

---

**User:**
Role trust policy에 Group 넣으면 안 돼? 우리 개발자들 다 `Developers` 그룹에 묶여 있어서 그룹 ARN 넣으면 편할 것 같은데.

---

**Assistant:**
안 돼. IAM Group은 Principal이 될 수 없어. 실제로 넣어보면 이렇게 거부돼.

```
$ aws iam update-assume-role-policy --role-name dev-role --policy-document file://trust.json
An error occurred (MalformedPolicyDocument) when calling the UpdateAssumeRolePolicy operation:
Invalid principal in policy: "AWS":"arn:aws:iam::111122223333:group/Developers"
```

이유는 Group이 **자격증명을 가진 주체(identity)가 아니라 User에 정책을 묶어 주는 컨테이너**라서야. API를 호출하는 건 항상 User이거나 Role 세션이지, Group이 호출하는 일은 없어. 그래서 STS 입장에서 "Group이 assume한다"는 상황 자체가 성립을 안 해.

## 그럼 어떻게 하냐

trust policy에는 계정 root를 넣고, "누가 실제로 assume하나"는 Group에 붙은 permission policy로 통제해.

dev-role의 trust policy:

```json
{ "Version": "2012-10-17",
  "Statement": [{ "Effect": "Allow",
                  "Principal": { "AWS": "arn:aws:iam::111122223333:root" },
                  "Action": "sts:AssumeRole" }] }
```

Developers 그룹에 붙이는 permission policy:

```json
{ "Version": "2012-10-17",
  "Statement": [{ "Effect": "Allow",
                  "Action": "sts:AssumeRole",
                  "Resource": "arn:aws:iam::111122223333:role/dev-role" }] }
```

`root`를 Principal에 넣으면 "이 계정 안의 누군가"까지만 허용한 거고, 그 계정 안에서 실제로 누구인지는 각자의 permission policy에 `sts:AssumeRole`이 있느냐로 갈려. 그러니까 그룹에 사람을 넣고 빼는 것만으로 assume 가능 여부가 바뀌어 — 네가 원한 효과는 이렇게 얻는 거야.

## 여기서 두 정책 차이가 다시 나온다

| | Trust policy | Permission policy |
|---|---|---|
| 붙는 곳 | Role 자체 (Role당 정확히 1개) | User / Group / Role (여러 개 가능) |
| 답하는 질문 | 누가 이 Role을 assume할 수 있나 | 이 주체가 무슨 API를 호출할 수 있나 |
| 종류 | 리소스 기반 정책 | 자격증명 기반 정책 |
| `Principal` 필드 | 있음 (필수) | 없음 |
| `Resource` 필드 | 없음 | 있음 |
| 평가 시점 | `AssumeRole` 호출 순간 | 임시 자격증명으로 실제 API 호출할 때 |

위 예제에서 `sts:AssumeRole`이 양쪽 JSON에 다 등장하는데, trust policy 쪽은 "허용해 줄 대상"으로, permission policy 쪽은 "호출할 수 있는 행동"으로 쓰인 거야. 같은 문자열이지만 방향이 반대야.

---

**User:**
Permission boundary는 뭐야? 콘솔에서 Role 만들 때 맨 아래 있던데.

---

**Assistant:**
그 주체가 가질 수 있는 권한의 **상한선**이야. permission policy가 아무리 넓어도 boundary 밖의 권한은 유효하지 않아. 주로 "개발자가 Role을 직접 만들 수는 있지만 Admin 권한은 못 만들게" 할 때 쓰고, 지금 단계에서는 안 건드려도 돼.

---

**User:**
그럼 실전으로 가보자. 우리는 계정이 3개(dev/stage/prod)이고 배포는 GitHub Actions로만 한다. 지금은 각 계정에 IAM User 만들어서 access key를 GitHub secrets에 넣어놨거든. 이걸 Role로 바꾸려면 어떻게 해? Terraform으로 짜줘.

---

**Assistant:**
GitHub secrets에 access key 넣는 거 — 딱 팀장이 하지 말라던 거네. GitHub Actions는 **OIDC**로 Role을 assume할 수 있어서 키가 아예 필요 없어.

```
[GitHub Actions job]                          [AWS STS]                    [IAM]
     |                                             |                          |
     |  1. GitHub이 job용 OIDC 토큰 발급              |                          |
     |     (repo/branch/env 정보가 claim에 있음)      |                          |
     |-- 2. AssumeRoleWithWebIdentity(토큰+RoleArn) ->|                          |
     |                                             |-- 3. trust policy 확인 -->|
     |                                             |   Federated 주체가 우리     |
     |                                             |   OIDC provider? aud/sub  |
     |                                             |   조건 통과?               |
     |<-- 4. 임시 자격증명 --------------------------|<-------------------------|
     |== 5. 임시 자격증명으로 ECS/S3 배포 API 호출 ==>
```

핵심은 3번이야. trust policy의 `Principal`이 `Federated` 타입으로 OIDC provider를 가리키고, `Condition`으로 "어느 repo, 어느 브랜치에서 온 토큰인지"를 검사해. `sub` 조건을 빼먹으면 **GitHub의 모든 repo**가 이 Role을 assume할 수 있게 되니까 절대 빼면 안 돼.

## Terraform

OIDC provider(`token.actions.githubusercontent.com`)는 계정당 하나만 있으면 되고 이미 만들어져 있다고 가정할게. 없으면 `aws_iam_openid_connect_provider`로 먼저 만들어. 참고로 요즘은 AWS가 GitHub 같은 주요 provider의 인증서를 자체 신뢰 저장소로 검증해서 thumbprint를 손으로 안 넣어도 돼.

```hcl
data "aws_iam_openid_connect_provider" "github" {
  url = "https://token.actions.githubusercontent.com"
}

data "aws_iam_policy_document" "github_actions_assume" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRoleWithWebIdentity"]

    principals {
      type        = "Federated"
      identifiers = [data.aws_iam_openid_connect_provider.github.arn]
    }

    # 토큰의 audience가 STS를 향한 것인지
    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:aud"
      values   = ["sts.amazonaws.com"]
    }

    # 어느 repo의 어느 브랜치에서 온 job인지 — 이 조건이 없으면 모든 repo가 assume 가능
    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:sub"
      values   = ["repo:my-org/my-service:ref:refs/heads/main"]
    }
  }
}

resource "aws_iam_role" "github_actions_deploy" {
  name               = "github-actions-deploy"
  assume_role_policy = data.aws_iam_policy_document.github_actions_assume.json
}
```

`my-org/my-service`는 실제 repo로 바꾸고, 브랜치가 아니라 GitHub environment 단위로 묶고 싶으면 `sub` 값을 `repo:my-org/my-service:environment:prod` 형태로 바꾸면 돼. permission policy(ECS 업데이트, S3 업로드 등)는 별도로 `aws_iam_role_policy`로 붙이고.

워크플로 쪽은 `aws-actions/configure-aws-credentials`에 `role-to-assume`만 주면 되고, job에 `permissions: id-token: write`가 있어야 GitHub이 OIDC 토큰을 발급해 줘.

---

**User:**
근데 아까 세션이 최대 1시간이라 했잖아. 12시간까지 되는 거 아냐? 콘솔에서 Role 만들 때 Maximum session duration 슬라이더가 12시간까지 올라가던데.

---

**Assistant:**
맞다, 정정한다 — Role의 MaxSessionDuration은 1시간~12시간 사이로 설정 가능하고, 다만 role chaining(역할이 또 다른 역할을 assume)일 때는 1시간으로 제한된다.

- Role 정의에 `MaxSessionDuration`이 있고 기본값이 1시간이라서, 내가 기본값을 상한으로 잘못 말했어. 콘솔 슬라이더 그대로 1~12시간이 맞아.
- `AssumeRole` 호출할 때 `DurationSeconds`로 세션 길이를 요청하는데, 이 값이 Role의 `MaxSessionDuration`을 넘으면 STS가 거부해. 요청 안 하면 1시간.
- **role chaining**은 예외야. Role 세션의 임시 자격증명으로 또 다른 Role을 assume하면 그 두 번째 세션은 `MaxSessionDuration`을 얼마로 잡아놨든 최대 1시간이야. `DurationSeconds`에 그 이상을 넣으면 에러 나.

Terraform에서는 `aws_iam_role`의 `max_session_duration`(초 단위, 3600~43200)으로 잡아. 위에 짜준 코드는 그 인자를 안 줬으니 기본 1시간이고, 배포 job은 보통 그 안에 끝나니까 그대로 둬도 돼.

---

**User:**
계정이 3개니까 이것도 궁금한데, dev 계정에서 prod 계정 Role을 assume하는 건 어떻게 되는 거야? cross-account라는 게 그거지?

---

**Assistant:**
응. 구조는 같은데 **양쪽 계정이 각각 허락해야** 돼. 한쪽만 열어놓으면 `AccessDenied`야.

```
  dev 계정 111122223333                     prod 계정 999988887777
 +----------------------------+           +------------------------------------+
 | role/dev-runner            |           | role/prod-deployer                 |
 | [permission policy]        |  assume   | [trust policy]                     |
 |  Allow sts:AssumeRole      | --------> |  Principal.AWS = arn:aws:iam::     |
 |  Resource = prod의         |           |    111122223333:role/dev-runner    |
 |    role/prod-deployer ARN  |           |  Action = sts:AssumeRole           |
 |  "저기로 가도 된다"          |           | [permission policy] ECS/S3 배포 권한 |
 +----------------------------+           |  "저기서 와도 된다"                  |
                                          +------------------------------------+
```

- **prod 쪽(trust policy)**: "dev 계정의 `dev-runner` Role이 나를 assume해도 된다". Principal에 상대 계정의 Role ARN을 넣어. 계정 root(`arn:aws:iam::111122223333:root`)를 넣으면 dev 계정 전체를 신뢰하는 거라 범위가 훨씬 넓어져.
- **dev 쪽(permission policy)**: "`dev-runner`는 prod의 `prod-deployer`를 assume할 수 있다". `sts:AssumeRole` + Resource에 상대 Role ARN.

호출은 `aws sts assume-role --role-arn arn:aws:iam::999988887777:role/prod-deployer --role-session-name deploy-from-dev`. 응답으로 받은 `Credentials`를 환경변수에 넣으면 그때부터 prod 계정 권한으로 동작해. `aws sts get-caller-identity` 찍어보면 `Arn`이 `arn:aws:sts::999988887777:assumed-role/prod-deployer/deploy-from-dev`로 나와.

주의점 두 개:
1. dev 쪽 호출자가 이미 다른 Role을 assume해서 받은 임시 자격증명이면, 여기서 prod로 가는 건 role chaining이라 아까 말한 1시간 제한에 걸려.
2. trust policy에 `Condition`으로 `aws:PrincipalTag`를 거는 식으로 더 좁히는 팀도 있는데, 그건 태그 기반 설계를 잡을 때 다시 보자.

---

**User:**
그럼 우리 상황에선 GitHub Actions에서 prod 배포할 때, prod 계정에 OIDC Role을 직접 만드는 게 나아? 아니면 dev 계정 Role로 들어간 다음 prod로 cross-account assume 하는 게 나아?

---

**Assistant:**
**세 계정 각각에 OIDC provider + Role을 직접 만드는 쪽**을 권해.

- dev를 거쳐 prod로 가면 GitHub → dev Role → prod Role이라 role chaining이 돼서 prod 세션이 1시간에 묶이고, 경로도 하나 더 늘어.
- 직접 가면 prod의 trust policy 하나만 보면 "누가 prod에 배포할 수 있는지"가 끝나. 감사할 때 훨씬 명확해.
- dev 계정이 털렸을 때 prod로 넘어가는 다리가 없어.

계정마다 위에 짜준 Terraform을 그대로 쓰되 `sub` 조건만 다르게 가져가면 돼 — 예를 들어 dev는 `repo:my-org/my-service:ref:refs/heads/*`처럼 브랜치 전체를 `StringLike`로 열고, prod는 `repo:my-org/my-service:environment:prod`로 GitHub environment 승인 게이트를 거친 job만 받는 식으로. cross-account assume는 사람이 dev에서 prod 리소스를 잠깐 조회해야 할 때 같은 케이스에 따로 남겨두고.
