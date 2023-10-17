import datetime
import logging
from typing import Any, List, Optional, Type, TypeVar
from pydantic import BaseModel
from models.base import Base
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update, func
from sqlalchemy.sql import text

ModelType = TypeVar("ModelType", bound=Base)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

from .repository import Repository


class RepositoryDB(Repository):
    def __init__(self, model_urls: Type[ModelType], model_urllogger: Type[ModelType], model_users: Type[ModelType]):
        self._model_urls = model_urls
        self._model_urllogger = model_urllogger
        self._model_users = model_users

    async def get(self, db: AsyncSession, id: Any) -> Optional[ModelType]:
        statement = select(self._model_urls).where(self._model.id == id)
        results = await db.execute(statement=statement)
        return results.scalar_one_or_none()

    async def get_id(self, db: AsyncSession, title: str) -> Optional[ModelType]:
        statement = select(self._model).where(self._model.title == title)
        results = await db.execute(statement=statement)
        return results.scalar_one_or_none()

    async def get_new_id(self, db: AsyncSession) -> int:
        statement = select(func.max(self._model_urls.id))
        result = await db.execute(statement=statement)
        max_id = result.one()
        next_id = max_id[0] + 1 if max_id is not None else 0
        return next_id

    async def ping(self, db) -> bool:
        # tatement = select(True).select_from(self._model)
        logging.info(f'ping')
        statement = select(True)
        try:
            q_result = await db.execute(statement=statement)
            result = q_result.one()[0]
            logging.info(f'result_one: {result}')
        except Exception as e:
            result = False
            logging.info(f'CRUD: ping: False')
        return result
    async def ping_all(self, db) -> dict:
        print(f'pnig_all')
        logging.info(f'ping all')
        result = {}
        begin = datetime.datetime.now()
        try:
            print(f'Call query')
            q_result = await db.execute(statement=text('select 1'))
            print(f'Query result: {q_result}')
            end = datetime.datetime.now()
            row = q_result.fetchone()
            print(f'row: {row}')
            if str(row[0]) == '1':
                result['DB'] = (end - begin).total_seconds()
            else:
                result['DB'] = 'Unavailable'
        except Exception as e:
            print(f'ping exception')
            logging.exception(f'Error: connecting to DB')
            result['DB'] = 'Unavailable'
        return result

    async def new_url(self, db: AsyncSession, data: dict):
        logging.info(f'CRUD: new_url')
        statement = insert(self._model_urls).values(data).returning(self._model_urls.id)
        result = await db.execute(statement=statement)
        row = result.fetchone()
        await db.commit()
        return row.id

    async def log_surl_call(self, db: AsyncSession, url_short: str) -> None:
        statement = insert(self._model_urllogger).values(
            {'url_short': url_short, 'created_at': datetime.datetime.now()}
        )
        await db.execute(statement=statement)
        await db.commit()
        logging.info(f'logging {url_short}')


    async def get_surl_id(self, db, url_short):
        statement = select(self._model_urls).where(self._model_urls.url_short == url_short)
        result = await db.execute(statement=statement)
        await db.commit()
        logging.info(result)
        return result.scalar_one_or_none()

    async def get_status_by_surl(self, db, url_short):
        statement = select(self._model_urllogger).where(self._model_urllogger.url_short == url_short)
        result = await db.execute(statement=statement)
        rows = result.fetchall()
        val_returned = len(rows)
        await db.commit()
        logging.info(f'get_status_by_surl(): lines number: {val_returned}')
        return val_returned

    async def check_surl_exists(self, db: AsyncSession, url_short: str) -> bool:
        returned_val = False
        statement = select(self._model_urls).where(self._model_urls.url_short == url_short)
        result = await db.execute(statement=statement)
        rows = result.fetchall()
        rows_number = len(rows)
        db.commit()
        if rows_number > 0:
            returned_val = True
        return returned_val

    async def get_url_by_surl(self, db: AsyncSession, url_short: str) -> Optional[str]:
        returned_val = None
        if await self.check_surl_exists(db, url_short):
            logging.info(f'Short url: {url_short} exists')
            await self.log_surl_call(db, url_short)   # Logging short url call
            statement = select(self._model_urls).where(self._model_urls.url_short == url_short)
            result = await db.execute(statement=statement)
            rows = result.fetchone()
            logging.info(f'dir(row): {dir(rows[0])}')
            logging.info(f'id: {rows[0].id}')
            logging.info(f'url: {rows[0].url_original}')
            logging.info(f'deleted: {rows[0].deleted}')
            if rows[0].deleted:
                returned_val = {'deleted': True}
            else:
                returned_val = {
                    'url_original': rows[0].url_original,
                    'deleted': False
                }

            await db.commit()

        return returned_val

    async def get_multi(
            self, db: AsyncSession, *, skip=0, limit=100
    ) -> List[ModelType]:
        statement = select(self._model_urls).offset(skip).limit(limit)
        results = await db.execute(statement=statement)
        await db.commit()
        return results.scalars().all()

    async def mark_deleted(self, db: AsyncSession, *, url_short: str) -> Optional[dict]:
        logging.info(f'Mark as deleted, short url: {url_short}')
        returned_val = None

        if await self.check_surl_exists(db, url_short):
            statement = update(self._model_urls).where(self._model_urls.url_short == url_short).values(deleted=True)
            result = await db.execute(statement=statement)
            await db.commit()
            logging.info(result)
            returned_val = True

        return returned_val
