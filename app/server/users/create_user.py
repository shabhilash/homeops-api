from sqlalchemy import exists
from sqlalchemy.orm import Session

from app.utils.db_init import engine
from app.utils.db_schemas import User


def create_user_if_not_exists(user_data):
    with Session(engine) as session:
        exists_query = session.query(
            exists().where(user_data['username'] == User.username)
        ).scalar()

        if not exists_query:
            new_user = User(**user_data)
            session.add(new_user)
            session.commit()
            status = {"message": "User created successfully"}
        else:
            status = {"message": "User already exists"}

    return status