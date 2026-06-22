# API Interceptor

Terminal-based API response interceptor using mitmproxy.

## Install

```bash
pip install mitmproxy
```

## Run

```bash
# Simple log output mode
mitmdump -s intercept.py --listen-port 8080

# Interactive TUI (see all traffic, filter, inspect)
mitmproxy -s intercept.py --listen-port 8080
```

## Configure your browser

Set proxy to `localhost:8080`.

**Chrome/Firefox quick way:** use a proxy toggle extension like "Proxy SwitchyOmega",  
or launch Chrome directly with:
```bash
google-chrome --proxy-server="http://localhost:8080"
```

## HTTPS support (one-time setup)

Visit `http://mitm.it` while the proxy is running and install the certificate for your OS/browser.

## Define rules

Edit `rules.json`. Rules reload automatically on save — no restart needed.

```json
[
  {
    "name": "Override broken checkout endpoint",
    "enabled": true,
    "match_url": "api/checkout",
    "response_status": 200,
    "response_body": { "order_id": "FAKE-123", "status": "confirmed" }
  }
]
```

| Field | Required | Description |
|---|---|---|
| `name` | no | Label shown in terminal logs |
| `enabled` | no | `true` by default; set `false` to skip |
| `match_url` | yes | Substring match against the full URL |
| `response_status` | no | Override the HTTP status code |
| `response_body` | no | Replace the response body (JSON object) |
| `response_headers` | no | Set or override response headers |

First matching rule wins. Original status code is logged alongside the new one.
