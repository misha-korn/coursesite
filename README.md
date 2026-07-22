# CourseSite

Бэкенд для платформы онлайн-курсов. Преподаватели заводят курсы с уроками, студенты их покупают, проходят и получают сертификат. Оплата через ЮKassa, тяжёлые задачи вынесены в Celery.

Проект учебный, но писал я его так, как делал бы на работе: чтобы не развалилось на схеме БД, платежах и правах доступа. Основная ценность тут не в количестве фич, а в том, как решены сложные места.

Фронтенд на React лежит отдельно, в репозитории coursesite-frontend.

## Стек

Python, Django 6, DRF, PostgreSQL. Celery с RabbitMQ в роли брокера и Redis под кэш. Оплата на ЮKassa, авторизация на JWT, защита логина от перебора через django-axes. Swagger собирается через drf-spectacular. Всё запускается в Docker, в проде добавляются nginx и gunicorn. Тесты на pytest, линтер ruff.

## Что умеет

- регистрация и вход, две роли: студент и преподаватель
- преподаватель создаёт и публикует свои курсы, добавляет к ним уроки
- каталог с рейтингом и числом студентов, чужие черновики в нём не показываются
- покупка курса через ЮKassa, после оплаты студент автоматически записывается на курс
- уроки открываются только тем, кто купил курс (и автору)
- прогресс по урокам, при прохождении всех выдаётся сертификат в PDF
- отзывы: только от купивших, один на курс, оценка от 1 до 5
- кэш каталога, письма о покупке и напоминания забросившим - в фоне

## Модели

- User - свой, с полем роли
- Category - категории курсов, могут быть вложенными
- Course - курс: цена в DecimalField, автор, категория, статус (черновик или опубликован)
- Lesson - урок внутри курса
- Enrollment - запись на курс, промежуточная модель through, хранит цену на момент покупки
- LessonProgress - прогресс студента по уроку
- Review - отзыв, оценка ограничена диапазоном 1-5 на уровне БД
- Payment - платёж со статусом и id на стороне провайдера
- Certificate - сертификат о прохождении

## Запуск

Нужен Docker.

```bash
git clone <url>
cd coursesite
cp .env.example .env
docker compose up --build

docker compose run --rm --entrypoint python web manage.py makemigrations
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
```

После этого:

- API: http://localhost:8000/api/
- Swagger: http://localhost:8000/api/docs/
- Админка: http://localhost:8000/admin/

## Переменные окружения

Лежат в .env, шаблон - в .env.example. Основные:

- DJANGO_SETTINGS_MODULE - config.settings.dev или config.settings.prod
- SECRET_KEY, DEBUG, ALLOWED_HOSTS, SITE_URL
- DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT
- CELERY_BROKER_URL (RabbitMQ), CELERY_RESULT_BACKEND, REDIS_CACHE_URL
- EMAIL_* для отправки писем
- YOOKASSA_SHOP_ID, YOOKASSA_SECRET_KEY, YOOKASSA_ENABLED (1 - реальные вызовы, иначе заглушка)

Реальный .env в git не попадает, он в .gitignore. В репозитории только пустой .env.example.

## Как решены сложные места

### Оплата и запись на курс

Оплата подтверждается вебхуком от ЮKassa. Пометка платежа оплаченным и создание записи на курс идут в одной транзакции, чтобы не было ситуации "деньги прошли, а доступа нет".

```python
@transaction.atomic
def handle_payment_succeeded(external_id):
    payment = Payment.objects.select_for_update().get(external_id=external_id)
    if payment.status == "succeeded":
        return
    payment.status = "succeeded"
    payment.save(update_fields=["status"])
    Enrollment.objects.get_or_create(
        student=payment.student, course=payment.course,
        defaults={"price_paid": payment.amount},
    )
```

Вебхук может прийти несколько раз, поэтому обработка идемпотентна: проверка статуса плюс get_or_create не дадут записать студента на курс дважды. select_for_update защищает от двух одновременных вебхуков. Сумму ставит сервер из цены курса, клиент её задать не может.

Сам провайдер спрятан за сервисным слоем, в разработке подменяется заглушкой по флагу YOOKASSA_ENABLED.

### Оптимизация запросов

В списках через select_related тянутся автор и категория, на странице курса через prefetch_related - уроки и отзывы. Средний рейтинг и число студентов считаются в БД через annotate, а не перебором в Python.

### Права доступа

Свои permissions на уровне объекта: преподаватель правит только свои курсы и уроки, контент урока видит только купивший, отзыв оставляет только тот, кто прошёл курс. Плюс фильтрация в get_queryset - чужие черновики вообще не попадают в выборку.

### Кэш

Каталог курсов кэшируется в Redis. Сброс идёт через сигналы, причём не только при изменении курса, но и при изменении отзыва или записи на курс, потому что от них зависят рейтинг и счётчик студентов в кэше.

### Фон

На Celery вынесены письмо после покупки и генерация PDF-сертификата. Через Celery Beat раз в день уходят напоминания тем, кто забросил обучение.

### Безопасность

JWT с ротацией refresh-токена и блэклистом, django-axes блокирует логин после пяти неудач, есть ограничение частоты запросов (DRF throttling и limit_req в nginx). Деньги хранятся в DecimalField. В проде включаются HTTPS и защищённые куки.

## Эндпоинты

- POST /api/auth/register/ - регистрация
- POST /api/auth/login/ и /refresh/ - JWT
- GET /api/me/ - текущий пользователь
- /api/courses/ - курсы, на список и деталь отдаются разные сериализаторы
- /api/lessons/ - уроки
- /api/reviews/ - отзывы
- GET /api/enrollments/ - мои курсы
- /api/lesson_progress/ - прогресс
- POST /api/payments/ - купить курс
- POST /api/payments/yookassa_webhook/ - вебхук ЮKassa
- GET /api/certificates/ - сертификаты
- GET /api/docs/ - Swagger

## Тесты

```bash
docker compose exec web pytest -v
```

Проверяют регистрацию и валидацию пароля, блокировку логина, права доступа (чужой курс не отредактировать), идемпотентность вебхука (два вызова дают одну запись) и то, что клиент не может подставить свою цену при оплате.

## Прод

Отдельный docker-compose.prod.yml: gunicorn вместо runserver, nginx раздаёт статику и медиа и проксирует на приложение, миграции применяет только один сервис. HTTPS вешается сверху платформой (Railway, Render) или через certbot на своём сервере.

```bash
docker compose -f docker-compose.prod.yml up --build -d
```

## Линтер

```bash
docker compose exec web ruff check .
docker compose exec web ruff format .
```

На каждый пуш в GitHub Actions прогоняются линтер и тесты.
