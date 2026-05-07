from fastapi import (
    Query,
    status,
    Depends,
    Request,
    APIRouter,
    HTTPException,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.user import UserRead, UserLogin, UserCreate, UserListItem
from app.services.user import UserService
from app.schemas.pagination import PaginatedResponse
from app.core.limiter import limiter

router = APIRouter(tags=["users"])


@router.post(
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


@router.post(
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


@router.get(
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


@router.get(
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
