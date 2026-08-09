# account/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
   path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("dashboard/admin/", views.dashboard_admin, name="dashboard_admin"),
    path('admin-dashboard/rh/sauvegarder/', views.crud_rh, name='crud_rh'),
    path('admin-dashboard/rh/supprimer/<int:rh_id>/', views.supprimer_rh, name='supprimer_rh'),
    path('admin-dashboard/departement/ajouter/', views.ajouter_departement, name='ajouter_departement'),
    path('admin-dashboard/poste/ajouter/', views.ajouter_poste, name='ajouter_poste'),
    # path('employe/pointer/', views.pointer_presence, name='pointer_presence'),
    # URL pour modifier le salaire de base d'un employé
    # path('admin-dashboard/employes/salaire/<int:employe_id>/', views.modifier_salaire_employe, name='modifier_salaire_employe')
# path('reset/', views.password_reset_step1, name='password_reset_step1'),
# path('reset/password/', views.password_reset_step2, name='password_reset_step2')


    path('reset-password/', views.password_reset_request, name='password_reset_step1'),

    # 2. La vue Django qui gère la confirmation avec le token (le lien reçu par email)
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='password_reset_confirm.html'
    ), name='password_reset_confirm'),

    # 3. La page affichée quand le mot de passe est bien changé
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='password_reset_complete.html'
    ), name='password_reset_complete'), 
]