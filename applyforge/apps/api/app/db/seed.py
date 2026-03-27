from app.core.security import hash_password
from app.db.session import Base, SessionLocal, engine
from app.models.entities import Application, ApplicationRun, ApplicationStep, CandidateProfile, Job, JobScore, User
from app.services.scoring import score_job


def run() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    user = db.query(User).filter(User.email == 'demo@applyforge.dev').first()
    if not user:
        user = User(email='demo@applyforge.dev', password_hash=hash_password('demo1234'))
        db.add(user)
        db.commit()
        db.refresh(user)

    profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == user.id).first()
    if not profile:
        profile = CandidateProfile(
            user_id=user.id,
            basics={'full_name': 'Alex Builder', 'target_role': 'Full Stack Engineer'},
            summary='Full-stack engineer with product and AI automation experience.',
            skills=['Python', 'FastAPI', 'TypeScript', 'React', 'Docker'],
            experience=[],
            projects=[],
            education=[],
            certifications=[],
            links=[{'type': 'linkedin', 'url': 'https://linkedin.com/in/example'}],
            fact_locked=True,
        )
        db.add(profile)
        db.commit()

    if db.query(Job).filter(Job.user_id == user.id).count() == 0:
        jobs = [
            Job(
                user_id=user.id,
                title='Senior Full Stack Engineer',
                company='Nimbus AI',
                location='Remote, US',
                description='Looking for FastAPI, React, TypeScript, Docker experience.',
                remote_type='remote',
                source='manual',
                application_url='https://example.com/job/1',
                dedupe_key='seed_job_1',
            ),
            Job(
                user_id=user.id,
                title='Backend Engineer',
                company='DataRail',
                location='New York, NY',
                description='Python, SQL, and cloud fundamentals needed.',
                remote_type='hybrid',
                source='manual',
                application_url='https://example.com/job/2',
                dedupe_key='seed_job_2',
            ),
        ]
        db.add_all(jobs)
        db.commit()

    for job in db.query(Job).filter(Job.user_id == user.id).all():
        if not db.query(JobScore).filter(JobScore.job_id == job.id).first():
            result = score_job(profile.__dict__, job.description, job.title)
            db.add(JobScore(job_id=job.id, **result))

    db.commit()

    first_app = db.query(Application).filter(Application.user_id == user.id).first()
    if not first_app:
        first_job = db.query(Job).filter(Job.user_id == user.id).first()
        first_app = Application(user_id=user.id, job_id=first_job.id, status='ready_to_apply')
        db.add(first_app)
        db.commit()
        db.refresh(first_app)
        run = ApplicationRun(application_id=first_app.id, mode='assisted', status='paused')
        db.add(run)
        db.commit()
        db.refresh(run)
        db.add_all(
            [
                ApplicationStep(run_id=run.id, name='open_application_url', status='completed', output={'ok': True}),
                ApplicationStep(run_id=run.id, name='pause_before_submit', status='paused', output={'requires_approval': True}),
            ]
        )
        db.commit()

    db.close()
    print('Seed complete: demo@applyforge.dev / demo1234')


if __name__ == '__main__':
    run()
