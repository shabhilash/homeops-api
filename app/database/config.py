import time

from sqlalchemy import Column, Integer, String, Text, event

from app.database.base import Base

class Config(Base):
    __tablename__ = 'config'

    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(255), unique=True, nullable=False)
    value = Column(Text, nullable=False)
    updated_at = Column(Integer, nullable=False, default=lambda: int(time.time()))  # Default timestamp

    def __repr__(self):
        return f"<Config(key={self.key}, value={self.value}, updated_at={self.updated_at})>"

@event.listens_for(Config, "before_insert")
@event.listens_for(Config, "before_update")
def update_timestamp(mapper, connection, target):
    target.updated_at = int(time.time())  # Set updated_at to current UNIX timestamp

