# account/urls.py
from django.urls import path
from . import views

urlpatterns = [
   path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("dashboard/admin/", views.dashboard_admin, name="dashboard_admin"),



]
