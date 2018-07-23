# Blogly Api

a simple mini graphql blog api built with flask.

## Setup local development

```bash
git clone https://github.com/marvinkome/blogly-api
cd blogly-api

# setup virtual env
virtualenv venv
source venv/bin/activate # or ./venv/bin/activate in windows

# install modules
pip install -r requirements.txt

# setup db
python manage.py db init
python manage.py db migrate
python manage.py db upgrade

# start the server
python manage.py runserver
```

## Accompanied Project

This project is part of the ReactPress full-stack project.
To see the frontend repo, check [Blogly](https://github.com/marvinkome/blogly)
