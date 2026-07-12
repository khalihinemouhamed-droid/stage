import random
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Presence
from employe.models import Employe
from leave.models import DemandeConge  # Chargement des données de congé
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.utils import timezone
from employe.models import Employe

from .models import Presence

@login_required
def dashboard_employe_view(request):
    # 1. Protection / Récupération ou création automatique du profil employé
    try:
        employe = request.user.employe
    except Employe.DoesNotExist:
        annee_actuelle = timezone.now().year
        numero_aleatoire = random.randint(1000, 9999)
        matricule_auto = f"EMP-{annee_actuelle}-{numero_aleatoire}"
        
        employe = Employe.objects.create(
            utilisateur=request.user,
            matricule=matricule_auto,
            date_embauche=timezone.now().date()
        )

    aujourdhui = timezone.now().date()
    maintenant = timezone.now().time()

    # 2. Chercher la présence de l'employé pour la journée
    presence_du_jour = Presence.objects.filter(employe=employe, date=aujourdhui).first()

    # 3. Gestion de l'action de pointage (POST)
    if request.method == 'POST':
        if not presence_du_jour:
            # Enregistrement de l'arrivée
            Presence.objects.create(
                employe=employe,
                date=aujourdhui,
                heure_arrivee=maintenant,
                statut='PRESENT'
            )
            messages.success(request, "Votre heure d'arrivée a été enregistrée avec succès !")
        elif static_presence := presence_du_jour:
            if not static_presence.heure_depart:
                # Enregistrement du départ
                static_presence.heure_depart = maintenant
                static_presence.save()
                messages.success(request, "Votre heure de départ a été enregistrée. Bonne soirée !")
        
        return redirect('dashboard_employe')

    # 4. Récupération de l'historique des présences (5 dernières)
    historique_presences = Presence.objects.filter(employe=employe).order_by('-date')[:5]
    
    # 5. Récupération des congés récents de l'employé (3 derniers)
    mes_conges_recents = DemandeConge.objects.filter(employe=employe).order_by('-dateDebut')[:3]

    context = {
        'presence_du_jour': presence_du_jour,
        'historique_presences': historique_presences,
        'mes_conges_recents': mes_conges_recents,
    }
    return render(request, 'dashboard_employe.html', context)


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.utils import timezone
from employe.models import Employe
from leave.models import DemandeConge 
from .models import Presence
import datetime
from django.core.exceptions import PermissionDenied

# def est_rh_ou_admin(user):
#     return user.is_staff or user.is_superuser

# # login_url='login' force Django à aller sur /login/ au lieu de /accounts/login/
# @user_passes_test(est_rh_ou_admin, login_url='login')


@login_required
def dashboard_rh_view(request):
    if request.user.role != "rh":
        raise PermissionDenied

    aujourdhui = datetime.date.today()

    # Compteurs Statistiques
    total_employes = Employe.objects.count()
    presents_aujourdhui = Presence.objects.filter(
        date=aujourdhui, statut="PRESENT"
    ).count()

    # Compte les congés dont le statut est exactement 'Approuvé'
    conges_en_cours = DemandeConge.objects.filter(statut="Approuvé").count()

    # Récupération de la liste complète
    demandes_conges = (
        DemandeConge.objects.select_related("employe__utilisateur")
        .all()
        .order_by("-dateDebut")
    )

    context = {
        "total_employes": total_employes,
        "presents_aujourdhui": presents_aujourdhui,
        "conges_en_cours": conges_en_cours,
        "demandes_conges": demandes_conges,
    }
    return render(request, "dashboard_rh.html", context)


@login_required
def traiter_conge_view(request, conge_id, action):
    if request.user.role != "rh":
        raise PermissionDenied

    conge = get_object_or_404(DemandeConge, id=conge_id)

    # Respect strict de tes STATUT_CHOICES
    if action == "approuver":
        conge.statut = "Approuvé"
    elif action == "refuser":
        conge.statut = "Refusé"

    conge.save()
    return redirect("dashboard_rh")