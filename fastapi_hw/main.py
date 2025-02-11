import re
from typing import Callable
import logging

import redis.asyncio as redis
from pathlib import Path
from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi_limiter import FastAPILimiter
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.routes.contacts import router as contacts_router
from src.routes.auth import router as auth_router
from src.routes.users import router as users_router
from src.conf.config import config


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
origins = ['*']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

user_agent_ban_list = [r"Googlebot", r"Python-urllib"]

@app.middleware('http')
async def user_agent_ban_middleware(request: Request, call_next: Callable):
    user_agent = request.headers.get('user-agent')
    if any(re.search(ban_pattern, user_agent) for ban_pattern in user_agent_ban_list):
        return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={"detail": "You are banned"})
    response = await call_next(request)
    return response


BASE_DIR = Path(__file__).resolve().parent
app.mount('/static', StaticFiles(directory=BASE_DIR / 'src' / 'static'), name='static')

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(contacts_router)


@app.on_event('startup')
async def startup():
    r = await redis.Redis(host=config.REDIS_DOMAIN, port=config.REDIS_PORT, db=0, password=config.REDIS_PASSWORD)
    await FastAPILimiter.init(r)


@app.get('/')
def index():
    return {'message': 'Welcome to HW_13'}

@app.get('/api/healthchecker')
async def healthchecker(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(text('SELECT 1'))
        res = result.fetchone()
        if res is None:
            raise HTTPException(status_code=500, detail='Database is not configured correctly')
        return {"message": "Service is running!"}
    except Exception as err:
        logging.error(f"Database connection error: {err}")
        raise HTTPException(status_code=500, detail='Database connection error')