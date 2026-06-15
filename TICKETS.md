# SQLI Interview Tracker — Ticket Board

> **42 tickets** to build a fully operational app.  
> Work in order. Respect dependencies. Mark ✅ when done.

**Legend:** 🔴 Critical · 🟡 High · 🟢 Normal · ⚪ Low  
**Estimates:** S = 2–4h · M = 4–8h · L = 1–2 days · XL = 2–3 days

---

## EPIC 0 — Project Setup (M1)

| ID | Title | Priority | Est. | Deps | Status |
|----|-------|----------|------|------|--------|
| INT-001 | Initialize monorepo structure | 🔴 | S | — | ⬜ |
| INT-002 | Setup Django backend with DRF | 🔴 | M | INT-001 | ⬜ |
| INT-003 | Setup Vue 3 + Vite frontend | 🔴 | M | INT-001 | ⬜ |
| INT-004 | Configure PostgreSQL + Docker Compose | 🔴 | M | INT-002 | ⬜ |
| INT-005 | Configure Tailwind with SQLI brand tokens | 🟡 | S | INT-003 | ⬜ |
| INT-006 | Setup linting & formatting (Ruff, ESLint, Prettier) | 🟢 | S | INT-002, INT-003 | ⬜ |
| INT-007 | Create Makefile & .env.example | 🟡 | S | INT-004 | ⬜ |
| INT-008 | Setup GitHub Actions CI pipeline | 🟢 | M | INT-006 | ⬜ |

### INT-001 — Initialize monorepo structure
**Description:** Create `backend/`, `frontend/`, `docker-compose.yml`, root `README.md`. Add `.gitignore` for Python + Node.

**Acceptance criteria:**
- [ ] Folder structure matches SPEC.md §4.1 and §4.2
- [ ] Root README explains how to start the project
- [ ] Git repo initialized with first commit

---

### INT-002 — Setup Django backend with DRF
**Description:** Django 5 project with DRF, CORS headers, django-environ for config.

**Acceptance criteria:**
- [ ] `python manage.py runserver` starts without error
- [ ] `/api/health/` returns `{"status": "ok"}`
- [ ] DRF browsable API accessible
- [ ] `requirements.txt` pinned

---

### INT-003 — Setup Vue 3 + Vite frontend
**Description:** Vue 3 + TypeScript + Vite + Vue Router + Pinia + Axios.

**Acceptance criteria:**
- [ ] `npm run dev` starts on port 5173
- [ ] Proxy to Django API configured in `vite.config.ts`
- [ ] Placeholder home page renders

---

### INT-004 — Configure PostgreSQL + Docker Compose
**Description:** `docker-compose.yml` with postgres:16, backend, frontend services.

**Acceptance criteria:**
- [ ] `docker compose up db backend` connects Django to Postgres
- [ ] Migrations run successfully
- [ ] Data persists in Docker volume

---

### INT-005 — Configure Tailwind with SQLI brand tokens
**Description:** Install TailwindCSS. Add SQLI colors from BRAND.md to `tailwind.config.js`.

**Acceptance criteria:**
- [ ] CSS variables for all SQLI colors
- [ ] Sample branded button component works
- [ ] Cream background + midnight sidebar preview page

---

### INT-006 — Setup linting & formatting
**Description:** Ruff + mypy (backend), ESLint + Prettier (frontend).

**Acceptance criteria:**
- [ ] `make lint` passes on empty project
- [ ] Pre-commit or CI-ready lint commands documented

---

### INT-007 — Create Makefile & .env.example
**Description:** Commands: `up`, `down`, `migrate`, `seed`, `test`, `lint`.

**Acceptance criteria:**
- [ ] `.env.example` lists all vars (DB, JWT, OPENAI_API_KEY, AI_PROVIDER)
- [ ] `make up` starts full stack
- [ ] `make migrate` runs Django migrations

---

### INT-008 — Setup GitHub Actions CI
**Description:** CI workflow: lint + test on push/PR.

**Acceptance criteria:**
- [ ] Workflow file in `.github/workflows/ci.yml`
- [ ] Runs backend tests and frontend lint
- [ ] Badge in README (optional)

---

## EPIC 1 — Authentication (M1)

