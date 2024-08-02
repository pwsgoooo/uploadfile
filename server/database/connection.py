from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base



dburl = 'sqlite:///./sql_app.db'

engine = create_engine(
    dburl,connect_args={"check_same_thread" : False}
)

SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush= False, bind=engine))

Base = declarative_base()

Base.query = SessionLocal.query_property()
