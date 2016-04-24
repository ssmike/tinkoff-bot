# Digger Bot Tinkoff Bank

## Как запускать?
* `docker-compose build` билдит контейнер
* `docker-compose run bot python manage.py create index` создает индекс `index`
* `docker-compose run bot python manage.py delete index` удаляет индекс `index`
* `docker-compose run bot python manage.py add index filename` добавляет в индекс `index` содержимое
файла `filename` в нашем формате.
* `docker-compose up` запускает бота
