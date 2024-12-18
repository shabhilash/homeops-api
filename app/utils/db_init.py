import logging
from sqlalchemy import create_engine, text, insert
from sqlalchemy.orm import sessionmaker

from app.conf.app_config import db_folder


##########
# TEST ENV
# DB_PATH = ":memory:"
# DB_CONN = db_create(DB_PATH)
##########

##########
# PROD ENV
DB_PATH = f"{db_folder}/homeops.sqlite"
##########

# Logger
logger = logging.getLogger("homeops.db")

engine = create_engine(f'sqlite:///{DB_PATH}',echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
status = SessionLocal().execute(text('SELECT 1'))
logger.info(status)

from app.utils.db_schemas import User
# Password is Passw0rd
admin_user = insert(User).values(username="homeops", first_name="Homeops", last_name="Admin",
                  email_address="homeops@homeops.local",
                  password="$2b$12$mHqyQGhUP14wUPUaddhTQuISx4WPEzfpm3Kand5RlorNNelNueYXW", enabled=1,
                  is_superuser=1).prefix_with("OR IGNORE", dialect="sqlite")
with engine.connect() as conn:
    result = conn.execute(admin_user)
    conn.commit()