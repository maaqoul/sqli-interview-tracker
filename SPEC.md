# SQLI Interview Tracker — Product & Technical Specification

**Version:** 1.0  
**Author:** SQLI Training Program  
**Target developer:** Python + Vue intern  
**Estimated effort:** 6–8 weeks (part-time)

---

## 1. Executive Summary

Build an internal **Interview Tracking & AI Assistant** platform for SQLI's recruitment team. The app manages the full hiring lifecycle — from job posting to offer — with integrated AI features for question generation, feedback summarization, and mock interview practice.

This project teaches: REST API design, Vue SPA architecture, PostgreSQL modeling, JWT auth, and production-grade AI integration.

---

## 2. Users & Roles

| Role | Permissions |
|------|-------------|
| **Admin** | Full access. Manage users, roles, system settings. |
| **Recruiter** | Create jobs, add/move candidates, schedule interviews, view all pipelines. |
| **Interviewer** | View assigned interviews, submit scorecards, access AI question generator. |
| **Hiring Manager** | View candidates for their department, approve/reject at final stage. |
| **Candidate** *(optional MVP+)* | View own status, access AI mock interview prep. |

**MVP ships with:** Admin, Recruiter, Interviewer.

---

## 3. Core Features

### 3.1 Authentication & Authorization

- Email + password login
- JWT access token (15 min) + refresh token (7 days)
- Role-based access control (RBAC) on every endpoint
- Password reset via email (can be mocked in dev with console output)

### 3.2 Job Openings

- CRUD job positions: title, department, location, level (junior/mid/senior/lead), description, required skills (tags), status (open/closed/on-hold)
- Link candidates to a job opening
- Each job has a configurable pipeline (default stages below)

### 3.3 Candidate Management

- CRUD candidates: name, email, phone, LinkedIn URL, resume (file upload PDF), source (referral/LinkedIn/job board), notes
- Assign to job opening + current pipeline stage
- Activity timeline (stage changes, notes, interviews, scorecards)
- Search & filter: by name, job, stage, date range
- **Kanban board view** — drag cards between stages
- **Table view** — sortable columns

**Default pipeline stages:**
```
Applied → Screening → Technical Interview → Culture Fit → Offer → Hired
                                                              ↘ Rejected (from any stage)
```

### 3.4 Interview Scheduling

- Create interview: candidate, job, type (phone/video/onsite), date/time, duration, location or video link
- Assign one or more interviewers
- Status: scheduled / completed / cancelled / no-show
- Calendar view (week/month) showing all upcoming interviews
- Email notification to interviewers (mock in dev, real SMTP in prod)

### 3.5 Scorecards & Feedback

- Post-interview scorecard form per interviewer:
  - Overall rating (1–5 stars)
  - Skill ratings: Technical, Communication, Problem Solving, Culture Fit, Leadership (1–5 each)
  - Strengths (text)
  - Weaknesses (text)
  - Recommendation: Strong Yes / Yes / Neutral / No / Strong No
  - Private notes (visible only to recruiter + admin)
- Aggregate scorecard view on candidate detail page
- Hiring decision button (advance / reject / hold) with mandatory reason

### 3.6 AI Features (core differentiator)

All AI features use an abstraction layer (`AIService`) so the provider can be swapped (OpenAI ↔ Ollama).

#### 3.6.1 AI Interview Question Generator
- Input: job title, level, skills, interview type (technical/behavioral/culture)
- Output: 8–12 tailored questions with difficulty tags
- Recruiter/interviewer can edit, save to interview, or regenerate

#### 3.6.2 AI Feedback Summarizer
- Input: all scorecards + interview notes for a candidate
- Output: structured summary — key strengths, concerns, consensus recommendation, suggested next step
- Displayed on candidate detail page as "AI Hiring Brief"

#### 3.6.3 AI Mock Interview (chat)
- Chat interface where a user (recruiter testing, or candidate in future) picks a role
- AI acts as interviewer, asks questions one at a time, gives brief feedback after each answer
- Session saved with transcript
- SQLI-branded system prompt: professional, constructive, CX/tech focused

#### 3.6.4 AI Resume Parser (stretch / INT-040)
- Upload PDF resume → extract skills, experience years, education
- Pre-fill candidate profile fields

### 3.7 Dashboard & Analytics

- **Pipeline funnel chart:** candidates per stage (per job or global)
- **Hiring velocity:** avg days per stage, time-to-hire
- **Interview load:** upcoming interviews this week per interviewer
- **Recent activity feed:** last 20 actions
- **AI usage stats:** questions generated, summaries created, mock sessions

### 3.8 Notifications

