from django.urls import path

from . import views_2fa

app_name = "2fa"

urlpatterns = [
    path("send-code/", views_2fa.send_2fa_code, name="send_code"),
    path("verify-code/", views_2fa.verify_2fa_code, name="verify_code"),
    path("setup/", views_2fa.setup_2fa, name="setup"),
    path("update-email/", views_2fa.update_2fa_email, name="update_email"),
]
