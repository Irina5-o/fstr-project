# FSTR API — REST-сервис для добавления перевалов

## Текущий статус
**Приложение успешно развернуто и работает на Yandex Cloud**

**Проверенные эндпоинты:**
- Swagger UI: https://bbacg4nrhlert7e578rs.containers.yandexcloud.net/swagger/ 
- Admin Panel: https://bbacg4nrhlert7e578rs.containers.yandexcloud.net/admin/  
- API Endpoints: https://bbacg4nrhlert7e578rs.containers.yandexcloud.net/api/submitData/ 

## Описание проекта
REST API для приёма и хранения информации о перевалах в рамках проекта ФСТР (Федерация спортивного туризма России).

Сервис предоставляет возможность:
- Отправлять информацию о перевале (POST)
- Получать список перевалов по email пользователя (GET)
- Получать подробную информацию о перевале по его ID (GET)
- Обновлять данные перевала, если его статус — "new" (PATCH)

Документация автоматически доступна через Swagger и ReDoc.

## Используемые технологии
- Python 3.11
- Django 5.2
- Django REST Framework
- PostgreSQL — база данных
- psycopg2-binary — драйвер PostgreSQL
- drf-yasg — автогенерация Swagger / ReDoc
- python-dotenv — хранение конфиденциальных данных в .env
- Docker & Docker Compose — контейнеризация
- GitHub Actions — CI/CD с деплоем на Yandex Cloud Serverless Containers

## Структура проекта
```
fstr-project/
├── fstr/                          # Django проект
│   ├── fstr/                      # Настройки проекта
│   │   ├── settings.py            # Настройки с подключением .env и автоматической конфигурацией для тестов
│   │   ├── urls.py                # Главные маршруты проекта
│   │   └── wsgi.py
│   ├── pereval/                   # Приложение перевалов
│   │   ├── models.py              # Модели пользователя, перевала, координат и изображений
│   │   ├── serializers.py         # Сериализаторы для POST/GET/PATCH
│   │   ├── views.py               # Реализация логики API
│   │   ├── urls.py                # Маршруты приложения
│   │   ├── tests.py               # Тесты API (24 теста)
│   │   └── admin.py               # Админ-панель
│   ├── manage.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── docker-compose.yml
├── .github/workflows/             # GitHub Actions для CI/CD
└── README.md
```

## Установка и запуск проекта

### Локальная разработка

1. Клонировать репозиторий:
```bash
git clone https://github.com/Irina5-o/fstr-project.git
cd fstr-project
```

2. Перейдите в папку проекта и создайте виртуальное окружение:
```bash
cd fstr
python -m venv venv
source venv/bin/activate  # для Linux/macOS
venv\Scripts\activate     # для Windows
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

4. Создайте файл `.env` и заполните его:
```bash
# Для разработки
SECRET_KEY=your-secret-key-here
DEBUG=True
FSTR_DB_NAME=fstr_db
FSTR_DB_LOGIN=postgres
FSTR_DB_PASS=your-password
FSTR_DB_HOST=localhost
FSTR_DB_PORT=5432
ALLOWED_HOSTS=localhost,127.0.0.1

# Для тестов отключите SSL:
DB_SSL_MODE=disable

# Для продакшена (Yandex Cloud) используйте:
# DB_SSL_MODE=require
```

5. Применить миграции и запустить сервер:
```bash
python manage.py migrate
python manage.py runserver
```

### Запуск через Docker
```bash
cd fstr
docker-compose up --build
```

**Примечание**: Миграции выполняются автоматически при запуске контейнера.

## Деплоймент

Проект автоматически развертывается на Yandex Cloud Serverless Containers через GitHub Actions. При каждом пуше в ветку `main` происходит автоматический деплой.

**Базовый URL**: `https://bbacg4nrhlert7e578rs.containers.yandexcloud.net`

### Примеры запросов к развернутому API:
```bash
# Создание перевала
curl -X POST https://bbacg4nrhlert7e578rs.containers.yandexcloud.net/api/submitData/ \
  -H "Content-Type: application/json" \
  -d '{
    "beauty_title": "пер.",
    "title": "Пхия",
    "other_titles": "Триев",
    "connect": "",
    "user": {
      "email": "user@example.com",
      "fam": "Иванов",
      "name": "Петр",
      "otc": "Сергеевич",
      "phone": "+7 999 123 45 67"
    },
    "coords": {
      "latitude": 45.3842,
      "longitude": 7.1525,
      "height": 1200
    },
    "level": {
      "winter": "",
      "summer": "1А",
      "autumn": "1А",
      "spring": ""
    },
    "images": [
      {
        "title": "Седловина",
        "image_url": "https://example.com/photo1.jpg"
      }
    ]
  }'

# Получение перевала по ID
curl https://bbacg4nrhlert7e578rs.containers.yandexcloud.net/api/submitData/1/

# Поиск по email
curl "https://bbacg4nrhlert7e578rs.containers.yandexcloud.net/api/submitData/?user__email=user@example.com"
```

