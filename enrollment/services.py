from django.db import transaction
from rest_framework.generics import get_object_or_404

from course.models import Course
from enrollment.models import Certificate, LessonProgress
from enrollment.tasks import generate_pdf_certificate


def issue_certificate(student, course_id):
    course = get_object_or_404(Course, id=course_id)

    total = course.lessons.count()

    if total == 0:
        return

    done = LessonProgress.objects.filter(
        student=student, lesson__course_id=course_id, is_completed=True
    ).count()

    if done == total:
        cert, created = Certificate.objects.get_or_create(course_id=course_id, student=student)

        if created:
            transaction.on_commit(
                lambda: generate_pdf_certificate.delay(cert.id),
            )
