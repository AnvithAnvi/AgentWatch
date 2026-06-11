from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app import models
from app.routes import projects, runs, spans, admin

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AgentWatch API",
    description="Simple monitoring API for AI agents.",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(projects.router)
app.include_router(runs.router)
app.include_router(spans.router)
app.include_router(admin.router)


@app.get("/")
def health_check():
    return {
        "status": "ok",
        "message": "AgentWatch API is running"
    }