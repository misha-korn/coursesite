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
from django.http import JsonResponse
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework import routers

from course.views import (
    CategoryViewSet,
    CourseImageViewSet,
    CourseViewSet,
    LessonImageViewSet,
    LessonViewSet,
)
from enrollment.views import CertificateViewSet, EnrollmentViewSet, LessonProgressViewSet
from payment.views import (
    BalanceEntryViewSet,
    PaymentViewSet,
    PayoutMethodViewSet,
    PayoutViewSet,
    YookassaWebhookView,
)
from review.views import ReviewViewSet
from user.views import (
    ChangePasswordView,
    EmailChangeConfirmView,
    EmailChangeRequestView,
    LogoutView,
    MeView,
    PasswordResetConfirmView,
    PasswordResetRequestView,
    PublicUserView,
    RegisterView,
    ThrottledObtainPairView,
    ThrottledTokenRefreshView,
    VerifyEmailConfirmView,
    VerifyEmailRequestView,
)


def health(request):
    return JsonResponse({"status": "ok"})


router = routers.DefaultRouter()

router.register("courses", CourseViewSet, basename="course")
router.register("courses-images", CourseImageViewSet, basename="course-image")
router.register("categories", CategoryViewSet, basename="category")
router.register("lessons", LessonViewSet, basename="lesson")
router.register("lessons-images", LessonImageViewSet, basename="lesson-image")
router.register("reviews", ReviewViewSet, basename="review")
router.register("enrollments", EnrollmentViewSet, basename="enrollment")
router.register("lesson_progress", LessonProgressViewSet, basename="lesson_progress")
router.register("certificates", CertificateViewSet, basename="certificate")
router.register("payments", PaymentViewSet, basename="payment")
router.register("payouts", PayoutViewSet, basename="payout")
router.register("balance-entries", BalanceEntryViewSet, basename="balance-entry")
router.register("payout-methods", PayoutMethodViewSet, basename="payout-method")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", health, name="health"),
    path("api/", include(router.urls)),
    path("api/auth/login/", ThrottledObtainPairView.as_view(), name="login"),
    path("api/auth/refresh/", ThrottledTokenRefreshView.as_view(), name="refresh"),
    path("api/auth/register/", RegisterView.as_view(), name="register"),
    path("api/auth/logout/", LogoutView.as_view(), name="logout"),
    path("api/auth/password/change/", ChangePasswordView.as_view(), name="change-password"),
    path(
        "api/auth/password/reset/",
        PasswordResetRequestView.as_view(),
        name="reset-request-password",
    ),
    path(
        "api/auth/password/reset/confirm/",
        PasswordResetConfirmView.as_view(),
        name="reset-confirm-password",
    ),
    path("api/auth/email/change/", EmailChangeRequestView.as_view(), name="change-request-email"),
    path(
        "api/auth/email/change/confirm/",
        EmailChangeConfirmView.as_view(),
        name="change-confirm-email",
    ),
    path("api/auth/email/verify/", VerifyEmailRequestView.as_view(), name="verify-request-email"),
    path(
        "api/auth/email/verify/confirm/",
        VerifyEmailConfirmView.as_view(),
        name="verify-confirm-email",
    ),
    path("api/me/", MeView.as_view(), name="me"),
    path("api/profile/<int:pk>/", PublicUserView.as_view(), name="profile"),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger"),
    path("api/payments/yookassa_webhook/", YookassaWebhookView.as_view(), name="yookassa-webhook"),
]

if settings.DEBUG:
    urlpatterns += [path("__debug__/", include("debug_toolbar.urls"))]
