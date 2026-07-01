# GitHub 계정 2개 SSH 분리 설정

회사(heumlabs)와 개인(VeritasForge) GitHub 계정을 한 대의 PC에서 섞이지 않게 쓰기 위한 SSH·git 설정입니다. **어느 계정으로 push할지(SSH 키)** 와 **커밋에 어떤 이메일이 찍힐지(git 저자)** 를 폴더별로 자동으로 갈라줍니다.

---

## 왜 필요한가

GitHub는 회사·개인 계정이 모두 같은 서버(`github.com`)를 씁니다. 그래서 아무 설정이 없으면:

- SSH가 어느 키로 인증할지 몰라 엉뚱한 계정으로 push되거나 권한 거부가 납니다.
- 개인 저장소에 회사 이메일로 커밋이 올라가(잔디가 안 심기고 회사 메일이 공개로 노출) 버립니다.

이 설정은 두 문제를 **폴더 위치만으로** 자동 해결합니다.

---

## 구성 파일

| 파일 | 역할 | 비밀? |
|---|---|---|
| `~/.ssh/config` | 어느 계정에 어느 SSH 키를 쓸지 지정 | 아니오 |
| `~/.gitconfig` | 기본(회사) 커밋 저자 + `~/lab` 개인 전환 규칙 | 아니오 |
| `~/.gitconfig-personal` | 개인 폴더에서만 적용될 커밋 저자 | 아니오 |
| `~/.ssh/setup-github-ssh.sh` | 새 PC에서 위 3개를 재현하는 스크립트 | 아니오 |
| `~/.ssh/id_ed25519` | 회사 SSH 개인키 | **예 (반출 금지)** |
| `~/.ssh/veritas_id_ed25519` | 개인 SSH 개인키 | **예 (반출 금지)** |

---

## 계정 매핑

| 구분 | GitHub 사용자 | SSH 키 | SSH 호스트 | 프로젝트 폴더 | 커밋 이메일 |
|---|---|---|---|---|---|
| 🏢 회사 | `heum-jaeyoungcho` | `id_ed25519` | `github.com` (기본) | `~/workspace` | `jaeyoung.cho@heumlabs.io` |
| 👤 개인 | `VeritasForge` | `veritas_id_ed25519` | `github.com-personal` (별칭) | `~/lab` | `greenfrog@outlook.kr` |

회사가 기본이라 회사 저장소는 평범한 URL을 그대로 쓰고, 개인만 `-personal` 별칭을 붙입니다.

---

## 동작 원리

두 가지가 **독립적으로** 작동하며, 개인 작업이 올바르려면 둘 다 맞아야 합니다.

```
① SSH 별칭 → "어느 계정으로 push되나"        ② 폴더 위치 → "커밋에 어떤 이메일이 찍히나"
   git@github.com:...          → 회사 키          ~/workspace 아래 → 회사 이메일
   git@github.com-personal:... → 개인 키          ~/lab 아래       → 개인 이메일 (자동)
```

`~/.gitconfig`의 `includeIf "gitdir:~/lab/"` 규칙이, 작업 중인 저장소가 `~/lab` 아래일 때만 개인 설정을 덮어씁니다.

```
                  git 명령을 실행한 폴더는?
                          │
          ┌───────────────┴────────────────┐
     ~/lab 아래                        그 외 전부
          │                                │
  개인 이메일로 전환                  회사 이메일(기본)
  greenfrog@outlook.kr           jaeyoung.cho@heumlabs.io
```

---

## 이 PC에서 쓰는 법

```bash
# 회사 저장소 — 기본 URL 그대로, ~/workspace 아래에서
cd ~/workspace
git clone git@github.com:heumlabs/repo.git

# 개인 저장소 — -personal 별칭 사용, ~/lab 아래에서
cd ~/lab
git clone git@github.com-personal:VeritasForge/repo.git
```

이미 받아둔 개인 저장소가 있다면 remote만 별칭으로 바꿉니다.

```bash
cd ~/lab/기존저장소
git remote set-url origin git@github.com-personal:VeritasForge/repo.git
```

동작 확인:

```bash
ssh -T git@github.com            # → heum-jaeyoungcho 인사가 나오면 정상
ssh -T git@github.com-personal   # → VeritasForge 인사가 나오면 정상
```

(위 명령의 종료 코드는 1이지만, "GitHub는 셸 접속을 안 준다"는 정상 응답입니다.)

---