| ID | Title | Priority | Est. | Deps | Status |
|----|-------|----------|------|------|--------|
| INT-009 | User model with roles (Admin/Recruiter/Interviewer/Manager) | 🔴 | M | INT-004 | ⬜ |
| INT-010 | JWT authentication (login, refresh, logout) | 🔴 | M | INT-009 | ⬜ |
| INT-011 | RBAC permission classes for DRF | 🔴 | M | INT-010 | ⬜ |
| INT-012 | Auth API: register, profile, change password | 🟡 | M | INT-010 | ⬜ |
| INT-013 | Vue auth store + Axios JWT interceptor | 🔴 | M | INT-010, INT-003 | ⬜ |
| INT-014 | Login & Register pages (SQLI branded) | 🔴 | M | INT-005, INT-013 | ⬜ |
| INT-015 | Vue Router auth guards | 🔴 | S | INT-013 | ⬜ |

### INT-009 — User model with roles
**Acceptance criteria:**
- [ ] Custom User model with email login
- [ ] Role field: admin, recruiter, interviewer, hiring_manager
- [ ] Admin can assign roles

### INT-010 — JWT authentication
**Acceptance criteria:**
- [ ] `POST /api/auth/login/` returns access + refresh tokens
- [ ] `POST /api/auth/refresh/` works
- [ ] Invalid credentials return 401

### INT-011 — RBAC permissions
**Acceptance criteria:**
- [ ] `IsRecruiter`, `IsInterviewer`, `IsAdmin` permission classes
- [ ] Test: interviewer cannot delete candidates
- [ ] Test: recruiter can create jobs

### INT-012 — Auth API extras
**Acceptance criteria:**
- [ ] `GET /api/auth/me/` returns current user
- [ ] `POST /api/auth/register/` (admin-only in prod)
- [ ] `POST /api/auth/change-password/`

### INT-013 — Vue auth store
**Acceptance criteria:**
- [ ] Pinia store: login, logout, refresh, user state
- [ ] Axios interceptor adds Bearer token
- [ ] Auto-refresh on 401

### INT-014 — Login & Register pages
**Acceptance criteria:**
- [ ] SQLI logo + "We Elevate. Digitally." tagline
- [ ] Cream background, cobalt CTA button
- [ ] Form validation, error messages
- [ ] Redirect to dashboard on success

### INT-015 — Router auth guards
**Acceptance criteria:**
- [ ] Unauthenticated users redirected to /login
- [ ] Role-based route restrictions (admin-only pages)

---

## EPIC 2 — Jobs & Pipeline (M2)

| ID | Title | Priority | Est. | Deps | Status |
|----|-------|----------|------|------|--------|
| INT-016 | JobOpening model + CRUD API | 🔴 | M | INT-011 | ⬜ |
| INT-017 | PipelineStage model (default + per-job) | 🔴 | M | INT-016 | ⬜ |
| INT-018 | Jobs list & detail Vue pages | 🟡 | M | INT-016, INT-014 | ⬜ |
| INT-019 | Job create/edit form with skills tags | 🟡 | M | INT-018 | ⬜ |

### INT-016 — JobOpening CRUD API
**Acceptance criteria:**
- [ ] Full CRUD at `/api/jobs/`
- [ ] Fields: title, department, location, level, description, skills, status
- [ ] Serializer validation, pagination
- [ ] API tests for CRUD

### INT-017 — PipelineStage model
**Acceptance criteria:**
- [ ] Default stages seeded: Applied, Screening, Technical, Culture Fit, Offer, Hired, Rejected
- [ ] Stages linked to job (or global default)
- [ ] Ordered by `order` field with color

### INT-018 — Jobs list & detail pages
**Acceptance criteria:**
- [ ] Table of jobs with status badges
- [ ] Click → job detail with candidate count per stage
- [ ] Empty state with SQLI copy

### INT-019 — Job create/edit form
**Acceptance criteria:**
- [ ] Form with all fields, skills as tag input
- [ ] Create and edit modes
- [ ] Success toast notification

---

## EPIC 3 — Candidates (M2)

| ID | Title | Priority | Est. | Deps | Status |
|----|-------|----------|------|------|--------|
| INT-020 | Candidate model + CRUD API | 🔴 | L | INT-017 | ⬜ |
| INT-021 | Resume file upload (PDF, max 5MB) | 🟡 | M | INT-020 | ⬜ |
| INT-022 | Move candidate between pipeline stages | 🔴 | M | INT-020 | ⬜ |
| INT-023 | Activity timeline (audit log) | 🟡 | M | INT-022 | ⬜ |
| INT-024 | Candidate list table view with search/filter | 🔴 | M | INT-020, INT-014 | ⬜ |
| INT-025 | Kanban board view (drag & drop) | 🔴 | L | INT-022, INT-024 | ⬜ |
| INT-026 | Candidate detail page with timeline | 🔴 | L | INT-023, INT-024 | ⬜ |

