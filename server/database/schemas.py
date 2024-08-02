from sqlalchemy import Column,Integer,String, Text, ForeignKey
# from sqlalchemy.orm import relationship
from .connection import Base



class BinaryImage (Base):
    __tablename__ = 'binimg'

    id = Column(Integer,autoincrement=True,primary_key=True,unique=True)
    filename = Column(String(50))
    mimetype = Column(String(50))
    content = Column(Text(5000))



class DataList(Base):
    __tablename__ = 'datalist'

    id = Column(Integer,autoincrement=True,primary_key=True,unique=True)
    title = Column(String(20))
    favorite = Column(String(20),ForeignKey(BinaryImage.filename))


