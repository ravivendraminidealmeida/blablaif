from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.api.deps import get_current_user
from app.core import security, config
from app.schemas import user as user_schema
from app.schemas import token as token_schema
from app.models import models

router = APIRouter()

@router.post("/register", response_model=user_schema.UserResponse)
def register_user(user_in: user_schema.UserCreate, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == user_in.email).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    
    # We should verify if the college_id exists, but omitting for brevity right now.
    college = db.query(models.College).filter(models.College.id == user_in.college_id).first()
    if not college:
        raise HTTPException(status_code=400, detail="College not found")

    user_data = user_in.model_dump(exclude={"password"})
    hashed_password = security.get_password_hash(user_in.password)
    db_user = models.User(**user_data, password_hash=hashed_password)
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.post("/login", response_model=token_schema.Token)
def login_access_token(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not security.verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=config.settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        {"sub": str(user.id)}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=user_schema.UserResponse)
def read_users_me(current_user: models.User = Depends(get_current_user)):
    return current_user

@router.patch("/me", response_model=user_schema.UserResponse)
def update_users_me(
    user_in: user_schema.UserUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    updates = user_in.model_dump(exclude_unset=True)

    if "email" in updates and updates["email"] != current_user.email:
        existing_user = db.query(models.User).filter(models.User.email == updates["email"]).first()
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(
                status_code=400,
                detail="The user with this email already exists in the system.",
            )

    for field, value in updates.items():
        setattr(current_user, field, value)

    db.commit()
    db.refresh(current_user)
    return current_user

@router.patch("/me/password", status_code=status.HTTP_204_NO_CONTENT)
def update_my_password(
    password_in: user_schema.PasswordUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if not security.verify_password(password_in.current_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="Current password is incorrect")

    current_user.password_hash = security.get_password_hash(password_in.new_password)
    db.commit()
    return None
