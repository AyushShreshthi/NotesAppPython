from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base, engine
from app.routes import auth, users, notes

# Creates tables if they don't exist (fine for dev; use Alembic migrations in production)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Notes Application Backend",
    description="FastAPI + PostgreSQL Notes app with JWT auth and soft delete",
    version="1.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"success": False, "message": "Validation error", "errors": exc.errors()},
    )


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(notes.router)


@app.get("/", tags=["Health"])
def health_check():
    return {"status": "ok", "service": "notes-app-backend"}
