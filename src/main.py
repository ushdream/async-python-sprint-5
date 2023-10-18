import logging

import uvicorn
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from api.v1 import base

from core.config import app_settings

app = FastAPI(
    title=app_settings.app_title,
    default_response_class=ORJSONResponse,
)

logging.info(f'\n_______________________\nApplication started\n_______________________\n')
app.include_router(base.api_router)
logging.info(f'api_router included')

if __name__ == '__main__':
    print('__main__')
    uvicorn.run(
        'main:app',
        host=app_settings.PROJECT_HOST,
        port=app_settings.PROJECT_PORT,
    )
