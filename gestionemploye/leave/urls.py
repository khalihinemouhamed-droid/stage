from django import views
from django.urls import path
from .views import demande_conge_view, valider_conges_list_view,traiter_conge

urlpatterns = [
    path('demande/', demande_conge_view, name='demande_conge'),
    path('gestion-validation/', valider_conges_list_view, name='admin_validation_conges'),
    path('rh/conge/<int:conge_id>/traiter/', traiter_conge, name='traiter_conge'),
]