from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.db import database
from app.models import models
from app.api import auth, rides
from app.api.deps import get_current_user
from app.services.seed import seed_initial_data

# Create tables
models.Base.metadata.create_all(bind=database.engine)
with database.SessionLocal() as db:
    seed_initial_data(db)

app = FastAPI(title="BlaBlaIF API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(rides.router, prefix="/api/v1", tags=["rides"])

@app.get("/")
def read_root(current_user: models.User = Depends(get_current_user)):
    return {"message": f"Welcome to BlaBlaIF API, {current_user.name}!"}
