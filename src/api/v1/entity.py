import datetime
import logging
import random

from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from db.db import get_session
from services.entity import entity_crud
from core.config import app_settings

router = APIRouter()
print(f'route is made')


async def check_allowed_ip(request: Request):
    logging.info(f'IP: {request.client.host}')

    def is_ip_banned(request):
        logging.info(f'request:\n{request}')
        try:
            real_ip = request.client.host
            logging.info(f'IP-address: {real_ip}')
            is_banned = real_ip in app_settings.BLACK_LIST
        except KeyError:
            logging.info("IP header not found")
            is_banned = True
        return is_banned

    if is_ip_banned(request):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)


@router.post(
    "/banch",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(check_allowed_ip)],
    description='Send banch of new URLs'
)
async def new_url_list(
        *,
        db: AsyncSession = Depends(get_session),
        urls_original: List[dict] = None
) -> List[dict]:
    """
    :param db:
    :param url_original: url
    :return: dict {'short_url': short_url}, where short_url - generated short url
    """

    returned_value = []
    for url_item in urls_original:
        logging.info(f'url_item: {url_item}')
        short_url = str(random.randint(10000000, 20000000))
        id = await entity_crud.new_url(
            db,
            {
                'url_original': url_item['original-url'],
                'url_short': short_url,
                'created_at': datetime.datetime.now(),
            }
        )
        logging.info(f'inserted URL id# {id}')
        if not id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="New item was not generated properly")
        returned_value.append({'short-url': short_url, 'short-id': id})

    return returned_value


@router.get(
    "/ping_db",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(check_allowed_ip)],
    description='Check if the DB is working'
)
async def ping(db: AsyncSession = Depends(get_session)) -> dict:
    """
    Check if the DB is alive
    :return: {'db_ready': db_ready}, db_ready is bool
    """
    db_ready = await entity_crud.ping(db=db)
    if not db_ready:
        print(f'db is not ready')
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Data Base is unavailable"
        )
    return {'db_ready': db_ready}


@router.get(
    "/ping",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(check_allowed_ip)],
    description='Check if the DB is working'
)
async def ping_all(db: AsyncSession = Depends(get_session)) -> dict:
    """
    Check if the DB is alive
    :return: {'db_ready': db_ready}, db_ready is bool
    """
    readiness = await entity_crud.ping_all(db=db)

    return readiness


@router.get(
    "/{url_short}/status",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(check_allowed_ip)],
    description='Get status of short URL'
)
async def get_status(
        *,
        db: AsyncSession = Depends(get_session),
        url_short: str
) -> dict:
    """
    :param db: db obj
    :param url_short:  short url
    :return: Number of short url calls
    """
    logging.info(f'get_status for {url_short}')
    result = await entity_crud.get_status_by_surl(db, url_short=url_short)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f'Short item {url_short} is not found'
        )
    return {'status': result}


@router.get(
    "/{url_short}",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(check_allowed_ip)],
    description='Get original URL by its short form'
)
async def read_entity_id(
        *,
        db: AsyncSession = Depends(get_session),
        url_short: str,
) -> Any:
    """
    Get original URL by short URL. This call is logged in urllogger table.
    """

    logging.info(f'Get url by short url: {url_short}')
    result = await entity_crud.get_url_by_surl(db=db, url_short=url_short)
    if not result:
        logging.info(f'short url {url_short} is not found')
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f'Short url {url_short} is not found'
        )
    elif result['deleted']:
        logging.info(f'short url {url_short} is deleted')
        raise HTTPException(
            status_code=status.HTTP_410_GONE, detail=f'short url {url_short} is deleted'
        )
    else:
        returned_val = {'url': result['url_original']}

    return returned_val


@router.post(
    "/{url_original}",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(check_allowed_ip)],
    description='Generate short URL'
)
async def new_url(
        *,
        db: AsyncSession = Depends(get_session),
        url_original: str
) -> dict:
    """
    :param db:
    :param url_original: url
    :return: dict {'short_url': short_url}, where short_url - generated short url
    """
    logging.info('new_url')

    short_url = str(random.randint(1000000, 2000000))
    result = await entity_crud.new_url(
        db,
        {
            'url_original': url_original,
            'url_short': short_url,
            'created_at': datetime.datetime.now(),
        }
    )
    logging.info(f'inserted URL id# {result}')
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="New item was not generated properly")

    return {'short_url': short_url}


@router.delete(
    "/{url_short}",
    dependencies=[Depends(check_allowed_ip)],
    description='Mark short URL as deleted'
)
async def delete_url(*, db: AsyncSession = Depends(get_session), url_short: str) -> Any:
    """
    Delete short URL. Jast mark it int the table urls as deleted.
    """
    logging.info('delete_entity')
    result = await entity_crud.mark_deleted(db=db, url_short=url_short)
    logging.info(result)
    if result:
        returned_val = {'deleted': True}
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'The short url {url_short} was not found and deleted'
        )

    return returned_val
