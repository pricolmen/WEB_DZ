Django Questions & Answers Platform
Веб-приложение для вопросов и ответов с поддержкой тегов, лайков и рейтинговой системой.

Быстрый запуск через Docker
Предварительные требования
Установленный Docker

Установленный Docker Compose

Запуск проекта
Клонируйте репозиторий


git clone https://github.com/pricolmen/WEB_DZ
cd questions

Запустите проект одной командой

docker-compose up --build

Откройте в браузере
http://localhost:8000

Локальная установка (без Docker)

Предварительные требования
Python 3.11+

PostgreSQL 13+

pip

Установка
Клонируйте репозиторий

git clone https://github.com/pricolmen/WEB_DZ
cd questions

Создайте виртуальное окружение
python -m venv venv
source venv/bin/activate  # Linux/MacOS
# или
venv\Scripts\activate     # Windows

Установите зависимости
pip install -r requirements.txt

Настройте базу данных PostgreSQL

Способ A: Через командную строку
# Создайте базу данных
createdb -U postgres mydjango_db

Способ B: Через pgAdmin

Откройте pgAdmin

Создайте новую базу данных: mydjango_db

Создайте пользователя: django_user с паролем password123

Настройте подключение к БД (если нужно изменить настройки по умолчанию)

В файле settings.py можно изменить настройки подключения:

python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'mydjango_db',           # имя вашей БД
        'USER': 'django_user',           # пользователь
        'PASSWORD': 'password123',       # пароль
        'HOST': 'localhost',             # хост
        'PORT': '5432',                  # порт
    }
}
Примените миграции
python manage.py migrate
Заполните базу тестовыми данными

python manage.py fill_db 500

Запустите сервер
python manage.py runserver

Откройте в браузере
http://localhost:8000
