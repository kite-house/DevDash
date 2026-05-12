<div align="center">
  <h1>🏆 IT-Cup</h1>
  <p><strong>Сайт для проведения IT-кубка: регистрация команд, динамическое скрытие кейсов, чат поддержки, статистика</strong></p>
  <p>
    <img src="https://img.shields.io/badge/Python-3.12.10-blue?style=flat-square&logo=python" alt="Python 3.12">
    <img src="https://img.shields.io/badge/Django-4.2-092E20?style=flat-square&logo=django" alt="Django">
    <img src="https://img.shields.io/badge/PostgreSQL-17.4-336791?style=flat-square&logo=postgresql" alt="PostgreSQL">
    <img src="https://img.shields.io/badge/Redis-7- DC382D?style=flat-square&logo=redis" alt="Redis">
    <img src="https://img.shields.io/badge/Docker-✓-2496ED?style=flat-square&logo=docker" alt="Docker">
    <img src="https://img.shields.io/badge/Bootstrap-5.3-7952B3?style=flat-square&logo=bootstrap" alt="Bootstrap 5">
    <img src="https://img.shields.io/badge/license-GPLv3-green?style=flat-square" alt="License GPLv3">
    <a href="https://github.com/kite-house/DevDash/actions/workflows/django-tests.yml">
      <img src="https://github.com/kite-house/DevDash/actions/workflows/django-tests.yml/badge.svg" alt="CI Status">
    </a>
  </p>
</div>

## ✨ О проекте

**IT-Cup** — это платформа для проведения хакатонов и IT-соревнований. Создана как замена сайтам на Тильде, где невозможно динамически управлять контентом. Реализована на Django с использованием PostgreSQL и Redis.

### Основные возможности:

- 🔐 **Секретная логика** — кейсы автоматически открываются за 2 дня до мероприятия (middleware)
- 👥 **Регистрация команд** — капитан создаёт команду, выбирает кейс (опционально)
- 📊 **Статистика турнира** — отображение активных и выбывших команд по контрольным точкам
- 💬 **Чат поддержки** — встроенный чат для общения команд с организаторами
- 📥 **Экспорт в Excel** — выгрузка списка участников из админ-панели
- ⚡ **Кеширование Redis** — ускорение загрузки страниц и хранение сессий
- 🐳 **Docker-first подход** — весь стек поднимается одной командой
- 🧪 **21 unit-тест** — полное покрытие моделей, views и бизнес-логики
- 🔄 **CI/CD** — автоматический прогон тестов через GitHub Actions

## 🛠 Стек технологий

