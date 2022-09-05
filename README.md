# Продуктовый помощник Foodgram (ДОПОЛНИТЬ)
![example workflow](https://github.com/MrGorkiy/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)

Проект доступен по адресу ...

## Описание проекта Foodgram
«Продуктовый помощник»: приложение-сайт, на котором пользователи будут публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Сервис «Список покупок» позволит пользователям создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

## Запуск с использованием CI/CD

Установить docker, docker-compose на сервере ВМ Yandex.Cloud:
```bash
ssh username@ip
sudo apt update && sudo apt upgrade -y && sudo apt install curl -y
sudo curl -fsSL https://get.docker.com -o get-docker.sh && sudo sh get-docker.sh && sudo rm get-docker.sh
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```
- Перенести файлы docker-compose.yml и default.conf на сервер.

```bash
scp docker-compose.yml username@server_ip:/home/<username>/
```
```bash
scp default.conf <username>@<server_ip>:/home/<username>/
```

- Заполните Secrets Actions по шаблону наполнения env переменных в GitHub Actions
    ```
    Наименование:        Содержание:
    DB_ENGINE            django.db.backends.postgresql # указываем, что работаем с postgresql
    DB_NAME              postgres # имя базы данных
    POSTGRES_USER        postgres # логин для подключения к базе данных
    POSTGRES_PASSWORD    postgres # пароль для подключения к БД (установите свой)
    DB_HOST              db # название сервиса (контейнера)
    DB_PORT              5432 # порт для подключения к БД 
    HOST                 194.212.231.123 # ip сервера
    USER                 MrGorkiy # UserName для подключению к серверу
    SSH_KEY              # Приватный ключ доступа для подключению к серверу `cat ~/.ssh/id_rsa`
    PASSPHRASE           # Серкретный ключ\фраза, если ваш ssh-ключ защищён фразой-паролем
    TELEGRAM_TO          # id чата пользователя или чата куда бот будет отправлять результат успешного выполнения
    TELEGRAM_TOKEN       # Токен бота ТГ для отправки уведомления
    DOCKER_USERNAME      # Имя пользователя Docker для публикации образов
    DOCKER_PASSWORD      # Пароль пользоывателя Docker
    ```

Скопировать на сервер настройки docker-compose.yml, default.conf из папки infra.

## Запуск проекта через Docker
- В папке infra выполнить команду, что бы собрать контейнер:
```bash
sudo docker-compose up -d
```

Для доступа к контейнеру выполните следующие команды:

```bash
docker-compose exec backend python manage.py makemigrations
```
```bash
docker-compose exec backend python manage.py migrate --noinput
```
```bash
docker-compose exec backend python manage.py createsuperuser
```
```bash
docker-compose exec backend python manage.py collectstatic --no-input
```

Дополнительно можно наполнить DB ингредиентами и тэгами:

```bash
sudo docker-compose exec backend python manage.py load_tags
```
```bash
sudo docker-compose exec backend python manage.py load_ingrs
```

## Запуск проекта в dev-режиме

- Установить и активировать виртуальное окружение

```bash
source /venv/bin/activated
```

- Установить зависимости из файла requirements.txt

```bash
python -m pip install --upgrade pip
```
```bash
pip install -r requirements.txt
```

- Выполнить миграции:

```bash
python manage.py migrate
```

- В папке с файлом manage.py выполнить команду:
```bash
python manage.py runserver
```

### Документация к API доступна после запуска
```url
http://127.0.0.1/api/docs/
```

Автор: [Брысин Максим](https://github.com/MrGorkiy)