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

# --- Line 2: 세션 비용 / 경과 시간 ---
COST=$(echo "$input" | jq -r '.cost.total_cost_usd // 0')
DURATION_MS=$(echo "$input" | jq -r '.cost.total_duration_ms // 0')

COST_FMT=$(printf '$%.2f' "$COST")
DURATION_SEC=$((DURATION_MS / 1000))
MINS=$((DURATION_SEC / 60))
SECS=$((DURATION_SEC % 60))

LINE2="💰 $COST_FMT | ⏱️ ${MINS}m ${SECS}s"

# --- Line 3: 컨텍스트 윈도우 크기 / 사용률(윈도우 크기 무관 %) progress bar / 남은 비율 ---
WINDOW_SIZE=$(echo "$input" | jq -r '.context_window.context_window_size // 0')
USED_PCT=$(echo "$input" | jq -r '.context_window.used_percentage // 0' | cut -d. -f1)
REMAINING=$(echo "$input" | jq -r '.context_window.remaining_percentage // 0' | cut -d. -f1)

# 윈도우 크기를 K/M 단위로 축약 (예: 200000 -> 200K, 1000000 -> 1M)
if [ "$WINDOW_SIZE" -ge 1000000 ]; then
  WINDOW_FMT="$((WINDOW_SIZE / 1000000))M"
else
  WINDOW_FMT="$((WINDOW_SIZE / 1000))K"
fi

# 사용률 progress bar 생성 (10칸, 임계값별 색상: <70% 초록, 70~89% 노랑, 90%+ 빨강)
GREEN='\033[32m'; YELLOW='\033[33m'; RED='\033[31m'; RESET='\033[0m'
if [ "$USED_PCT" -ge 90 ]; then BAR_COLOR="$RED"
elif [ "$USED_PCT" -ge 70 ]; then BAR_COLOR="$YELLOW"
else BAR_COLOR="$GREEN"; fi

BAR_WIDTH=10
FILLED=$((USED_PCT * BAR_WIDTH / 100))
EMPTY=$((BAR_WIDTH - FILLED))
BAR=""
[ "$FILLED" -gt 0 ] && printf -v FILL "%${FILLED}s" && BAR="${FILL// /▓}"
[ "$EMPTY" -gt 0 ] && printf -v PAD "%${EMPTY}s" && BAR="${BAR}${PAD// /░}"

LINE3="🔢 window:${WINDOW_FMT} | ${BAR_COLOR}${BAR}${RESET} used:${USED_PCT}% remaining:${REMAINING}%"

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
echo "$LINE4"
