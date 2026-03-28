from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import (
    admin,
    application_runs,
    applications,
    auth,
    companies,
    files,
    inbox,
    jobs,
    profile,
    resume_templates,
    resume_themes,
    roles,
    setup,
)
from app.core.config import settings
from app.db.session import Base, engine
from app.models import entities  # noqa: F401
from app.services.resume_themes import seed_resume_themes


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    Path(settings.storage_path).mkdir(parents=True, exist_ok=True)
    Path(settings.artifacts_path).mkdir(parents=True, exist_ok=True)
    from app.db.session import SessionLocal

    db = SessionLocal()
    try:
        seed_resume_themes(db)
    finally:
        db.close()
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(profile.router)
app.include_router(roles.router)
app.include_router(companies.router)
app.include_router(jobs.router)
app.include_router(applications.router)
app.include_router(application_runs.router)
app.include_router(files.router)
app.include_router(resume_themes.router)
app.include_router(resume_templates.router)
app.include_router(inbox.router)
app.include_router(setup.router)
app.include_router(admin.router)


@app.get("/")
def root() -> dict:
    return {"name": "ApplyForge API", "status": "running", "product": "ApplyForge"}
