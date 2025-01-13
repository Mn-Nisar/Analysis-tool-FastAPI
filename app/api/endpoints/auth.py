from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
from pydantic import BaseModel, EmailStr
from typing import Annotated

from app.core.database import get_db
from app.db.models import User
from app.utils.security import hash_password, verify_password
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import JWTError, jwt

router = APIRouter()

SECRET_KEY = 'kje8twul$718up0(f^yfw6!*0%c3ghbx%ptmqhhg9o@s6a(#0j'
ALGORITHM = 'HS256'

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')

class CreateUserRequest(BaseModel):
    name:str
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    Token_type: str


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def create_user(create_user_request:CreateUserRequest,db: Session = Depends(get_db),
                         ):
    
    existing_user = db.query(User).filter(User.email == create_user_request.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered."
        )
    
    create_user_model = User(name=create_user_request.name,
                            email=create_user_request.email,
                            password=bcrypt_context.hash(create_user_request.password))
    db.add(create_user_model)
    db.commit() 
    db.refresh(create_user_model)
    return {"message": "User registered successfully", "user_id": create_user_model.id}


@router.post("/login")
async def login_user(email: str, password: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    return {"message": "Login successful", "user_id": user.id}

@router.post("/token", status_code=status.HTTP_200_OK)
async def login_for_access_token(form_data:Annotated[OAuth2PasswordRequestForm, Depends()],
                                db: Session = Depends(get_db)):
    print("form_data")
    print(form_data.username)
    print(form_data.password)

    print("form_data")

    user = authenticate_user(form_data.username, form_data.password, db)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    token = create_access_token(user.name, user.email, timedelta(minutes=60))

    return {'access_token':token, 'token_type':'bearer'}

def authenticate_user(email:str, password:str,db):
    user = db.query(User).filter(User.email == email).first()
    if not user or bcrypt_context.verify(bcrypt_context.hash(password), user.password):
        return False

    return user

def create_access_token(name:str, email:str, expires_delta: timedelta):
    encode = {'sub':name, 'id':email}
    expires = datetime.utcnow() + expires_delta
    encode.update({'exp':expires})
    return jwt.encode(encode,SECRET_KEY,algorithm=ALGORITHM)



def verify_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload  # Return the decoded token payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    payload = verify_access_token(token)
