from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.config import settings
from .core.database import Base, engine
from .api import auth, users, students, groups, contracts, payments, attendance, turnstile, reports

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Bunyodkor CIMS API",
    description="Complete Information Management System for Bunyodkor Football Academy",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.FRONTEND_URL,
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",  # Vite default port
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(students.router, prefix="/api/students", tags=["Students"])
app.include_router(groups.router, prefix="/api/groups", tags=["Groups"])
app.include_router(contracts.router, prefix="/api/contracts", tags=["Contracts"])
app.include_router(payments.router, prefix="/api/payments", tags=["Payments"])
app.include_router(attendance.router, prefix="/api/attendance", tags=["Attendance"])
app.include_router(turnstile.router, prefix="/api/turnstile", tags=["Turnstile"])
app.include_router(reports.router, prefix="/api/reports", tags=["Reports"])


@app.get("/")
async def root():
    return {
        "message": "Welcome to Bunyodkor CIMS API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