### INT-020 — Candidate CRUD API
**Acceptance criteria:**
- [ ] CRUD at `/api/candidates/`
- [ ] Filter by: job_id, stage, search (name/email), date range
- [ ] Linked to job + current stage
- [ ] API tests

### INT-021 — Resume upload
**Acceptance criteria:**
- [ ] `POST /api/candidates/{id}/upload-resume/` accepts PDF
- [ ] File stored in `media/resumes/`
- [ ] Max 5MB, PDF only validation
- [ ] Download link on candidate detail

### INT-022 — Move stage API
**Acceptance criteria:**
- [ ] `POST /api/candidates/{id}/move-stage/` with `{stage_id, reason}`
- [ ] Creates activity log entry
- [ ] Rejected stage available from any stage

### INT-023 — Activity timeline
**Acceptance criteria:**
- [ ] `GET /api/candidates/{id}/timeline/` returns chronological events
- [ ] Events: created, stage_change, note_added, interview_scheduled, scorecard_submitted
- [ ] Shows user who performed action + timestamp

### INT-024 — Candidate table view
**Acceptance criteria:**
- [ ] Sortable columns: name, job, stage, date, source
- [ ] Search bar + filter dropdowns
- [ ] Pagination (20 per page)
- [ ] Click row → detail page

### INT-025 — Kanban board
**Acceptance criteria:**
- [ ] Columns = pipeline stages with candidate cards
- [ ] Drag card between columns triggers move-stage API
- [ ] Card shows: name, job, days in stage
- [ ] Toggle between table ↔ kanban views

### INT-026 — Candidate detail page
**Acceptance criteria:**
- [ ] Header: name, contact, current stage badge, job
- [ ] Tabs: Overview, Timeline, Interviews, Scorecards, AI Brief
- [ ] Quick actions: Schedule Interview, Add Note, Move Stage, Reject
- [ ] Resume preview/download

---

## EPIC 4 — Interviews & Scorecards (M3)

| ID | Title | Priority | Est. | Deps | Status |
|----|-------|----------|------|------|--------|
| INT-027 | Interview model + CRUD API | 🔴 | M | INT-020 | ⬜ |
| INT-028 | Assign multiple interviewers to interview | 🟡 | S | INT-027 | ⬜ |
| INT-029 | Interview calendar view (Vue) | 🟡 | L | INT-027, INT-014 | ⬜ |
| INT-030 | Schedule interview form/modal | 🔴 | M | INT-027, INT-026 | ⬜ |
| INT-031 | Scorecard model + submit API | 🔴 | M | INT-027 | ⬜ |
| INT-032 | Scorecard form UI for interviewers | 🔴 | L | INT-031, INT-014 | ⬜ |
| INT-033 | Aggregate scorecard view on candidate page | 🟡 | M | INT-031, INT-026 | ⬜ |

### INT-027 — Interview CRUD API
**Acceptance criteria:**
- [ ] CRUD at `/api/interviews/`
- [ ] Fields: candidate, job, type, scheduled_at, duration, location, video_link, status
- [ ] Filter by: date range, interviewer, status

### INT-028 — Multiple interviewers
**Acceptance criteria:**
- [ ] M2M interview ↔ interviewers
- [ ] Interviewer sees only their assigned interviews
- [ ] Notification created on assignment

### INT-029 — Calendar view
**Acceptance criteria:**
- [ ] Week view showing interviews as blocks
- [ ] Color-coded by interview type
- [ ] Click block → interview detail modal

### INT-030 — Schedule interview form
**Acceptance criteria:**
- [ ] Modal/form from candidate detail or calendar
- [ ] Date/time picker, interviewer multi-select
- [ ] Type: phone / video / onsite
- [ ] Creates notification for assigned interviewers

### INT-031 — Scorecard API
**Acceptance criteria:**
- [ ] `POST /api/scorecards/` linked to interview + interviewer
- [ ] Fields: overall_rating, skill_ratings (JSON), strengths, weaknesses, recommendation, private_notes
- [ ] One scorecard per interviewer per interview (unique constraint)
- [ ] Private notes hidden from interviewers (only recruiter/admin)

