from sqlalchemy import Column,Integer,String, LargeBinary
from sqlalchemy.orm import relationship
from .connection import Base







class BinaryImage(Base):
    __tablename__ = 'binimg'

    id = Column(Integer,autoincrement=True,primary_key=True,nullable=False)
    title = Column(String(20))
    filename = Column(String(20))
    content = Column(LargeBinary)
