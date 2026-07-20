"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework import routers

from course.views import CategoryViewSet, CourseViewSet, LessonViewSet
from enrollment.views import CertificateViewSet, EnrollmentViewSet, LessonProgressViewSet
from payment.views import PaymentViewSet, YookassaWebhookView
from review.views import ReviewViewSet
from user.views import MeView, RegisterView, ThrottledObtainPairView, ThrottledTokenRefreshView

router = routers.DefaultRouter()

router.register("courses", CourseViewSet, basename="course")
router.register("categories", CategoryViewSet, basename="category")
router.register("lessons", LessonViewSet, basename="lesson")
router.register("reviews", ReviewViewSet, basename="review")
router.register("enrollments", EnrollmentViewSet, basename="enrollment")
router.register("lesson_progress", LessonProgressViewSet, basename="lesson_progress")
router.register("certificates", CertificateViewSet, basename="certificate")
router.register("payments", PaymentViewSet, basename="payment")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
    path("api/auth/login/", ThrottledObtainPairView.as_view(), name="login"),
    path("api/auth/refresh/", ThrottledTokenRefreshView.as_view(), name="refresh"),
    path("api/auth/register/", RegisterView.as_view(), name="register"),
    path("api/me/", MeView.as_view(), name="me"),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger"),
    path("api/payments/yookassa_webhook/", YookassaWebhookView.as_view(), name="yookassa-webhook"),
]

if settings.DEBUG:
    urlpatterns += [path("__debug__/", include("debug_toolbar.urls"))]
