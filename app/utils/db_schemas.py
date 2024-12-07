from sqlalchemy import Column, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from app.utils.db_init import engine

# SQLAlchemy Setup
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    username=Column(String(16), primary_key=True)
    first_name=Column(String(30))
    last_name=Column(String(30))
    email_address=Column(String(50), nullable=False)
    password=Column(String())
    enabled=Column(Boolean)



# Create tables if they do not exist
Base.metadata.create_all(bind=engine)
