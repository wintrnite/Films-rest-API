from enum import Enum

DB_FILE_PATH = 'app/app.db'


class ErrorMessage(Enum):
    INCORRECT_LOGIN = 'incorrect login'
    INCORRECT_PASSWORD = 'incorrect password'
    FILM_NOT_FOUND = 'film is not found'
    NOT_FULL_ENTITY = 'not full entity'
    ALREADY_EXIST = 'already exist'
    INCORRECT_RATE_RANGE = 'incorrect range of rate, must be in 0 to 10'


class Sort(Enum):
    BY_RATE = 'rate'
