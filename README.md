# yatube

### Описание проекта:
Учебный проект, соц. сеть дневников. Разработан по классической MVT архитектуре. Базируется
на фреймворке Django. Используется пагинация постов и кэширование. Регистрация реализована с верификацией данных, 
сменой и восстановлением пароля через почту. Написаны тесты, проверяющие работу сервиса.

### Установка и запуск проекта:

Клонировать репозиторий и перейти в него в командной строке (используем ssh):

```
git clone git@github.com:trdMichaelM/yatube.git
```

```
cd yatube
```

Файл .env.example переименовываем в .env и прописываем в нем SECRET_KEY

```
mv .env.example .env
nano .env
```

Создать и активировать виртуальное окружение:

```
python3 -m venv venv
```

```
source venv/bin/activate (for Linux)
```

Обновить pip до последней версии:
```
python3 -m pip install --upgrade pip
```

Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```

Дополнительно установить модули django-debug-toolbar и dotenv:

```
pip install django-debug-toolbar python-dotenv
```

Выполнить миграции:

```
python3 manage.py migrate
```

Запустить проект:

```
python3 manage.py runserver
```

### Используется:

```
Python 3.9 Django 2.2
```
