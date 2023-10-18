import uuid
from datetime import timedelta
from typing import Annotated
import logging

from fastapi import Query
from fastapi.security import OAuth2PasswordRequestForm

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from authentication.auth_utils import fake_users_db, pwd_context, authenticate_user, Token, create_access_token
from authentication.auth_utils import ACCESS_TOKEN_EXPIRE_MINUTES, User, get_current_active_user

from db.db import get_session
from services.entity import entity_crud

router_auth = APIRouter()


@router_auth.post("/sign_up/", status_code=status.HTTP_201_CREATED)
async def new_user(
        *,
        user_name: Annotated[str, Query(min_length=4, max_length=64)],
        password: Annotated[str, Query(min_length=4)],
        db: AsyncSession = Depends(get_session),
):
    logging.info(f'new user: {user_name}, {password}')
    result: bool = False
    try:
        password_hashed = pwd_context.hash(password)
        account_id = uuid.uuid4()
        fake_users_db[user_name] = {
            "username": user_name,
            "hashed_password": password_hashed,
            "disabled": False,
            "account_id": account_id
        }
        logging.info(fake_users_db)
        logging.info(f'user {user_name} added with password {password}')
        logging.info(f'hashed password: {fake_users_db[user_name]["hashed_password"]}')

        id = await entity_crud.new_user(db, user_name, password_hashed, account_id)
        fake_users_db[user_name][id] = id

        result = True
    except Exception as e:
        logging.exception(f'Error: Sign-up:\n{e}')

    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST
        )
    return {user_name: fake_users_db[user_name]["hashed_password"]}


@router_auth.post("/token", response_model=Token)
async def login_for_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    logging.info(f'login: user: {user}')
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router_auth.get("/users/me/", status_code=status.HTTP_200_OK, response_model=User)
async def read_users_me(
        current_user: Annotated[User, Depends(get_current_active_user)]
):
    logging.info(f'GET current_user: {current_user}')
    return current_user


@router_auth.get("/check_me", status_code=status.HTTP_200_OK)
async def read_own_items(
        current_user: Annotated[User, Depends(get_current_active_user)]
):
    logging.info(f'user is authorized: {current_user}')
    return {'user': current_user}
