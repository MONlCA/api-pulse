# API Pulse

A tiny, dependency-free Python CLI that checks HTTP endpoints and reports status, latency, and overall health.

## Features

- Monitor multiple endpoints from one JSON config
- Report HTTP status codes and response times
- Classify endpoints as `HEALTHY`, `SLOW`, or `DOWN`
- Configure latency and timeout thresholds
- Machine-readable JSON output for scripts and automation
- Non-zero exit code when an endpoint is down
- No third-party Python packages

## Quick start

Python 3.9+ recommended.

```bash
python3 api_pulse.py
```

API Pulse reads `endpoints.json` by default.

```json
{
  "endpoints": [
    {"name": "GitHub", "url": "https://github.com"},
    {"name": "Example", "url": "https://example.com"}
  ]
}
```

## Options

```bash
python3 api_pulse.py --config endpoints.json
python3 api_pulse.py --slow 1000
python3 api_pulse.py --timeout 3
python3 api_pulse.py --json
```

## Example output

```text
API PULSE
──────────────────────────────────────────────────────────────
✓ GitHub                 200     124ms  HEALTHY
✓ Example                200     231ms  HEALTHY
⚠ Internal API           200    1241ms  SLOW
✗ Bad endpoint           ---        --  DOWN
──────────────────────────────────────────────────────────────
2 healthy  •  1 slow  •  1 down
```

Actual response times depend on your connection and the services being checked.

## Tests

```bash
python3 -m unittest -v
```

## Why this exists

Checking whether a service is reachable is often the first step in debugging an API or integration problem. API Pulse keeps that workflow intentionally simple while exposing useful signals for troubleshooting and automation.

## Roadmap

- Repeated checks and uptime history
- Expected status code per endpoint
- Custom request headers
- Response body assertions
- CSV history export
- Concurrent endpoint checks

## License

MIT
