from typing import Optional

from pydantic import BaseModel


class FilmModel(BaseModel):
    id: int
    film_name: str
    slug: str
    year: int

    class Config:
        orm_mode = True


class UserModel(BaseModel):
    id: int
    user_name: str
    password: str

    class Config:
        orm_mode = True


class RateModel(BaseModel):
    id: int
    user_id: int
    film_id: int
    rate: int

    class Config:
        orm_mode = True


class CommentModel(BaseModel):
    id: int
    user_id: int
    film_id: int
    comment: str

    class Config:
        orm_mode = True


class FilmWithMoreInfoModel(BaseModel):
    id: int
    film_name: str
    slug: str
    year: int
    average_rate: Optional[float]
    rate_number: Optional[int]
    comment_number: Optional[int]

    class Config:
        orm_mode = True
