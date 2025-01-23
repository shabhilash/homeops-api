from datetime import datetime

from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from app.utils.db_init import engine

# SQLAlchemy Setup
Base = declarative_base()

class User(Base):  # SQLAlchemy model
    __tablename__ = 'users'

    username = Column(String(16), primary_key=True)
    first_name = Column(String(30), nullable=True)
    last_name = Column(String(30), nullable=True)
    email_address = Column(String(50), nullable=False)
    password = Column(String, nullable=True)
    enabled = Column(Boolean, default=False)
    is_superuser = Column(Boolean, default=False)
    created_date = Column(DateTime, default=datetime.now)
    updated_date = Column(DateTime,default=datetime.now,onupdate=datetime.now)



# Create tables if they do not exist
Base.metadata.create_all(bind=engine)
