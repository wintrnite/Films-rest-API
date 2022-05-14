from http import HTTPStatus
from typing import Any, Optional, Union

import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic.error_wrappers import ValidationError
from sqlalchemy import desc
from sqlalchemy.exc import SQLAlchemyError

from app.constants import ErrorMessage, Sort
from app.create_entities import create_comment_with_rate, create_new_user, create_rate
from app.db import Base, CommentOrm, FilmOrm, RateOrm, create_session, engine, init_db
from app.db_models import CommentModel, FilmWithMoreInfoModel, RateModel
from app.db_queries import get_films_with_more_info
from app.request_models import (
    CertainFilmResponse,
    CreatedReviewResponse,
    FilmsResponse,
    NewRate,
    NewReview,
    NewUser,
    RegisteredUserResponse,
    UpdatedReviewResponse,
)
from app.update_entities import update_comment_with_rate, update_rate
from app.utils import check_user_registration

app = FastAPI()
security = HTTPBasic()


@app.on_event("startup")
def startup():
    init_db(Base, engine)


@app.get('/films')
def show_films(
        credentials: HTTPBasicCredentials = Depends(security),
        substr: Optional[str] = Query(None),
        year: Optional[int] = Query(None),
        sort: Optional[str] = Query(None),
        film_id: Optional[int] = Query(None),
        limit: Optional[int] = Query(None),
) -> FilmsResponse:
    login, password = credentials.username, credentials.password
    check_user_registration(login, password)
    response = FilmsResponse(films=[])
    with create_session() as session:
        films_query = (
            get_films_with_more_info(session)
                .group_by(FilmOrm.id)
                .filter(*get_filters(substr, year, film_id))
        )
        if sort == Sort.BY_RATE.value:
            films_query = films_query.order_by(desc(RateOrm.rate))
        if limit:
            films_query = films_query.limit(limit)
        films = films_query.all()
        for film in films:
            response.films.append(FilmWithMoreInfoModel.from_orm(film))
    return response


# не получается перенести эту функцию в другой файл
def get_filters(
        substr: Optional[str],
        year: Optional[int],
        film_id: Optional[int],
) -> list[Union[Any, bool]]:
    filters = []
    if substr:
        filters.append(FilmOrm.film_name.contains(substr))
    if year:
        filters.append(FilmOrm.year == year)
    if film_id:
        filters.append(FilmOrm.id >= film_id)
    return filters


@app.post('/films/{film_slug}')
def create_review_to_film(
        film_slug: str,
        review: Union[NewReview, NewRate],
        credentials: HTTPBasicCredentials = Depends(security),
) -> CreatedReviewResponse:
    login, password = credentials.username, credentials.password
    check_user_registration(login, password)
    try:
        with create_session() as session:
            if isinstance(review, NewReview):
                create_comment_with_rate(film_slug, login, review, session)
            elif isinstance(review, NewRate):
                create_rate(film_slug, login, review, session)
            return CreatedReviewResponse(created=review)
    except SQLAlchemyError as film_not_found:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail=ErrorMessage.FILM_NOT_FOUND.value
        ) from film_not_found


@app.put('/films/{film_slug}')
def update_review_to_film(
        film_slug: str,
        review: Union[NewReview, NewRate],
        credentials: HTTPBasicCredentials = Depends(security),
) -> UpdatedReviewResponse:
    login, password = credentials.username, credentials.password
    check_user_registration(login, password)
    try:
        with create_session() as session:
            if isinstance(review, NewReview):
                update_comment_with_rate(film_slug, login, review, session)
            elif isinstance(review, NewRate):
                update_rate(film_slug, login, review, session)
            return UpdatedReviewResponse(updated=review)
    except SQLAlchemyError as film_not_found:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail=ErrorMessage.FILM_NOT_FOUND.value
        ) from film_not_found


@app.get('/films/{film_slug}')
def show_certain_film(
        film_slug: str, credentials: HTTPBasicCredentials = Depends(security)
) -> CertainFilmResponse:
    login, password = credentials.username, credentials.password
    check_user_registration(login, password)
    showing_comments = []
    showing_rates = []
    with create_session() as session:
        try:
            film = FilmWithMoreInfoModel.from_orm(
                get_films_with_more_info(session)
                    .filter(FilmOrm.slug == film_slug)
                    .one()
            )
        except ValidationError as film_not_found:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail=ErrorMessage.FILM_NOT_FOUND.value,
            ) from film_not_found
        comments = session.query(CommentOrm).filter(CommentOrm.film_id == film.id).all()
        rates = session.query(RateOrm).filter(RateOrm.film_id == film.id).all()
        for comment in comments:
            showing_comments.append(CommentModel.from_orm(comment))
        for rate in rates:
            showing_rates.append(RateModel.from_orm(rate))

    return CertainFilmResponse(
        film_info=film, comments=showing_comments, rates=showing_rates
    )


@app.post('/register')
def register_new_user(user: NewUser) -> RegisteredUserResponse:
    create_new_user(user)
    return RegisteredUserResponse(registered_user_login=user.login)


if __name__ == '__main__':
    init_db(Base, engine)
    uvicorn.run(app, host='0.0.0.0', port=8000)
