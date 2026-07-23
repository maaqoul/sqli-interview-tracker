# Manual Frontend Test Checklist

Step-by-step checks for the SQLI Interview Tracker UI. Covers the acceptance demo script in [SPEC.md §10](./SPEC.md#10-acceptance-demo-script) plus a few related flows.

**Prerequisites**

- App running (`make up` / `docker compose up`, or local `make dev-backend` + `make dev-frontend`)
- Demo data loaded (`make seed` or `docker compose exec backend python manage.py seed_demo`)
- Demo password for all seed users: `DemoPass123!`

| Role | Email |
|------|-------|
| Admin | `admin@sqli.com` |
| Recruiter | `recruiter1@sqli.com` |
| Interviewer | `interviewer1@sqli.com` |

Mark each box when verified.

---

## A. Acceptance demo script (SPEC.md §10)

### 1. Login as recruiter (SQLI branded login)

- [ ] Open the app (Docker: http://localhost — local: http://localhost:5173)
- [ ] Login page shows SQLI branding (logo / brand colors, not a generic form)
- [ ] Sign in as `recruiter1@sqli.com` / `DemoPass123!`
- [ ] Lands on dashboard (or app shell with sidebar)

### 2. Create job "Senior Python Developer — Paris"

- [ ] Go to **Jobs** → create job
- [ ] Title: `Senior Python Developer — Paris` (or edit seed job / create equivalent)
- [ ] Location includes Paris; department/level set
- [ ] Job saves and appears in the jobs list / detail

### 3. Add candidate with resume upload

- [ ] Open **Candidates** → add / create candidate
- [ ] Fill name, email, link to a job
- [ ] Upload a resume file (PDF or DOCX)
- [ ] Candidate detail shows uploaded resume / download link

### 4. Drag candidate Applied → Screening (kanban)

- [ ] Open candidates **kanban** view for a job (or pipeline board)
- [ ] Drag a card from **Applied** to **Screening**
- [ ] Stage updates without a full page reload
- [ ] Candidate detail / activity reflects the new stage

### 5. Schedule technical interview, assign interviewer

- [ ] From candidate or **Interviews**, schedule an interview
- [ ] Type: technical / video (or equivalent)
- [ ] Assign `interviewer1@sqli.com` (or another interviewer)
- [ ] Interview appears on calendar / candidate timeline

### 6. Login as interviewer → scorecard → submit

- [ ] Log out; sign in as `interviewer1@sqli.com` / `DemoPass123!`
- [ ] Open **My Interviews** (or assigned interview)
- [ ] Open scorecard form
- [ ] Set overall + skill star ratings, recommendation, strengths/weaknesses
- [ ] Submit; interview marked completed / scorecard saved

### 7. AI Summarize → hiring brief

- [ ] As recruiter (or admin), open candidate detail with scorecards
- [ ] Click **Generate Brief** / AI Hiring Brief action
- [ ] Brief shows strengths, concerns, recommendation, next step
- [ ] Disclaimer visible: AI-assisted — human decision required

### 8. AI Question Generator → ~10 questions

- [ ] Open **AI Tools** → Question Generator
- [ ] Select a job / level → **Generate Questions**
- [ ] Loading state appears; 8–12 questions return (types + difficulty)
- [ ] Can copy / regenerate

### 9. AI Mock Interview → answer 3 questions

- [ ] AI Tools → **Mock Interview**
- [ ] Start session for a role/level
- [ ] Answer at least 3 questions (AI feedback + next question)
- [ ] End session; summary / session saved (visible in history if available)

### 10. Dashboard funnel chart

- [ ] Open **Dashboard**
- [ ] Funnel / pipeline chart renders with stage counts
- [ ] Stats cards load without errors

### 11. `docker compose up` + `make test`

- [ ] From a clean shell: `cp .env.example .env` (if needed) then `docker compose up --build`
- [ ] Frontend reachable on http://localhost (nginx)
- [ ] API via same origin: http://localhost/api/ (proxied to Django)
- [ ] `make test` passes with coverage ≥ 70%

---

## B. Smoke checks (roles & shell)

- [ ] Admin can open **Settings** and manage users (role / active)
- [ ] Recruiter cannot register users (403 / UI hidden)
- [ ] Interviewer cannot create jobs (redirect / forbidden)
- [ ] Sidebar collapses; notifications bell opens unread list
- [ ] Logout clears session; protected routes redirect to login

---

## C. Result

| Area | Pass? | Notes |
|------|-------|-------|
| SPEC §10 steps 1–11 | | |
| Role / shell smoke | | |
| Blockers | | |

Tester: ______________  Date: ______________
