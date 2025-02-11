from pathlib import Path

from fastapi import APIRouter, HTTPException, Depends, status, Security, BackgroundTasks, Request, Form
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.entity.models import User
from src.repository import users as repository_users
from src.schemas.user import UserSchema, UserResponse, TokenSchema, RequestEmail, PasswordResetRequestSchema, \
    PasswordResetConfirmSchema
from src.services.auth import auth_service, RESET_TOKEN_EXPIRE_MINUTES
from src.services.email import send_email
from src.services.reset_pass import send_email_pass

router = APIRouter(prefix='/auth', tags=['auth'])
get_refresh_token = HTTPBearer()
BASE_DIR = Path('.')
templates = Jinja2Templates(directory=BASE_DIR/'src'/'services'/'templates')

@router.post('/signup', response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(body: UserSchema, db: AsyncSession = Depends(get_db)):
    exist_user = await repository_users.get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Email already exists')
    body.password = auth_service.get_password_hash(body.password)
    new_user = await repository_users.create_user(body, db)
    return new_user

@router.post('/login', response_model=TokenSchema)
async def login(body: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    user = await repository_users.get_user_by_email(body.username, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Please, contact support')
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Please, contact support')
    access_token = await auth_service.create_access_token(data={'sub': user.email, 'test': 'Bob Bobov'})
    refresh_token = await auth_service.create_refresh_token(data={'sub': user.email})
    await repository_users.update_token(user, refresh_token, db)
    return {'access_token': access_token, 'refresh_token': refresh_token, 'token_type': 'bearer'}

@router.get('/refresh_token', response_model=TokenSchema)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Security(get_refresh_token), db: AsyncSession = Depends(get_db)):
    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user.refresh_token != token:
        await repository_users.update_token(user, None, db)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid refresh token')

    access_token = await auth_service.create_access_token(data={'sub': email})
    refresh_token = await auth_service.create_refresh_token(data={'sub': email})
    await repository_users.update_token(user, refresh_token, db)
    return  {'access_token': access_token, 'refresh_token': refresh_token, 'token_type': 'bearer'}

@router.post('/logout', status_code=status.HTTP_200_OK)
async def logout(current_user: User = Depends(auth_service.get_current_user), db: AsyncSession = Depends(get_db)):
    await repository_users.logout_user(current_user, db)
    return {'message': 'Successfully logged out'}

@router.get('/confirmed_email/{token}')
async def confirmed_email(token: str, db: AsyncSession = Depends(get_db)):
    email = await auth_service.get_email_from_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Verification error')
    if user.confirmed:
        return {'message': 'Your email is already confirmed'}
    await repository_users.confirmed_email(email, db)
    return {'message': 'Email confirmed'}

@router.post('/request_email')
async def request_email(body: RequestEmail, background_tasks: BackgroundTasks, request: Request, db: AsyncSession = Depends(get_db)):
    user = await repository_users.get_user_by_email(body.email, db)
    if user.confirmed:
        return {'message': 'Your email is already confirmed'}
    if user:
        background_tasks.add_task(send_email, user.email, user.username, str(request.base_url))
    return {'message': 'Check your email for confirmation.'}

@router.post('/reset_password/{token}')
async def reset_password(token: str, new_password: str = Form(PasswordResetConfirmSchema), db: AsyncSession = Depends(get_db)):
    email = await auth_service.verify_refresh_password_token(token)

    if len(new_password) < 8 or new_password.isdigit():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Password too weak')

    hashed_password = auth_service.get_password_hash(new_password)
    await repository_users.update_user_password(email, hashed_password, db)

    auth_service.cache.setex(f'used_token:{token}', RESET_TOKEN_EXPIRE_MINUTES * 60, 'used')
    return {'message': 'Password successfully reset'}

@router.get('/reset_password/{token}', response_class=HTMLResponse)
async def show_reset_password_form(request: Request, token: str):
    return templates.TemplateResponse('reset_password_form.html', {'request': request, 'token': token})

@router.post('/request_reset_password', dependencies=[Depends(RateLimiter(times=1, seconds=60))])
async def request_reset_password(body: PasswordResetRequestSchema, background_tasks: BackgroundTasks, request: Request, db: AsyncSession = Depends(get_db)):
    user = await repository_users.get_user_by_email(body.email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if user:
        background_tasks.add_task(send_email_pass, user.email, user.username, str(request.base_url))
    return {'message': 'Password reset link sent, please, check your email.'}