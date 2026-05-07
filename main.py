import os

from fastapi import FastAPI, Depends, status, HTTPException, Query, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.db.session import get_db
from app.schemas.user import UserRead, UserCreate, UserLogin, UserListItem
from app.services.user import UserService
from app.schemas.pagination import PaginatedResponse
from app.core.limiter import limiter

app = FastAPI(title="Something API")

origins = [
    "http://localhost",
    "http://localhost:8000",
]

ALLOWED_HOSTS = {"localhost", "127.0.0.1"}

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.middleware("http")
async def ignore_favicon(request: Request, call_next):
    host = request.headers.get("host", "").split(":")[0]

    if host not in ALLOWED_HOSTS:
        return Response(status_code=403)

    if request.url.path == "/favicon.ico":
        return Response(content="", media_type="image/x-icon")

    return await call_next(request)


# @app.get("/faivicon.ico", include_in_schema=False)
# async def favicon():
#     return Response(status_code=204)


@app.get("/", response_class=HTMLResponse)
async def main(request: Request):
    return """
    <html>
        <head>
            <title>Test</title>
        </head>
        <style>
            h1 {
                color: white;
                text-align: center;
            }

            body {
                margin: 0;
                height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                background-color: black; 
            }
        </style>
        <body>
            <h1>Hello Bitchass</h1>
        </body>
    </html>
    """


@app.post(
    path="/users/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    tags=["auth"],
    summary="Регистрация нового пользователя",
)
@limiter.limit("5/minute")
async def register(
    request: Request, body: UserCreate, db: AsyncSession = Depends(get_db)
):
    service = UserService(db)
    user, created = await service.register(
        username=body.username, email=body.email, password=body.password
    )
    if not created:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Пользователь с таким именем уже существует.",
        )
    return user


@app.post(
    "/users/login",
    response_model=UserRead,
    tags=["auth"],
    summary="Вход (аутентификация)",
)
@limiter.limit("10/minute")
async def login(request: Request, body: UserLogin, db: AsyncSession = Depends(get_db)):
    service = UserService(db)
    user = await service.login(username=body.username, password=body.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверное имя пользователя или пароль.",
        )
    return user


# Users: list & detail


@app.get(
    path="/users/list",
    response_model=PaginatedResponse[UserListItem],
    tags=["users"],
    summary="Список всех пользователей",
)
@limiter.limit("30/minute")
async def list_users(
    request: Request,
    page: int = Query(default=1, ge=1, description="Номер страницы"),
    page_size: int = Query(default=10, ge=1, le=100, description="Кол-во на странице"),
    db: AsyncSession = Depends(get_db),
):
    service = UserService(db)
    return await service.get_all(page=page, page_size=page_size)


@app.get(
    path="/users/{user_id}",
    response_model=UserRead,
    tags=["users"],
    summary="Детальная информация о пользователе",
)
@limiter.limit("30/minute")
async def get_user(request: Request, user_id: int, db: AsyncSession = Depends(get_db)):
    service = UserService(db)
    user = await service.get_by_id(user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Пользователь с id={user_id} не найден.",
        )
    return user
