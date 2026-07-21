from django.apps import AppConfig


class CoursesiteConfig(AppConfig):
    name = "course"

    def ready(self):
        import course.signals
