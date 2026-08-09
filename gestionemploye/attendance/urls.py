from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/employe/', views.dashboard_employe_view, name='dashboard_employe'),
    path('rh/dashboard/', views.dashboard_rh, name='dashboard_rh'),
    path('rh/employe/enregistrer/', views.crud_employe, name='crud_employe'),
    path('rh/employe/<int:employe_id>/supprimer/', views.supprimer_employe, name='supprimer_employe_rh'),
    path('admin-dashboard/bulletin/emettre/', views.emettre_fiche_paie, name='emettre_fiche_paie'),
    path('admin-dashboard/bulletin/<int:fiche_id>/supprimer/', views.supprimer_fiche_paie, name='supprimer_fiche_paie'),
    path('rh/paie/calculer-ajax/', views.calculer_paie_ajax, name='calculer_paie_ajax'),
]
