from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from app.database import Base, engine, SessionLocal
from app.routers import auth, competitions, applications, admin
from app.init_data import seed_data

app = FastAPI(title="Grant Cabinet API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()
    try:
        seed_data(db)
    finally:
        db.close()


@app.exception_handler(Exception)
async def unhandled_exception_handler(_, exc: Exception):
    return JSONResponse(status_code=500, content={"detail": f"Внутренняя ошибка сервера: {str(exc)}"})


@app.get("/health")
def health():
    return {"status": "ok"}


app.include_router(auth.router)
app.include_router(competitions.router)
app.include_router(applications.router)
app.include_router(admin.router)