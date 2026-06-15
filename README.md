# SQLI Interview Tracker — Intern Project

> **"We Elevate. Digitally."** — Internal interview & candidate tracking platform for SQLI recruiters and hiring managers, with AI-assisted interview workflows.

**GitHub:** https://github.com/maaqoul/sqli-interview-tracker  
**Intern guide (start here):** [`INTERN-GUIDE.md`](./INTERN-GUIDE.md) — setup, UI specs, API, everything  
**Commits & PRs:** [`WORKFLOW.md`](./WORKFLOW.md) — definition of done, how to commit, open PRs  
**2-week plan:** [`2-WEEK-PLAN.md`](./2-WEEK-PLAN.md)

---

## Quick start (scaffold is ready)

```bash
git clone https://github.com/maaqoul/sqli-interview-tracker.git
cd sqli-interview-tracker
cp .env.example .env
make setup

# Terminal 1
make dev-backend    # http://localhost:8000/api/health/

# Terminal 2
make dev-frontend   # http://localhost:5173
```

**Your first ticket: INT-009** (User model with roles). Tickets INT-001 → INT-008 are already done.

A full-stack **Interview Tracking App** branded for [SQLI](https://www.sqli.com) — the European leader in Customer Experience & Digital Transformation (2,200+ employees, 12 countries, founded 1990, Euronext: SQI.PA).

The app lets SQLI HR teams:
- Track candidates through a hiring pipeline
- Schedule and score interviews
- Use **AI** to generate questions, summarize feedback, and run mock interview sessions
- View dashboards on hiring velocity and pipeline health

**Stack (mandatory):**
| Layer | Tech |
|-------|------|
| Backend | Python 3.12 + **Django 5** + **Django REST Framework** |
| Frontend | **Vue 3** + Vite + Pinia + Vue Router |
| Database | PostgreSQL 16 |
| AI | OpenAI API (or Ollama for local dev) |
| Auth | JWT (djangorestframework-simplejwt) |

---

## Files in this folder

| File | Purpose |
|------|---------|
| [`WORKFLOW.md`](./WORKFLOW.md) | **Definition of done, commits, PRs** — how to ship work |
| [`INTERN-GUIDE.md`](./INTERN-GUIDE.md) | Complete intern guide — local setup, UI specs, API, troubleshooting |
| [`SPEC.md`](./SPEC.md) | Full product & technical specification |
| [`BRAND.md`](./BRAND.md) | SQLI brand guide — colors, typography, logo URLs |
| [`TICKETS.md`](./TICKETS.md) | **Human-readable ticket board** — start here |
| [`tickets.csv`](./tickets.csv) | Import into GitHub Issues / Plane / Taiga |
| [`tickets.json`](./tickets.json) | Same tickets, JSON format |
| [`IMPORT-GUIDE.md`](./IMPORT-GUIDE.md) | How to load tickets into free Jira-like tools |

---

## Quick start for the intern

```bash
# 1. Read the spec
cat SPEC.md

# 2. Import tickets (pick one method from IMPORT-GUIDE.md)
#    Recommended: GitHub Projects (free) or Plane Community (free)

# 3. Work tickets in order: SETUP → AUTH → CORE → AI → UI → DEPLOY
#    Each ticket has: ID, priority, estimate, acceptance criteria, dependencies

# 4. Target: MVP operational in ~6–8 weeks (part-time intern pace)
```

---

## Definition of Done (whole project)

The app is **operational** when ALL of these work end-to-end:

- [ ] Recruiter logs in with SQLI-branded UI
- [ ] Creates a job opening and adds candidates
- [ ] Moves candidates through pipeline stages (drag or button)
- [ ] Schedules an interview and assigns interviewers
- [ ] Interviewer fills a scorecard after the interview
- [ ] AI generates role-specific interview questions
- [ ] AI summarizes interview notes into a hiring recommendation
- [ ] AI mock interview chat works for candidate prep
- [ ] Dashboard shows pipeline stats
- [ ] App runs via `docker compose up` with README instructions
- [ ] 20+ API tests pass, critical frontend flows work

---

## SQLI context (why this project)

SQLI positions itself as a **CX & digital transformation partner** with **AI embedded at every stage** — from strategy to deployment. They serve large enterprises (Puratos, Alstom, Bioderma, Aréas Assurances…) across:

- Application Engineering
- Data & AI
- Experience Platform
- Customer Activation
- Digital Strategy

Building an AI-powered interview tracker mirrors SQLI's real internal needs (2,200 employees, constant hiring) and demonstrates skills they'd value: Python APIs, Vue SPAs, PostgreSQL, and practical AI integration.

---

## Who to ask for help

Bring blockers to your mentor with:
1. Ticket ID (e.g. `INT-023`)
2. What you tried
3. Error message or screenshot

Good luck — elevate digitally. 🚀
