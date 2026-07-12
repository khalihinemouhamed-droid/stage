from django.urls import path
from . import views

urlpatterns = [
    # C'est cette URL qui affichera le dashboard de l'employé
    path('dashboard/employe/', views.dashboard_employe_view, name='dashboard_employe'),
    path('rh/dashboard/', views.dashboard_rh_view, name='dashboard_rh'),
    path("conge/<int:conge_id>/<str:action>/", views.traiter_conge_view,name="traiter_conge",),
]