from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.accounts.models import Role, User
from apps.ai_assistant.models import AISession, AISessionType
from apps.candidates.models import Candidate, CandidateSource, CandidateStatus
from apps.candidates.services import log_candidate_created
from apps.interviews.models import Interview, InterviewStatus, InterviewType
from apps.interviews.services import log_interview_scheduled, notify_interviewers
from apps.jobs.models import JobOpening, JobStatus
from apps.jobs.services import seed_default_pipeline_stages
from apps.scorecards.models import Recommendation, Scorecard
from apps.scorecards.services import finalize_scorecard_submission


DEMO_PASSWORD = "DemoPass123!"

USERS = [
    {
        "email": "admin@sqli.com",
        "first_name": "Alex",
        "last_name": "Admin",
        "role": Role.ADMIN,
    },
    {
        "email": "recruiter1@sqli.com",
        "first_name": "Marie",
        "last_name": "Recruiter",
        "role": Role.RECRUITER,
    },
    {
        "email": "recruiter2@sqli.com",
        "first_name": "Jean",
        "last_name": "Dupont",
        "role": Role.RECRUITER,
    },
    {
        "email": "interviewer1@sqli.com",
        "first_name": "Sara",
        "last_name": "Lee",
        "role": Role.INTERVIEWER,
    },
    {
        "email": "interviewer2@sqli.com",
        "first_name": "Tom",
        "last_name": "Brown",
        "role": Role.INTERVIEWER,
    },
    {
        "email": "interviewer3@sqli.com",
        "first_name": "Nina",
        "last_name": "Rossi",
        "role": Role.INTERVIEWER,
    },
]

JOBS = [
    {
        "title": "Senior Python Developer",
        "department": "Engineering",
        "location": "Paris",
        "level": "senior",
        "description": "Build APIs and data platforms for SQLI digital programs.",
        "skills": ["Python", "Django", "PostgreSQL"],
    },
    {
        "title": "Frontend Vue Engineer",
        "department": "Engineering",
        "location": "Lyon",
        "level": "mid",
        "description": "Ship polished Vue 3 experiences with TypeScript.",
        "skills": ["Vue", "TypeScript", "Tailwind"],
    },
    {
        "title": "UX Designer",
        "department": "Design",
        "location": "Remote",
        "level": "mid",
        "description": "Design hiring and candidate journeys for SQLI products.",
        "skills": ["Figma", "Research", "Prototyping"],
    },
]

FIRST_NAMES = [
    "Camille", "Lucas", "Emma", "Hugo", "Chloe", "Louis", "Lea", "Nathan",
    "Manon", "Arthur", "Ines", "Paul", "Jade", "Theo", "Alice",
]
LAST_NAMES = [
    "Martin", "Bernard", "Dubois", "Thomas", "Robert", "Richard", "Petit",
    "Durand", "Leroy", "Moreau", "Simon", "Laurent", "Lefebvre", "Michel", "Garcia",
]


