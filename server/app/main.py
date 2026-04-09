from fastapi import FastAPI, Depends
from app.db import database
from app.models import models
from app.api import auth
from app.api.deps import get_current_user

# Create tables
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="BlaBlaIF API")

app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])

@app.get("/")
def read_root(current_user: models.User = Depends(get_current_user)):
    return {"message": f"Welcome to BlaBlaIF API, {current_user.name}!"}
