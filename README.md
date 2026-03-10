## Запуск проекта в Docker с docker-compose

### 1. Предварительные требования

- Установлены **Docker** и **Docker Compose** (современная команда `docker compose`).
- В корне проекта находится файл `requirements.txt` с зависимостями Python (у вас уже есть).

Из ключевых библиотек для работы проекта в контейнерах должны быть установлены (в `requirements.txt`):

- **Django**
- **psycopg2** (или `psycopg2-binary`) — драйвер PostgreSQL
- **celery**
- **redis**
- **python-dotenv**
- **djangorestframework**
- **django-filter**
- **drf-yasg**
- **djangorestframework-simplejwt**

### 2. Подготовка `.env`

1. Скопируйте пример:

```bash
cp .env.example .env
```

2. Отредактируйте `.env` для работы внутри Docker-сети. Минимальный набор переменных:

```env
SECRET_KEY=your_django_secret_key

NAME=djangodb           # имя БД внутри контейнера Postgres
USER=djangouser         # пользователь БД
PASSWORD=djangopass     # пароль БД
HOST=db                 # имя сервиса базы данных из docker-compose
PORT=5432               # порт Postgres внутри контейнера

STRIPE_PUBLIC_KEY=your_stripe_public_key
STRIPE_SECRET_KEY=your_stripe_secret_key

CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/1
CELERY_TIMEZONE=Europe/Moscow
CELERY_TASK_TRACK_STARTED=True
CELERY_TASK_TIME_LIMIT=1800
```

> **Важно**: значения `HOST=db`, `CELERY_BROKER_URL=redis://redis:6379/0` и `CELERY_RESULT_BACKEND=redis://redis:6379/1` должны совпадать с названиями сервисов `db` и `redis` в `docker-compose.yml`.

### 3. Структура docker-compose

Файл `docker-compose.yml` в корне проекта описывает следующие сервисы:

- **db** — PostgreSQL
- **redis** — Redis для брокера/бэкенда Celery
- **web** — Django-приложение (бэкенд)
- **celery** — Celery worker
- **celery_beat** — Celery Beat для периодических задач

Все сервисы используют переменные из `.env` (через `env_file: .env` и подстановку `${VAR}`).

### 4. Запуск проекта

Из корня проекта выполните:

```bash
docker compose up --build
```

При первом запуске:

- Соберётся образ для сервиса `web`.
- Поднимутся контейнеры: `db`, `redis`, `web`, `celery`, `celery_beat`.
- В контейнере `web` автоматически выполняется команда:
  - `python manage.py migrate`
  - затем запуск сервера: `python manage.py runserver 0.0.0.0:8000`

Если хотите запускать в фоне:

```bash
docker compose up --build -d
```

### 5. Создание суперпользователя

После первого запуска (когда миграции выполнены) создайте суперпользователя:

```bash
docker compose exec web python manage.py createsuperuser
```

### 6. Проверка работоспособности проекта

1. Откройте в браузере:
   - API / сайт: `http://localhost:8000/`
   - Документация Swagger (если настроено): например, `http://localhost:8000/swagger/`
2. Убедитесь, что:
   - API отвечает без ошибок.
   - Авторизация/регистрация работают (если настроены).
3. Проверьте Celery и Celery Beat:
   - Просмотрите логи контейнеров:

```bash
docker compose logs celery
docker compose logs celery_beat
```

   - Убедитесь, что:
     - Celery worker подключён к Redis.
     - Celery Beat успешно планирует задачи (в том числе `deactivate_inactive_users` и отправку писем при обновлении курса).

### 7. Остановка и удаление контейнеров

Остановить контейнеры (без удаления данных БД):

```bash
docker compose down
```

Остановить и удалить контейнеры вместе с томами (включая данные Postgres):

```bash
docker compose down -v
```

### 8. Краткое резюме команд

- **Запуск (foreground)**:

```bash
docker compose up --build
```

- **Запуск (background)**:

```bash
docker compose up --build -d
```

- **Создание суперпользователя**:

```bash
docker compose exec web python manage.py createsuperuser
```

- **Просмотр логов Celery / Beat**:

```bash
docker compose logs celery
docker compose logs celery_beat
```

- **Остановка**:

```bash
docker compose down
```

