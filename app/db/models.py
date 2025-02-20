from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import as_declarative
from sqlalchemy import JSON

@as_declarative()
class Base:
    id: int
    __name__: str

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(String(50), index=True)
    email = Column(String(100), unique=True, index=True)
    password = Column(String(255))
    analyses = relationship("Analysis", back_populates="user")

class Analysis(Base):
    __tablename__ = "analysis"
    id = Column(Integer, primary_key=True, autoincrement=True, index=True) 
    user_id = Column(Integer, ForeignKey('users.id'), index=True)  
    no_of_test = Column(Integer)
    no_of_control = Column(Integer)
    no_of_batches = Column(Integer, nullable=True)
    exp_type = Column(String(50))
    file_url = Column(String(255))
    index_col  = Column(String(255) , nullable=True)
    normalized_data = Column(String(255) , nullable=True)
    resedue_data = Column(String(255) , nullable=True)
    column_data = Column(JSON, nullable=True)
    user = relationship("User", back_populates="analyses")
