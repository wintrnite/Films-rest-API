import os
from base64 import b64encode
from typing import Union

import bcrypt
import pytest
from fastapi.testclient import TestClient
from requests import Response

from app.constants import DB_FILE_PATH
from app.db import Base, CommentOrm, RateOrm, UserOrm, create_session, engine, init_db
from app.db_models import UserModel
from app.request_models import NewRate, NewReview, NewUser
from app.urls import app


@pytest.fixture(scope='session', autouse=True)
def _init_db():
    init_db(Base, engine)
    yield
    os.remove(DB_FILE_PATH)


@pytest.fixture(scope='session', autouse=True)
def test_client():
    client = TestClient(app)
    return client


@pytest.fixture(scope='session')
def _fill_test_user():
    with create_session() as session:
        test = CorrectTestUser()
        test_user = UserOrm(
            user_name=test.user_name,
            password=bcrypt.hashpw(test.password.encode('utf-8'), bcrypt.gensalt()),
        )
        session.add(test_user)


@pytest.fixture()
def response_get_films_with_registered_user(_fill_test_user, test_client) -> Response:
    correct_user = CorrectTestUser()
    basic_decoded_token = _get_basic_decoded_token(correct_user)
    return _get_response_films_get_request_with_token(basic_decoded_token, test_client)


@pytest.fixture()
def response_get_films_with_incorrect_password(
    _fill_test_user, test_client
) -> Response:
    user_with_incorrect_password = TestUserWithIncorrectPassword()
    basic_decoded_token = _get_basic_decoded_token(user_with_incorrect_password)
    return _get_response_films_get_request_with_token(basic_decoded_token, test_client)


@pytest.fixture()
def response_get_films_with_incorrect_login(_fill_test_user, test_client) -> Response:
    user_with_incorrect_login = TestUserWithIncorrectLogin()
    basic_decoded_token = _get_basic_decoded_token(user_with_incorrect_login)
    return _get_response_films_get_request_with_token(basic_decoded_token, test_client)


@pytest.fixture()
def response_register_new_user(_fill_test_user, test_client) -> Response:
    correct_user = AnotherCorrectUser()
    new_user = NewUser(login=correct_user.user_name, password=correct_user.password)
    return _register_new_user(new_user, test_client)


@pytest.fixture()
def new_user_added_to_db() -> bool:
    needed_user = AnotherCorrectUser()
    with create_session() as session:
        user = (
            session.query(UserOrm)
            .filter(UserOrm.user_name == needed_user.user_name)
            .first()
        )
    return user is not None


@pytest.fixture()
def response_show_certain_correct_film(test_client, _fill_test_user) -> Response:
    user = CorrectTestUser()
    token = _get_basic_decoded_token(user)
    return _response_show_certain_film('snatch', token, test_client)


@pytest.fixture()
def response_create_review(_fill_test_user, test_client):
    user = CorrectTestUser()
    token = _get_basic_decoded_token(user)
    full_review = TestingReviewInformation().review_to_post
    return _response_create_new_review('snatch', token, full_review, test_client)


@pytest.fixture()
def new_review_added_to_db() -> bool:
    needed_review = TestingReviewInformation().review_to_post
    with create_session() as session:
        review = (
            session.query(RateOrm, CommentOrm)
            .filter(
                RateOrm.rate == needed_review.rate,
                CommentOrm.comment == needed_review.comment,
            )
            .join(RateOrm, RateOrm.film_id == CommentOrm.film_id)
            .first()
        )
    return review is not None


@pytest.fixture()
def response_create_rate(_fill_test_user, test_client):
    user = CorrectTestUser()
    token = _get_basic_decoded_token(user)
    rate = TestingRateInformation().rate_to_post
    return _response_create_new_review('the-gentlemen', token, rate, test_client)


@pytest.fixture()
def new_rate_added_to_db() -> bool:
    needed_rate = TestingRateInformation().rate_to_post
    with create_session() as session:
        rate = session.query(RateOrm).filter(RateOrm.rate == needed_rate.rate).first()
    return rate is not None


@pytest.fixture()
def response_update_review(_fill_test_user, test_client) -> Response:
    user = CorrectTestUser()
    token = _get_basic_decoded_token(user)
    review = TestingReviewInformation().review_to_put
    return _response_update_review('snatch', token, review, test_client)


@pytest.fixture()
def review_updated() -> bool:
    needed_review = TestingReviewInformation.review_to_put
    with create_session() as session:
        review = (
            session.query(RateOrm, CommentOrm)
            .filter(
                RateOrm.rate == needed_review.rate,
                CommentOrm.comment == needed_review.comment,
            )
            .join(RateOrm, RateOrm.film_id == CommentOrm.film_id)
            .first()
        )
    return review is not None


@pytest.fixture()
def response_update_rate(_fill_test_user, test_client) -> Response:
    user = CorrectTestUser()
    token = _get_basic_decoded_token(user)
    rate = TestingRateInformation().rate_to_put
    return _response_update_review('the-gentlemen', token, rate, test_client)


@pytest.fixture()
def rate_updated() -> bool:
    needed_rate = TestingRateInformation().rate_to_put
    with create_session() as session:
        rate = session.query(RateOrm).filter(RateOrm.rate == needed_rate.rate)
    return rate is not None


def _response_show_certain_film(
    film_name: str, token: str, client: TestClient
) -> Response:
    return client.get(f'/films/{film_name}', headers=_get_headers(token))


def _register_new_user(user: NewUser, client: TestClient) -> Response:
    return client.post('/register', data=user.json())


def _get_response_films_get_request_with_token(token: str, client) -> Response:
    return client.get('/films', headers=_get_headers(token))


def _response_create_new_review(
    film: str, token: str, review: Union[NewReview, NewRate], client: TestClient
):
    return client.post(
        f'/films/{film}', data=review.json(), headers=_get_headers(token)
    )


def _response_update_review(
    film: str, token: str, review: Union[NewReview, NewRate], client: TestClient
):
    return client.put(f'/films/{film}', data=review.json(), headers=_get_headers(token))


def _get_basic_decoded_token(user: UserModel) -> str:
    token = f'{user.user_name}:{user.password}'.encode('utf-8')
    return f'Basic {b64encode(token).decode("utf-8")}'


def _get_headers(token) -> dict[str, str]:
    return {'Authorization': f'{token}'}


class CorrectTestUser(UserModel):
    id = 1
    user_name = 'kek'
    password = 'kek'


class TestUserWithIncorrectPassword(UserModel):
    id = 1
    user_name = 'kek'
    password = 'kekSHREK'


class TestUserWithIncorrectLogin(UserModel):
    id = 1
    user_name = 'SHREK'
    password = 'kek'


class AnotherCorrectUser(UserModel):
    id = 2
    user_name = 'meow'
    password = 'meow'


class TestingReviewInformation:
    review_to_post = NewReview(rate=10, comment='i love it')
    review_to_put = NewReview(rate=9, comment='good')


class TestingRateInformation:
    rate_to_post = NewRate(rate=10)
    rate_to_put = NewRate(rate=9)
