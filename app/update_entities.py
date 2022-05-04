from http import HTTPStatus

from fastapi import HTTPException
from sqlalchemy.orm import sessionmaker

from app.constants import ErrorMessage
from app.db_queries import (
    get_film_by_slug,
    get_user_by_login,
    get_users_film_comment,
    get_users_film_rate,
)
from app.request_models import NewRate, NewReview


def update_comment_with_rate(
    film_slug: str, login: str, review: NewReview, session: sessionmaker
) -> None:
    film = get_film_by_slug(film_slug, session)
    user = get_user_by_login(login, session)
    rate_row = get_users_film_rate(film, session, user)
    comment_row = get_users_film_comment(film, session, user)
    if not rate_row or not comment_row:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=ErrorMessage.NOT_FULL_ENTITY.value,
        )
    rate_row.rate = review.rate
    comment_row.comment = review.comment


def update_rate(
    film_slug: str, login: str, review: NewRate, session: sessionmaker
) -> None:
    user = get_user_by_login(login, session)
    film = get_film_by_slug(film_slug, session)
    rate_row = get_users_film_rate(film, session, user)
    if not rate_row:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=ErrorMessage.NOT_FULL_ENTITY.value,
        )
    rate_row.rate = review.rate
