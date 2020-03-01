
DB

local
set -x DATABASE_URL postgresql://localhost/habiter_db

heroku pg:pull postgresql-perpendicular-23539 habiter_db
heroku pg:push habiter_db postgresql-perpendicular-23539

https://devcenter.heroku.com/articles/heroku-postgresql

CREATE TABLE leetcode_problems(
   id serial PRIMARY KEY,
   link VARCHAR (500) NOT NULL,
   active BOOLEAN DEFAULT TRUE
)


CREATE TABLE leetcode_teams(
   id serial PRIMARY KEY,
   link VARCHAR (100) NOT NULL,
   team_name VARCHAR(100),
   timezone VARCHAR(30) NOT NULL,
   created_on TIMESTAMP NOT NULL DEFAULT NOW(),
   sent INTEGER DEFAULT 0,
   claimed INTEGER DEFAULT 0
);

>>> habiter_db=# \dt
             List of relations
 Schema |     Name     | Type  |   Owner
--------+--------------+-------+-----------
 public | leetcode_team_invites | table | lessandro
(1 row)

UPDATE leetcode_team_invites SET sent = FALSE;


====
habiter.app

some eraly stage commits
da44cf263b5e087f1fdff4f306a716a1ff0bc593
638622aecffbd7b60460c5dccdd056ed715c30d0
-----
# Python: Getting Started

A barebones Django app, which can easily be deployed to Heroku.

This application supports the [Getting Started with Python on Heroku](https://devcenter.heroku.com/articles/getting-started-with-python) article - check it out.

## Running Locally

Make sure you have Python 3.7 [installed locally](http://install.python-guide.org). To push to Heroku, you'll need to install the [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli), as well as [Postgres](https://devcenter.heroku.com/articles/heroku-postgresql#local-setup).

```sh
$ git clone https://github.com/heroku/python-getting-started.git
$ cd python-getting-started

$ python3 -m venv getting-started
$ pip install -r requirements.txt

$ createdb python_getting_started

$ python manage.py migrate
$ python manage.py collectstatic

$ heroku local
```

Your app should now be running on [localhost:5000](http://localhost:5000/).

## Deploying to Heroku

```sh
$ heroku create
$ git push heroku master

$ heroku run python manage.py migrate
$ heroku open
```
or

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

## Documentation

For more information about using Python on Heroku, see these Dev Center articles:

- [Python on Heroku](https://devcenter.heroku.com/categories/python)