- In-app notification bell (new interview assigned, scorecard due, stage change)
- Mark as read / mark all read
- (Stretch) Email notifications via Django email backend

---

## 4. Technical Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Vue 3 SPA (Vite)                      │
│  Router │ Pinia │ Axios │ TailwindCSS │ Lucide Icons    │
└────────────────────────┬────────────────────────────────┘
                         │ HTTPS / JSON
                         │ JWT Bearer token
┌────────────────────────▼────────────────────────────────┐
│              Django 5 + DRF (Backend API)                │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌───────────┐ │
│  │ Auth App │ │ Jobs App │ │Candidates│ │ AI App    │ │
│  └──────────┘ └──────────┘ └──────────┘ └───────────┘ │
│  ┌──────────┐ ┌──────────┐ ┌──────────────────────────┐│
│  │Interview │ │Dashboard │ │ AIService (OpenAI/Ollama)  ││
│  └──────────┘ └──────────┘ └──────────────────────────┘│
└────────────────────────┬────────────────────────────────┘
                         │
              ┌──────────▼──────────┐
              │   PostgreSQL 16     │
              │   + Media storage   │
              │     (resumes)       │
              └─────────────────────┘
```

### 4.1 Backend structure

```
backend/
├── config/                 # Django settings, urls, wsgi
├── apps/
│   ├── accounts/           # User, Role, JWT auth
│   ├── jobs/               # JobOpening, PipelineStage
│   ├── candidates/         # Candidate, ActivityLog
│   ├── interviews/         # Interview, Scorecard
│   ├── ai_assistant/       # AI endpoints, prompts, AIService
│   ├── notifications/      # In-app notifications
│   └── dashboard/          # Analytics aggregation endpoints
├── media/                  # Uploaded resumes
├── requirements.txt
├── Dockerfile
└── manage.py
```

### 4.2 Frontend structure

```
frontend/
├── public/assets/          # SQLI logos (see BRAND.md)
├── src/
│   ├── api/                # Axios client + endpoint modules
│   ├── components/
│   │   ├── common/         # Button, Modal, Table, Badge
│   │   ├── layout/         # Sidebar, TopBar, AppShell
│   │   ├── candidates/     # Kanban, CandidateCard, Timeline
│   │   ├── interviews/     # Calendar, ScorecardForm
│   │   └── ai/             # QuestionGen, MockChat, Summary
│   ├── views/              # Page-level components
│   ├── stores/             # Pinia stores (auth, candidates, etc.)
│   ├── router/             # Vue Router + auth guards
│   ├── styles/             # Tailwind + SQLI CSS variables
│   └── utils/
├── package.json
├── tailwind.config.js      # SQLI colors
└── Dockerfile
```

### 4.3 Database schema (core tables)

```
users
  id, email, password_hash, first_name, last_name, role, avatar, created_at

job_openings
  id, title, department, location, level, description, skills[], status, created_by, created_at

pipeline_stages
  id, job_id (nullable=default), name, order, color

candidates
  id, first_name, last_name, email, phone, linkedin, resume_file, source,
  job_id, current_stage_id, status, created_at, updated_at

candidate_activities
  id, candidate_id, user_id, action_type, description, metadata, created_at

interviews
  id, candidate_id, job_id, type, scheduled_at, duration_min, location,
  video_link, status, created_by, created_at

interview_interviewers (M2M)
  interview_id, user_id

scorecards
  id, interview_id, interviewer_id, overall_rating, skill_ratings (JSONB),
  strengths, weaknesses, recommendation, private_notes, submitted_at

ai_sessions
  id, type (questions|summary|mock), user_id, candidate_id (nullable),
  input_data (JSONB), output_data (JSONB), created_at

notifications
  id, user_id, title, message, link, is_read, created_at
```

### 4.4 API endpoints (REST)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/login/` | Login → JWT tokens |
| POST | `/api/auth/refresh/` | Refresh access token |
| POST | `/api/auth/register/` | Register (admin only in prod) |
| GET/POST | `/api/users/` | List/create users |
| GET/PUT/DELETE | `/api/users/{id}/` | User detail |
| GET/POST | `/api/jobs/` | Job openings |
| GET/PUT/DELETE | `/api/jobs/{id}/` | Job detail |
| GET/POST | `/api/candidates/` | Candidates (filterable) |
| GET/PUT/DELETE | `/api/candidates/{id}/` | Candidate detail |
| POST | `/api/candidates/{id}/move-stage/` | Move to stage |
| GET | `/api/candidates/{id}/timeline/` | Activity timeline |
| GET/POST | `/api/interviews/` | Interviews |
| GET/PUT/DELETE | `/api/interviews/{id}/` | Interview detail |
| GET/POST | `/api/scorecards/` | Scorecards |
| POST | `/api/ai/generate-questions/` | AI question generator |
| POST | `/api/ai/summarize-feedback/` | AI feedback summary |
| POST | `/api/ai/mock-interview/` | AI mock interview turn |
| GET | `/api/ai/sessions/` | Past AI sessions |
| GET | `/api/dashboard/stats/` | Dashboard metrics |
| GET | `/api/dashboard/funnel/` | Pipeline funnel data |
| GET/PUT | `/api/notifications/` | Notifications |

