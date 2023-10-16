import logging
#import core.logger
#logging.basicConfig(filename=log_file_name, level=logging.NOTSET, format=format_str, datefmt='%m/%d/%Y %I:%M:%S %p')

import uvicorn
from fastapi import FastAPI, Depends
from fastapi.responses import ORJSONResponse, PlainTextResponse

from core import config

from api.v1 import base

from core.config import app_settings

app = FastAPI(
    title=app_settings.app_title,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
)

logging.info(f'\n_______________________\nFastAPI started\n_______________________\n')
app.include_router(base.api_router)
logging.info(f'api_router included')

print(f'PROJECT_HOST: {app_settings.PROJECT_HOST}')
print(f'PROJECT_PORT: {app_settings.PROJECT_PORT}')
print(f'database_dsn: {app_settings.database_dsn}')

if __name__ == '__main__':
    print('__main__')
    print(f'PROJECT_HOST: {app_settings.PROJECT_HOST}')
    print(f'PROJECT_PORT: {app_settings.PROJECT_PORT}')
    uvicorn.run(
        'main:app',
        host=app_settings.PROJECT_HOST,
        port=app_settings.PROJECT_PORT,
    )
