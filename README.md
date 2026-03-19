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

## CI/CD (GitHub Actions): тесты на каждый push + авто-деплой на сервер

В репозитории добавлен workflow `.github/workflows/ci-cd.yml` со следующей логикой:

- **Tests**: запускается **на каждый `push`** и прогоняет `python manage.py test` с PostgreSQL и Redis как сервисами GitHub Actions.
- **Deploy**: запускается **только после успешных тестов** и **только при `push` в ветку `develop`**. Деплой выполняется по SSH: код синхронизируется на сервер (rsync), затем выполняется `docker compose up -d --build` и миграции.

### Настройка удалённого сервера (Ubuntu/Debian)

Ниже приведён базовый вариант деплоя через Docker Compose (как и локальный запуск).

1. Установите Docker и Docker Compose на сервере.

2. Установите `rsync` (он нужен для синхронизации кода с GitHub Actions):

```bash
sudo apt-get update
sudo apt-get install -y rsync
```

3. Создайте пользователя для деплоя (пример: `deploy`) и добавьте его в группу `docker`:

```bash
sudo adduser deploy
sudo usermod -aG docker deploy
```

4. Подготовьте папку под приложение (пример: `/opt/djangorestproject`):

```bash
sudo mkdir -p /opt/djangorestproject
sudo chown -R deploy:deploy /opt/djangorestproject
```

5. Настройте SSH доступ.

- **Рекомендуется**: отключить парольный вход и использовать ключи.
- В GitHub Secrets будет храниться **приватный ключ**, а на сервере должен быть соответствующий **публичный ключ** в `~deploy/.ssh/authorized_keys`.

6. Создайте файл окружения на сервере: `/opt/djangorestproject/.env`

Важно:
- Workflow **не копирует** локальный `.env` (он исключён из синхронизации).
- Переменные из `.env` должны соответствовать вашему `docker-compose.yml`.
- Для compose-сети в `.env` используйте `HOST=db`, а для Celery/Redis — `redis://redis:6379/...`.

Пример (адаптируйте под себя):

```env
SECRET_KEY=your_django_secret_key

NAME=djangodb
USER=djangouser
PASSWORD=djangopass
HOST=db
PORT=5432

STRIPE_PUBLIC_KEY=your_stripe_public_key
STRIPE_SECRET_KEY=your_stripe_secret_key

CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/1
CELERY_TIMEZONE=Europe/Moscow
CELERY_TASK_TRACK_STARTED=True
CELERY_TASK_TIME_LIMIT=1800
```

### Настройка GitHub Secrets

Откройте репозиторий → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**.

Нужно добавить:

- **`SSH_HOST`**: IP/домен сервера (например, `203.0.113.10`)
- **`SSH_PORT`**: SSH порт (обычно `22`)
- **`SSH_USER`**: пользователь на сервере (например, `deploy`)
- **`SSH_PRIVATE_KEY`**: приватный ключ (OpenSSH), который имеет доступ к серверу
- **`DEPLOY_PATH`**: путь на сервере, куда синхронизируется проект (например, `/opt/djangorestproject`)

### Как запустить workflow и деплой

- **Автоматически (тесты)**: просто сделайте `git push` в любую ветку — job **Tests** запустится сам.
- **Автоматически (деплой)**: сделайте `git push` в ветку `develop` — после успешных тестов запустится job **Deploy**.
- **Вручную**: GitHub → вкладка **Actions** → workflow **CI/CD** → **Run workflow**.

### Как проверить, что деплой прошёл

На сервере (под пользователем с доступом к Docker):

```bash
cd /opt/djangorestproject
docker compose ps
docker compose logs -n 200 web
docker compose logs -n 200 celery
docker compose logs -n 200 celery_beat
```

