## Requirements
- Python 3.5.2
- (Optional) virtualenv
- (Optional) direnv (2.5.0 or later)
- (Optional) pythonz

## Initial Setup

```
$ pip install -r requirements.txt
$ brew install rabbitmq
$ brew services start rabbitmq
$ python manage.py migrate
```

## Run Server

```
$ celery -A seot_server worker -B
$ python manage.py runserver
```

## Deploying to Dokku

```
$ sudo dokku plugin:install https://github.com/dokku/dokku-rabbitmq.git rabbitmq
$ sudo dokku plugin:install https://github.com/dokku/dokku-mysql.git mysql
$ dokku apps:create seot
$ dokku rabbitmq:create seot
$ dokku mysql:create seot
$ dokku rabbitmq:link seot
$ dokku mysql:link seot
```