class Command(BaseCommand):
    help = "Seed demo users, jobs, candidates, interviews, and scorecards."

    def add_arguments(self, parser):
        parser.add_argument(
            "--flush-demo",
            action="store_true",
            help="Delete previously seeded demo emails/jobs before recreating.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        seed_default_pipeline_stages()

        if options["flush_demo"]:
            self._flush_demo()

        users = self._seed_users()
        admin = users["admin@sqli.com"]
        recruiter = users["recruiter1@sqli.com"]
        interviewers = [
            users["interviewer1@sqli.com"],
            users["interviewer2@sqli.com"],
            users["interviewer3@sqli.com"],
        ]

        jobs = self._seed_jobs(recruiter)
        candidates = self._seed_candidates(jobs, recruiter)
        interviews = self._seed_interviews(
            candidates, jobs, recruiter, interviewers, admin
        )
        scorecards = self._seed_scorecards(interviews, interviewers)
        self._seed_ai_sessions(admin, candidates[0] if candidates else None)

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("Demo data ready."))
        self.stdout.write(f"  Users:        {len(users)}")
        self.stdout.write(f"  Jobs:         {len(jobs)}")
        self.stdout.write(f"  Candidates:   {len(candidates)}")
        self.stdout.write(f"  Interviews:   {len(interviews)}")
        self.stdout.write(f"  Scorecards:   {len(scorecards)}")
        self.stdout.write("")
        self.stdout.write(self.style.WARNING("Login credentials (password for all):"))
        self.stdout.write(f"  {DEMO_PASSWORD}")
        self.stdout.write("")
        for spec in USERS:
            self.stdout.write(f"  {spec['role']:16} {spec['email']}")

    def _flush_demo(self):
        emails = [u["email"] for u in USERS]
        titles = [j["title"] for j in JOBS]
        JobOpening.objects.filter(title__in=titles, created_by__email__in=emails).delete()
        User.objects.filter(email__in=emails).delete()
        self.stdout.write("Removed previous demo users/jobs.")

    def _seed_users(self):
        users = {}
        for spec in USERS:
            user, created = User.objects.get_or_create(
                email=spec["email"],
                defaults={
                    "first_name": spec["first_name"],
                    "last_name": spec["last_name"],
                    "role": spec["role"],
                    "is_staff": spec["role"] == Role.ADMIN,
                    "is_superuser": spec["role"] == Role.ADMIN,
                },
            )
            if created:
                user.set_password(DEMO_PASSWORD)
                user.save()
                self.stdout.write(f"Created user {user.email}")
            else:
                # Ensure password is known for demo
                user.set_password(DEMO_PASSWORD)
                user.first_name = spec["first_name"]
                user.last_name = spec["last_name"]
                user.role = spec["role"]
                user.save()
                self.stdout.write(f"Updated user {user.email}")
            users[user.email] = user
        return users

    def _seed_jobs(self, recruiter):
        jobs = []
        for spec in JOBS:
            job, created = JobOpening.objects.get_or_create(
                title=spec["title"],
                created_by=recruiter,
                defaults={
                    "department": spec["department"],
                    "location": spec["location"],
                    "level": spec["level"],
                    "description": spec["description"],
                    "skills": spec["skills"],
                    "status": JobStatus.OPEN,
                },
            )
            if created:
                self.stdout.write(f"Created job {job.title}")
            jobs.append(job)
        return jobs

    def _seed_candidates(self, jobs, recruiter):
        """15 candidates spread across jobs and stages."""
        candidates = []
        sources = list(CandidateSource.values)
        stage_orders = [1, 1, 2, 2, 3, 3, 3, 4, 4, 5, 5, 6, 6, 7, 2]

        for i in range(15):
            job = jobs[i % len(jobs)]
            stage = job.pipeline_stages.get(order=stage_orders[i])
            email = f"candidate{i + 1:02d}@example.com"
            status = CandidateStatus.ACTIVE
            if stage.name == "Rejected":
                status = CandidateStatus.REJECTED
            elif stage.name == "Hired":
                status = CandidateStatus.HIRED

            candidate, created = Candidate.objects.get_or_create(
                email=email,
                job=job,
                defaults={
                    "first_name": FIRST_NAMES[i],
                    "last_name": LAST_NAMES[i],
                    "phone": f"+3360000{i + 1:04d}",
                    "source": sources[i % len(sources)],
                    "current_stage": stage,
                    "status": status,
                },
            )
            if created:
                log_candidate_created(candidate=candidate, user=recruiter)
                self.stdout.write(
                    f"Created candidate {candidate} -> {stage.name} ({job.title})"
                )
            candidates.append(candidate)
        return candidates

    def _seed_interviews(self, candidates, jobs, recruiter, interviewers, admin):
        """8 interviews: mix of past and future."""
        now = timezone.now()
        plan = [
            # past completed-ish
            (-10, InterviewType.PHONE, InterviewStatus.COMPLETED, [0, 0]),
            (-7, InterviewType.VIDEO, InterviewStatus.COMPLETED, [0, 1]),
            (-5, InterviewType.ONSITE, InterviewStatus.COMPLETED, [1, 2]),
            (-3, InterviewType.VIDEO, InterviewStatus.COMPLETED, [0]),
            (-1, InterviewType.PHONE, InterviewStatus.COMPLETED, [1]),
            # future
            (2, InterviewType.VIDEO, InterviewStatus.SCHEDULED, [0, 1]),
            (4, InterviewType.ONSITE, InterviewStatus.SCHEDULED, [2]),
            (6, InterviewType.PHONE, InterviewStatus.SCHEDULED, [0, 2]),
        ]
        interviews = []
        for idx, (day_offset, itype, status, iv_idxs) in enumerate(plan):
            candidate = candidates[idx]
            job = candidate.job
            existing = Interview.objects.filter(
                candidate=candidate,
                type=itype,
                status=status,
            ).first()
            if existing:
                interviews.append(existing)
                continue

            interview = Interview.objects.create(
                candidate=candidate,
                job=job,
                type=itype,
                scheduled_at=now + timedelta(days=day_offset, hours=10),
                duration_min=60,
                status=status,
                created_by=recruiter,
                video_link="https://meet.example.com/sqli-demo" if itype == InterviewType.VIDEO else "",
                location="SQLI Paris HQ" if itype == InterviewType.ONSITE else "",
            )
            assigned = [interviewers[i] for i in iv_idxs]
            interview.interviewers.set(assigned)
            log_interview_scheduled(interview=interview, user=recruiter)
            if status == InterviewStatus.SCHEDULED:
                notify_interviewers(
                    interview=interview,
                    interviewer_ids=[u.id for u in assigned],
                )
            interviews.append(interview)
            self.stdout.write(
                f"Created interview #{interview.id} ({itype}/{status}) for {candidate}"
            )
        return interviews

    def _seed_scorecards(self, interviews, interviewers):
        """5 scorecards on past interviews."""
        skill = {
            "technical": 4,
            "communication": 3,
            "problem_solving": 4,
            "culture_fit": 3,
            "leadership": 3,
        }
        plans = [
            (0, 0, 4, Recommendation.YES, "Strong Django depth", "Limited frontend"),
            (1, 0, 5, Recommendation.STRONG_YES, "Excellent system design", "None major"),
            (1, 1, 4, Recommendation.YES, "Clear communicator", "Needs mentoring practice"),
            (2, 1, 3, Recommendation.NEUTRAL, "Solid basics", "Weak on architecture"),
            (3, 0, 4, Recommendation.YES, "Good ownership", "Vue experience light"),
        ]
        created = []
        for iv_idx, user_idx, rating, rec, strengths, weaknesses in plans:
            interview = interviews[iv_idx]
            interviewer = interviewers[user_idx]
            if not interview.interviewers.filter(id=interviewer.id).exists():
                interview.interviewers.add(interviewer)
            if Scorecard.objects.filter(interview=interview, interviewer=interviewer).exists():
                continue
            sc = Scorecard.objects.create(
                interview=interview,
                interviewer=interviewer,
                overall_rating=rating,
                skill_ratings=skill,
                strengths=strengths,
                weaknesses=weaknesses,
                recommendation=rec,
                private_notes="Seeded demo note.",
            )
            finalize_scorecard_submission(scorecard=sc, user=interviewer)
            created.append(sc)
            self.stdout.write(f"Created scorecard for interview #{interview.id}")
        return created

    def _seed_ai_sessions(self, user, candidate):
        if AISession.objects.filter(user=user, type=AISessionType.QUESTIONS).exists():
            return
        AISession.objects.create(
            type=AISessionType.QUESTIONS,
            user=user,
            input_data={"job_title": "Senior Python Developer", "level": "senior"},
            output_data={
                "questions": [
                    {
                        "question": "Explain Django ORM N+1 and how you avoid it.",
                        "type": "technical",
                        "difficulty": "hard",
                    }
                ]
                * 8
            },
        )
        if candidate:
            AISession.objects.create(
                type=AISessionType.SUMMARY,
                user=user,
                candidate=candidate,
                input_data={"candidate_id": candidate.id},
                output_data={
                    "strengths": ["Strong technical fundamentals"],
                    "concerns": ["Limited leadership examples"],
                    "recommendation": "yes",
                    "suggested_next_step": "Proceed to final interview.",
                },
            )
