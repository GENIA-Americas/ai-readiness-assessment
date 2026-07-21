from fastapi import FastAPI

from app.config import settings
from app.db import Base, engine
from app.routers import assessments

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.app_name,
    description="Backend API for scoring organizational AI readiness.",
    version="0.1.0",
)

app.include_router(assessments.router)


@app.get("/health")
def health():
    return {"status": "ok"}
