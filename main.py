from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import os

from config import settings
from database import Base, engine
from routers import analytics_router, auth_router, transactions_router

# Create all tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.app_name,
    description="""
## Finance Tracking System API

A backend system for managing personal financial records with role-based access control.

### Roles
| Role     | Permissions |
|----------|-------------|
| viewer   | View own transactions and summary |
| analyst  | View + filters + category/monthly analytics |
| admin    | Full access: create, update, delete, manage users |

### Quick Start
1. **Register** a user via `POST /auth/register`
2. **Login** via `POST /auth/login` to get a Bearer token
3. Use the token in the **Authorize** button above
4. Start exploring endpoints

> Tip: Use the seeded data by running `python seed.py` for instant test data.
    """,
    version="1.0.0",
    contact={"name": "Finance System"},
)

# CORS - allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler for unhandled errors
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred. Please try again."},
    )


# Include routers
app.include_router(auth_router)
app.include_router(transactions_router)
app.include_router(analytics_router)


@app.get("/health", tags=["Health"])
def health():
    return {"status": "healthy"}


# Serve frontend — must be LAST so it doesn't override API routes
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

    @app.get("/", tags=["Frontend"])
    def frontend():
        """Serve the frontend UI."""
        return FileResponse(os.path.join(static_dir, "index.html"))
else:
    @app.get("/", tags=["Health"])
    def root():
        return {"status": "ok", "app": settings.app_name, "version": "1.0.0", "docs": "/docs"}
