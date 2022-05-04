from http import HTTPStatus

import bcrypt
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from app.constants import ErrorMessage
from app.db import CommentOrm, RateOrm, UserOrm, create_session
from app.db_queries import (
    get_film_by_slug,
    get_user_by_login,
    get_users_film_comment,
    get_users_film_rate,
)
from app.request_models import NewRate, NewReview, NewUser


def create_comment_with_rate(
    film_slug: str, login: str, review: NewReview, session: sessionmaker
) -> None:
    film = get_film_by_slug(film_slug, session)
    user = get_user_by_login(login, session)
    rate_row = get_users_film_rate(film, session, user)
    comment_row = get_users_film_comment(film, session, user)
    if rate_row or comment_row:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT, detail=ErrorMessage.ALREADY_EXIST.value
        )
    new_rate = RateOrm(user_id=user.id, film_id=film.id, rate=review.rate)
    new_comment = CommentOrm(user_id=user.id, film_id=film.id, comment=review.comment)
    session.add_all([new_rate, new_comment])


def create_rate(
    film_slug: str, login: str, review: NewRate, session: sessionmaker
) -> None:
    film = get_film_by_slug(film_slug, session)
    user = get_user_by_login(login, session)
    rate_row = get_users_film_rate(film, session, user)
    if rate_row:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT, detail=ErrorMessage.ALREADY_EXIST.value
        )
    new_rate = RateOrm(user_id=user.id, film_id=film.id, rate=review.rate)
    session.add(new_rate)


def create_new_user(user: NewUser) -> None:
    try:
        with create_session() as session:
            new_user = UserOrm(
                user_name=user.login,
                password=bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt()),
            )
            session.add(new_user)
    except IntegrityError as user_already_exist:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT, detail=ErrorMessage.ALREADY_EXIST.value
        ) from user_already_exist
