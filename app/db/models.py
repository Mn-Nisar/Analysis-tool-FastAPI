from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import as_declarative

@as_declarative()
class Base:
    id: int
    __name__: str

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)  # auto_increment
    name = Column(String(50), index=True)
    email = Column(String(100), unique=True, index=True)
    password = Column(String(255))