## 다른 PC에서 재현하기

개인키는 **복사하지 않습니다.** 각 PC에서 키를 새로 만들고 공개키만 GitHub에 등록합니다. 노트북을 잃어버려도 그 PC 키만 GitHub에서 지우면 되고, 다른 기기는 안전합니다.

### 1. 스크립트를 새 PC로 가져오기

```bash
# 예: 기존 PC에서 스크립트만 당겨오기 (개인키는 절대 가져오지 않음)
scp 기존PC:~/.ssh/setup-github-ssh.sh ~/
```

USB나 메신저로 파일을 옮기거나 내용을 복사해 저장해도 됩니다.

### 2. 새 PC에서 실행

```bash
bash ~/setup-github-ssh.sh
```

키 2개가 새로 생기고 `~/.ssh/config`·`~/.gitconfig`·`~/.gitconfig-personal`이 깔린 뒤, **등록할 공개키 2개**가 화면에 출력됩니다. 기존 파일이 있으면 `.bak.날짜`로 백업한 뒤 새로 씁니다.

### 3. 출력된 공개키를 GitHub에 등록

계정별로 각각 등록합니다.

- **회사 공개키** → 회사 계정으로 로그인 → <https://github.com/settings/keys> → New SSH key
- **개인 공개키** → 개인 계정으로 로그인 → 같은 페이지에서 등록

### 4. 확인

```bash
ssh -T git@github.com            # → 회사 계정 인사
ssh -T git@github.com-personal   # → 개인 계정 인사
```

---

## 환경이 다를 때 (커스터마이즈)

GitHub 사용자명·이메일·폴더가 다른 PC라면 `setup-github-ssh.sh` 맨 위 `===== 수정 =====` 변수만 고치면 됩니다.

```bash
WORK_EMAIL="jaeyoung.cho@heumlabs.io"   # 회사 이메일
WORK_NAME="heum-jaeyoungcho"            # 회사 커밋 이름
PERSONAL_EMAIL="greenfrog@outlook.kr"   # 개인 이메일
PERSONAL_NAME="VeritasForge"            # 개인 커밋 이름
WORK_DIR="$HOME/workspace"              # 회사 폴더
LAB_DIR="$HOME/lab"                     # 개인 폴더
```

- **커밋 이름만 바꾸고 싶으면** `~/.gitconfig`(회사)·`~/.gitconfig-personal`(개인)의 `name =` 줄만 수정하면 됩니다.
- **키에 비밀번호를 걸고 싶으면** 스크립트의 `ssh-keygen ... -N ""`에서 `-N ""`를 지우면 실행 중 물어봅니다. macOS는 keychain에 저장돼 이후엔 안 물어봅니다.

---

## 주의사항

- **개인키(`id_ed25519`, `veritas_id_ed25519`)를 기기 간에 복사하지 마세요.** 이 설정의 핵심은 PC마다 키를 새로 만드는 것입니다. 옮기는 건 스크립트 하나면 충분합니다.
- **개인 작업은 반드시 `~/lab` 아래 + `-personal` 별칭 두 가지를 함께** 지켜야 합니다. 하나만 지키면 커밋 이메일과 push 계정이 어긋납니다.
  - `~/lab`에 뒀지만 기본 URL로 clone → 커밋은 개인 이메일인데 push는 회사 키로 시도 → 권한 거부
  - 별칭은 맞췄지만 `~/workspace`에 둠 → push는 되지만 커밋에 회사 이메일이 박힘
- 스크립트는 여러 번 실행해도 안전합니다. 키가 이미 있으면 재사용하고 config는 백업 후 다시 씁니다.

---

## 트러블슈팅

| 증상 | 원인 / 해결 |
|---|---|
| `Permission denied (publickey)` | 공개키가 해당 GitHub 계정에 등록되지 않음. 위 3단계 재확인. |
| 개인 repo push가 회사 계정으로 나감 | remote가 기본 URL임. `git remote set-url origin git@github.com-personal:...`로 교체. |
| 커밋 이메일이 계속 회사 것 | 저장소가 `~/lab` 밖에 있음. `git config user.email`로 확인 후 폴더 위치 조정. |
| Linux/WSL에서 `Bad configuration option: UseKeychain` | 스크립트가 만드는 config엔 `IgnoreUnknown UseKeychain`이 있어 무시됩니다. 수동 작성한 macOS용 config를 쓰는 경우 이 줄을 추가하세요. |
