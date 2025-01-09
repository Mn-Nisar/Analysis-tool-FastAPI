from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.db.models import User
from app.utils.security import hash_password, verify_password

router = APIRouter()

@router.post("/register")
def register_user(name:str, email: str, password: str, db: Session = Depends(get_db)):
    hashed_password = hash_password(password)
    user = User(name=name,email=email, password=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"email": user.email, "id": user.id}

@router.post("/login")
def login_user(email: str, password: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    return {"message": "Login successful", "user_id": user.id}
