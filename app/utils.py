from http import HTTPStatus

import bcrypt
from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError

from app.constants import ErrorMessage
from app.db import UserOrm, create_session


def check_user_registration(login: str, password: str) -> None:
    try:
        with create_session() as session:
            user = session.query(UserOrm).filter(UserOrm.user_name == login).one()
            hashed_password = user.password
            if not bcrypt.hashpw(password.encode(), hashed_password) == hashed_password:
                raise HTTPException(
                    status_code=HTTPStatus.UNAUTHORIZED,
                    detail=ErrorMessage.INCORRECT_PASSWORD.value,
                )
    except SQLAlchemyError as incorrect_login:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail=ErrorMessage.INCORRECT_LOGIN.value,
        ) from incorrect_login
