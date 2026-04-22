from fastapi import FastAPI, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.user import UserRead, UserCreate, UserLogin, UserListItem
from app.services.user import UserService

app = FastAPI(title="Something API")


@app.post(
    path="/users/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    tags=["auth"],
    summary="Registration of new user"
)
async def register(body: UserCreate, db: AsyncSession = Depends(get_db)):
    service = UserService(db)
    user, created = await service.register(
        username=body.username,
        email=body.email,
        password=body.password
    )
    if not created:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Пользователь с таким именем уже существует."
        )
    return user


@app.post(
    "/users/login",
    response_model=UserRead,
    tags=["auth"],
    summary="Вход (аутентификация)",
)
async def login(body: UserLogin, db: AsyncSession = Depends(get_db)):
    service = UserService(db)
    user = await service.login(username=body.username, password=body.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверное имя пользователя или пароль."
        )
    return user


# Users: list & detail

@app.get(
    path="/users/list",
    response_model=list[UserListItem],
    tags=["users"],
    summary="Список всех пользователей",
)
async def list_users(db: AsyncSession = Depends(get_db)):
    service = UserService(db)
    return await service.get_all()


@app.get(
    path="/users/{user_id}",
    response_model=UserRead,
    tags=["users"],
    summary="Детальная информация о пользователе",
)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    service = UserService(db)
    user = await service.get_by_id(user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Пользователь с id={user_id} не найден."
        )
    return user