| Компонент | Технология |
|-----------|------------|
| **Язык** | [Python 3.12](https://www.python.org/) |
| **Веб-фреймворк** | [Django 4.2](https://www.djangoproject.com/) |
| **База данных** | [PostgreSQL 17.4](https://www.postgresql.org/) |
| **Кеш и сессии** | [Redis 7](https://redis.io/) |
| **Формы** | [django-crispy-forms](https://django-crispy-forms.readthedocs.io/) + Bootstrap 5 |
| **Excel-экспорт** | [openpyxl](https://openpyxl.readthedocs.io/) |
| **Контейнеризация** | [Docker](https://www.docker.com/) + [Docker Compose](https://docs.docker.com/compose/) |
| **CI/CD** | [GitHub Actions](https://github.com/features/actions) |
| **Фронтенд** | HTML5, CSS3, [Bootstrap 5.3](https://getbootstrap.com/) |
| **Лицензия** | [GPL v3.0](https://www.gnu.org/licenses/gpl-3.0.html) |

## 🚀 Быстрый старт

### Предварительные требования

- Установленные [Docker](https://docs.docker.com/get-docker/) и [Docker Compose](https://docs.docker.com/compose/install/)

### Установка и запуск

1. **Клонируйте репозиторий**
   ```bash
   git clone https://github.com/твой-юзер/devdash.git
   cd devdash
   ```

2. **Настройте переменные окружения**

   Скопируйте файл с примером конфигурации:
   ```bash
   cp .env.example .env
   ```

   Минимально необходимые настройки:
   ```ini
   # Django
   SECRET_KEY = "change-me-in-production"
   DEBUG = True

   # PostgreSQL
   DB_NAME = "devdash"
   DB_USER = "postgres"
   DB_PASS = "postgres"
   DB_HOST = "postgres_db"
   DB_PORT = "5432"

   # Redis
   REDIS_HOST = "redis"
   REDIS_PORT = "6379"
   REDIS_DB = "0"
   ```

3. **Запустите все сервисы**
   ```bash
   docker-compose up -d --build
   ```

4. **Примените миграции и создайте администратора**
   ```bash
   docker-compose exec app python manage.py migrate
   docker-compose exec app python manage.py createsuperuser
   ```

5. **Проверьте работу**
   - Главная страница: http://localhost:8000
   - Админ-панель: http://localhost:8000/admin
   - Статистика: http://localhost:8000/statistics

## 📖 Использование

### 🏠 Главная страница

Отображает информацию о ближайшем мероприятии:
- 📅 Дата проведения
- 📍 Место проведения
- 💰 Призовой фонд
- 🔒 Статус доступности кейсов

### 👥 Регистрация команды

1. Войдите в систему (или создайте аккаунт через админ-панель)
2. Перейдите на страницу регистрации команды
3. Введите название команды и ФИО капитана
4. При желании выберите кейс (если кейсы уже открыты)
5. Нажмите «Зарегистрировать команду»

### 📋 Кейсы

Кейсы автоматически становятся доступными за 2 дня до мероприятия. До этого момента:
- Поле выбора кейса скрыто при регистрации
- Страница `/cases/` недоступна и перенаправляет на главную

Логика реализована через context processor — проверка `cases_visible_date` из модели `Event`.

### 💬 Чат поддержки

1. Зайдите в карточку своей команды
2. Нажмите «💬 Чат поддержки»
3. Отправляйте сообщения — администраторы увидят их в админ-панели
4. Ответы администратора выделяются цветом и помечаются бейджем «Поддержка»

### 📊 Статистика

На странице `/statistics/` отображается:
- Список всех команд с капитанами и кейсами
- Статус: «В игре» или «Выбыла»
- Прогресс-бары по контрольным точкам (пройдено / всего)

### 📥 Экспорт в Excel

1. Зайдите в админ-панель → Teams
2. Выберите нужные команды галочками
3. В выпадающем списке действий выберите «📥 Выгрузить выбранные команды в Excel»
4. Файл `.xlsx` скачается автоматически

## 🧩 Архитектура

### Модели данных

```
Event ───────────── мероприятие (дата, место, призовой фонд, дата открытия кейсов)
  ├── Case ──────── кейсы (название, описание)
  ├── Team ──────── команды (название, капитан, кейс, статус активности)
  │     └── ChatMessage ─── сообщения чата поддержки
  └── CheckPoint ── контрольные точки (название, порядок)
        └── TeamCheckPointStatus ── статусы прохождения КП командами
```

### Секретная логика

```
context_processors.py
    └── cases_visibility(request)
        └── Проверяет: сейчас >= Event.cases_visible_date?
            ├── Да → can_view_cases = True (кейсы видны)
            └── Нет → can_view_cases = False (кейсы скрыты)
```

### Кеширование

```
views.py
    ├── home()       → кеш 5 минут
    ├── case_list()  → кеш 15 минут
    └── statistics() → кеш 1 минута

admin.py
    └── При сохранении/удалении → cache.delete()
```

## 🧪 Тестирование

Проект содержит 21 unit-тест, покрывающий:

| Тест-класс | Что проверяет |
|------------|---------------|
| `EventModelTest` | Создание Event, verbose_name |
| `CaseModelTest` | Создание Case, связь с Event |
| `TeamModelTest` | Создание Team, уникальность имени |
| `CheckPointModelTest` | Создание CheckPoint, ordering |
| `ChatMessageModelTest` | Сообщения пользователя и админа |
| `HomeViewTest` | Главная с ивентом и без |
| `CaseListViewTest` | Секретная логика: скрытие/открытие кейсов |
| `TeamRegistrationTest` | Регистрация, закрытая регистрация, неавторизованный доступ |
| `TeamChatTest` | Доступ к чату, отправка сообщений |
| `StatisticsViewTest` | Активные/выбывшие команды |
| `CaseVisibilityLogicTest` | Проверка логики дат |

### Запуск тестов

```bash
# Все тесты
docker-compose exec app python manage.py test core

# С подробным выводом
docker-compose exec app python manage.py test core -v 2

# Конкретный класс
docker-compose exec app python manage.py test core.tests.CaseListViewTest
```

## 📁 Структура проекта

```
devdash/
├── .github/
│   └── workflows/
│       └── django-tests.yml        # GitHub Actions CI
├── accounts/                        # Приложение аутентификации
│   ├── urls.py                      # Маршруты login/logout
│   └── __init__.py
├── core/                            # Основное приложение
│   ├── models.py                    # Модели: Event, Case, Team, CheckPoint, ChatMessage
│   ├── views.py                     # Представления: home, case_list, register_team, etc.
│   ├── urls.py                      # Маршруты: /, /cases/, /team/register/, /statistics/
│   ├── admin.py                     # Админ-панель + экспорт в Excel
│   ├── forms.py                     # Форма регистрации команды, форма чата
│   ├── context_processors.py        # Секретная логика видимости кейсов
│   ├── tests.py                     # 21 unit-тест
│   └── __init__.py
├── devdash/                         # Конфигурация проекта
│   ├── settings.py                  # Настройки Django
│   ├── urls.py                      # Корневые URL-маршруты
│   ├── wsgi.py
│   └── asgi.py
├── templates/                       # HTML-шаблоны
│   ├── base.html                    # Базовый шаблон с навигацией
│   ├── accounts/
│   │   └── login.html               # Страница входа
│   └── core/
│       ├── home.html                # Главная страница
│       ├── case_list.html           # Список кейсов
│       ├── register_team.html       # Регистрация команды
│       ├── team_detail.html         # Карточка команды
│       ├── team_chat.html           # Чат поддержки
│       └── statistics.html          # Статистика турнира
├── static/                          # Статические файлы
├── media/                           # Загружаемые файлы
├── .env.example                     # Пример переменных окружения
├── .gitignore
├── .dockerignore
├── docker-compose.yml               # Docker Compose (PostgreSQL + Redis + App)
├── dockerfile
├── manage.py
├── requirements.txt                 # Зависимости Python
└── LICENSE                          # GNU GPL v3.0
```

## 🔄 CI/CD

При каждом пуше в `main` или создании Pull Request-а GitHub Actions:

1. Запускает контейнер PostgreSQL
2. Устанавливает Python и зависимости
3. Применяет миграции
4. Запускает тесты

Статус сборки отображается бейджем вверху README.

## 🤝 Вклад в проект

Будем рады вашим идеям и улучшениям! Чтобы внести вклад:

1. Форкните репозиторий
2. Создайте ветку для фичи (`git checkout -b feature/amazing-feature`)
3. Закоммитьте изменения (`git commit -m '✨ Add some amazing feature'`)
4. Запушьте ветку (`git push origin feature/amazing-feature`)
5. Откройте Pull Request

## 📄 Лицензия

Проект распространяется под лицензией GNU General Public License v3.0. Подробности в файле [LICENSE](LICENSE).
