from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.config import settings
from backend.app.database import init_db
from backend.app.routes import projects, files, settings as settings_routes, ws, mcp

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize SQLite schema
    await init_db()
    yield

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Autonomous AI Software Engineer Agent Workspace API",
    lifespan=lifespan
)

# Enable CORS for frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(projects.router)
app.include_router(files.router)
app.include_router(settings_routes.router)
app.include_router(mcp.router)
app.include_router(ws.router)

@app.get("/api/health")
async def health():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION
    }
