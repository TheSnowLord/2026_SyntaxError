from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.solve import router as solve_router
from app.database.db import create_db

app = FastAPI(
    title="AgentForge AI Backend",
    version="1.0.0",
    description="Backend for Multi-Agent Collaboration"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routes
app.include_router(solve_router)


# Create database when server starts
@app.on_event("startup")
def startup():
    create_db()


# Root endpoint
@app.get("/")
def root():
    return {
        "message": "AgentForge AI Backend is Running 🚀"
    }


# Health check endpoint
@app.get("/health")
def health():
    return {
        "status": "healthy"
    }
