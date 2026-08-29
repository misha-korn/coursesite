from pathlib import Path
from uuid import uuid4


def lesson_image_path(instance, filename):
    ext = Path(filename).suffix.lower()
    return f"lessons/{instance.lesson_id}/{uuid4().hex[:8]}{ext}"

def course_image_path(instance, filename):
    ext = Path(filename).suffix.lower()
    return f"courses/{instance.course_id}/{uuid4().hex[:8]}{ext}"

def category_image_path(instance, filename):
    ext = Path(filename).suffix.lower()
    return f"categories/{instance.pk}/{uuid4().hex[:8]}{ext}"