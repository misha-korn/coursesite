import environ
from django.contrib.auth import get_user_model
from django.core.management import BaseCommand
from django.db import transaction

from config.settings.base import BASE_DIR
from course.models import Category, Course, Lesson

env = environ.Env(DEBUG=(bool, False))
environ.Env.read_env(BASE_DIR / ".env")

User = get_user_model()

CATEGORIES = {
    "programming": ["web-development", "mobile-development", "databases", "devops", "testing"],
    "data": ["data-analytics", "machine-learning", "data-visualization"],
    "design": ["ux-ui-design", "graphic-design", "motion-design"],
    "marketing": ["seo", "advertising", "content-marketing"],
    "business": ["management", "sales", "finance"],
    "languages": ["english", "german", "chinese"],
}

COURSES = [
    (
        "web-development",
        "React с нуля",
        "Компоненты, состояние, хуки и роутинг. Собираем рабочее SPA.",
        "3490.00",
        [
            ("Что такое компонент", 15),
            ("Состояние и хуки", 25),
            ("Роутинг", 20),
            ("Работа с API", 30),
        ],
    ),
    (
        "databases",
        "PostgreSQL для разработчиков",
        "Индексы, планы запросов, транзакции и блокировки на практике.",
        "3990.00",
        [
            ("Модель данных", 20),
            ("Индексы и EXPLAIN", 35),
            ("Транзакции", 30),
            ("Блокировки и дедлоки", 25),
        ],
    ),
    (
        "devops",
        "Docker и CI/CD на практике",
        "Контейнеры, compose, пайплайны GitHub Actions, деплой на сервер.",
        "3690.00",
        [
            ("Образы и контейнеры", 25),
            ("docker compose", 30),
            ("GitHub Actions", 30),
            ("Деплой на VPS", 25),
        ],
    ),
    (
        "data-analytics",
        "SQL для аналитика",
        "От простых выборок до оконных функций и CTE.",
        "2490.00",
        [("SELECT и фильтры", 20), ("JOIN и агрегация", 30), ("Оконные функции", 35)],
    ),
    (
        "ux-ui-design",
        "UX/UI: интерфейсы, которые понятны",
        "Исследование пользователей, прототипы, дизайн-система.",
        "3290.00",
        [("Исследование пользователей", 25), ("Прототипирование", 30), ("Дизайн-система", 25)],
    ),
    (
        "mobile-development",
        "Мобильные приложения на Flutter",
        "Один код для iOS и Android: от виджетов до публикации в сторах.",
        "4290.00",
        [
            ("Виджеты и вёрстка", 20),
            ("Навигация", 20),
            ("Состояние приложения", 30),
            ("Публикация в сторы", 15),
        ],
    ),
    (
        "testing",
        "Тестирование на pytest",
        "Фикстуры, параметризация, моки и покрытие. Тесты, которым можно верить.",
        "2890.00",
        [("Первый тест", 15), ("Фикстуры", 25), ("Моки и заглушки", 30), ("Покрытие и CI", 20)],
    ),
    (
        "machine-learning",
        "Машинное обучение: первые модели",
        "Регрессия, классификация, оценка качества. Без лишней математики.",
        "5490.00",
        [
            ("Как учится модель", 25),
            ("Линейная регрессия", 30),
            ("Классификация", 30),
            ("Переобучение", 20),
        ],
    ),
    (
        "seo",
        "SEO: продвижение без бюджета",
        "Семантика, техническая оптимизация, ссылки и аналитика.",
        "1990.00",
        [("Как работает поиск", 20), ("Семантическое ядро", 30), ("Техническая оптимизация", 25)],
    ),
    (
        "english",
        "Английский для IT",
        "Лексика разработчика, чтение документации, собеседование на английском.",
        "2290.00",
        [
            ("Лексика разработчика", 20),
            ("Чтение документации", 25),
            ("Переписка в команде", 20),
            ("Собеседование", 30),
        ],
    ),
]


class Command(BaseCommand):
    help = "Seed database"

    @transaction.atomic
    def handle(self, *args, **options):
        if Course.objects.exists() or Category.objects.exists():
            self.stdout.write("Database Seeded")
            return

        teacher = User.objects.create_user(
            username="proger322",
            password=env("TEACHER_PASSWORD"),
            email=env("TEACHER_EMAIL"),
            role=User.Role.TEACHER,
        )

        for parent_title in CATEGORIES.keys():
            parent = Category.objects.create(
                name=parent_title,
                slug=parent_title,
            )

            for child_title in CATEGORIES[parent_title]:
                Category.objects.create(
                    name=child_title,
                    slug=child_title,
                    parent=parent,
                )

        programming = Category.objects.get(name="programming")

        course = Course.objects.create(
            title="Django REST API",
            description="Django rest-framework",
            status=Course.Status.PUBLISHED,
            category=programming,
            author=teacher,
            price="2990.00",
        )

        for i, title in enumerate(["Введение", "Модели и ORM", "DRF", "Деплой"], start=1):
            Lesson.objects.create(
                course=course,
                title=title,
                number=i,
                content=f"Content of lesson {title}...",
                duration_minutes=20,
            )

        for category_slug, title, description, price, lessons in COURSES:
            new_course = Course.objects.create(
                title=title,
                description=description,
                status=Course.Status.PUBLISHED,
                category=Category.objects.get(slug=category_slug),
                author=teacher,
                price=price,
            )

            for i, (lesson_title, minutes) in enumerate(lessons, start=1):
                Lesson.objects.create(
                    course=new_course,
                    title=lesson_title,
                    number=i,
                    content=f"Материал урока «{lesson_title}».",
                    duration_minutes=minutes,
                )

        return self.stdout.write(self.style.SUCCESS("Successfully created database"))
