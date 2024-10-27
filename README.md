1. Создание виртуального окружения в папке, где будет размещен проект (python -m venv venv)
2. Запуск виртуального окружения (.\venv\Scripts\activate)
3. Клонирование репозитория (https://github.com/afkproger/hhelper)
4. Установка зависимостей (pip install django==4.2.1), (pip install djangorestframework), (pip install django-cors-headers), (pip install psycopg2)
5. Так как данные размещены в PostgreSQL необходимо дополнительно установить его
6. Создаем базу данных с названием hhelper
7. В рабочей директории (hhelper) открывается файл settings.py
8. DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'hhelper',  # имя базы данных
        'USER': <Ваше имя пользователя>,  # имя пользователя 
        'PASSWORD': <Ваш пароль>,  # пароль пользователя
        'HOST': 'localhost',  # адрес хоста, обычно 'localhost'
        'PORT': '5432',  # порт, по умолчанию '5432'
    }
}
9. Сохранить изменения
10. Переход в рабочую директорию
11. Переход в рабочую консоль (python manage.py shell), (из example_data запустить load_data)
12. Установка миграций (python manage.py makemigrations), (python manage.py migrate)
13. Запуск сервера (python manage.py runserver)
