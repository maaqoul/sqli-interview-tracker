# 2-Week Sprint Plan — SQLI Interview Tracker

**Intern:** starts at ticket **INT-009** (scaffold is done for INT-001 → INT-008)  
**Mentor:** [@maaqoul](https://github.com/maaqoul)  
**Repo:** https://github.com/maaqoul/sqli-interview-tracker  
**Pace:** ~4–6 hours/day, 5 days/week

---

## What's already done (don't redo)

| Ticket | Status | What was scaffolded |
|--------|--------|---------------------|
| INT-001 | ✅ Done | Monorepo structure |
| INT-002 | ✅ Done | Django 5 + DRF + Spectacular |
| INT-003 | ✅ Done | Vue 3 + Vite + TS + Router + Pinia + Axios |
| INT-004 | ✅ Done | docker-compose.yml (Postgres + backend + frontend) |
| INT-005 | ✅ Done | Tailwind + SQLI color tokens |
| INT-006 | ✅ Done | Ruff (backend), lint script (frontend) |
| INT-007 | ✅ Done | Makefile + .env.example |
| INT-008 | ✅ Done | GitHub Actions CI |

**Verify on day 1:**
```bash
git clone https://github.com/maaqoul/sqli-interview-tracker.git
cd sqli-interview-tracker
cp .env.example .env
make setup
make dev-backend    # terminal 1 → http://localhost:8000/api/health/
make dev-frontend   # terminal 2 → http://localhost:5173
```

---

## Week 1 — Auth + Jobs + Candidates (MVP core)

**Goal:** Recruiter can log in, create jobs, add candidates, move them on a kanban board.

### Monday — Auth backend (INT-009 → INT-012)

| Time | Ticket | Deliverable |
|------|--------|-------------|
| AM | INT-009 | Custom User model with roles |
| PM | INT-010 | JWT login / refresh endpoints |

**End of day check:** `curl -X POST localhost:8000/api/auth/login/` returns tokens.

### Tuesday — Auth frontend (INT-013 → INT-015)

| Time | Ticket | Deliverable |
|------|--------|-------------|
| AM | INT-013 | Pinia auth store wired to real API |
| PM | INT-014, INT-015 | Login page works, route guards |

**End of day check:** Login → dashboard with real JWT. Logout works.

### Wednesday — Jobs (INT-016 → INT-019)

| Time | Ticket | Deliverable |
|------|--------|-------------|
| AM | INT-016, INT-017 | JobOpening + PipelineStage APIs, seed default stages |
| PM | INT-018, INT-019 | Jobs list + create/edit form in Vue |

**End of day check:** Create "Senior Python Developer — Paris" job in UI.

### Thursday — Candidates API (INT-020 → INT-023)

| Time | Ticket | Deliverable |
|------|--------|-------------|
| AM | INT-020 | Candidate CRUD with filters |
| PM | INT-021, INT-022, INT-023 | Resume upload, move-stage, timeline |

**End of day check:** API tests pass. Move candidate via API.

### Friday — Candidates UI (INT-024 → INT-026)

| Time | Ticket | Deliverable |
|------|--------|-------------|
| AM | INT-024 | Candidate table with search/filter |
| PM | INT-025, INT-026 | Kanban board + candidate detail page |

**Week 1 demo (record 2 min):**
1. Login as recruiter
2. Create a job
3. Add 3 candidates
4. Drag one from Applied → Screening on kanban
5. Open candidate detail → see timeline

---

## Week 2 — Interviews + AI + Ship

**Goal:** Full interview loop with scorecards, 2 AI features, deployable app.

### Monday — Interviews (INT-027 → INT-030)

| Time | Ticket | Deliverable |
|------|--------|-------------|
| AM | INT-027, INT-028 | Interview CRUD + assign interviewers |
| PM | INT-029, INT-030 | Calendar view + schedule modal |

**End of day check:** Schedule interview from candidate detail.

### Tuesday — Scorecards (INT-031 → INT-033)

| Time | Ticket | Deliverable |
|------|--------|-------------|
| AM | INT-031 | Scorecard API |
| PM | INT-032, INT-033 | Scorecard form + aggregate view |

**End of day check:** Interviewer submits scorecard, visible on candidate page.

### Wednesday — AI backend (INT-034 → INT-035)

| Time | Ticket | Deliverable |
|------|--------|-------------|
| AM | INT-034 | AIService with OpenAI + Ollama providers |
| PM | INT-035 | Question generator API + UI panel |

**End of day check:** Generate 10 Python interview questions for a job.

### Thursday — AI features + layout (INT-036 → INT-039)

| Time | Ticket | Deliverable |
|------|--------|-------------|
| AM | INT-036, INT-037 | Feedback summarizer + mock interview chat |
| PM | INT-038, INT-039 | AI session history + app shell layout |

**End of day check:** AI Hiring Brief on candidate with scorecards. Mock chat works.

### Friday — Dashboard + deploy (INT-040 → INT-043, INT-046)

| Time | Ticket | Deliverable |
|------|--------|-------------|
| AM | INT-040, INT-041 | Dashboard funnel + notifications |
| PM | INT-043, INT-046, INT-047 | Seed data + Docker + README |

**Week 2 / final demo (5 min — SPEC.md §10):**
1. Login (SQLI branded)
2. Create job + add candidate + kanban move
3. Schedule interview → submit scorecard
4. AI summarize feedback
5. AI generate questions
6. AI mock interview (3 questions)
7. Dashboard stats
8. `docker compose up` works

---

## Tickets deferred (post 2-week, if time allows)

| Ticket | Why deferred |
|--------|--------------|
| INT-042 | Settings page — nice to have |
| INT-044 | Full 70% test coverage — aim for 50% in 2 weeks |
| INT-045 | Formal test checklist |
| INT-048 | Recorded demo — do on last day if time |

---

## Daily routine

```
09:00  Pull latest, check GitHub Issues assigned to you
09:15  Move ticket to "In Progress" on Project board
       Work until acceptance criteria ✅
17:00  Open PR referencing ticket (e.g. "INT-020: Candidate CRUD API")
17:30  Move ticket to "In Review" → mentor reviews
```

### PR rules
- One PR per ticket (or max 2 related tickets)
- Branch naming: `INT-020-candidate-crud`
- PR description: paste acceptance criteria + how you tested

---

## GitHub board columns

```
Backlog → In Progress → In Review → Done
```

Filter by milestone:
- **W1** = INT-009 → INT-026
- **W2** = INT-027 → INT-047

---

## When you're stuck

1. Read the ticket acceptance criteria again
2. Check `SPEC.md` for architecture context
3. Comment on the GitHub issue with: what you tried + error message
4. Tag mentor: `@maaqoul`

---

## Success criteria (end of 2 weeks)

- [ ] Auth works (real JWT, not placeholder)
- [ ] Jobs + candidates CRUD + kanban
- [ ] Interviews scheduled + scorecards submitted
- [ ] At least 2 AI features working (questions + summarizer minimum)
- [ ] SQLI branding throughout
- [ ] `docker compose up` runs the full stack
- [ ] README documents how to start the project

Good luck — elevate digitally. 🚀
