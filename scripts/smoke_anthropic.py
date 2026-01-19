#!/usr/bin/env python
import os
import sys
import json
import anthropic

"""CI smoke test for Anthropic connectivity.
- Exits 0 if:
  * request succeeds OR
  * API returns credit/balance error (valid key but no credits)
- Exits 1 on auth errors or connectivity issues.
"""

def main() -> int:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ANTHROPIC_API_KEY not set; skipping smoke test.")
        return 0
    try:
        client = anthropic.Anthropic(api_key=api_key)
        # Minimal request
        resp = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1,
            messages=[{"role": "user", "content": "ping"}],
        )
        # If we got here, the API is reachable and authorized
        print("Anthropic smoke success: response received.")
        return 0
    except anthropic.APIStatusError as e:
        # Accept low-credit as success (connectivity + auth OK)
        try:
            data = e.response.json()
        except Exception:
            data = {"error": {"message": str(e)}}
        msg = json.dumps(data)
        print(f"Anthropic smoke APIStatusError: {msg}")
        if "credit balance" in msg.lower() or "too low" in msg.lower():
            print("Treating low-credit error as success.")
            return 0
        if "invalid api key" in msg.lower() or "authentication" in msg.lower():
            print("Authentication error; failing.")
            return 1
        # Other API errors: consider transient but fail to surface issues
        return 1
    except Exception as e:
        print(f"Anthropic smoke unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
