from typing import Union

from pydantic import BaseModel, validator

from app.db_models import CommentModel, FilmWithMoreInfoModel, RateModel


class NewUser(BaseModel):
    login: str
    password: str


class NewReview(BaseModel):
    comment: str
    rate: int

    @validator('rate')
    def rate_must_be_from_0_to_10(cls: BaseModel, v: int) -> int:
        if not 0 <= v <= 10:
            raise ValueError()
        return v


class NewRate(BaseModel):
    rate: int

    @validator('rate')
    def rate_must_be_from_0_to_10(cls: BaseModel, v: int) -> int:
        if not 0 <= v <= 10:
            raise ValueError('incorrect range of rate, must be in 0 to 10')
        return v


class FilmsResponse(BaseModel):
    films: list[FilmWithMoreInfoModel]


class CreatedReviewResponse(BaseModel):
    created: Union[NewReview, NewRate]


class UpdatedReviewResponse(BaseModel):
    updated: Union[NewReview, NewRate]


class CertainFilmResponse(BaseModel):
    film_info: FilmWithMoreInfoModel
    comments: list[CommentModel]
    rates: list[RateModel]


class RegisteredUserResponse(BaseModel):
    registered_user_login: str