### INT-032 — Scorecard form UI
**Acceptance criteria:**
- [ ] Star ratings for overall + 5 skills
- [ ] Recommendation dropdown: Strong Yes → Strong No
- [ ] Text areas for strengths/weaknesses/notes
- [ ] Submit → marks interview as completed
- [ ] "My Interviews" page for interviewers

### INT-033 — Aggregate scorecards
**Acceptance criteria:**
- [ ] Candidate detail shows all scorecards in a summary card
- [ ] Average ratings computed
- [ ] Recommendation consensus shown (e.g., "3/4 recommend Yes")

---

## EPIC 5 — AI Features (M4)

| ID | Title | Priority | Est. | Deps | Status |
|----|-------|----------|------|------|--------|
| INT-034 | AIService abstraction (OpenAI + Ollama providers) | 🔴 | L | INT-002 | ⬜ |
| INT-035 | AI Interview Question Generator (API + UI) | 🔴 | L | INT-034, INT-016 | ⬜ |
| INT-036 | AI Feedback Summarizer (API + UI) | 🔴 | L | INT-034, INT-031 | ⬜ |
| INT-037 | AI Mock Interview chat (API + UI) | 🔴 | XL | INT-034, INT-014 | ⬜ |
| INT-038 | AI session history & logging | 🟡 | M | INT-034 | ⬜ |

### INT-034 — AIService abstraction
**Acceptance criteria:**
- [ ] `AIService` base class with 3 methods
- [ ] `OpenAIProvider` using gpt-4o-mini (or gpt-4)
- [ ] `OllamaProvider` for local llama3
- [ ] Provider selected via `AI_PROVIDER` env var
- [ ] Unit tests with mocked responses
- [ ] Rate limiting: max 20 AI calls/user/hour

### INT-035 — AI Question Generator
**Acceptance criteria:**
- [ ] `POST /api/ai/generate-questions/` with job context
- [ ] Returns 8–12 questions with type (technical/behavioral) and difficulty
- [ ] Vue panel: select job → generate → display → copy/save
- [ ] Loading spinner during generation (up to 10s)
- [ ] "Regenerate" button

### INT-036 — AI Feedback Summarizer
**Acceptance criteria:**
- [ ] `POST /api/ai/summarize-feedback/` with candidate_id
- [ ] Aggregates all scorecards + notes
- [ ] Returns: strengths[], concerns[], recommendation, suggested_next_step
- [ ] "AI Hiring Brief" card on candidate detail
- [ ] Disclaimer: "AI-assisted — human decision required"

### INT-037 — AI Mock Interview chat
**Acceptance criteria:**
- [ ] Chat UI with message bubbles (SQLI branded)
- [ ] User selects role/level → AI asks first question
- [ ] User answers → AI gives brief feedback + next question
- [ ] Session saved to `ai_sessions` table
- [ ] "End session" → shows summary of performance
- [ ] System prompt: professional SQLI interviewer persona

### INT-038 — AI session history
**Acceptance criteria:**
- [ ] `GET /api/ai/sessions/` lists past sessions
- [ ] Filter by type (questions/summary/mock)
- [ ] View past mock interview transcripts

---

## EPIC 6 — Dashboard, Notifications & Layout (M5)

| ID | Title | Priority | Est. | Deps | Status |
|----|-------|----------|------|------|--------|
| INT-039 | App shell layout (sidebar + topbar) | 🔴 | M | INT-005, INT-014 | ⬜ |
| INT-040 | Dashboard with funnel chart & stats | 🔴 | L | INT-020, INT-027, INT-039 | ⬜ |
| INT-041 | In-app notification system | 🟡 | M | INT-009, INT-039 | ⬜ |
| INT-042 | Settings & user profile page | 🟢 | M | INT-012, INT-039 | ⬜ |

### INT-039 — App shell layout
**Acceptance criteria:**
- [ ] Sidebar: logo, nav links (Dashboard, Candidates, Jobs, Interviews, AI Tools, Settings)
- [ ] Collapsible sidebar with icon-only mode
- [ ] Topbar: user avatar, notification bell, logout
- [ ] Midnight blue sidebar, cream content area
- [ ] Responsive: sidebar collapses on tablet