### 4.5 AI Service design

```python
# apps/ai_assistant/services.py

class AIService:
    def generate_questions(self, job_title, level, skills, interview_type) -> list[dict]: ...
    def summarize_feedback(self, scorecards: list, notes: list) -> dict: ...
    def mock_interview_turn(self, role, history: list, user_answer: str) -> dict: ...

class OpenAIProvider(AIService): ...   # production
class OllamaProvider(AIService): ...    # local dev (llama3)
```

**Environment variables:**
```
OPENAI_API_KEY=sk-...
AI_PROVIDER=openai          # or "ollama"
OLLAMA_BASE_URL=http://localhost:11434
```

**System prompts must:**
- Be professional and constructive
- Never make final hiring decisions (always "recommendation")
- Include disclaimer: "AI-assisted — human decision required"

---

## 5. Non-Functional Requirements

| Requirement | Target |
|-------------|--------|
| API response time | < 500ms (non-AI endpoints) |
| AI response time | < 10s with loading indicator |
| Concurrent users | 50 (MVP) |
| Uptime | 99% (single-server deploy) |
| Data privacy | Resumes stored securely, private notes RBAC-enforced |
| Mobile | Responsive down to 768px (tablet minimum) |
| Accessibility | Basic WCAG — keyboard nav, contrast ratios per BRAND.md |
| i18n | English only (MVP), French labels as stretch goal |

---

## 6. DevOps

```yaml
# docker-compose.yml services:
# - db (postgres:16)
# - backend (django + gunicorn)
# - frontend (nginx serving Vue build)
# - (optional) ollama for local AI
```

- `.env.example` with all required variables
- `Makefile` with: `make up`, `make down`, `make test`, `make seed`, `make migrate`
- Seed command creates: 3 users (admin, recruiter, interviewer), 2 jobs, 10 candidates, 5 interviews
- GitHub Actions CI: lint + test on PR

---

## 7. Testing requirements

| Layer | Minimum |
|-------|---------|
| Backend unit tests | Models, serializers, permissions |
| Backend API tests | Auth, CRUD for each resource, AI endpoints (mocked) |
| Frontend | Manual test checklist (see TICKETS.md INT-038) |
| Coverage target | 70% backend |

---

## 8. Out of scope (MVP)

- SSO / LDAP integration
- Calendar sync (Google Calendar, Outlook)
- Offer letter generation
- Multi-tenant (multiple companies)
- Mobile native app
- Video call integration (Zoom/Teams)
- GDPR data export automation

---

## 9. Milestones

| Milestone | Tickets | Deliverable |
|-----------|---------|-------------|
| M1 — Foundation | INT-001 → INT-008 | Project runs, auth works, DB connected |
| M2 — Core CRUD | INT-009 → INT-018 | Jobs, candidates, pipeline |
| M3 — Interviews | INT-019 → INT-025 | Scheduling + scorecards |
| M4 — AI | INT-026 → INT-032 | All 3 AI features working |
| M5 — UI/Brand | INT-033 → INT-037 | SQLI-branded, polished UI |
| M6 — Ship | INT-038 → INT-042 | Tests, Docker, docs, deploy |

---

## 10. Acceptance demo script

When the project is done, record a 5-minute demo showing:

1. Login as recruiter (SQLI branded login page)
2. Create job "Senior Python Developer — Paris"
3. Add candidate with resume upload
4. Drag candidate from Applied → Screening on kanban
5. Schedule technical interview, assign interviewer
6. Login as interviewer → open scorecard → submit ratings
7. Click "AI Summarize" → see hiring brief
8. Open AI Question Generator → generate 10 questions
9. Start AI Mock Interview → answer 3 questions
10. View dashboard funnel chart
11. Show `docker compose up` + `make test` passing

---

## 11. Reference links

- SQLI website: https://www.sqli.com
- SQLI group page: https://sqli.com/fr-fr/groupe-sqli
- Brand case study: https://cdlx.de/projects/sqli
- Django REST Framework: https://www.django-rest-framework.org
- Vue 3 docs: https://vuejs.org
- OpenAI API: https://platform.openai.com/docs
