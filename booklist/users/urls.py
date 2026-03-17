from django.urls import include, path

from . import views, views_email_verification

app_name = "users"

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register_view, name="register"),
    path("login-form/", views.login_form_partial, name="login_form_partial"),
    # Email verification during registration
    path(
        "verify-email/", views_email_verification.verify_email_code, name="verify_email"
    ),
    path(
        "resend-verification/",
        views_email_verification.resend_verification_code,
        name="resend_verification",
    ),
    # 2FA management
    path("2fa/", include("users.urls_2fa", namespace="2fa")),
]
