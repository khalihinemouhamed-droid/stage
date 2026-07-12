from django.urls import path
from . import views

urlpatterns = [
    # Employés
    path("employes/", views.liste_employes, name="liste_employes"),
    path("employes/ajouter/", views.ajouter_employe, name="ajouter_employe"),
    path("employes/modifier/<int:employe_id>/", views.modifier_employe, name="modifier_employe"),
    path("employes/<int:employe_id>/", views.detail_employe, name="detail_employe"),
    path("employes/supprimer/<int:employe_id>/", views.supprimer_employe, name="supprimer_employe"),

    # Postes
    path("postes/", views.liste_postes, name="liste_postes"),
    path("postes/ajouter/", views.ajouter_poste, name="ajouter_poste"),
    path("postes/supprimer/<int:poste_id>/", views.supprimer_poste, name="supprimer_poste"),

    # Départements
    path("departements/", views.liste_departements, name="liste_departements"),
    path("departements/ajouter/", views.ajouter_departement, name="ajouter_departement"),
    path("departements/supprimer/<int:departement_id>/", views.supprimer_departement, name="supprimer_departement"),
]
