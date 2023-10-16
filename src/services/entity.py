from models.urls import URLs as URLsModel
from models.urllogger import URLLogger as URLLoggerModel
from .base import RepositoryDB

class RepositoryEntity(RepositoryDB):
    pass

entity_crud = RepositoryEntity(URLsModel, URLLoggerModel)

