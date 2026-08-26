"""Report who is blocked waiting on the maintainer.

Four checks. The last two produce no GitHub notification of their own, which is
most of the reason this exists: a workflow run held for first-time-contributor
approval strands a pull request silently, and an issue comment that nobody
answers looks identical to one that needed no answer.

Read-only. Prints a Markdown report to stdout, or nothing at all when the
queue is empty. Deciding what to do about the report belongs to the workflow.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import UTC, datetime, timedelta

REPO = os.environ.get("REPO", "PesanteAnalytics/contoso-universe-gen")

# GitHub reports how the commenter relates to the repository. These three mean
# the comment came from the maintainer side, so it does not count as waiting.
# Bots are not covered here — `author_association` has no value for them, so
# they are filtered on `user.type` instead.
MAINTAINER_SIDE = {"OWNER", "MEMBER", "COLLABORATOR"}

STALE_COMMENT_DAYS = 14


def gh(*args: str) -> object:
    """Run a gh command and parse its JSON output."""
    result = subprocess.run(
        ["gh", *args], capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    if result.returncode != 0:
        print(f"::error::gh {' '.join(args)} failed: {result.stderr.strip()}", file=sys.stderr)
        raise SystemExit(1)
    return json.loads(result.stdout or "[]")


def parse(ts: str) -> datetime:
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


def humanise(delta: timedelta) -> str:
    hours = delta.total_seconds() / 3600
    if hours < 1:
        return "under an hour"
    if hours < 48:
        return f"{int(hours)}h"
    return f"{int(hours // 24)} days"


def is_outsider(association: str) -> bool:
    return association.upper() not in MAINTAINER_SIDE


def pull_requests_waiting(now: datetime, seen: set[int]) -> list[str]:
    """Open PRs where an outsider spoke or pushed after the maintainer last did."""
    found = []
    # The REST API carries author_association; `gh pr list --json` does not.
    prs = gh(
        "api", f"repos/{REPO}/pulls?state=open&per_page=50",
        "--jq", "[.[] | {number, title, url: .html_url, createdAt: .created_at,"
                " login: .user.login, side: .author_association}]",
    )

    for pr in prs:
        if not is_outsider(pr["side"]):
            continue

        comments = gh(
            "api", f"repos/{REPO}/issues/{pr['number']}/comments",
            "--jq", "[.[] | {at: .created_at, who: .user.login, side: .author_association}]",
        )
        commits = gh(
            "api", f"repos/{REPO}/pulls/{pr['number']}/commits",
            "--jq", "[.[] | .commit.committer.date]",
        )

        last_maintainer = max(
            (parse(c["at"]) for c in comments if not is_outsider(c["side"])), default=None
        )
        outsider_events = [parse(c["at"]) for c in comments if is_outsider(c["side"])]
        outsider_events += [parse(d) for d in commits]
        outsider_events.append(parse(pr["createdAt"]))
        last_outsider = max(outsider_events)

        if last_maintainer is not None and last_maintainer >= last_outsider:
            continue  # the ball is in their court, not ours

        never_answered = last_maintainer is None
        note = "with no reply at all yet" if never_answered else "since your last reply"
        seen.add(pr["number"])
        found.append(
            f"- [ ] **[#{pr['number']}]({pr['url']})** — {pr['title']}\n"
            f"      {pr['login']} has been waiting **{humanise(now - last_outsider)}** {note}."
        )

    return found


def runs_blocked() -> list[str]:
    """Workflow runs held for approval. GitHub does not chase you about these."""
    runs = gh(
        "run", "list", "--repo", REPO, "--limit", "40",
        "--json", "databaseId,conclusion,headBranch,event,url",
    )
    return [
        f"- [ ] **CI is blocked** on `{r['headBranch']}` — [approve the run]({r['url']})\n"
        f"      GitHub holds every push from a first-time contributor for manual approval."
        for r in runs
        if r["conclusion"] == "action_required"
    ]


def comments_unanswered(now: datetime, already_reported: set[int]) -> list[str]:
    """Issue comments from outsiders with no maintainer reply after them.

    Only on threads that are still open — a closed issue needs no reply — and
    skipping pull requests already listed above, so nobody appears twice.
    """
    cutoff = now - timedelta(days=STALE_COMMENT_DAYS)

    open_threads = gh(
        "api", f"repos/{REPO}/issues?state=open&per_page=100",
        "--jq", "[.[] | .url]",
    )
    still_open = set(open_threads)

    comments = gh(
        "api", f"repos/{REPO}/issues/comments?sort=created&direction=desc&per_page=100",
        "--jq", "[.[] | {at: .created_at, who: .user.login, side: .author_association,"
                " bot: (.user.type == \"Bot\"), url: .html_url, issue: .issue_url}]",
    )

    latest_by_issue: dict[str, dict] = {}
    for c in comments:
        if parse(c["at"]) < cutoff or c["issue"] not in still_open:
            continue
        latest_by_issue.setdefault(c["issue"], c)  # the API already sorted newest first

    out = []
    for c in latest_by_issue.values():
        number = int(c["issue"].rsplit("/", 1)[-1])
        # `author_association` has no value for bots, so ask what the account is.
        if c["bot"] or not is_outsider(c["side"]) or number in already_reported:
            continue
        out.append(
            f"- [ ] **Unanswered** on #{number} — "
            f"[{c['who']}]({c['url']}) wrote {humanise(now - parse(c['at']))} ago."
        )
    return out


def main() -> None:
    now = datetime.now(UTC)
    reported: set[int] = set()

    sections = [
        ("Pull requests waiting on you", pull_requests_waiting(now, reported)),
        ("Continuous integration blocked", runs_blocked()),
        ("Comments with no reply", comments_unanswered(now, reported)),
    ]

    if not any(items for _, items in sections):
        return  # nothing waiting: print nothing, and the workflow closes the issue

    print("Someone is waiting on a reply from you.\n")
    for heading, items in sections:
        if items:
            print(f"### {heading}\n")
            print("\n".join(items))
            print()
    print(
        "---\n"
        f"Checked {now:%Y-%m-%d %H:%M} UTC. This issue closes itself once the queue is empty, "
        "so there is no need to close it by hand."
    )


if __name__ == "__main__":
    main()
