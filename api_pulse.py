#!/usr/bin/env python3
"""API Pulse: dependency-free HTTP endpoint health checks."""

import argparse
import json
import time
import urllib.error
import urllib.request
from pathlib import Path


def check_endpoint(name, url, timeout=5.0, slow_ms=750):
    start = time.perf_counter()
    request = urllib.request.Request(url, headers={"User-Agent": "api-pulse/1.0"})

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            status = response.status
        latency_ms = round((time.perf_counter() - start) * 1000)
        state = "HEALTHY" if 200 <= status < 400 and latency_ms < slow_ms else "SLOW"
        if status >= 400:
            state = "DOWN"
        return {"name": name, "url": url, "status": status, "latency_ms": latency_ms, "state": state, "error": None}
    except urllib.error.HTTPError as exc:
        latency_ms = round((time.perf_counter() - start) * 1000)
        return {"name": name, "url": url, "status": exc.code, "latency_ms": latency_ms, "state": "DOWN", "error": str(exc.reason)}
    except (urllib.error.URLError, TimeoutError, ValueError) as exc:
        latency_ms = round((time.perf_counter() - start) * 1000)
        reason = getattr(exc, "reason", exc)
        return {"name": name, "url": url, "status": None, "latency_ms": latency_ms, "state": "DOWN", "error": str(reason)}


def load_config(path):
    data = json.loads(path.read_text(encoding="utf-8"))
    endpoints = data.get("endpoints", [])
    if not endpoints:
        raise ValueError("config must contain at least one endpoint")
    for endpoint in endpoints:
        if "name" not in endpoint or "url" not in endpoint:
            raise ValueError("each endpoint needs a name and url")
    return endpoints


def print_report(results):
    print("\nAPI PULSE")
    print("─" * 62)
    for result in results:
        icon = {"HEALTHY": "✓", "SLOW": "⚠", "DOWN": "✗"}[result["state"]]
        status = str(result["status"]) if result["status"] is not None else "---"
        latency = f"{result['latency_ms']}ms"
        print(f"{icon} {result['name'][:22]:<22} {status:>3}  {latency:>8}  {result['state']}")

    counts = {state: sum(r["state"] == state for r in results) for state in ("HEALTHY", "SLOW", "DOWN")}
    print("─" * 62)
    print(f"{counts['HEALTHY']} healthy  •  {counts['SLOW']} slow  •  {counts['DOWN']} down\n")


def main():
    parser = argparse.ArgumentParser(description="Check HTTP endpoints for status and response time.")
    parser.add_argument("--config", type=Path, default=Path("endpoints.json"), help="JSON config file")
    parser.add_argument("--timeout", type=float, default=5.0, help="request timeout in seconds")
    parser.add_argument("--slow", type=int, default=750, help="latency threshold in milliseconds")
    parser.add_argument("--json", action="store_true", help="print machine-readable JSON")
    args = parser.parse_args()

    if args.timeout <= 0 or args.slow < 1:
        parser.error("timeout and slow threshold must be positive")

    try:
        endpoints = load_config(args.config)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        parser.error(str(exc))

    results = [check_endpoint(e["name"], e["url"], args.timeout, args.slow) for e in endpoints]

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print_report(results)

    raise SystemExit(1 if any(r["state"] == "DOWN" for r in results) else 0)


if __name__ == "__main__":
    main()
