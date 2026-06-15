# Intern Developer Guide — SQLI Interview Tracker

> **Read this document first.** It has everything: local setup, UI specs, API reference, workflow, and troubleshooting.

| Link | What |
|------|------|
| Repo | https://github.com/maaqoul/sqli-interview-tracker |
| Your sprint plan | [`2-WEEK-PLAN.md`](./2-WEEK-PLAN.md) |
| Tickets | https://github.com/maaqoul/sqli-interview-tracker/issues |
| First ticket | [INT-009 — User model](https://github.com/maaqoul/sqli-interview-tracker/issues/9) |
| Full product spec | [`SPEC.md`](./SPEC.md) |
| Brand colors/fonts | [`BRAND.md`](./BRAND.md) |
| **Commits, PRs & DoD** | [`WORKFLOW.md`](./WORKFLOW.md) |

---

## Table of contents

1. [What you're building](#1-what-youre-building)
2. [Prerequisites](#2-prerequisites)
3. [Local setup — step by step](#3-local-setup--step-by-step)
4. [Running the app (3 ways)](#4-running-the-app-3-ways)
5. [Project structure tour](#5-project-structure-tour)
6. [How to work day-to-day](#6-how-to-work-day-to-day)
7. [UI specifications (all screens)](#7-ui-specifications-all-screens)
8. [Design system & components](#8-design-system--components)
9. [API reference](#9-api-reference)
10. [AI integration guide](#10-ai-integration-guide)
11. [Testing guide](#11-testing-guide)
12. [Troubleshooting](#12-troubleshooting)
13. [Definition of done](#13-definition-of-done)

---

## 1. What you're building

An internal **interview tracking tool** for [SQLI](https://www.sqli.com) — a European digital transformation company (~2,200 employees, tagline: *"We Elevate. Digitally."*).

Recruiters use it to:
- Track candidates through a hiring pipeline (Applied → Hired)
- Schedule interviews and collect scorecards
- Use **AI** to generate questions, summarize feedback, and run mock interviews

### Stack (don't change this)

| Layer | Technology |
|-------|------------|
| Backend | Python 3.12, Django 5, Django REST Framework |
| Frontend | Vue 3, TypeScript, Vite, Pinia, Vue Router, Tailwind CSS |
| Database | PostgreSQL 16 |
| Auth | JWT (`djangorestframework-simplejwt`) |
| AI | OpenAI API (or Ollama for free local dev) |
| API docs | Swagger at `/api/docs/` |

### What's already done for you

Tickets **INT-001 → INT-008** are closed on GitHub. The scaffold includes:
- Django project with health endpoint
- Vue app with SQLI login + dashboard shell
- Docker Compose, Makefile, CI pipeline
- SQLI color tokens in Tailwind

**You start at INT-009.**

---

## 2. Prerequisites

Install these before day 1:

| Tool | Version | Check | Install |
|------|---------|-------|---------|
| Python | 3.12+ | `python3 --version` | https://python.org |
| Node.js | 20+ | `node --version` | https://nodejs.org |
| Git | any | `git --version` | `brew install git` |
| Docker | optional | `docker --version` | https://docker.com |
| PostgreSQL | optional | `psql --version` | `brew install postgresql@16` |

**Accounts you need:**
- GitHub account (you'll be invited to the repo)
- OpenAI API key (ask mentor) OR Ollama installed locally (free)

---

## 3. Local setup — step by step

### Step 1 — Clone the repo

```bash
git clone https://github.com/maaqoul/sqli-interview-tracker.git
cd sqli-interview-tracker
```

### Step 2 — Environment variables

```bash
cp .env.example .env
```

Open `.env` and set at minimum:

```env
DJANGO_SECRET_KEY=any-random-string-at-least-50-chars-long-for-dev-only-ok
DJANGO_DEBUG=True

# For local dev without Docker, SQLite is used automatically.
# For Docker/Postgres (recommended):
DATABASE_URL=postgres://sqli:sqli_dev_password@localhost:5432/sqli_interviews

# AI — pick one:
AI_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here

# OR free local AI:
# AI_PROVIDER=ollama
# OLLAMA_BASE_URL=http://localhost:11434
```

### Step 3 — Install dependencies

```bash
make setup
```

This runs:
- `python -m venv` + `pip install` in `backend/`
- `npm install` in `frontend/`

If `make setup` fails, do it manually:

```bash
# Backend
cd backend
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cd ..

# Frontend
cd frontend
npm install
cd ..
```

### Step 4 — Database migrations

```bash
cd backend
source .venv/bin/activate
python manage.py migrate
cd ..
```

### Step 5 — Verify backend

```bash
make dev-backend
```

Open http://localhost:8000/api/health/ — you should see:

```json
{"status": "ok", "service": "sqli-interview-tracker"}
```

Also check:
- http://localhost:8000/api/ — API root
- http://localhost:8000/api/docs/ — Swagger UI

### Step 6 — Verify frontend

In a **second terminal**:

```bash
make dev-frontend
```

Open http://localhost:5173 — you should see the SQLI login page.

- Click **Sign in** → redirects to dashboard (placeholder auth for now)
- Dashboard shows "API Status" — should say ✓ Backend healthy

### Step 7 — Run tests

```bash
make test
```

Expected: `2 passed` (health check tests).

---

## 4. Running the app (3 ways)

### Option A — Make commands (recommended for daily dev)

```bash
# Terminal 1 — backend (auto-reloads on file change)
make dev-backend

# Terminal 2 — frontend (hot reload)
make dev-frontend
```

| Service | URL |
|---------|-----|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000/api/ |
| Swagger docs | http://localhost:8000/api/docs/ |
| Django admin | http://localhost:8000/admin/ |

### Option B — Docker Compose (full stack with Postgres)

```bash
cp .env.example .env
docker compose up
```

| Service | URL |
|---------|-----|
| Frontend | http://localhost:5173 |
| Backend | http://localhost:8000 |
| Postgres | localhost:5432 |

Stop: `docker compose down`

### Option C — Manual (if Make doesn't work)

```bash
# Backend
cd backend && source .venv/bin/activate
python manage.py runserver

# Frontend (new terminal)
cd frontend && npm run dev
```

---

## 5. Project structure tour

```
sqli-interview-tracker/
├── backend/                    ← Python Django API
│   ├── config/                 ← settings, urls, wsgi
│   │   ├── settings.py         ← main config (DB, JWT, AI keys)
│   │   └── urls.py             ← routes to /api/
│   ├── apps/
│   │   └── core/               ← health check (you'll add more apps)
│   ├── manage.py
│   └── requirements.txt
│
├── frontend/                   ← Vue 3 SPA
│   ├── src/
│   │   ├── api/client.ts       ← Axios instance (JWT interceptor)
│   │   ├── router/index.ts     ← routes + auth guards
│   │   ├── stores/auth.ts      ← Pinia auth store
│   │   ├── views/              ← page components (one per screen)
│   │   ├── components/         ← reusable UI pieces
│   │   └── style.css           ← Tailwind + SQLI CSS variables
│   ├── public/assets/          ← put SQLI logos here
│   └── vite.config.ts          ← dev server + API proxy
│
├── docker-compose.yml
├── Makefile                    ← shortcuts: up, test, lint, seed
├── .env.example
├── SPEC.md                     ← full product spec
├── BRAND.md                    ← colors, fonts, logos
├── 2-WEEK-PLAN.md              ← your daily schedule
└── INTERN-GUIDE.md             ← this file
```

### Where to add your code

| Feature | Backend (create app in `apps/`) | Frontend |
|---------|----------------------------------|----------|
| Auth | `apps/accounts/` | `stores/auth.ts`, `views/LoginView.vue` |
| Jobs | `apps/jobs/` | `views/JobsView.vue`, `components/jobs/` |
| Candidates | `apps/candidates/` | `views/CandidatesView.vue`, `components/candidates/` |
| Interviews | `apps/interviews/` | `views/InterviewsView.vue`, `components/interviews/` |
| AI | `apps/ai_assistant/` | `components/ai/`, `views/AIToolsView.vue` |
| Dashboard | `apps/dashboard/` | `views/DashboardView.vue` |

---

## 6. How to work day-to-day

> **Full guide:** [`WORKFLOW.md`](./WORKFLOW.md) — definition of done, commit format, PR step-by-step, review process.

### Morning routine

```
1. git pull origin main
2. Open GitHub Issues → pick your ticket (e.g. INT-009)
3. Move ticket to "In Progress" on Project board
4. Create branch: git checkout -b INT-009-user-model
5. Code until acceptance criteria are ✅
6. Open PR → tag @maaqoul for review
```

### Branch naming

```
INT-009-user-model
INT-020-candidate-crud
```

See [`WORKFLOW.md`](./WORKFLOW.md) for commit format, PR template, and full git commands.

### When you're stuck

1. Re-read the ticket acceptance criteria on GitHub
2. Check this guide's UI spec for the screen you're building
3. Comment on the GitHub issue: what you tried + error message
4. Tag `@maaqoul`

---

## 7. UI specifications (all screens)

### Global layout — App Shell

Every authenticated page uses this layout. Build this in **INT-039**.

```
┌──────────────────────────────────────────────────────────────────┐
│ ┌─────────────┐  ┌─────────────────────────────────────────────┐ │
│ │             │  │  Topbar                          🔔  👤 ▾   │ │
│ │   SIDEBAR   │  ├─────────────────────────────────────────────┤ │
│ │  (midnight) │  │                                             │ │
│ │             │  │              MAIN CONTENT                   │ │
│ │  SQLI logo  │  │              (cream background)             │ │
│ │             │  │                                             │ │
│ │  Dashboard  │  │                                             │ │
│ │  Candidates │  │                                             │ │
│ │  Jobs       │  │                                             │ │
│ │  Interviews │  │                                             │ │
│ │  AI Tools   │  │                                             │ │
│ │  Settings   │  │                                             │ │
│ │             │  │                                             │ │
│ │  [collapse] │  │                                             │ │
│ └─────────────┘  └─────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
```

| Element | Spec |
|---------|------|
| Sidebar width | 256px expanded, 64px collapsed |
| Sidebar bg | `#1A1F4E` (midnight blue) |
| Active nav item | `bg-white/10` + sky blue left border 3px |
| Inactive nav item | `text-white/60`, hover `text-white` |
| Content bg | `#FAF7F2` (cream) |
| Content padding | 32px |
| Topbar height | 56px, white bg, bottom border `gray-100` |

**Sidebar nav items (in order):**
1. Dashboard — icon: `LayoutDashboard`
2. Candidates — icon: `Users`
3. Jobs — icon: `Briefcase`
4. Interviews — icon: `Calendar`
5. AI Tools — icon: `Sparkles`
6. Settings — icon: `Settings`

---

### Screen 1 — Login (`/login`) — INT-014

**Already scaffolded.** Wire to real API in INT-013.

```
┌────────────────────────────────────────┐
│                                        │
│              [SQLI LOGO]               │
│        We Elevate. Digitally.          │
│          Interview Tracker             │
│                                        │
│   ┌──────────────────────────────┐     │
│   │  Sign in                     │     │
│   │                              │     │
│   │  Email    [_______________]  │     │
│   │  Password [_______________]  │     │
│   │                              │     │
│   │  [ error message if any ]    │     │
│   │                              │     │
│   │  [    Sign in (cobalt)    ]  │     │
│   └──────────────────────────────┘     │
│                                        │
└────────────────────────────────────────┘
```

| Element | Spec |
|---------|------|
| Page bg | Cream `#FAF7F2` |
| Card | White, `rounded-xl`, `p-8`, max-width 400px, centered |
| Logo | `sqli-logo.svg` from `public/assets/`, height 40px |
| Tagline | `text-sqli-cobalt`, `text-sm`, `font-medium` |
| CTA button | Full width, cobalt bg, white text, `rounded-lg`, `py-2.5` |
| Button hover | `#003399` |
| Input focus | Ring `sqli-sky` 2px |
| Error text | Red `#EF4444`, `text-sm` |

**States:**
- Default: empty form
- Loading: button shows "Signing in…", disabled
- Error: red message below password field
- Success: redirect to `/dashboard`

---

### Screen 2 — Dashboard (`/dashboard`) — INT-040

```
┌─────────────────────────────────────────────────────────────┐
│  Dashboard                                                  │
│  Overview of your hiring pipeline                           │
│                                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ Open Jobs│  │Candidates│  │This Week │  │ Avg Hire │   │
│  │    12    │  │    47    │  │    8     │  │  18 days │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
│                                                             │
│  ┌─────────────────────────┐  ┌─────────────────────────┐   │
│  │  Pipeline Funnel      │  │  Recent Activity        │   │
│  │  [bar chart]          │  │  • Jean moved to Tech   │   │
│  │  Applied ████ 15      │  │  • Scorecard submitted  │   │
│  │  Screening ███ 8      │  │  • New candidate added  │   │
│  │  Technical ██ 5       │  │  • Interview scheduled  │   │
│  └─────────────────────────┘  └─────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Upcoming Interviews (this week)                   │   │
│  │  Mon 10:00 — Jean Dupont — Technical — M. Martin    │   │
│  │  Tue 14:00 — Sara Lee — Culture — A. Bernard       │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

| Element | Spec |
|---------|------|
| Page title | `text-2xl font-semibold text-sqli-midnight` |
| Subtitle | `text-gray-500 text-sm` |
| Stat cards | White bg, `rounded-xl`, `p-6`, number in `text-3xl font-bold text-sqli-cobalt` |
| Chart | Use Chart.js — horizontal bar chart, stage colors from BRAND.md |
| Activity feed | List with avatar circle + action text + relative time ("2h ago") |

**Data source:** `GET /api/dashboard/stats/` and `GET /api/dashboard/funnel/`

---

### Screen 3 — Candidates List (`/candidates`) — INT-024, INT-025

**Two views toggled by tabs: Table | Kanban**

#### Table view

```
┌─────────────────────────────────────────────────────────────┐
│  Candidates                    [+ Add Candidate]  [Table|Kanban]
│                                                             │
│  🔍 Search...    Job: [All ▾]   Stage: [All ▾]             │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ Name ▲      │ Job              │ Stage    │ Added    │ │
│  ├─────────────┼──────────────────┼──────────┼──────────┤ │
│  │ Jean Dupont │ Sr Python Dev    │ ● Tech   │ 3d ago   │ │
│  │ Sara Lee    │ UX Designer      │ ● Screen │ 1d ago   │ │
│  │ Tom Brown   │ Sr Python Dev    │ ● Applied│ today    │ │
│  └───────────────────────────────────────────────────────┘ │
│                                        ← 1  2  3 →         │
└─────────────────────────────────────────────────────────────┘
```

| Element | Spec |
|---------|------|
| Add button | Cobalt, top-right, icon `Plus` + "Add Candidate" |
| View toggle | Segmented control: Table / Kanban |
| Stage badge | Colored dot + label, colors per BRAND.md pipeline table |
| Row click | Navigate to `/candidates/:id` |
| Pagination | 20 per page, bottom-right |

#### Kanban view

```
┌──────────────────────────────────────────────────────────────────────────┐
│  Applied (3)  │ Screening (2) │ Technical (1) │ Culture (0) │ Offer (1) │
│ ┌───────────┐ │ ┌───────────┐ │ ┌───────────┐ │             │ ┌───────┐ │
│ │ Tom Brown │ │ │ Sara Lee  │ │ │ Jean D.   │ │  (empty)    │ │ Ali K │ │
│ │ Sr Python │ │ │ UX Design │ │ │ Sr Python │ │             │ │ Sr Py │ │
│ │ 2d in stg │ │ │ 1d in stg │ │ │ 5d in stg │ │             │ │ 3d    │ │
│ └───────────┘ │ └───────────┘ │ └───────────┘ │             │ └───────┘ │
│ ┌───────────┐ │ ┌───────────┐ │               │             │           │
│ │ ...       │ │ │ ...       │ │               │             │           │
│ └───────────┘ │ └───────────┘ │               │             │           │
└──────────────────────────────────────────────────────────────────────────┘
```

| Element | Spec |
|---------|------|
| Columns | One per pipeline stage, horizontal scroll if >5 |
| Column header | Stage name + count badge, stage color as top border 3px |
| Card | White, `rounded-lg`, `p-3`, shadow on hover, draggable |
| Card content | Name (bold), job title (gray sm), "Xd in stage" (xs gray) |
| Drag | Drop on column → calls `POST /api/candidates/:id/move-stage/` |
| Empty column | Dashed border placeholder: "Drop candidates here" |

**Library suggestion:** `@vueuse/integrations/useSortable` or `vuedraggable`

---

### Screen 4 — Candidate Detail (`/candidates/:id`) — INT-026

```
┌─────────────────────────────────────────────────────────────┐
│  ← Back to Candidates                                       │
│                                                             │
│  Jean Dupont                    [Schedule Interview] [Reject]│
│  jean@email.com · +33 6 12 34 56 78                        │
│  Senior Python Developer — Paris    Stage: ● Technical      │
│                                                             │
│  [Overview] [Timeline] [Interviews] [Scorecards] [AI Brief] │
│  ─────────────────────────────────────────────────────────  │
│                                                             │
│  ┌─ Overview tab ──────────────────────────────────────┐   │
│  │  LinkedIn: linkedin.com/in/jeandupont               │   │
│  │  Source: LinkedIn                                   │   │
│  │  Resume: [📄 jean_cv.pdf] [Download]                │   │
│  │  Notes: Strong Python background, 5 years Django... │   │
│  │                                                     │   │
│  │  Quick actions:                                     │   │
│  │  [Move to next stage ▾]  [Add note]                 │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

#### Timeline tab

Vertical timeline, newest first:

```
● Today 14:30 — Stage changed to Technical (by Recruiter A)
● Today 10:00 — Interview scheduled: Technical, Dec 20 10:00
● Yesterday — Scorecard submitted by M. Martin (Rating: 4/5)
● 3 days ago — Candidate added (by Recruiter A)
```

#### AI Brief tab (INT-036)

```
┌─ AI Hiring Brief ─────────────────────────────────────────┐
│  ⚡ Generated by AI — human decision required              │
│                                                          │
│  Strengths:                                              │
│  • Strong Django/DRF experience                          │
│  • Clear communication in screening                      │
│                                                          │
│  Concerns:                                               │
│  • Limited Vue.js exposure                               │
│                                                          │
│  Recommendation: Yes (3/4 interviewers)                  │
│  Suggested next step: Proceed to Culture Fit interview   │
│                                                          │
│  [Regenerate Brief]                                      │
└──────────────────────────────────────────────────────────┘
```

---

### Screen 5 — Add/Edit Candidate (modal) — INT-020

Modal overlay, max-width 600px:

| Field | Type | Required |
|-------|------|----------|
| First name | text | yes |
| Last name | text | yes |
| Email | email | yes |
| Phone | tel | no |
| LinkedIn URL | url | no |
| Job opening | select dropdown | yes |
| Source | select: LinkedIn, Referral, Job board, Other | no |
| Resume | file upload (PDF, max 5MB) | no |
| Notes | textarea | no |

Buttons: **Cancel** (ghost) | **Save Candidate** (cobalt)

---

### Screen 6 — Jobs List (`/jobs`) — INT-018

```
┌─────────────────────────────────────────────────────────────┐
│  Job Openings                          [+ Create Job]       │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ Title                  │ Dept    │ Candidates │ Status│ │
│  ├────────────────────────┼─────────┼────────────┼───────┤ │
│  │ Senior Python Developer│ Eng     │ 8          │ ● Open│ │
│  │ UX Designer            │ Design  │ 3          │ ● Open│ │
│  │ DevOps Engineer        │ Infra   │ 0          │ ○ Hold│ │
│  └───────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

**Status badges:**
- Open → green dot
- Closed → gray dot
- On hold → amber dot

### Screen 7 — Job Create/Edit Form (`/jobs/new`, `/jobs/:id/edit`) — INT-019

| Field | Type | Required |
|-------|------|----------|
| Title | text | yes |
| Department | text | yes |
| Location | text | yes |
| Level | select: Junior, Mid, Senior, Lead | yes |
| Description | textarea (rich text optional) | yes |
| Required skills | tag input (type + enter to add) | no |
| Status | select: Open, Closed, On hold | yes |

---

### Screen 8 — Interviews Calendar (`/interviews`) — INT-029

```
┌─────────────────────────────────────────────────────────────┐
│  Interviews                    [+ Schedule Interview]       │
│                                                             │
│  ◀  Week of Dec 16–22, 2025  ▶        [Week] [Month]      │
│                                                             │
│  Mon 16    Tue 17    Wed 18    Thu 19    Fri 20             │
│  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐         │
│  │10:00 │  │      │  │14:00 │  │      │  │10:00 │         │
│  │Jean  │  │      │  │Sara  │  │      │  │Tom   │         │
│  │Tech  │  │      │  │Cult. │  │      │  │Phone │         │
│  └──────┘  └──────┘  └──────┘  └──────┘  └──────┘         │
└─────────────────────────────────────────────────────────────┘
```

| Element | Spec |
|---------|------|
| Interview block colors | Phone: sky blue, Video: cobalt, Onsite: midnight |
| Block content | Time, candidate name, interview type |
| Click block | Opens detail modal with edit/cancel |
| Empty day | No blocks, just grid lines |

### Screen 9 — Schedule Interview (modal) — INT-030

| Field | Type | Required |
|-------|------|----------|
| Candidate | select (pre-filled if opened from candidate page) | yes |
| Job | auto-filled from candidate | yes |
| Type | radio: Phone / Video / Onsite | yes |
| Date | date picker | yes |
| Time | time picker | yes |
| Duration | select: 30, 45, 60, 90 min | yes |
| Location / Video link | text | conditional |
| Interviewers | multi-select (user list) | yes |

---

### Screen 10 — Scorecard Form (`/interviews/:id/scorecard`) — INT-032

```
┌─────────────────────────────────────────────────────────────┐
│  Scorecard — Jean Dupont — Technical Interview              │
│  Dec 20, 2025 · 60 min                                      │
│                                                             │
│  Overall Rating          ★ ★ ★ ★ ☆                         │
│                                                             │
│  Technical               ★ ★ ★ ★ ☆                         │
│  Communication           ★ ★ ★ ☆ ☆                         │
│  Problem Solving         ★ ★ ★ ★ ☆                         │
│  Culture Fit             ★ ★ ★ ☆ ☆                         │
│  Leadership              ★ ★ ☆ ☆ ☆                         │
│                                                             │
│  Strengths                                                │
│  [____________________________________________]             │
│                                                             │
│  Weaknesses                                               │
│  [____________________________________________]             │
│                                                             │
│  Recommendation   [Strong Yes ▾]                            │
│                                                             │
│  Private notes (recruiter only)                             │
│  [____________________________________________]             │
│                                                             │
│  [Cancel]  [Submit Scorecard]                               │
└─────────────────────────────────────────────────────────────┘
```

| Element | Spec |
|---------|------|
| Star rating | Click to set 1–5, filled = `#F59E0B` amber, empty = gray |
| Recommendation options | Strong Yes (green), Yes (light green), Neutral (gray), No (orange), Strong No (red) |
| Submit | Cobalt button, marks interview as "completed" |

**"My Interviews" page** (`/my-interviews`) — for interviewers:
- List of assigned interviews with status: pending scorecard / completed
- Click → scorecard form

---

### Screen 11 — AI Tools (`/ai`) — INT-035, INT-037

Three tabs:

#### Tab 1: Question Generator (INT-035)

```
┌─────────────────────────────────────────────────────────────┐
│  AI Interview Assistant                                     │
│  [Question Generator] [Mock Interview] [History]            │
│                                                             │
│  Job: [Senior Python Developer ▾]                          │
│  Level: [Senior ▾]   Type: [Technical ▾]                   │
│                                                             │
│  [✨ Generate Questions]                                    │
│                                                             │
│  ┌─ Generated Questions ─────────────────────────────────┐  │
│  │  1. [Technical · Hard] Explain Django ORM N+1...     │  │
│  │  2. [Technical · Medium] How would you design a...   │  │
│  │  3. [Behavioral · Easy] Tell me about a time...      │  │
│  │  ...                                                  │  │
│  │  [Copy All]  [Regenerate]  [Save to Interview]        │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

#### Tab 2: Mock Interview Chat (INT-037)

```
┌─────────────────────────────────────────────────────────────┐
│  Mock Interview                                             │
│  Role: [Senior Python Developer ▾]  [Start Session]        │
│                                                             │
│  ┌─ Chat ──────────────────────────────────────────────┐   │
│  │ 🤖 Welcome! I'll be interviewing you for the Senior │   │
│  │    Python Developer role. Let's begin.              │   │
│  │                                                     │   │
│  │ 🤖 Question 1: Can you explain the difference      │   │
│  │    between async and sync in Python?                │   │
│  │                                                     │   │
│  │ 👤 async uses event loop and await...               │   │
│  │                                                     │   │
│  │ 🤖 Good answer! You covered the basics well.        │   │
│  │    Question 2: How would you design a REST API...   │   │
│  └─────────────────────────────────────────────────────┘   │
│  [Type your answer...                          ] [Send]     │
│  [End Session]                                              │
└─────────────────────────────────────────────────────────────┘
```

| Element | Spec |
|---------|------|
| AI messages | Left-aligned, `bg-sqli-gray-100`, robot icon |
| User messages | Right-aligned, `bg-sqli-cobalt text-white` |
| AI badge | Gradient sky→cobalt pill: "AI" |
| Loading | Three bouncing dots while waiting for AI |
| Disclaimer | Footer: "AI-assisted — for practice only" |

---

### Screen 12 — Settings (`/settings`) — INT-042

| Section | Fields |
|---------|--------|
| Profile | First name, last name, email (read-only), avatar upload |
| Security | Change password (current, new, confirm) |
| Admin only: Users | Table of users with role dropdown (Admin, Recruiter, Interviewer, Hiring Manager) |

---

### Screen 13 — Notifications (dropdown in topbar) — INT-041

```
┌─ Notifications ──────────────┐
│ ● Interview assigned         │
│   Jean Dupont — Dec 20       │
│   2 hours ago                │
│                              │
│ ○ Scorecard due              │
│   Sara Lee — Culture fit     │
│   1 day ago                  │
│                              │
│ [Mark all as read]           │
└──────────────────────────────┘
```

Bell icon with red badge showing unread count.

---

### Screen 14 — Error pages

| Page | Content |
|------|---------|
| 404 | "Page not found" + SQLI ascender watermark + [Go to Dashboard] |
| 403 | "You don't have permission" + contact admin message |
| 500 | "Something went wrong" + [Retry] |

---

## 8. Design system & components

Build these reusable components in `frontend/src/components/common/`:

### Buttons

| Variant | Classes | Use |
|---------|---------|-----|
| Primary | `bg-sqli-cobalt text-white hover:bg-blue-800 rounded-lg px-4 py-2` | Main actions |
| Secondary | `border border-sqli-cobalt text-sqli-cobalt hover:bg-sqli-cobalt/5 rounded-lg px-4 py-2` | Cancel, secondary |
| Danger | `bg-red-500 text-white hover:bg-red-600 rounded-lg px-4 py-2` | Reject, delete |
| Ghost | `text-gray-600 hover:bg-gray-100 rounded-lg px-4 py-2` | Tertiary |

### Badges

```html
<!-- Stage badge example -->
<span class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium"
      style="background: #6EC4E820; color: #0047BB;">
  <span class="w-1.5 h-1.5 rounded-full" style="background: #6EC4E8"></span>
  Screening
</span>
```

### Cards

```html
<div class="bg-white rounded-xl border border-sqli-gray-100 p-6 shadow-sm">
  <!-- content -->
</div>
```

### Form inputs

```html
<input class="w-full rounded-lg border border-gray-200 px-3 py-2
              focus:outline-none focus:ring-2 focus:ring-sqli-sky focus:border-transparent" />
```

### Toast notifications

Use a simple toast for success/error after actions:
- Success: green left border, "Candidate saved"
- Error: red left border, show API error message
- Position: top-right, auto-dismiss 4s

### Loading states

| Context | Pattern |
|---------|---------|
| Full page | Centered spinner (cobalt) |
| Button | Text changes to "Saving…", disabled |
| Table | Skeleton rows (gray pulse) |
| AI generation | Spinner + "Generating…" (up to 10s) |

### Responsive breakpoints

| Breakpoint | Behavior |
|------------|----------|
| ≥ 1024px | Full sidebar + content |
| 768–1023px | Collapsed sidebar (icons only) |
| < 768px | Sidebar hidden, hamburger menu (stretch goal) |

---

## 9. API reference

Base URL: `http://localhost:8000/api/`

Auth header: `Authorization: Bearer <access_token>`

Full interactive docs: http://localhost:8000/api/docs/

### Auth — INT-010

| Method | Endpoint | Body | Response |
|--------|----------|------|----------|
| POST | `/auth/login/` | `{email, password}` | `{access, refresh}` |
| POST | `/auth/refresh/` | `{refresh}` | `{access}` |
| GET | `/auth/me/` | — | `{id, email, role, first_name, last_name}` |
| POST | `/auth/register/` | `{email, password, first_name, last_name, role}` | user object (admin only) |

### Jobs — INT-016

| Method | Endpoint | Notes |
|--------|----------|-------|
| GET | `/jobs/` | Paginated, filter by status |
| POST | `/jobs/` | Create job |
| GET | `/jobs/:id/` | Detail with candidate counts per stage |
| PUT | `/jobs/:id/` | Update |
| DELETE | `/jobs/:id/` | Soft delete or hard delete |

### Candidates — INT-020

| Method | Endpoint | Notes |
|--------|----------|-------|
| GET | `/candidates/` | Filter: `?job_id=&stage=&search=&page=` |
| POST | `/candidates/` | Create |
| GET | `/candidates/:id/` | Detail |
| PUT | `/candidates/:id/` | Update |
| POST | `/candidates/:id/move-stage/` | `{stage_id, reason}` |
| GET | `/candidates/:id/timeline/` | Activity log |
| POST | `/candidates/:id/upload-resume/` | multipart PDF |

### Interviews — INT-027

| Method | Endpoint | Notes |
|--------|----------|-------|
| GET | `/interviews/` | Filter: `?date_from=&date_to=&interviewer=` |
| POST | `/interviews/` | Create with interviewer IDs |
| GET | `/interviews/:id/` | Detail |
| PUT | `/interviews/:id/` | Update status, etc. |

### Scorecards — INT-031

| Method | Endpoint | Notes |
|--------|----------|-------|
| POST | `/scorecards/` | One per interviewer per interview |
| GET | `/scorecards/?candidate_id=` | All scorecards for candidate |

### AI — INT-034

| Method | Endpoint | Body |
|--------|----------|------|
| POST | `/ai/generate-questions/` | `{job_title, level, skills[], interview_type}` |
| POST | `/ai/summarize-feedback/` | `{candidate_id}` |
| POST | `/ai/mock-interview/` | `{role, level, history[], user_answer}` |
| GET | `/ai/sessions/` | Past AI sessions |

### Dashboard — INT-040

| Method | Endpoint | Response |
|--------|----------|----------|
| GET | `/dashboard/stats/` | `{open_jobs, total_candidates, interviews_this_week, avg_time_to_hire}` |
| GET | `/dashboard/funnel/` | `[{stage, count, color}]` |

### Standard error format

```json
{
  "detail": "Error message here"
}
```

Or field errors:
```json
{
  "email": ["This field is required."],
  "password": ["Password too short."]
}
```

---

## 10. AI integration guide

### Setup OpenAI (recommended)

1. Get API key from mentor
2. Add to `.env`: `OPENAI_API_KEY=sk-...`
3. Set `AI_PROVIDER=openai`

### Setup Ollama (free, local)

```bash
# Install Ollama: https://ollama.com
ollama pull llama3
ollama serve
```

In `.env`:
```env
AI_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
```

### Backend structure (INT-034)

Create `backend/apps/ai_assistant/services.py`:

```python
class AIService:
    def generate_questions(self, job_title, level, skills, interview_type) -> list: ...
    def summarize_feedback(self, scorecards, notes) -> dict: ...
    def mock_interview_turn(self, role, level, history, user_answer) -> dict: ...

class OpenAIProvider(AIService):
    # uses openai library, model gpt-4o-mini

class OllamaProvider(AIService):
    # HTTP calls to OLLAMA_BASE_URL
```

Factory in `services.py`:
```python
def get_ai_service() -> AIService:
    if settings.AI_PROVIDER == "ollama":
        return OllamaProvider()
    return OpenAIProvider()
```

### System prompts (put in `prompts.py`)

**Question generator:**
```
You are an expert technical interviewer at SQLI, a European digital transformation company.
Generate {n} interview questions for a {level} {job_title} position.
Skills: {skills}. Interview type: {interview_type}.
Return JSON: [{"question": "...", "type": "technical|behavioral", "difficulty": "easy|medium|hard"}]
```

**Mock interview:**
```
You are a professional interviewer at SQLI conducting a {level} {role} interview.
Ask one question at a time. After the candidate answers, give brief constructive feedback (2 sentences max), then ask the next question.
Be professional, encouraging, and focused on CX/technology skills.
```

**Feedback summarizer:**
```
Analyze these interview scorecards and notes for a hiring decision.
Return JSON: {"strengths": [], "concerns": [], "recommendation": "...", "suggested_next_step": "..."}
Do NOT make the final hiring decision — provide a recommendation only.
```

### Rate limiting

Max 20 AI calls per user per hour. Return `429 Too Many Requests` if exceeded.

### Always show disclaimer in UI

> "AI-assisted — human decision required"

---

## 11. Testing guide

### Backend tests

```bash
cd backend && source .venv/bin/activate
pytest -v                    # run all
pytest apps/core/tests.py -v # run one file
pytest --cov=apps            # with coverage
```

**What to test (per feature):**
- Model creation and validation
- API endpoints (happy path + 401/403/400)
- Permissions (interviewer can't delete candidates)
- AI endpoints with mocked `AIService` (don't call real OpenAI in tests)

Example test pattern:
```python
class CandidateAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.recruiter = User.objects.create_user(
            email="r@sqli.com", password="test", role="recruiter"
        )
        self.client.force_authenticate(self.recruiter)

    def test_create_candidate(self):
        response = self.client.post("/api/candidates/", {
            "first_name": "Jean", "last_name": "Dupont",
            "email": "jean@test.com", "job_id": 1,
        })
        self.assertEqual(response.status_code, 201)
```

### Frontend manual testing

After each screen, verify:
- [ ] Page loads without console errors
- [ ] Loading state shows while fetching
- [ ] Empty state shows when no data
- [ ] Error state shows on API failure
- [ ] Form validation works (required fields)
- [ ] Success toast after save
- [ ] Navigation works (back buttons, sidebar links)
- [ ] SQLI colors match BRAND.md

### Linting

```bash
make lint
# or separately:
cd backend && ruff check .
cd frontend && npm run lint
```

---

## 12. Troubleshooting

### Backend won't start

| Error | Fix |
|-------|-----|
| `ModuleNotFoundError: No module named 'django'` | `cd backend && source .venv/bin/activate && pip install -r requirements.txt` |
| `port 8000 already in use` | `lsof -i :8000` then `kill <PID>` or use `python manage.py runserver 8001` |
| Database connection error | Check `.env` DATABASE_URL, or use SQLite (remove DATABASE_URL) |
| Migration errors | `python manage.py migrate --run-syncdb` or delete `db.sqlite3` and re-migrate |

### Frontend won't start

| Error | Fix |
|-------|-----|
| `npm ERR!` on install | Delete `node_modules` + `package-lock.json`, run `npm install` again |
| Port 5173 in use | `npm run dev -- --port 5174` |
| API calls fail (CORS) | Make sure backend is running. Check `vite.config.ts` proxy. |
| `Cannot find module '@/...'` | Check `vite.config.ts` has the `@` alias |

### Docker issues

| Error | Fix |
|-------|-----|
| `Cannot connect to Docker daemon` | Start Docker Desktop |
| Postgres won't start | `docker compose down -v` then `docker compose up` (⚠️ deletes data) |
| Backend can't reach db | Wait for db healthcheck, or `docker compose up db` first |

### AI not working

| Error | Fix |
|-------|-----|
| `401 Unauthorized` from OpenAI | Check `OPENAI_API_KEY` in `.env` |
| `Connection refused` Ollama | Run `ollama serve` in a terminal |
| Slow responses (>10s) | Normal for AI. Show loading spinner. Use `gpt-4o-mini` for speed. |
| `429 Rate limit` | Your rate limiter is working. Wait or adjust in settings. |

### Auth issues

| Error | Fix |
|-------|-----|
| 401 on all API calls | Check JWT token in localStorage. Try logout + login. |
| Token expired | Implement refresh in Axios interceptor (INT-013) |
| CORS error with credentials | Backend `CORS_ALLOWED_ORIGINS` must include `http://localhost:5173` |

---

## 13. Definition of done

> **Full guide:** [`WORKFLOW.md`](./WORKFLOW.md) — 4 levels of done (ticket, PR, week, project).

The project is **complete** when you can demo this flow live:

```
1.  Open http://localhost:5173 → SQLI login page
2.  Login as recruiter → dashboard with real stats
3.  Create job "Senior Python Developer — Paris"
4.  Add candidate with PDF resume
5.  Drag candidate from Applied → Screening on kanban
6.  Schedule technical interview, assign interviewer
7.  Login as interviewer → submit scorecard with ratings
8.  View AI Hiring Brief on candidate page
9.  Generate 10 interview questions with AI
10. Complete 3-question mock interview chat
11. Dashboard funnel chart shows correct counts
12. docker compose up starts everything
13. make test passes
```

Record a 5-minute screen recording of this flow for INT-048.

---

## Quick links

| Resource | URL |
|----------|-----|
| Django REST Framework docs | https://www.django-rest-framework.org |
| Vue 3 docs | https://vuejs.org |
| Pinia docs | https://pinia.vuejs.org |
| Tailwind CSS docs | https://tailwindcss.com |
| Lucide icons (Vue) | https://lucide.dev/guide/packages/lucide-vue-next |
| Chart.js | https://www.chartjs.org |
| OpenAI API docs | https://platform.openai.com/docs |
| SQLI website (brand ref) | https://www.sqli.com |
| SQLI brand case study | https://cdlx.de/projects/sqli |

---

**Questions?** Comment on your GitHub issue or tag `@maaqoul`.

Good luck — elevate digitally. 🚀
