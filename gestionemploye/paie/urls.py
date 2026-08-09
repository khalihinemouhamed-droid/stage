from django.urls import path
from . import views

urlpatterns = [
    path("salaires/", views.liste_salaires, name="liste_salaires"),
    path("salaires/ajouter/", views.ajouter_salaire, name="ajouter_salaire"),
    path("salaires/modifier/<int:salaire_id>/", views.modifier_salaire, name="modifier_salaire"),
    path("salaires/supprimer/<int:salaire_id>/", views.supprimer_salaire, name="supprimer_salaire"),
    path("mes-fiches-paie/", views.mes_fiches_paie_view, name="mes_fiches_paie"),
]

