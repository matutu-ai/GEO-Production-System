#!/usr/bin/env python3
"""Check GEO task status through curl instead of Python HTTPS clients."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


DEFAULT_API_URL = "https://api.housun.shop"
DEFAULT_USERNAME = "admin"
DEFAULT_PASSWORD = "admin123"
DEFAULT_LOG = "task_status.log"


class ScriptError(RuntimeError):
    """Raised when curl or the API response cannot be validated."""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check GEO task status via curl and write task_status.log"
    )
    parser.add_argument("--url", default=os.getenv("GEO_API_URL", DEFAULT_API_URL))
    parser.add_argument("--task-id", default=os.getenv("GEO_TASK_ID", ""))
    parser.add_argument("--token", default=os.getenv("GEO_API_TOKEN", ""))
    parser.add_argument(
        "--username",
        default=os.getenv("GEO_API_USERNAME", DEFAULT_USERNAME),
    )
    parser.add_argument(
        "--password",
        default=os.getenv("GEO_API_PASSWORD", DEFAULT_PASSWORD),
    )
    parser.add_argument("--log", default=os.getenv("GEO_STATUS_LOG", DEFAULT_LOG))
    parser.add_argument("--max-attempts", type=int, default=30)
    parser.add_argument("--poll-interval", type=float, default=2.0)
    parser.add_argument("--timeout", type=float, default=10.0)
    return parser.parse_args()


def curl_json(
    method: str,
    url: str,
    token: str = "",
    data: Optional[str] = None,
    timeout: float = 10.0,
) -> Dict[str, Any]:
    command = [
        "curl",
        "-sS",
        "-m",
        str(int(timeout)),
        "-X",
        method,
        "-w",
        "\n%{http_code}",
    ]
    headers = ["-H", "Accept: application/json"]
    if token:
        headers.extend(["-H", f"Authorization: Bearer {token}"])
    if data is not None:
        headers.extend(["-H", "Content-Type: application/json", "-d", data])

    command.extend(headers)
    command.append(url)

    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout + 5,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise ScriptError(f"curl timeout: {url}") from exc
    except OSError as exc:
        raise ScriptError(f"curl execution failed: {exc}") from exc

    if completed.returncode != 0:
        detail = completed.stderr.strip() or "curl failed"
        raise ScriptError(f"curl error for {url}: {detail}")

    output = completed.stdout.strip()
    if not output:
        raise ScriptError(f"empty curl response for {url}")

    body, _, raw_status = output.rpartition("\n")
    try:
        http_status = int(raw_status)
    except ValueError as exc:
        raise ScriptError(f"missing HTTP status from curl: {output}") from exc

    if http_status < 200 or http_status >= 300:
        raise ScriptError(
            f"HTTP {http_status} from {url}: {body or completed.stderr.strip()}"
        )

    try:
        payload = json.loads(body or "{}")
    except json.JSONDecodeError as exc:
        raise ScriptError(f"invalid JSON from {url}: {body[:500]}") from exc

    if not isinstance(payload, dict):
        raise ScriptError(f"unexpected JSON shape from {url}: {type(payload).__name__}")
    return payload


def get_token(args: argparse.Namespace) -> str:
    if args.token:
        return args.token

    login_payload = json.dumps(
        {
            "username": args.username,
            "password": args.password,
        },
        ensure_ascii=False,
    )
    login = curl_json(
        "POST",
        f"{args.url}/login",
        data=login_payload,
        timeout=args.timeout,
    )
    token = login.get("token")
    if not token:
        raise ScriptError("login response did not include token")
    return token


def resolve_task_id(args: argparse.Namespace, token: str) -> str:
    if args.task_id:
        return args.task_id

    payload = curl_json(
        "GET",
        f"{args.url}/projects",
        token=token,
        timeout=args.timeout,
    )
    projects = payload.get("projects") or []
    if not projects:
        raise ScriptError("no projects returned, cannot resolve a task_id")

    completed = [
        item
        for item in projects
        if str(item.get("status", "")).upper() == "COMPLETED"
    ]
    candidates = completed or projects
    latest = max(
        candidates,
        key=lambda item: item.get("updated_time")
        or item.get("updated_at")
        or item.get("created_time")
        or item.get("created_at")
        or "",
    )
    task_id = latest.get("task_id") or latest.get("id")
    if not task_id:
        raise ScriptError("latest project has no task_id")
    return task_id


def log_status(log_path: Path, task_id: str, status: str, progress: Any) -> None:
    timestamp = datetime.now().strftime("%H:%M:%S")
    line = f"{timestamp} | {task_id} | {status} | {progress}\n"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(line)
    print(line.rstrip())


def main() -> int:
    args = parse_args()
    log_path = Path(args.log).expanduser()
    token = get_token(args)
    task_id = resolve_task_id(args, token)

    for attempt in range(1, args.max_attempts + 1):
        task = curl_json(
            "GET",
            f"{args.url}/tasks/{task_id}",
            token=token,
            timeout=args.timeout,
        )
        status = str(task.get("status") or task.get("project_status") or "UNKNOWN").upper()
        progress = task.get("progress", "")
        log_status(log_path, task_id, status, progress)

        if status == "COMPLETED":
            print(f"\nVerified: task {task_id} is COMPLETED with progress=100")
            return 0
        if status == "FAILED":
            error = task.get("error_message") or task.get("message") or "unknown error"
            raise ScriptError(f"task {task_id} failed: {error}")

        if attempt < args.max_attempts:
            time.sleep(args.poll_interval)

    raise ScriptError(
        f"task {task_id} did not complete after {args.max_attempts} attempts"
    )


if __name__ == "__main__":
    try:
        sys.exit(main())
    except ScriptError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
