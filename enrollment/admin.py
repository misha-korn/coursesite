from django.contrib import admin
from enrollment.models import Enrollment, Certificate, LessonProgress

admin.site.register(Enrollment)
admin.site.register(Certificate)
admin.site.register(LessonProgress)
