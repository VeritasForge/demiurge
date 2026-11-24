# MCP 서버 설치·설정 참고

deep-research가 쓰는 MCP 도구를 사람이 설치·설정할 때 보는 참고 자료다. 조사 실행 중에는 읽을 필요가 없다.

## SNS API용 MCP 서버 (향후 참조용)

SNS API에 직접 접근하려면 MCP 서버를 설정합니다. 현재는 WebSearch `site:` 연산자로 충분하며,
API 접근이 필요해지면 아래 구성을 참고하세요:

```jsonc
// .mcp.json 예시 (향후 설정 시)
{
  "mcpServers": {
    "reddit": {
      "command": "npx",
      "args": ["-y", "@anthropic/mcp-reddit"],
      "env": {
        "REDDIT_CLIENT_ID": "<your-client-id>",
        "REDDIT_CLIENT_SECRET": "<your-client-secret>"
      }
    }
    // Twitter/X API는 별도 MCP 서버 패키지 확인 필요
  }
}
```

> **참고**: MCP 서버 패키지명은 예시이며, 실제 사용 시 최신 패키지를 확인하세요.


## MCP 서버 설정 가이드 (Web Fetch 강화)

WebFetch의 봇 탐지 취약성을 보완하기 위해 MCP Browser 도구를 설정합니다.
Error Resilience Protocol의 Fallback Tool Chain에서 사용됩니다.

### Tier 1: Playwright MCP (무료, 기본 권장)

Microsoft 공식 Playwright MCP 서버. 실제 Chromium 브라우저를 headless로 실행하여
JavaScript 렌더링 및 기본적인 봇 탐지를 우회합니다.

**설치 (CLI)**:
```bash
claude mcp add playwright npx @playwright/mcp@latest -- --headless
```

**설정 (.mcp.json)**:
```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["@playwright/mcp@latest", "--headless"]
    }
  }
}
```

**주요 옵션**:
- `--headless`: 브라우저 창 없이 실행 (기본 권장)
- `--browser firefox`: Firefox 사용 (기본: Chrome)
- `--viewport-size 1280x720`: 뷰포트 크기 지정

**주요 도구**: `browser_navigate`, `browser_snapshot`, `browser_click`, `browser_take_screenshot`

**한계**: Cloudflare Turnstile/CAPTCHA는 일관되게 통과하지 못할 수 있음

### 설정 확인

```bash
# 설치된 MCP 서버 목록 확인
claude mcp list

# 정상 연결 시 출력 예시
# playwright: npx @playwright/mcp@latest --headless - ✓ Connected
```
