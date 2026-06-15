# How to Import Tickets into Free Jira-like Tools

You have **48 tickets** in 3 formats. Pick the tool you prefer.

---

## Option 1: GitHub Projects (Recommended — 100% free)

Best if you already use GitHub.

### Steps

1. Create a new GitHub repo: `sqli-interview-tracker`
2. Push the project folder
3. Go to **Issues → Import issues** (or create manually from `TICKETS.md`)
4. For bulk import, use the GitHub CLI:

```bash
# Install gh if needed: brew install gh

# Create issues from CSV (one-liner script)
cd projects/04-sqli-interview-tracker
python3 scripts/import_github_issues.py tickets.csv
```

Or manually: create milestones `M1` through `M6`, then create issues using titles from `TICKETS.md`.

5. Enable **GitHub Projects** (Board view):
   - Columns: `Backlog` → `In Progress` → `In Review` → `Done`
   - Group by: Milestone
   - Filter labels: `backend`, `frontend`, `ai`, `setup`

### Labels to create

```
setup, backend, frontend, auth, jobs, candidates, interviews,
scorecards, ai, dashboard, notifications, branding, testing, devops, docs
```

### Milestones

| Milestone | Due (suggested) | Tickets |
|-----------|-----------------|---------|
| M1 — Foundation | Week 1–2 | INT-001 → INT-015 |
| M2 — Core CRUD | Week 3 | INT-016 → INT-026 |
| M3 — Interviews | Week 4 | INT-027 → INT-033 |
| M4 — AI | Week 5–6 | INT-034 → INT-038 |
| M5 — UI/Polish | Week 7 | INT-039 → INT-042 |
| M6 — Ship | Week 8 | INT-043 → INT-048 |

---

## Option 2: Plane (Free — closest to Jira)

https://plane.so — free cloud tier, Jira-like UI.

### Steps

1. Create free account at https://app.plane.so
2. Create project: **SQLI Interview Tracker**
3. Go to **Settings → Import**
4. Upload `tickets.csv` (Plane supports CSV import)
5. Map columns:
   - `title` → Title
   - `description` → Description
   - `priority` → Priority
   - `labels` → Labels
   - `milestone` → Cycle/Sprint

### Cycles (sprints)

Create 8 cycles matching the sprint table in `TICKETS.md`.

---

## Option 3: Taiga (Open source, free)

https://taiga.io — scrum/kanban, free for public projects.

### Steps

1. Create project at https://taiga.io
2. Choose **Scrum** template
3. Create user stories from `TICKETS.md` (copy/paste acceptance criteria)
4. Create sprints M1–M6
5. Use `tickets.json` with Taiga import API if comfortable, or manual entry

---

## Option 4: Just use TICKETS.md (zero setup)

Open [`TICKETS.md`](./TICKETS.md) and check off tickets manually:

```markdown
| INT-001 | Initialize monorepo | ... | ✅ |
```

Works fine for a solo intern. No tool needed.

---

## Option 5: Notion / Linear / Trello

### Notion
- Create a database with columns matching `tickets.csv`
- Import CSV directly: **⋯ → Import → CSV**

### Trello
- One board, lists = milestones (M1–M6)
- One card per ticket, paste acceptance criteria in description
- Labels = priority (Critical/High/Normal)

### Linear (free for small teams)
- Import via CSV at Settings → Import

---

## GitHub import helper script

Save as `scripts/import_github_issues.py`:

```python
#!/usr/bin/env python3
"""Import tickets.csv as GitHub issues. Requires: gh auth login"""
import csv, subprocess, sys

PRIORITY_TO_LABEL = {
    "Critical": "priority:critical",
    "High": "priority:high",
    "Normal": "priority:normal",
}

def main(csv_path: str):
    with open(csv_path) as f:
        for row in csv.DictReader(f):
            labels = row["labels"].split(",") + [PRIORITY_TO_LABEL.get(row["priority"], "")]
            body = f"""## Description
{row['description']}

## Acceptance Criteria
{row['acceptance_criteria']}

## Meta
- **Epic:** {row['epic']}
- **Estimate:** {row['estimate']}
- **Dependencies:** {row['dependencies']}
- **Milestone:** {row['milestone']}
"""
            cmd = [
                "gh", "issue", "create",
                "--title", f"[{row['id']}] {row['title']}",
                "--body", body,
                "--label", ",".join(filter(None, labels)),
            ]
            if row["milestone"]:
                cmd.extend(["--milestone", row["milestone"]])
            print(f"Creating {row['id']}...")
            subprocess.run(cmd, check=True)

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "tickets.csv")
```

---

## Recommended workflow for the intern

```
Week 1:  Import tickets → GitHub Projects
         Pick INT-001, move to "In Progress"
         PR per ticket (or per 2-3 related tickets)
         Move to "Done" when acceptance criteria met

Daily:   Standup comment on current ticket
         Blocked? Tag mentor with ticket ID

End:     All 48 tickets in "Done" column = project complete
```