### INT-040 — Dashboard
**Acceptance criteria:**
- [ ] Pipeline funnel chart (candidates per stage) — use Chart.js or similar
- [ ] Stat cards: total candidates, open jobs, interviews this week, avg time-to-hire
- [ ] Recent activity feed (last 20 events)
- [ ] AI usage stats widget

### INT-041 — Notifications
**Acceptance criteria:**
- [ ] `GET /api/notifications/` + mark read endpoints
- [ ] Bell icon with unread count badge
- [ ] Dropdown list with click → navigate to relevant page
- [ ] Auto-create on: interview assigned, scorecard due, stage change

### INT-042 — Settings page
**Acceptance criteria:**
- [ ] Edit profile (name, avatar)
- [ ] Change password
- [ ] Admin section: user management table (list users, change roles)

---

## EPIC 7 — Seed Data, Tests & Deploy (M6)

| ID | Title | Priority | Est. | Deps | Status |
|----|-------|----------|------|------|--------|
| INT-043 | Seed command with demo data | 🟡 | M | INT-033 | ⬜ |
| INT-044 | Backend test suite (70% coverage target) | 🔴 | L | INT-038 | ⬜ |
| INT-045 | Frontend manual test checklist | 🟡 | S | INT-042 | ⬜ |
| INT-046 | Docker production build + nginx | 🔴 | M | INT-004 | ⬜ |
| INT-047 | Project README & API documentation | 🔴 | M | INT-046 | ⬜ |
| INT-048 | Final demo & acceptance review | 🔴 | M | ALL | ⬜ |

### INT-043 — Seed command
**Acceptance criteria:**
- [ ] `make seed` or `python manage.py seed_demo`
- [ ] Creates: 1 admin, 2 recruiters, 3 interviewers
- [ ] 3 job openings, 15 candidates across stages
- [ ] 8 interviews (past + future), 5 scorecards
- [ ] Prints login credentials to console

### INT-044 — Backend tests
**Acceptance criteria:**
- [ ] Tests for: auth, jobs, candidates, interviews, scorecards, AI (mocked)
- [ ] Permission tests (role-based access)
- [ ] `make test` runs all, 70%+ coverage
- [ ] CI passes

### INT-045 — Frontend test checklist
**Acceptance criteria:**
- [ ] `TESTING.md` with step-by-step manual test cases
- [ ] Covers all demo script steps from SPEC.md §10
- [ ] All items pass

### INT-046 — Docker production build
**Acceptance criteria:**
- [ ] Multi-stage Dockerfiles for backend + frontend
- [ ] Nginx serves Vue build, proxies /api to Django
- [ ] `docker compose up` starts everything
- [ ] Works on fresh machine with only Docker installed

### INT-047 — Documentation
**Acceptance criteria:**
- [ ] README: architecture diagram (mermaid), setup, env vars, make commands
- [ ] API docs via DRF Spectacular (Swagger UI at /api/docs/)
- [ ] BRAND.md followed in UI

### INT-048 — Final demo
**Acceptance criteria:**
- [ ] 5-minute screen recording of demo script (SPEC.md §10)
- [ ] All 42 prior tickets marked done
- [ ] No critical bugs open

---

## Dependency graph (simplified)

```
INT-001 → INT-002/003 → INT-004 → INT-009 → INT-010 → INT-011
                                              ↓
INT-016 → INT-017 → INT-020 → INT-022 → INT-025/026
                         ↓
                    INT-027 → INT-031 → INT-033
                         ↓
INT-034 → INT-035/036/037
                         ↓
INT-039 → INT-040/041 → INT-043 → INT-044 → INT-046 → INT-048
```

---

## Sprint suggestion (8 weeks, part-time)

| Week | Focus | Tickets |
|------|-------|---------|
| 1 | Setup + Auth | INT-001 → INT-015 |
| 2 | Jobs + Candidates API | INT-016 → INT-023 |
| 3 | Candidate UI | INT-024 → INT-026 |
| 4 | Interviews + Scorecards | INT-027 → INT-033 |
| 5 | AI Backend | INT-034 → INT-038 |
| 6 | AI UI + Layout | INT-035 → INT-039 (UI parts) |
| 7 | Dashboard + Polish | INT-040 → INT-042 |
| 8 | Tests + Deploy + Demo | INT-043 → INT-048 |
