#!/usr/bin/env python3
"""Bootstrap GitHub repo: labels, milestones, issues from tickets.csv."""
import csv
import subprocess
import sys
import time
from pathlib import Path

REPO = "maaqoul/sqli-interview-tracker"
DONE_TICKETS = {f"INT-{i:03d}" for i in range(1, 9)}

LABELS = [
    "setup", "backend", "frontend", "auth", "jobs", "candidates", "interviews",
    "scorecards", "ai", "dashboard", "notifications", "branding", "testing",
    "devops", "docs", "infrastructure", "python", "vue", "docker", "database",
    "api", "security", "layout", "quality", "ci", "release",
    "priority:critical", "priority:high", "priority:normal",
    "status:done",
]

MILESTONES = [
    ("W1 — Auth + Jobs + Candidates", "Week 1: INT-009 → INT-026"),
    ("W2 — Interviews + AI + Ship", "Week 2: INT-027 → INT-047"),
    ("M1 — Foundation", "Scaffold + Auth"),
    ("M2 — Core CRUD", "Jobs + Candidates"),
    ("M3 — Interviews", "Scheduling + Scorecards"),
    ("M4 — AI", "AI features"),
    ("M5 — UI/Polish", "Layout + Dashboard"),
    ("M6 — Ship", "Tests + Deploy"),
]

W1_TICKETS = {f"INT-{i:03d}" for i in range(9, 27)}
W2_TICKETS = {f"INT-{i:03d}" for i in range(27, 49)}


def run(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    print("→", " ".join(cmd[:6]), "..." if len(cmd) > 6 else "")
    return subprocess.run(cmd, check=check, capture_output=True, text=True)


def gh(*args: str, check: bool = True) -> subprocess.CompletedProcess:
    return run(["gh", *args], check=check)


def create_labels() -> None:
    for label in LABELS:
        color = "d73a4a" if "critical" in label else "0075ca"
        if "done" in label:
            color = "0e8a16"
        elif "high" in label:
            color = "e99695"
        gh("label", "create", label, "--color", color, "--repo", REPO, check=False)


def create_milestones() -> None:
    for title, desc in MILESTONES:
        gh(
            "api", "repos/{}/milestones".format(REPO),
            "-f", f"title={title}",
            "-f", f"description={desc}",
            check=False,
        )


def milestone_for(ticket_id: str, csv_milestone: str) -> str:
    if ticket_id in W1_TICKETS:
        return "W1 — Auth + Jobs + Candidates"
    if ticket_id in W2_TICKETS:
        return "W2 — Interviews + AI + Ship"
    mapping = {
        "M1": "M1 — Foundation",
        "M2": "M2 — Core CRUD",
        "M3": "M3 — Interviews",
        "M4": "M4 — AI",
        "M5": "M5 — UI/Polish",
        "M6": "M6 — Ship",
    }
    return mapping.get(csv_milestone, csv_milestone)


def create_issues(csv_path: Path) -> None:
    with csv_path.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    for row in rows:
        ticket_id = row["id"]
        labels = [l.strip() for l in row["labels"].split(",") if l.strip()]
        priority = row["priority"]
        if priority == "Critical":
            labels.append("priority:critical")
        elif priority == "High":
            labels.append("priority:high")
        else:
            labels.append("priority:normal")

        if ticket_id in DONE_TICKETS:
            labels.append("status:done")

        body = f"""## Ticket `{ticket_id}`

{row['description']}

## Acceptance Criteria
{row['acceptance_criteria']}

## Meta
| Field | Value |
|-------|-------|
| Epic | {row['epic']} |
| Estimate | {row['estimate']} |
| Dependencies | {row['dependencies'] or '—'} |
| Sprint | {milestone_for(ticket_id, row['milestone'])} |

---
📋 See also: [`2-WEEK-PLAN.md`](https://github.com/{REPO}/blob/main/2-WEEK-PLAN.md)
"""
        cmd = [
            "gh", "issue", "create",
            "--repo", REPO,
            "--title", f"[{ticket_id}] {row['title']}",
            "--body", body,
            "--milestone", milestone_for(ticket_id, row["milestone"]),
        ]
        for label in labels:
            cmd.extend(["--label", label])

        result = run(cmd, check=False)
        if result.returncode != 0:
            print(f"  ⚠ Failed {ticket_id}: {result.stderr}")
        else:
            print(f"  ✓ {ticket_id}")

        if ticket_id in DONE_TICKETS:
            # Close scaffolded tickets
            issue_num = result.stdout.strip().split("/")[-1] if result.stdout else ""
            if issue_num.isdigit():
                gh("issue", "close", issue_num, "--repo", REPO, check=False)
                print(f"    → closed (scaffold done)")

        time.sleep(0.5)  # avoid rate limits


def main() -> None:
    csv_path = Path(sys.argv[1] if len(sys.argv) > 1 else "tickets.csv")
    print(f"Setting up {REPO}...")
    create_labels()
    create_milestones()
    create_issues(csv_path)
    print("\n✅ Done! View issues:")
    print(f"   https://github.com/{REPO}/issues")


if __name__ == "__main__":
    main()
