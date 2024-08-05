from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base



dburl = 'mysql+pymysql://test:Testtest12@localhost:3306/typeupload'

engine = create_engine(
    dburl,echo=True
)
    # dburl,connect_args={"check_same_thread" : False}, pool_recycle=3600

SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush= False, bind=engine))

Base = declarative_base()

Base.query = SessionLocal.query_property()
