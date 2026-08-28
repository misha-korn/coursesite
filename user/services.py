import uuid
from pathlib import Path


def user_image_path(instance, filename):
    ext = Path(filename).suffix.lower()
    pk = instance.pk
    hexx = uuid.uuid4().hex
    if pk is None:
        pk = hexx
    return f"users/{pk}/avatar{hexx[:8]}{ext}"
