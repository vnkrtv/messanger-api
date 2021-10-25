# Messenger API

## Основные детали реализации  
- Конфигурирование:
    - Настройки приложения хранятся в messenger/settings.py и задаются через переменные окружения  
    - Примеры переменных окружения хранятся в deploy/.env.* файлах  
- Запуск:
    - Приложения разворачивается с использованием docker-compose  
    - Запуск производится с помощью команды messenger-api, которая запускает gunicorn с параметрами, заданными в настройках  
- Структура:
    - Проект разбит на логические приложения, заданные в настройках, при этом:
    - Каждое приложение можно "отключить", просто убрав его из списка Config.apps
    - Каждое приложение либо реализует определенную логику (ручки), либо каким-то образом влияет на обработку запросов (middlewares)  
- Кеш:
    - Реализован с помощью библиотеки aiohttp-cache
    - Поддерживается 2 бэкенда для кеша - память и redis 
    - Выбор кеша происходит с помощью задания определенных переменных окружения   
    - Обеспечено кеширование запроса на получения сообщений, а также инвалидация кеша при добавлении нового сообщения в чат   
- Троттлинг
    - Учитывая специфику java тестов (запуск контейнера с приложением), вынести его на сторону nginx не представлялось возможным, поэтому был реализован самописный велосипед в лице throttling_app  
    - При этом с поомщью переменной окружения NGINX_THROTTLING можно отключить троттлинг на стороне приложения и оставить это nginx  
- Авторизация:
    - Доступ пользователя к ресурсам, требующих авторизацию, определяется на соновании наличия Authorization хедера в запросе   
    - Формат токена/хедера задается в настройках приложения - Config.Auth
    - Активные сессии пользователей хранятся в кеше и удаляются спустя заданное время  
    - session_id "протухает" за время, заданное в Config.Auth.token_lifetime  
    - Все сессии пользователей записываются в БД
- CI:
    - При каждом пуше:
        - Проверяется код стайл (flake8/pylint)
        - Запускаются тесты 
        - Проверяется корректная сборка docker-compose
- Поиск по сообщениям (ДЗ5):
    -  Реализована следующая схема:
        - При успешном запросе на поиск сообщений, создается задание, помещающееся в очередь задач RabbitMQ 
        - Обработкой задач занимается отдельный микросервис consumer, представляющий собой идентичный контейнер с приложением - отличаются только entrypoint'ы  
        - При обработке задачи ее результат помещается консьюмером в быстрое хранилище (в качестве него был выбран redis), из которого потом приложение и достает нужные сообщения  
        - При каждом запросе на получение сообщений из таска redis удаляет уже полученные сообщения 
        - Поиск сообщений происходит с помощью gist индекса по полю text таблицы с сообщениями с использованием встроенных в PostgreSQL средств FTS (tsvectors)

## Документация  

Указана в спеке OpenAPI - swagger.yml

Большинство команд, необходимых для работы с проектом, реализовано в виде make команд в Makefile:  
- `make help` - доступные команды 


## Запуск  
- Prod
    - `make run-prod`
- Dev
    - `make venv`
    - `make run-dev`  
- Линтера кода  
    - `make lint`  
- Тестов  
    - `make test` - запустит тесты
    - `make tests-html-coverage-report` - запустит тесты и откроет в браузере отчет с покрытием кода тестами 

## Регистрация и авторизация пользователей  

- Регистрация:  
```sh
$ curl -XPOST 0.0.0.0:8080/v1/auth/register -H 'Content-Type: application/json' -d '{"user_name": "some user", "password": "pass"}' -w '%{http_code}'
201
``` 
- Получения session_id (в рамках приложения это тип токена доступа - возможно задать произвольный тип в секции Config.Auth.token_type в файле messenfer/settings.py):  
```sh
$ curl -XPOST 0.0.0.0:8080/v1/auth/login -H 'Content-Type: application/json' -d '{"user_name": "some user", "password": "pass"}'
{"session_id": "5d3e9ce435ba11eca6b50242ac1f0006"}
```
- Для запросов к ручкам, требующих авторизацию, требуется указывать session_id в Authorization хедере:  
```sh
$ curl -X<method> 0.0.0.0:8080/<uri> -H 'Authorization: session_id 5d3e9ce435ba11eca6b50242ac1f0006' ...
```  
- Для прекращения пользовательской сессии достаточно выполнить logout запрос: 
```sh
$ curl -XPOST 0.0.0.0:8080/v1/auth/logout -H 'Authorization: session_id 5d3e9ce435ba11eca6b50242ac1f0006' -w '%{http_code}'  
200

```  

# Домашнее задание к 7 лекции

## TL;DR
Написать ansible playbook, который:
* Запустит контейнер с базой данных
* Запустит контейнер с приложением

### Выполнение
1. Сделайте ветку `ansible` в репозитории с вашим проектом
2. В ветке `ansible` в корне нужно создать 2 файла
* `.gitlab-ci.yml` следующего содержания:
```yml
include:
  - project: 'school/2021-09/backend/python/homeworks/7' # или 'school/2021-09/backend/java/homeworks/7' 
    ref: master
    file: '.gitlab-ci.yml'
    
variables:
  APP_PORT: 8080 # порт, который слушает приложение при запуске
```
* `playbook.yml`, содержащий playbook для запуска контейнеров
3. Создайте MR ветки `ansible` в `master`
4. Проверка MR должна быть зеленой

## Нюансы
* В корне должен лежать `Dockerfile`, сборка контейнера будет выполняться командой `docker build -t $CI_REGISTRY_IMAGE .`
* Для указания образа внутри `playbook.yml` используйте `{{ lookup('env', 'CI_REGISTRY_IMAGE') }}`, аналогично для проброса портов можно использовать переменную окружения APP_PORT

## Как разрабатывать локально
1. Устанавливаем зависимости: `pip install ansible==4.7.0 docker==5.0.2 docker-compose==1.29.2`
2. Пишем `playbook.yml`
3. Запускаем `ansible-playbook`. Т.к. у нас нет похода по ssh, применять мы будем локально: `ansible-playbook -c local -i localhost playbook.yml`

## Варианты реализации
1. Описать явно в `playbook`'e `docker_network`, 2 `docker_container`, пробросить порты, задать обоим контейнерам общую сеть
2. Написать `docker-compose.yml` и применить его через `docker_compose` в `playbook`'e

## Подсказки
1. https://github.com/grigory51/shbr-devops/tree/master/presentation/03-run-ansible
2. https://docs.ansible.com/ansible/latest/collections/community/docker/docker_container_module.html
3. https://docs.ansible.com/ansible/latest/collections/community/docker/docker_network_module.html
4. https://docs.ansible.com/ansible/latest/collections/community/docker/docker_compose_module.html
5. https://docs.ansible.com/ansible/latest/collections/ansible/builtin/wait_for_module.html
