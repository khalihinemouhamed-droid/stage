from django.urls import path

from .views import demande_conge_view, traiter_conge, valider_conges_list_view

urlpatterns = [
    path('demande/', demande_conge_view, name='demande_conge'),
    path('gestion-validation/', valider_conges_list_view, name='admin_validation_conges'),
    path('rh/conge/<int:conge_id>/traiter/', traiter_conge, name='traiter_conge'),
]
