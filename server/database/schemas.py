from sqlalchemy import Column,Integer,String, BLOB,Text, ForeignKey
from sqlalchemy.orm import relationship
from .connection import Base







class DataList(Base):
    __tablename__ = 'datalist'

    id = Column(Integer,autoincrement=True,primary_key=True,nullable=False)
    title = Column(String(20))
    favorite = Column(String(20))

    # img_rel = relationship(BinaryImage, backref= "list_rel")

    # def __repr__(self):
    #     return f"BinaryImage{self.id}: {self.id}"


class BinaryImage (Base):
    __tablename__ = 'binimg'

    id = Column(Integer,autoincrement=True,primary_key=True,nullable=False)
    filename = Column(String(50))
    mimetype = Column(String(50))
    content = Column(BLOB(5000))

    # list_rel = relationship(DataList, backref= "img_rel")

    # def __repr__(self):
    #     return f"BinaryImage{self.id}: id: {self.list_rel}"
