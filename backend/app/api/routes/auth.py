from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.database import get_db
from app.db.models.user import User, UserRole
from app.schemas.auth import UserCreate, UserLogin, TokenResponse, UserResponse
from app.core.security import hash_password, verify_password, create_access_token, get_current_user

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(User).where(User.email == user_data.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=user_data.email,
        password_hash=hash_password(user_data.password),
        role=user_data.role or UserRole.OPERATOR,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)

    return UserResponse(id=user.id, email=user.email, role=user.role.value)


@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == credentials.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role.value, "email": user.email}
    )

    return TokenResponse(
        access_token=access_token,
        user_id=user.id,
        role=user.role.value,
        email=user.email,
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == int(current_user["id"])))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return UserResponse(id=user.id, email=user.email, role=user.role.value)
