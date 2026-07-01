#!/usr/bin/env bash
# ============================================================
#  setup-github-ssh.sh
#  새 PC에서 회사/개인 GitHub 분리 설정을 재현한다.
#
#  하는 일:
#   1) SSH 키쌍 2개를 "새로" 생성 (개인키는 이 PC 밖으로 나가지 않음)
#      - 이미 같은 이름의 키가 있으면 건드리지 않고 재사용
#   2) ~/.ssh/config, ~/.gitconfig, ~/.gitconfig-personal 작성
#      - 기존 파일이 있으면 .bak 으로 백업 후 새로 씀
#   3) 회사/개인 프로젝트 폴더 생성 (~/workspace, ~/lab)
#   4) GitHub에 등록할 공개키 2개를 출력
#
#  사용법:  bash setup-github-ssh.sh
# ============================================================
set -euo pipefail

# ===== 필요하면 이 부분만 수정 =====
WORK_EMAIL="jaeyoung.cho@heumlabs.io"     # 회사
WORK_NAME="heum-jaeyoungcho"
WORK_KEY="$HOME/.ssh/id_ed25519"

PERSONAL_EMAIL="greenfrog@outlook.kr"     # 개인
PERSONAL_NAME="VeritasForge"
PERSONAL_KEY="$HOME/.ssh/veritas_id_ed25519"

WORK_DIR="$HOME/workspace"                # 회사 프로젝트 폴더 (기본 계정)
LAB_DIR="$HOME/lab"                       # 개인 프로젝트 폴더 (개인으로 자동 전환)
# ===================================

HOSTTAG="$(hostname -s 2>/dev/null || hostname 2>/dev/null || echo pc)"
STAMP="$(date +%Y%m%d-%H%M%S 2>/dev/null || echo bak)"

mkdir -p "$HOME/.ssh"
chmod 700 "$HOME/.ssh"

backup() { [ -f "$1" ] && cp "$1" "$1.bak.$STAMP" && echo "  (기존 $1 백업함)"; return 0; }

gen_key() {
  # $1=키경로 $2=이메일 $3=라벨
  if [ -f "$1" ]; then
    echo "• $3 키 이미 있음 → 재사용: $1"
  else
    echo "• $3 키 생성: $1"
    # 무암호 키. 비밀번호를 걸고 싶으면 아래 줄에서 -N "" 를 지우면 실행 중 물어봄.
    ssh-keygen -t ed25519 -f "$1" -C "$2 ($HOSTTAG)" -N ""
  fi
}

echo "==> 1. SSH 키 준비"
gen_key "$WORK_KEY" "$WORK_EMAIL" "회사"
gen_key "$PERSONAL_KEY" "$PERSONAL_EMAIL" "개인"

echo
echo "==> 2. ~/.ssh/config 작성"
backup "$HOME/.ssh/config"
cat > "$HOME/.ssh/config" <<EOF
# 회사(heumlabs)를 기본 github.com 으로, 개인(veritas)은 별칭 사용
Host *
  IgnoreUnknown UseKeychain
  AddKeysToAgent yes
  UseKeychain yes
  IdentitiesOnly yes

# 기본: 회사 GitHub  →  git@github.com:heumlabs/repo.git
Host github.com
  HostName github.com
  User git
  IdentityFile $WORK_KEY

# 개인 GitHub  →  git@github.com-personal:$PERSONAL_NAME/repo.git
Host github.com-personal
  HostName github.com
  User git
  IdentityFile $PERSONAL_KEY
EOF
chmod 600 "$HOME/.ssh/config"

echo "==> 3. ~/.gitconfig 작성 (회사 기본 + ~/lab 개인 자동전환)"
backup "$HOME/.gitconfig"
cat > "$HOME/.gitconfig" <<EOF
[user]
	name = $WORK_NAME
	email = $WORK_EMAIL

[includeIf "gitdir:$LAB_DIR/"]
	path = ~/.gitconfig-personal
EOF

backup "$HOME/.gitconfig-personal"
cat > "$HOME/.gitconfig-personal" <<EOF
[user]
	name = $PERSONAL_NAME
	email = $PERSONAL_EMAIL
EOF

echo "==> 4. 프로젝트 폴더 생성"
mkdir -p "$WORK_DIR" "$LAB_DIR"
echo "  $WORK_DIR (회사)  /  $LAB_DIR (개인)"

echo
echo "================ 다음 할 일: 공개키 등록 ================"
echo
echo "[회사] 아래 공개키를 회사 GitHub 계정에 등록"
echo "       https://github.com/settings/keys (회사 계정 로그인 상태에서)"
echo "-------------------------------------------------------"
cat "$WORK_KEY.pub"
echo "-------------------------------------------------------"
echo
echo "[개인] 아래 공개키를 개인 GitHub 계정에 등록"
echo "       https://github.com/settings/keys (개인 계정 로그인 상태에서)"
echo "-------------------------------------------------------"
cat "$PERSONAL_KEY.pub"
echo "-------------------------------------------------------"
echo
echo "등록이 끝나면 아래로 확인:"
echo "  ssh -T git@github.com            # → 회사 계정 인사가 나와야 함"
echo "  ssh -T git@github.com-personal   # → 개인 계정 인사가 나와야 함"
echo
echo "clone 예시:"
echo "  cd ~/workspace && git clone git@github.com:heumlabs/repo.git"
echo "  cd ~/lab       && git clone git@github.com-personal:$PERSONAL_NAME/repo.git"
