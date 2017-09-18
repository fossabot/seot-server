## Requirements
[![FOSSA Status](https://app.fossa.io/api/projects/git%2Bgithub.com%2Fshimojo-lab%2Fseot-server.svg?type=shield)](https://app.fossa.io/projects/git%2Bgithub.com%2Fshimojo-lab%2Fseot-server?ref=badge_shield)

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


## License
[![FOSSA Status](https://app.fossa.io/api/projects/git%2Bgithub.com%2Fshimojo-lab%2Fseot-server.svg?type=large)](https://app.fossa.io/projects/git%2Bgithub.com%2Fshimojo-lab%2Fseot-server?ref=badge_large)