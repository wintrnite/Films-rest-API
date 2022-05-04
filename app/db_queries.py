from typing import Union

from fastapi import HTTPException
from sqlalchemy import distinct, func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

from app.constants import ErrorMessage
from app.db import CommentOrm, FilmOrm, RateOrm, UserOrm


def get_users_film_comment(
    film: FilmOrm, session: sessionmaker, user: UserOrm
) -> CommentOrm:
    return (
        session.query(CommentOrm)
        .filter(CommentOrm.user_id == user.id, CommentOrm.film_id == film.id)
        .first()
    )


def get_user_by_login(login: str, session: sessionmaker) -> UserOrm:
    return session.query(UserOrm).filter(UserOrm.user_name == login).one()


def get_film_by_slug(film_slug: str, session: sessionmaker) -> FilmOrm:
    try:
        return session.query(FilmOrm).filter(FilmOrm.slug == film_slug).one()
    except SQLAlchemyError as film_not_found:
        raise HTTPException(
            status_code=404, detail=ErrorMessage.FILM_NOT_FOUND.value
        ) from film_not_found


def get_users_film_rate(film: FilmOrm, session: sessionmaker, user: UserOrm) -> RateOrm:
    return (
        session.query(RateOrm)
        .filter(RateOrm.user_id == user.id, RateOrm.film_id == film.id)
        .first()
    )


def get_films_with_more_info(
    session: sessionmaker,
) -> Union[FilmOrm, RateOrm, CommentOrm]:
    return (
        session.query(
            FilmOrm.id,
            FilmOrm.film_name,
            FilmOrm.slug,
            FilmOrm.year,
            func.avg(RateOrm.rate).label('average_rate'),
            func.count(distinct(RateOrm.rate)).label('rate_number'),
            func.count(distinct(CommentOrm.comment)).label('comment_number'),
        )
        .outerjoin(RateOrm, RateOrm.film_id == FilmOrm.id)
        .outerjoin(CommentOrm, CommentOrm.film_id == FilmOrm.id)
    )
