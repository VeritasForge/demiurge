#!/bin/bash
input=$(cat)

# --- Line 1: 모델 / 버전 / effort / thinking / agent ---
MODEL=$(echo "$input" | jq -r '.model.display_name')
VERSION=$(echo "$input" | jq -r '.version')
EFFORT=$(echo "$input" | jq -r '.effort.level // empty')
THINKING=$(echo "$input" | jq -r '.thinking.enabled // false')
AGENT=$(echo "$input" | jq -r '.agent.name // empty')

LINE1="[$MODEL] v$VERSION"
[ -n "$EFFORT" ] && LINE1="$LINE1 | effort:$EFFORT"
if [ "$THINKING" = "true" ]; then
  LINE1="$LINE1 | thinking:on"
else
  LINE1="$LINE1 | thinking:off"
fi
[ -n "$AGENT" ] && LINE1="$LINE1 | agent:$AGENT"

# --- Line 2: 세션 비용 / 경과 시간 / 현재 작업 디렉토리 / git 브랜치 ---
COST=$(echo "$input" | jq -r '.cost.total_cost_usd // 0')
DURATION_MS=$(echo "$input" | jq -r '.cost.total_duration_ms // 0')

COST_FMT=$(printf '$%.2f' "$COST")
DURATION_SEC=$((DURATION_MS / 1000))
MINS=$((DURATION_SEC / 60))
SECS=$((DURATION_SEC % 60))

# 브랜치는 statusline JSON에 없으므로(payload 확인 완료) git을 직접 호출해서 얻는다
CURRENT_DIR=$(echo "$input" | jq -r '.workspace.current_dir // .cwd // empty')
HOME_ALIAS="~"
DIR_FMT="${CURRENT_DIR/#$HOME/$HOME_ALIAS}"

# detached HEAD면 --show-current가 빈 값이라 짧은 커밋 해시로 대체, git 저장소가 아니면 브랜치 생략
BRANCH=$(git -C "$CURRENT_DIR" branch --show-current 2>/dev/null)
[ -z "$BRANCH" ] && BRANCH=$(git -C "$CURRENT_DIR" rev-parse --short HEAD 2>/dev/null)

LINE2="💰 $COST_FMT | ⏱️ ${MINS}m ${SECS}s | 📁 $DIR_FMT"
[ -n "$BRANCH" ] && LINE2="$LINE2 | 🌿 $BRANCH"

# --- Line 3: 컨텍스트 윈도우 크기 / 사용률(윈도우 크기 무관 %) 도넛 게이지 / 남은 비율 / 사용한도 ---
WINDOW_SIZE=$(echo "$input" | jq -r '.context_window.context_window_size // 0')
USED_PCT=$(echo "$input" | jq -r '.context_window.used_percentage // 0' | cut -d. -f1)
REMAINING=$(echo "$input" | jq -r '.context_window.remaining_percentage // 0' | cut -d. -f1)

# 윈도우 크기를 K/M 단위로 축약 (예: 200000 -> 200K, 1000000 -> 1M)
if [ "$WINDOW_SIZE" -ge 1000000 ]; then
  WINDOW_FMT="$((WINDOW_SIZE / 1000000))M"
else
  WINDOW_FMT="$((WINDOW_SIZE / 1000))K"
fi

GREEN='\033[32m'; YELLOW='\033[33m'; RED='\033[31m'; RESET='\033[0m'

# 원형 채움 문자 하나로 표현하는 도넛 게이지 글자 (○0-12% ◔13-37% ◑38-62% ◕63-87% ●88-100%, <70% 초록/70~89% 노랑/90%+ 빨강)
donut_glyph() {
  local pct="$1"
  local color glyph
  if [ "$pct" -ge 90 ]; then color="$RED"
  elif [ "$pct" -ge 70 ]; then color="$YELLOW"
  else color="$GREEN"; fi

  if [ "$pct" -ge 88 ]; then glyph="●"
  elif [ "$pct" -ge 63 ]; then glyph="◕"
  elif [ "$pct" -ge 38 ]; then glyph="◑"
  elif [ "$pct" -ge 13 ]; then glyph="◔"
  else glyph="○"; fi

  echo -e "${color}${glyph}${RESET}"
}

# 사용한도(rate_limits, 5시간/7일 윈도우) 도넛형 게이지 — LINE3 remaining 오른편에 '|'로 이어붙임
# rate_limits는 Claude.ai Pro/Max 구독자 + 세션 첫 API 응답 이후에만 제공됨 -> 없으면 n/a로 표시
FIVE_HOUR_PCT=$(echo "$input" | jq -r '.rate_limits.five_hour.used_percentage // empty' | cut -d. -f1)
SEVEN_DAY_PCT=$(echo "$input" | jq -r '.rate_limits.seven_day.used_percentage // empty' | cut -d. -f1)

# donut_glyph에 값 없음(n/a) 처리와 퍼센트 표기를 얹은 래퍼
make_donut() {
  local pct="$1"
  if [ -z "$pct" ]; then
    echo "n/a"
    return
  fi
  echo -e "$(donut_glyph "$pct") ${pct}%"
}

DONUT_5H=$(make_donut "$FIVE_HOUR_PCT")
DONUT_7D=$(make_donut "$SEVEN_DAY_PCT")

LINE3="🔢 window:${WINDOW_FMT} | $(donut_glyph "$USED_PCT") used:${USED_PCT}% remaining:${REMAINING}% | 🎯 5h:${DONUT_5H} | 7d:${DONUT_7D}"

# --- Line 4: KV Cache(프롬프트 캐싱) 히트율 ---
CACHE_READ=$(echo "$input" | jq -r '.context_window.current_usage.cache_read_input_tokens // 0')
CACHE_CREATE=$(echo "$input" | jq -r '.context_window.current_usage.cache_creation_input_tokens // 0')
FRESH_IN=$(echo "$input" | jq -r '.context_window.current_usage.input_tokens // 0')

CACHE_TOTAL=$((CACHE_READ + CACHE_CREATE + FRESH_IN))
if [ "$CACHE_TOTAL" -gt 0 ]; then
  CACHE_HIT_PCT=$((CACHE_READ * 100 / CACHE_TOTAL))
else
  CACHE_HIT_PCT=0
fi

LINE4="⚡ cache hit:${CACHE_HIT_PCT}% (read:${CACHE_READ} create:${CACHE_CREATE} fresh:${FRESH_IN})"

echo "$LINE1"
echo "$LINE2"
echo -e "$LINE3"
echo -e "$LINE4"
