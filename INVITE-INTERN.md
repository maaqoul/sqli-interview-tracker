# Invite the Intern to GitHub

Repo: **https://github.com/maaqoul/sqli-interview-tracker**

---

## Step 1 — Invite intern as collaborator

Replace `INTERN_GITHUB_USERNAME` with their actual GitHub username.

```bash
gh api repos/maaqoul/sqli-interview-tracker/collaborators/INTERN_GITHUB_USERNAME \
  -X PUT \
  -f permission=push
```

Or via the UI:
1. Go to https://github.com/maaqoul/sqli-interview-tracker/settings/access
2. Click **Add people**
3. Search their GitHub username or email
4. Role: **Write** (can push branches + open PRs)

---

## Step 2 — Create the Project board (one-time, ~2 min)

GitHub Projects needs the `project` scope on your token. Run once:

```bash
gh auth refresh -s project,read:project
```

Then create the board:

1. Go to https://github.com/maaqoul/sqli-interview-tracker
2. Click **Projects** tab → **New project**
3. Template: **Board**
4. Name: `Sprint Board`
5. Add columns: `Backlog` | `In Progress` | `In Review` | `Done`
6. Click **+ Add item** → **Add existing issues** → select all open issues
7. Group by: **Milestone** (W1 / W2)

---

## Step 3 — Send this to the intern

Copy-paste:

---

**Subject: Your 2-week SQLI Interview Tracker project**

Hi,

Your project is ready. Here's everything you need:

**Repo:** https://github.com/maaqoul/sqli-interview-tracker  
**Start here:** Read [`INTERN-GUIDE.md`](https://github.com/maaqoul/sqli-interview-tracker/blob/main/INTERN-GUIDE.md) (setup, UI specs, API — everything)  
**Sprint plan:** [`2-WEEK-PLAN.md`](https://github.com/maaqoul/sqli-interview-tracker/blob/main/2-WEEK-PLAN.md)  
**First ticket:** [INT-009 — User model with roles](https://github.com/maaqoul/sqli-interview-tracker/issues/9)

**Setup:**
```bash
git clone https://github.com/maaqoul/sqli-interview-tracker.git
cd sqli-interview-tracker
cp .env.example .env
make setup
make dev-backend   # terminal 1
make dev-frontend  # terminal 2
```

Tickets INT-001 → INT-008 are already done (scaffold). You start at INT-009.

**Daily workflow:**
1. Pick a ticket from Week 1 milestone
2. Branch: `git checkout -b INT-009-user-model`
3. PR when done → tag me for review

Questions? Comment on the GitHub issue.

---

## Step 4 — Assign first tickets (optional)

```bash
# Assign INT-009 and INT-010 to intern
gh issue edit 9 --repo maaqoul/sqli-interview-tracker --add-assignee INTERN_GITHUB_USERNAME
gh issue edit 10 --repo maaqoul/sqli-interview-tracker --add-assignee INTERN_GITHUB_USERNAME
```

---

## What's already on GitHub

| Item | Count | Link |
|------|-------|------|
| Issues (total) | 48 | https://github.com/maaqoul/sqli-interview-tracker/issues |
| Closed (scaffold done) | 8 | INT-001 → INT-008 |
| Open (for intern) | 40 | INT-009 → INT-048 |
| Milestones | W1, W2 + M1–M6 | Filter by milestone on Issues page |
| Labels | 30+ | priority, area, status:done |

---

## When intern finishes Week 1

Review their PRs, then assign Week 2 tickets (INT-027+).

Week 1 demo checklist is in `2-WEEK-PLAN.md` → "Week 1 demo".
