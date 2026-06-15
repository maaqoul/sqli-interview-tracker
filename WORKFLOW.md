# Workflow — Definition of Done, Commits & Pull Requests

> How to know when a ticket is finished, how to commit properly, and how to open a PR your mentor can review fast.

| Link | What |
|------|------|
| Tickets | https://github.com/maaqoul/sqli-interview-tracker/issues |
| Mentor | [@maaqoul](https://github.com/maaqoul) |

---

## Table of contents

1. [Definition of Done — 4 levels](#1-definition-of-done--4-levels)
2. [Git workflow overview](#2-git-workflow-overview)
3. [How to commit](#3-how-to-commit)
4. [How to open a Pull Request](#4-how-to-open-a-pull-request)
5. [PR review process](#5-pr-review-process)
6. [What NOT to do](#6-what-not-to-do)
7. [Cheat sheet](#7-cheat-sheet)

---

## 1. Definition of Done — 4 levels

### Level 1 — A single ticket is done when:

Every item in the ticket's **acceptance criteria** on GitHub is checked off.

Example for INT-009:

- [ ] Custom User model with email login
- [ ] Role field: admin, recruiter, interviewer, hiring_manager
- [ ] Admin can assign roles

**Plus these are always required:**

| Check | How to verify |
|-------|---------------|
| Code runs locally | `make dev-backend` and/or `make dev-frontend` without errors |
| No broken existing features | Health check still works: `curl localhost:8000/api/health/` |
| Tests added or updated | `make test` passes (backend tests for API/model changes) |
| No debug code left | No `print()`, `console.log()` debug statements, no commented-out blocks |
| Migrations committed | If you changed models: `python manage.py makemigrations` + commit the migration file |
| Branch pushed | `git push` succeeded |
| PR opened | PR links to the ticket (`Closes INT-009`) |

**A ticket is NOT done if:**
- "It works on my machine" but tests fail
- Acceptance criteria are partially done
- You pushed directly to `main` (never do this)
- PR is open but has no description

---

### Level 2 — A Pull Request is done when:

| Check | Detail |
|-------|--------|
| **Scope** | One ticket per PR (max 2 if tightly related, e.g. INT-009 + INT-010) |
| **Title** | Format: `INT-XXX: short description` |
| **Description** | Uses the PR template below — filled in, not empty |
| **Tests** | `make test` passes locally before opening PR |
| **Lint** | `make lint` passes (or no new lint errors) |
| **CI green** | GitHub Actions check passes on the PR |
| **Self-reviewed** | You read your own diff on GitHub before requesting review |
| **Reviewed by mentor** | @maaqoul approved the PR |
| **Merged** | Squash-merged into `main` |
| **Ticket closed** | GitHub issue auto-closes via `Closes INT-XXX` in PR body |

---

### Level 3 — End of Week 1 is done when:

You can demo this live (record 2 min):

1. Login as recruiter (real JWT, not placeholder)
2. Create a job: "Senior Python Developer — Paris"
3. Add 3 candidates
4. Drag one candidate from Applied → Screening on kanban
5. Open candidate detail → timeline shows the stage change

**Week 1 tickets:** INT-009 → INT-026 (all closed)

---

### Level 4 — Project is done when:

Full 5-minute demo (see [`INTERN-GUIDE.md`](./INTERN-GUIDE.md) §13):

1. SQLI-branded login works
2. Jobs + candidates CRUD + kanban
3. Interview scheduled + scorecard submitted
4. AI question generator works
5. AI feedback summarizer works
6. AI mock interview chat works (3+ questions)
7. Dashboard shows funnel chart
8. `docker compose up` runs the full stack
9. `make test` passes
10. README documents how to start the project

**All tickets INT-009 → INT-048 closed. INT-048 demo recorded.**

---

## 2. Git workflow overview

```
main ─────●────────●────────●────────●──── (protected, mentor merges)
           \      /          \
            ●────●            ●────●
         INT-009            INT-020
         branch              branch
              \                /
               ●──── PR ──────●  → review → merge → delete branch
```

**Rules:**
- `main` is protected — you never push to it directly
- One branch per ticket: `INT-009-user-model`
- Open a PR when ready for review
- Mentor merges after approval
- Delete branch after merge
- Pull `main` before starting a new ticket

---

## 3. How to commit

### Before every commit

```bash
# 1. See what changed
git status
git diff

# 2. Run tests (backend changes)
make test

# 3. Stage only relevant files (not .env, not db.sqlite3)
git add backend/apps/accounts/models.py
git add backend/apps/accounts/migrations/0001_initial.py
# or stage all tracked changes in a folder:
git add backend/apps/accounts/
```

**Never commit:**
- `.env` (secrets)
- `db.sqlite3` / `test_db.sqlite3`
- `node_modules/` or `.venv/`
- `__pycache__/`
- IDE files (`.idea/`, `.vscode/`)

These are already in `.gitignore` — if `git status` shows them, don't `git add` them.

---

### Commit message format

```
INT-XXX: imperative verb + what changed
```

| ✅ Good | ❌ Bad |
|---------|--------|
| `INT-009: add User model with role field` | `fix` |
| `INT-010: implement JWT login and refresh endpoints` | `wip` |
| `INT-020: add candidate CRUD API with filters` | `done stuff` |
| `INT-025: build kanban board with drag and drop` | `INT-009` (no description) |
| `INT-034: add AIService with OpenAI provider` | `asdfasdf` |

**Rules:**
- Start with ticket ID: `INT-XXX:`
- Use imperative mood: "add", "fix", "implement" (not "added", "fixed")
- Lowercase after the colon
- One logical change per commit (OK to have multiple commits per PR)
- Max ~72 characters for the subject line

---

### Multi-commit example (one PR, several commits — that's fine)

```bash
git commit -m "INT-009: add User model with role field"
git commit -m "INT-009: add UserSerializer and admin registration"
git commit -m "INT-009: add tests for User model and roles"
```

All three commits go in one PR. They get squash-merged into one commit on `main`.

---

### Full commit workflow (copy-paste)

```bash
# Start from latest main
git checkout main
git pull origin main

# Create branch for your ticket
git checkout -b INT-009-user-model

# ... write code ...

# Commit
git add backend/apps/accounts/
git commit -m "INT-009: add User model with role field"

# More work? Commit again
git add backend/apps/accounts/
git commit -m "INT-009: add tests for User model and roles"

# Push branch to GitHub
git push -u origin INT-009-user-model
```

---

## 4. How to open a Pull Request

### Step 1 — Push your branch

```bash
git push -u origin INT-009-user-model
```

### Step 2 — Create PR on GitHub

**Option A — GitHub CLI (fastest):**

```bash
gh pr create \
  --title "INT-009: User model with roles" \
  --body "$(cat <<'EOF'
## Ticket
Closes INT-009

## What I did
- Created custom User model in `apps/accounts/`
- Added role field: admin, recruiter, interviewer, hiring_manager
- Registered in Django admin
- Added model tests

## How to test
1. `cd backend && source .venv/bin/activate`
2. `python manage.py migrate`
3. `python manage.py createsuperuser`
4. Open http://localhost:8000/admin/ → verify User model with roles
5. `make test` → all pass

## Acceptance criteria
- [x] Custom User model with email login
- [x] Role field with 4 roles
- [x] Admin can assign roles

## Screenshots
(optional — add if UI changes)
EOF
)"
```

**Option B — GitHub website:**

1. Go to https://github.com/maaqoul/sqli-interview-tracker
2. You'll see a yellow banner: **"INT-009-user-model had recent pushes"** → click **Compare & pull request**
3. Fill in title and description using the template below
4. Click **Create pull request**

---

### PR template (copy this every time)

```markdown
## Ticket
Closes INT-XXX

## What I did
- bullet point 1
- bullet point 2

## How to test
1. step by step instructions so mentor can verify
2. include commands to run
3. include URLs to open

## Acceptance criteria
- [x] criterion from the GitHub issue
- [x] criterion 2
- [x] criterion 3

## Screenshots
(optional — required for UI tickets INT-014+)
```

**Important:**
- `Closes INT-XXX` auto-closes the GitHub issue when PR is merged
- "How to test" must be copy-pasteable — mentor shouldn't guess
- Check off acceptance criteria yourself before requesting review

---

### Step 3 — Request review

1. On the PR page, click **Reviewers** → select `@maaqoul`
2. Move ticket to **In Review** on the Project board
3. Comment on the GitHub issue: "PR ready for review: #XX"

---

### Step 4 — After merge

```bash
git checkout main
git pull origin main
git branch -d INT-009-user-model        # delete local branch
```

Start next ticket:

```bash
git checkout -b INT-010-jwt-auth
```

---

## 5. PR review process

```
You open PR
    ↓
Mentor reviews (24–48h)
    ↓
  ┌─────────────────┐
  │  Approved ✅     │ → Mentor merges → ticket closed → you pull main
  └─────────────────┘
  ┌─────────────────┐
  │ Changes requested│ → You fix on same branch → push → re-request review
  └─────────────────┘
```

### If mentor requests changes

```bash
# Stay on your branch (don't create a new one)
git checkout INT-009-user-model

# Make fixes
# ...

git add .
git commit -m "INT-009: address review — add missing migration"
git push

# Comment on PR: "Fixed, ready for re-review"
```

**Do NOT** open a new PR for fixes. Push to the same branch.

### What mentor checks

| Area | What they look for |
|------|-------------------|
| Correctness | Does it match acceptance criteria? |
| Tests | Are critical paths tested? |
| Security | No secrets in code, permissions enforced |
| Code style | Readable, follows existing patterns |
| Scope | No unrelated changes bundled in |
| Migrations | Model changes have migration files |
| UI | Matches BRAND.md colors and INTERN-GUIDE wireframes |

---

## 6. What NOT to do

| ❌ Never | ✅ Instead |
|----------|-----------|
| Push to `main` directly | Always use a branch + PR |
| One giant PR with 10 tickets | One PR per ticket (max 2 related) |
| Commit `.env` or API keys | Use `.env.example`, keep secrets local |
| `git add .` blindly | Check `git status` first |
| Commit messages like "fix" or "wip" | `INT-XXX: describe what changed` |
| Open PR with empty description | Fill in the template |
| Merge your own PR | Wait for mentor approval |
| Leave PR open for days without update | Communicate blockers on the issue |
| Skip tests because "it's just UI" | At minimum: manual test steps in PR |

---

## 7. Cheat sheet

```bash
# ── START NEW TICKET ──
git checkout main && git pull origin main
git checkout -b INT-XXX-short-name

# ── WHILE WORKING ──
make dev-backend          # terminal 1
make dev-frontend         # terminal 2
make test                 # before committing
make lint                 # before PR

# ── COMMIT ──
git status                # review changes
git add <files>           # stage specific files
git commit -m "INT-XXX: what you did"
git push -u origin INT-XXX-short-name

# ── OPEN PR ──
gh pr create --title "INT-XXX: title" --body "Closes INT-XXX ..."

# ── AFTER MERGE ──
git checkout main && git pull origin main
git branch -d INT-XXX-short-name

# ── IF CONFLICTS ON MAIN ──
git checkout INT-XXX-short-name
git fetch origin
git merge origin/main     # resolve conflicts, commit, push
```

### Quick reference

| Item | Format |
|------|--------|
| Branch name | `INT-XXX-short-description` |
| Commit message | `INT-XXX: imperative description` |
| PR title | `INT-XXX: short description` |
| PR body first line | `Closes INT-XXX` |
| Ticket done | All acceptance criteria ✅ + PR merged |
| Week 1 done | Demo script passes live |
| Project done | Full 5-min demo + all tickets closed |

---

**Questions about workflow?** Comment on your GitHub issue or tag `@maaqoul`.
