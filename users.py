from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy.orm import Session
import bcrypt

from db import get_db
from models import User
from auth import create_access_token, create_refresh_token


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


# =========================
# SIGN UP
# =========================

@router.post("/signup")
def signup(
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):

    # Check username
    existing_username = (
        db.query(User)
        .filter(User.username == username)
        .first()
    )

    if existing_username:
        raise HTTPException(
            status_code=400,
            detail="Username already exists"
        )

    # Check email
    existing_email = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    if existing_email:
        raise HTTPException(
            status_code=400,
            detail="Email already exists"
        )

    # Validate password
    if len(password) < 6:
        raise HTTPException(
            status_code=400,
            detail="Password must be at least 6 characters"
        )

    # Hash password
    hashed_password = bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

    # Create user
    new_user = User(
        username=username,
        email=email,
        password=hashed_password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "User created successfully",
        "user": {
            "id": new_user.id,
            "username": new_user.username,
            "email": new_user.email,
            "image": new_user.image
        }
    }


# =========================
# SIGN IN
# =========================

@router.post("/signin")
def signin(
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):

    # Find user
    user = (
        db.query(User)
        .filter(User.username == username)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    # Verify password
    password_valid = bcrypt.checkpw(
        password.encode("utf-8"),
        user.password.encode("utf-8")
    )

    if not password_valid:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    # Create access token
    access_token = create_access_token({
        "user_id": user.id,
        "username": user.username
    })

    # Create refresh token
    refresh_token = create_refresh_token(
        user.id,
        db
    )

    return {
        "message": "Login successful",

        "access_token": access_token,
        "refresh_token": refresh_token,

        "token_type": "bearer",

        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "image": user.image
        }
    }
