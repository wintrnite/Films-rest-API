import json
from http import HTTPStatus

from requests import Response

from app.constants import ErrorMessage


def test_show_films_with_registered_user(
    response_get_films_with_registered_user: Response,
):
    assert response_get_films_with_registered_user.status_code == HTTPStatus.OK


def test_dont_show_films_with_incorrect_login(
    response_get_films_with_incorrect_login: Response,
):
    assert (
        response_get_films_with_incorrect_login.status_code == HTTPStatus.UNAUTHORIZED
    )
    assert json.loads(response_get_films_with_incorrect_login.content) == {
        'detail': ErrorMessage.INCORRECT_LOGIN.value
    }


def test_dont_show_films_with_incorrect_password(
    response_get_films_with_incorrect_password: Response,
):
    assert (
        response_get_films_with_incorrect_password.status_code
        == HTTPStatus.UNAUTHORIZED
    )
    assert json.loads(response_get_films_with_incorrect_password.content) == {
        'detail': ErrorMessage.INCORRECT_PASSWORD.value
    }


def test_register_new_user(
    response_register_new_user: Response, new_user_added_to_db: bool
):
    assert response_register_new_user.status_code == HTTPStatus.OK
    assert new_user_added_to_db


def test_register_existing_user(response_register_new_user):
    assert response_register_new_user.status_code == HTTPStatus.CONFLICT


def test_show_certain_film(response_show_certain_correct_film: Response):
    assert response_show_certain_correct_film.status_code == HTTPStatus.OK


def test_create_review(response_create_review, new_review_added_to_db):
    assert response_create_review.status_code == HTTPStatus.OK
    assert new_review_added_to_db


def test_update_review(response_update_review, review_updated):
    assert response_update_review.status_code == HTTPStatus.OK
    assert review_updated


def test_create_rate(response_create_rate, new_rate_added_to_db):
    assert response_create_rate.status_code == HTTPStatus.OK
    assert new_rate_added_to_db


def test_update_rate(response_update_rate, rate_updated):
    assert response_update_rate.status_code == HTTPStatus.OK
    assert rate_updated
