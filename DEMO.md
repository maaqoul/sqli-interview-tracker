# Final demo & acceptance (INT-048)

Record a **~5 minute** walkthrough of [SPEC.md §10](./SPEC.md#10-acceptance-demo-script). Use Docker (`docker compose up`) so the demo matches production.

## Before you record

- [ ] `docker compose up --build` — app at http://localhost
- [ ] Demo data loaded (seed on start or `docker compose exec backend python manage.py seed_demo`)
- [ ] Password for seed users: `DemoPass123!`
- [ ] Browser zoom readable; hide personal bookmarks if needed
- [ ] No critical bugs blocking the flows below

## Recording script (SPEC §10)

| # | Show | Suggested narration |
|---|------|---------------------|
| 1 | Login as recruiter | SQLI branded login → `recruiter1@sqli.com` |
| 2 | Create / open a job | e.g. Senior Python Developer — Paris |
| 3 | Add candidate + resume | Upload PDF/DOCX |
| 4 | Kanban move | Applied → Screening |
| 5 | Schedule interview | Assign interviewer |
| 6 | Interviewer scorecard | Switch user → submit ratings |
| 7 | AI Hiring Brief | Candidate detail → Generate Brief |
| 8 | Question Generator | AI Tools → ~10 questions |
| 9 | Mock Interview | Answer 3 questions → end session |
| 10 | Dashboard funnel | Pipeline chart + stats |
| 11 | Ops proof | Terminal: stack running; mention `make test` / CI green |

**Where to store the video:** attach to the internship deliverable / mentor review (GitHub Release, Drive, or Loom). Link it from the PR or mentor email — do not commit large binaries to git.

## Acceptance checklist

- [ ] Screen recording completed (~5 min, steps 1–11)
- [ ] All tickets INT-001 → INT-048 marked ✅ in [`TICKETS.md`](./TICKETS.md)
- [ ] No critical bugs open (P0 that blocks demo)
- [ ] README setup works on a fresh machine with Docker only
- [ ] Swagger available at `/api/docs/`
- [ ] Branding consistent with [`BRAND.md`](./BRAND.md)

## Demo credentials (quick copy)

| Role | Email | Password |
|------|-------|----------|
| Recruiter | `recruiter1@sqli.com` | `DemoPass123!` |
| Interviewer | `interviewer1@sqli.com` | `DemoPass123!` |
| Admin | `admin@sqli.com` | `DemoPass123!` |
