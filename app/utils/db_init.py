import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

##########
# TEST ENV
# DB_PATH = ":memory:"
# DB_CONN = db_create(DB_PATH)
##########

##########
# PROD ENV
DB_PATH = "D:/ash/github/homeops-api/app/db/homeops.sqlite"
##########

# Logger
logger = logging.getLogger("homeops.db")

engine = create_engine(f'sqlite:///{DB_PATH}',echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
status = SessionLocal().execute(text('SELECT 1'))
logger.info(status)