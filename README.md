# WeatherEmail

For notes on some technical ideas about sacling this app please, [see this doc](./doc/notes.md).

## What follows is a living document on setting up this app.

## NOTE about emails:
I've set up an app using my personal email and obviously have not committed the password to it:

`EMAIL_HOST_PASSWORD = 'YOU_WISH_YOU_KNEW'`

## Pre-reqs - be sure to have 'virtualenv' available from the command line:
`virtualenv --version`
If not install using:
`pip install virtualenv`

1. Clone repo.
2. CD into repo directory.
3. Run (to note the 'venv' virtualenv name is ignored in .gitignore):
```
virtualenv venv
source venv/bin/activate
```

## To install requirements:
(inside VM)
`pip install -r requirements.txt` OR `pip install -r requirements_dev.txt`


## Before running the app do the needed DB migrations:
In virtualenv (venv) cd into app:
`cd weatheremail`
Then run:
`./manage.py migrate`

Also you can create a superuser (not currently used for this app though):
`./manage.py createsuperuser`
You can use this to log in to:
http://127.0.0.1:8000/admin/


## To run unit tests:
In virtualenv (venv) cd into app:
`cd weatheremail`
Then run:
`./manage.py test`


## To run:
In virtualenv (venv) cd into app:
`cd weatheremail`
Then run:
`./manage.py runserver_plus`
(To be in virtualenv run `source venv/bin/activate` in the repo dir.)


## To run celery task(s) - We'll be running celery as well as celery beat (each in their own terminal tab/window):

Pre-Req. - RabbitMQ installed (I used: `brew install rabbitmq` - for Mac)

Run rabbitmq (in terminal):
`brew services start rabbitmq`

Run each of these inside the VM (venv) in its own terminal tab/window:
(cd into app for each command)
`cd weatheremail`
`celery -A weatheremail worker -l info`

`cd weatheremail`
`celery -A weatheremail beat`

#### * To note, the periodic task that queues up the email tasks per each user is set currently to run at 10am
