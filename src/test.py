from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, String, Integer, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
from typing import List, Optional
import uvicorn
import asyncpg
from pydantic import BaseModel
from sqlalchemy import JSON
from sqlalchemy.sql import func
from sqlalchemy import DateTime
import sqlalchemy

app = FastAPI()

Base = sqlalchemy.orm.declarative_base()


class URL(Base):
    __tablename__ = "urls"
    id = Column(Integer, primary_key=True, index=True)
    link = Column(String, unique=True, index=True)
    shortened_link = Column(String, unique=True, index=True)
    deleted = Column(Boolean, default=False)


engine = create_engine("postgresql+asyncpg://username:password@localhost/db_name")
Base.metadata.create_all(bind=engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class UrlCreate(BaseModel):
    url: str


@app.post("/")
async def shorten_url(url: UrlCreate, db=Depends(get_db)):
    db_url = add_url(url.url, db)
    return {"shortened_url": db_url.shortened_link}


def add_url(url: str, db):
    db_url = URL(link=url)
    db.add(db_url)
    db.commit()
    return db_url


@app.get("/{shortened_url_id}")
async def redirect_to_original_url(shortened_url_id: str, db=Depends(get_db)):
    db_link = get_url_by_shortened_id(shortened_url_id, db)
    if not db_link:
        raise HTTPException(status_code=410, detail="URL not found")
    return RedirectResponse(db_link.link)


def get_url_by_shortened_id(shortened_url_id: str, db):
    query = db.query(Url).filter(Url.shortened_link == shortened_url_id)
    db_link = query.first()
    if db_link:
        return db_link
    return None


class URLStatus(BaseModel):
    full_info: Optional[bool] = False
    max_result: Optional[int] = 10
    offset: Optional[int] = 0


@app.get("/{shortened_url_id}/status")
async def get_url_status(shortened_url_id: str, status: UrlStatus, db=Depends(get_db)):
    db_link = get_url_by_shortened_id(shortened_url_id, db)
    if not db_link:
        raise HTTPException(status_code=410, detail="URL not found")
    result = {"total_clicks": get_total_clicks(db_link)}
    if status.full_info:
        urls = get_click_urls(db_link, status.offset, status.max_result)
        result["click_urls"] = [{"datetime": url.datetime, "client_info": url.client_info} for url in urls]
    return result


def get_total_clicks(db_link):
    return db.query(Click).filter(Click.url_id == db_link.id).count()


def get_click_urls(db_link, offset: int, max_result: int):
    query = db.query(Click).filter(Click.url_id == db_link.id).order_by(Click.datetime.desc())
    return query.offset(offset).limit(max_result).all()


class Click(Base):
    __tablename__ = "clicks"
    id = Column(Integer, primary_key=True, index=True)
    url_id = Column(Integer)
    datetime = Column(DateTime, default=func.now())
    client_info = Column(JSON)


@app.get("/ping")
async def ping_db():
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        return {"status": "Database is accessible"}
    except:
        raise HTTPException(status_code=500, detail="Database is not accessible")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8080)