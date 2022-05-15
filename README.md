# Films API

## Usage

| Request                   | Description                                                          |
|:--------------------------|:---------------------------------------------------------------------|
| `POST /register`          | Register new user                                                    |
| `GET /films`              | Get films list  (only for registered users)                          |
| `GET /films/{film-slug}`  | Get certain film with comments and rates (only for registered users) |
| `POST /films/{film-slug}` | Create a review or rate of the film (only for registered users)      |
| `PUT /films/{film-slug}`  | Update a review or rate of the film (only for registered users)      |

___

Firstly, you need to register

Request:

`POST /register`

Body (example):

```json
{
  "login": "shrek",
  "password": "shrek_admin"
}
```

Response:

```json
{
  "registered_user_login": "shrek"
}
```

Other endpoints are accessible only for registered users. So, you need to add `Authorization: Basic *your_token*` in
header of further requests, where `*your_token*` is a `*your_login*:*your_password*` encoded in Base64.
___

Request:

`GET /films`

Query params:

| Query param | Description                                  | Value   |
|:------------|:---------------------------------------------|:--------|
| `substr`    | Filter films by substr                       | Any str |
| `year`      | Filter films by year                         | Any int |
| `sort`      | Sort by criterion (only `best` is available) | `best`  |
| `film_id`   | Start index of showing films                 | Any int |
| `limit`     | Limit of showing films                       | Any int |

Response:

```json
{
  "films": [
    {
      "id": 1,
      "film_name": "The Gentlemen",
      "slug": "the-gentlemen",
      "year": 2019,
      "average_rate": null,
      "rate_number": 0,
      "comment_number": 0
    },
    {
      "id": 2,
      "film_name": "Kizumonogatari",
      "slug": "kizumonogatari",
      "year": 2016,
      "average_rate": null,
      "rate_number": 0,
      "comment_number": 0
    }
  ]
}
```

___

Request:

`GET /films/the-gentlemen`

Response:

```json
{
  "film_info": {
    "id": 1,
    "film_name": "The Gentlemen",
    "slug": "the-gentlemen",
    "year": 2019,
    "average_rate": null,
    "rate_number": 0,
    "comment_number": 0
  },
  "comments": [],
  "rates": []
}
```

___

Request:

`POST /films/the-gentlemen`

Body (create review):

```json
{
  "comment": "very good",
  "rate": 10
}
```

Response:

```json
{
  "created": {
    "comment": "very good",
    "rate": 10
  }
}
```

Body (create rate):

```json
{
  "rate": 10
}
```

Response:

```json
{
  "created": {
    "rate": 10
  }
}
```

___
Request:

`PUT /films/the-gentlemen`

Body (update review):

```json
{
  "comment": "hmmm",
  "rate": 9
}
```

Response:

```json
{
  "updated": {
    "comment": "hmmm",
    "rate": 9
  }
}
```

Body (update rate):

```json
{
  "rate": 9
}
```

Response:

```json
{
  "updated": {
    "rate": 9
  }
}
```

___

### Create venv:

    make venv

### Run tests:

    make test

### Run linters:

    make lint

### Run formatters:

    make format

### Run app:

    make up

App data base in  **app/app.db**

# TODO

* Рефакторинг кода в соответствии с принципами SOLID
