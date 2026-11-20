"""Pre-run gate for the PR review cron job.

Lists open, non-draft PRs where MiroCillik's review is requested directly, or
where one of TEAMS is requested (reviewed the same way, full verdict). GitHub
drops the request once a review is submitted, so a PR only comes back when the
author re-requests a review. Team-requested PRs authored by MiroCillik are
skipped (he can't review his own PR for the team).

Guard: if the agent already tried the same head commit MAX_ATTEMPTS times and
the PR is still in the queue (posting failed), skip it until new commits land.

Last stdout line is the wakeAgent gate read by the Hermes cron scheduler.
"""

import json
import os
import subprocess
import sys
import time
from pathlib import Path

GH = "/opt/homebrew/bin/gh"
PROJECTS = Path.home() / "Projects"
STATE = Path.home() / ".hermes" / "cron" / "pr-review-state.json"
MAX_PER_RUN = 3
MAX_ATTEMPTS = 2
ME = "MiroCillik"
TEAMS = ["keboola/ajda-swimlane"]
BASE_QUERY = "is:pr is:open draft:false archived:false"


def search(qualifier):
    return gh_json("api", "-X", "GET", "search/issues", "-f", f"q={BASE_QUERY} {qualifier}",
                   "-f", "sort=created", "-f", "order=asc", "-f", "per_page=50")["items"]


def fetch_items():
    """Direct requests first, then team requests; dedupe, oldest first."""
    found = {}
    for item in search("user-review-requested:@me"):
        found[item["html_url"]] = (item, "user")
    for team in TEAMS:
        for item in search(f"team-review-requested:{team}"):
            found.setdefault(item["html_url"], (item, f"team:{team}"))
    return sorted(found.values(), key=lambda pair: pair[0]["created_at"])


def gh_json(*args):
    out = subprocess.run([GH, *args], capture_output=True, text=True, timeout=120)
    if out.returncode != 0:
        raise RuntimeError(f"gh {' '.join(args)} failed: {out.stderr.strip()}")
    return json.loads(out.stdout)


def local_clone(owner_repo):
    name = owner_repo.split("/")[1]
    path = PROJECTS / name
    if not (path / ".git").exists():
        return None
    url = subprocess.run(
        ["git", "-C", str(path), "remote", "get-url", "origin"],
        capture_output=True, text=True,
    ).stdout.strip()
    return str(path) if owner_repo.lower() in url.lower() else None


def main():
    state = json.loads(STATE.read_text()) if STATE.exists() else {}
    pairs = fetch_items()
    items = [item for item, _ in pairs]

    queue, skipped = [], []
    for item, via in pairs:
        owner_repo = item["repository_url"].split("/repos/")[1]
        number = item["number"]
        key = f"{owner_repo}#{number}"
        if via != "user" and item["user"]["login"] == ME:
            skipped.append({"pr": key, "reason": f"own PR, requested via {via}"})
            continue
        pr = gh_json("api", f"repos/{owner_repo}/pulls/{number}")
        head = pr["head"]["sha"]
        seen = state.get(key, {})
        attempts = seen.get("attempts", 0) if seen.get("head") == head else 0
        if attempts >= MAX_ATTEMPTS:
            skipped.append({"pr": key, "head": head, "reason": f"{attempts} attempts on this commit already"})
            continue
        if len(queue) >= MAX_PER_RUN:
            continue
        queue.append({
            "pr": key,
            "url": pr["html_url"],
            "title": pr["title"],
            "author": pr["user"]["login"],
            "base": pr["base"]["ref"],
            "head_branch": pr["head"]["ref"],
            "head_sha": head,
            "requested_via": via,
            "local_clone": local_clone(owner_repo),
        })
        state[key] = {"head": head, "attempts": attempts + 1, "last": int(time.time())}

    open_keys = {f"{i['repository_url'].split('/repos/')[1]}#{i['number']}" for i in items}
    state = {k: v for k, v in state.items() if k in open_keys}
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(state, indent=2))

    if not queue:
        if skipped:
            print(json.dumps({"skipped": skipped}, indent=2))
        print(json.dumps({"wakeAgent": False}))
        return

    print(json.dumps({"to_review": queue, "skipped": skipped,
                      "waiting_for_next_run": max(0, len(items) - len(queue) - len(skipped))}, indent=2))
    print(json.dumps({"wakeAgent": True}))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # noqa: BLE001
        print(f"PR queue check failed: {exc}", file=sys.stderr)
        sys.exit(1)
