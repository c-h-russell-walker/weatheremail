# WeatherEmail

## What follows is potentially a living document on setting up this app. TODOs will be added.

## Pre-reqs - be sure to have 'virtualenv' available form the command line:
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

## To run:
In virtualenv (venv) cd into app:
`cd weatheremail`
Then run:
`./manage.py runserver_plus`
(To be in virtualenv run `source venv/bin/activate` in the repo dir.)


## To run celery task(s):

Pre-Req. - RabbitMQ installed (I used: `brew install rabbitmq` - for Mac)

Run rabbitmq (in terminal):
`brew services start rabbitmq`

Inside VM (venv):
`celery -A weatheremail worker -l info`

