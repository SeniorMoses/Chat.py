from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta, timezone
import jwt
import secrets

from models import User, RefreshToken
from db import get_db
from config import (
SECRET,
TOKEN_EXPIRE_MINUTES,
TOKEN_EXPIRE_DAYS
)

oauth2_scheme = OAuth2PasswordBearer(
tokenUrl="/login"
)

def create_access_token(user_data: dict):

    exp = (
    datetime.now(timezone.utc)
    + timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    )

    payload = {
    "user_id": user_data["user_id"],
    "username": user_data["username"],
    "exp": exp
    }

    return jwt.encode(
    payload,
    SECRET,
    algorithm="HS256"
    )

def create_refresh_token(
    user_id: int,
    db: Session
 ):

    raw_token = secrets.token_urlsafe(64)

    exp = (
    datetime.now(timezone.utc)
    + timedelta(days=TOKEN_EXPIRE_DAYS)
    )

    refresh_token = RefreshToken(
    token=raw_token,
    user_id=user_id,
    exp_at=exp
    )

    db.add(refresh_token)
    db.commit()
    db.refresh(refresh_token)

    return raw_token

def decode_token(
token: str,
db: Session
):

    try:

        payload = jwt.decode(
        token,
        SECRET,
        algorithms=["HS256"]
        )

        user_id = payload.get("user_id")

        if not user_id:
            raise HTTPException(
            status_code=401,
            detail="Invalid token"
            )

        user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
        )

        if not user:

            raise HTTPException(
            status_code=404,
            detail="User not found"
            )

        return user

    except jwt.ExpiredSignatureError:

        raise HTTPException(
        status_code=401,
        detail="Token expired"
        )

    except jwt.InvalidTokenError:

        raise HTTPException(
        status_code=401,
        detail="Invalid token"
        )

def get_current_user(
token: str = Depends(oauth2_scheme),
db: Session = Depends(get_db)
):

    return decode_token(token, db)

def get_admin(
user: User = Depends(get_current_user)
):

    if user.role != "admin":

        raise HTTPException(
        status_code=403,
        detail="User forbidden"
        )

    return user
