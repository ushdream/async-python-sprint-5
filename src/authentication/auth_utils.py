from datetime import datetime, timedelta
from typing import Annotated
import logging

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
import uuid

from core.config import app_settings

SECRET_KEY = app_settings.SECRET_KEY

ALGORITHM = app_settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = app_settings.ACCESS_TOKEN_EXPIRE_MINUTES

users_db = {
    "johndoe": {
        "username": "johndoe",
        "account_id": uuid.uuid4(),
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        "disabled": False,
    }
}


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class User(BaseModel):
    username: str
    account_id: uuid.UUID
    disabled: bool | None = None


class UserInDB(User):
    hashed_password: str


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password, hashed_password):
    verification = pwd_context.verify(plain_password, hashed_password)
    logging.info(f'veify_password: {verification}')
    return verification


def get_password_hash(password):
    passwoed_hash = pwd_context.hash(password)
    logging.info(f'get_password_hash:\n   password = {password}\n   password_hash = {passwoed_hash}')
    return passwoed_hash


def get_user(db, username: str):
    logging.info('get user')
    if username in db:
        user_dict = db[username]
        logging.info(f'user: {username}')
        return UserInDB(**user_dict)
    logging.info('user is not found')


def authenticate_user(fake_db, username: str, password: str):
    logging.info('authenticate_user')
    user = get_user(fake_db, username)
    logging.info(f'user: {user}')
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        logging.info('password is not veryfied')
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    logging.info('create access token')
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    logging.info(f'access token: {encoded_jwt}')
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        logging.info(f'get_current_user: token: {token}')
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        logging.info(f'decoded payload: {username}')
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
        logging.info(f'generated token: {token_data}')
    except JWTError:
        raise credentials_exception
    user = get_user(users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
        current_user: Annotated[User, Depends(get_current_user)]
):
    logging.info(f'get_current_active_user: {current_user.disabled}')
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
