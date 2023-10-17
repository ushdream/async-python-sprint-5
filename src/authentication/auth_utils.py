from datetime import datetime, timedelta
from typing import Annotated
import logging

from fastapi import Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from core.config import app_settings

print('auth.py imported')
# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = app_settings.SECRET_KEY

ALGORITHM = app_settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = app_settings.ACCESS_TOKEN_EXPIRE_MINUTES

fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        # "full_name": "John Doe",
        #"email": "johndoe@example.com",
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
    # email: str | None = None
    # full_name: str | None = None
    disabled: bool | None = None


class UserInDB(User):
    hashed_password: str


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password, hashed_password):
    verification = pwd_context.verify(plain_password, hashed_password)
    print(f'veify_password: {verification}')
    return verification


def get_password_hash(password):
    passwoed_hash = pwd_context.hash(password)
    print(f'get_password_hash:\n   password = {password}\n   password_hash = {passwoed_hash}')
    return passwoed_hash


def get_user(db, username: str):
    print(f'get user')
    if username in db:
        user_dict = db[username]
        print(f'user: {username}')
        return UserInDB(**user_dict)
    print(f'user is not found')


def authenticate_user(fake_db, username: str, password: str):
    print(f'authenticate_user')
    user = get_user(fake_db, username)
    print(f'user: {user}')
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        print(f'password is not veryfied')
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    print(f'create access token')
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    print(f'access token: {encoded_jwt}')
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        print(f'get_current_user: token: {token}')
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        print(f'decoded payload: {username}')
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
        print(f'generated token: {token_data}')
    except JWTError:
        raise credentials_exception
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
        current_user: Annotated[User, Depends(get_current_user)]
):
    print(f'get_current_active_user: {current_user.disabled}')
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
