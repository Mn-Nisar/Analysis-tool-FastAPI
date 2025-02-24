from sqlalchemy import Column, Integer, String, ForeignKey, Float, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import as_declarative

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
    lable_free = relationship("LableFree", back_populates="user")
class Analysis(Base):
    __tablename__ = "analysis"
    id = Column(Integer, primary_key=True, autoincrement=True, index=True) 
    user_id = Column(Integer, ForeignKey('users.id'), index=True)  
    no_of_test = Column(Integer, nullable=True)
    no_of_control = Column(Integer, nullable=True)
    no_of_batches = Column(Integer, nullable=True)
    exp_type = Column(String(50),nullable=True)
    file_url = Column(String(255),nullable=True)
    index_col  = Column(String(255) , nullable=True)
    normalized_data = Column(String(255) , nullable=True)
    resedue_data = Column(String(255) , nullable=True)
    column_data = Column(JSON, nullable=True)

    batch_data = Column(JSON, nullable=True)
    pv_method = Column(String(50), nullable=True)
    pv_cutoff = Column(Float, nullable=True)
    ratio_up = Column(Float, nullable=True)
    ratio_down = Column(Float, nullable=True)
    log2_cut = Column(Float, nullable=True)
    control_name = Column(String(255) , nullable=True)
    final_data = Column(String(255) , nullable=True)
    diffential_data = Column(String(255) , nullable=True)

    user = relationship("User", back_populates="analyses")

class LableFree(Base):
    __tablename__ = "lable_free_analysis"
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), index=True)
    result = Column(String(255), nullable=True)

    user = relationship("User", back_populates="lable_free")