### CI/CD процесс:
- Автоматические тесты при каждом PR
- Автоматический деплой на Yandex Cloud Serverless Containers при пуше в main
- Health-checks и мониторинг

## Документация API

После запуска проекта, API-документация доступна по адресам:
- **Swagger UI**: https://bbacg4nrhlert7e578rs.containers.yandexcloud.net/swagger/
- **ReDoc**: https://bbacg4nrhlert7e578rs.containers.yandexcloud.net/redoc/

## Основные эндпоинты

- `POST /api/submitData/` - Добавить новый перевал
- `GET /api/submitData/?user__email=example@mail.ru` - Получить список перевалов по email
- `GET /api/submitData/<id>/` - Получить информацию о перевале по ID
- `PATCH /api/submitData/<id>/` - Обновить перевал (только если status = "new")

## Пример POST-запроса

```json
{
  "beauty_title": "пер.",
  "title": "Пхия",
  "other_titles": "Триев",
  "connect": "",
  "user": {
    "email": "qwerty@mail.ru",
    "fam": "Пупкин",
    "name": "Василий",
    "otc": "Иванович",
    "phone": "+7 555 55 55"
  },
  "coords": {
    "latitude": "45.3842",
    "longitude": "7.1525",
    "height": "1200"
  },
  "level": {
    "winter": "",
    "summer": "1А",
    "autumn": "1А",
    "spring": ""
  },
  "images": [
    {"title": "Седловина", "image_url": "http://example.com/image1.jpg"},
    {"title": "Подъем", "image_url": "http://example.com/image2.jpg"}
  ]
}
```

## Пример ответа при успешном создании

```json
{
  "status": 200,
  "message": null,
  "id": 1
}
```

## Статусы модерации перевалов

- `new` - Новая запись (можно редактировать)
- `pending` - На модерации
- `accepted` - Принята
- `rejected` - Отклонена

## Ограничения и бизнес-логика

- **Редактирование**: Перевал можно редактировать только если его статус — "new"
- **Пользователи**: При создании перевала система автоматически находит существующего пользователя по email или создает нового
- **Защита данных**: Данные пользователя (email, ФИО, телефон) защищены от изменений при создании новых перевалов
- **Уникальность**: Email пользователя должен быть уникальным в системе
- **Изображения**: При обновлении перевала старые изображения полностью заменяются новыми

## Тестирование
 
Проект покрыт 24 автоматическими тестами, которые проверяют:

- Создание перевалов с валидными и невалидными данными
- Получение данных по ID и email
- Обновление перевалов (только со статусом "new")
- Защиту данных пользователя от изменений
- Обработку ошибок и граничные случаи
- Работу моделей и сериализаторов
- Дублирование email пользователей

**Автоматическая конфигурация тестов:**
- При запуске тестов автоматически отключается SSL для локальной БД
- Включаются оптимизации для ускорения тестов (MD5PasswordHasher)
- Проверка на использование внешней БД Yandex Cloud (тесты не могут использовать внешнюю БД)

**Результаты тестирования:** 24/24 тестов проходят успешно

```bash
# Локальный запуск тестов
cd fstr
python manage.py test

# Запуск тестов через Docker
docker-compose run web python manage.py test

# Запуск с подробным выводом
python manage.py test -v 2

# Запуск конкретного теста
python manage.py test pereval.tests.PerevalAPITestCase.test_duplicate_user_email
```

### Важные примечания для тестирования:

1. **Локальная база данных**: Тесты требуют локальную PostgreSQL базу данных
2. **SSL отключение**: Для тестов автоматически отключается SSL режим
3. **Внешняя БД**: Тесты не могут использовать внешнюю БД Yandex Cloud

Если тесты пытаются использовать внешнюю БД Yandex Cloud, система выдаст ошибку с инструкциями по настройке локальной БД.

## Контакты

**Разработчик**: Ирина  
**Email**: irinaosk206@gmail.com  
**GitHub**: [Irina5-o](https://github.com/Irina5-o)

---

Проект выполнен в рамках учебного задания для Федерации спортивного туризма России (ФСТР).