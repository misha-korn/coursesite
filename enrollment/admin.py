from django.contrib import admin

from enrollment.models import Certificate, Enrollment, LessonProgress

admin.site.register(Enrollment)
admin.site.register(Certificate)
admin.site.register(LessonProgress)
