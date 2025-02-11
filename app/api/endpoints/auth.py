from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from datetime import timedelta, datetime
from pydantic import BaseModel, EmailStr
from typing import Annotated

from app.core.database import get_async_session
from app.db.models import User
from app.utils.security import hash_password, verify_password
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import JWTError, jwt

router = APIRouter()

SECRET_KEY = 'kje8twul$718up0(f^yfw6!*0%c3ghbx%ptmqhhg9o@s6a(#0j'
ALGORITHM = 'HS256'

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='token')

class CreateUserRequest(BaseModel):
    name:str
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    Token_type: str


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def create_user(
    create_user_request: CreateUserRequest, 
    db: AsyncSession = Depends(get_async_session) 
):
    print(create_user_request)

    stmt = select(User).where(User.email == create_user_request.email)
    result = await db.execute(stmt)  
    existing_user = result.scalars().first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered."
        )

    create_user_model = User(
        name=create_user_request.name,
        email=create_user_request.email,
        password=bcrypt_context.hash(create_user_request.password)
    )

    db.add(create_user_model)
    await db.commit()  
    await db.refresh(create_user_model)

    return {"message": "User registered successfully", "user_id": create_user_model.id}


@router.post("/login")
async def login_user(
    email: str, 
    password: str, 
    db: AsyncSession = Depends(get_async_session)  
):
    stmt = select(User).where(User.email == email)
    result = await db.execute(stmt)  
    user = result.scalars().first()

    if not user or not verify_password(password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    return {"message": "Login successful", "user_id": user.id}


@router.post("/token", status_code=status.HTTP_200_OK)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], 
    db: AsyncSession = Depends(get_async_session)  
):
    user = await authenticate_user(form_data.username, form_data.password, db) 

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    access_token = create_access_token(user.name, user.email, timedelta(minutes=70))
    refresh_token = create_refresh_token(user.id, timedelta(days=7))

    return {'access_token': access_token, 'token_type': 'bearer', 'refresh_token': refresh_token}

async def authenticate_user(email: str, password: str, db: AsyncSession):
    stmt = select(User).where(User.email == email)
    result = await db.execute(stmt) 
    user = result.scalars().first()

    if not user or not bcrypt_context.verify(password, user.password):  
        return False

    return user

def create_access_token(name: str, email: str, expires_delta: timedelta):
    encode = {'sub': name, 'id': email}
    expires = datetime.utcnow() + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        return payload  
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_user(
    token: str = Depends(oauth2_bearer), 
    db: AsyncSession = Depends(get_async_session) 
):
    payload = verify_access_token(token)
    email = payload.get("id")

    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )
    
    stmt = select(User).where(User.email == email)
    result = await db.execute(stmt)
    user = result.scalars().first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    
    return user


def create_refresh_token(user_id: int, expires_delta: timedelta):
    print("user_iduser_iduser_iduser_iduser_iduser_iduser_iduser_id",user_id)
    encode = {'sub': str(user_id)}
    expires = datetime.utcnow() + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

@router.post("/refresh-token", status_code=status.HTTP_200_OK)
async def refresh_token(
    refresh_token: str, 
    db: AsyncSession = Depends(get_async_session) 
):
    try:
        payload = verify_access_token(refresh_token)
        user_id = payload.get("sub")

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )

        stmt = select(User).where(User.id == user_id)
        result = await db.execute(stmt)  
        user = result.scalars().first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )

        new_access_token = create_access_token(user.name, user.email, timedelta(minutes=60))

        return {"access_token": new_access_token, "token_type": "bearer"}

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    


# test user 
# nisar@gmail.com
# ciods_123
# eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJuaXNhciIsImlkIjoibmlzYXJAZ21haWwuY29tIiwiZXhwIjoxNzM5MjYxODgwfQ.wEUX0KVArl386hM8QOP9QTChsMMYWANGUsuZdpQEC-I

# {
#   "noOfTest": 0,
#   "noOfControl": 0,
#   "noOfBatches": 0,
#   "expType": "techrep",
#   "fileUrl": "app/analysis-files/TECHNICAL.csv"
# }

# 24