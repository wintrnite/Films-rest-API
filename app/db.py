from contextlib import contextmanager
from pathlib import Path
from typing import Any

import sqlalchemy as sa
from sqlalchemy import CheckConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.constants import DB_FILE_PATH

engine = sa.create_engine(f'sqlite:///{DB_FILE_PATH}')
Base = declarative_base()


@contextmanager
def create_session(**kwargs: Any) -> sessionmaker:
    new_session = Session(**kwargs)
    try:
        yield new_session
        new_session.commit()
    except Exception:
        new_session.rollback()
        raise
    finally:
        new_session.close()


class FilmOrm(Base):  # type: ignore
    __tablename__ = 'films'

    id = sa.Column(sa.Integer, primary_key=True)
    film_name = sa.Column(sa.String(), nullable=False)
    slug = sa.Column(sa.String(), unique=True, nullable=False)
    year = sa.Column(sa.Integer, nullable=False)


class UserOrm(Base):  # type: ignore
    __tablename__ = 'users'

    id = sa.Column(sa.Integer, primary_key=True)
    user_name = sa.Column(sa.String(), unique=True, nullable=False)
    password = sa.Column(sa.String(), nullable=False)


class RateOrm(Base):  # type: ignore
    __tablename__ = 'rates'
    __table_args__ = (CheckConstraint('0 <= rate <= 10'),)

    id = sa.Column(sa.Integer, primary_key=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'), nullable=False)
    film_id = sa.Column(sa.Integer, sa.ForeignKey('films.id'), nullable=False)
    rate = sa.Column(sa.Integer, nullable=False)


class CommentOrm(Base):  # type: ignore
    __tablename__ = 'comments'

    id = sa.Column(sa.Integer, primary_key=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'), nullable=False)
    film_id = sa.Column(sa.Integer, sa.ForeignKey('films.id'), nullable=False)
    comment = sa.Column(sa.String(), nullable=False)


Session = sessionmaker(bind=engine)


def init_db(base: declarative_base, db_engine: sa.create_engine) -> None:
    if not Path(DB_FILE_PATH).is_file():
        base.metadata.create_all(db_engine)
        with create_session() as session:
            films = (
                FilmOrm(film_name='The Gentlemen', slug='the-gentlemen', year=2019),
                FilmOrm(film_name='Kizumonogatari', slug='kizumonogatari', year=2016),
                FilmOrm(film_name='Snatch', slug='snatch', year=2000),
                FilmOrm(
                    film_name='Lock, Stock and Two Smoking Barrels',
                    slug='lock-stock-and-two-smoking-barrels',
                    year=1998,
                ),
                FilmOrm(
                    film_name='The Shawshank Redemption',
                    slug='the-shawshank-redemption',
                    year=1994,
                ),
            )
            session.add_all(films)
