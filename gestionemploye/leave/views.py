import random
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from employe.models import Employe
from .models import DemandeConge

# ==========================================
# 1. VUE CÔTÉ EMPLOYÉ : POUR FAIRE UNE DEMANDE
# ==========================================
@login_required
def demande_conge_view(request):
    # Sécurité automatique UNIQUE pour l'employé connecté
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

    if request.method == 'POST':
        date_debut = request.POST.get('dateDebut')
        date_fin = request.POST.get('dateFin')
        motif = request.POST.get('motif')

        if date_debut and date_fin:
            if date_debut > date_fin:
                messages.error(request, "Erreur : La date de début ne peut pas être après la date de fin.")
            else:
                # On enregistre la demande pour CET employé uniquement
                DemandeConge.objects.create(
                    employe=employe,
                    dateDebut=date_debut,
                    dateFin=date_fin,
                    motif=motif
                )
                messages.success(request, "Votre demande de congé a été soumise avec succès.")
                return redirect('demande_conge')
        else:
            messages.error(request, "Veuillez remplir tous les champs.")

    # L'employé ne voit QUE ses propres demandes
    mes_demandes = DemandeConge.objects.filter(employe=employe).order_by('-dateDebut')

    context = {
        'mes_demandes': mes_demandes,
    }
    return render(request, 'demande_conge.html', context)


# ==========================================
# 2. VUE CÔTÉ RH / ADMIN : POUR VALIDER (PAS DE MÉLANGE !)
# ==========================================
def est_rh_ou_admin(user):
    return user.is_staff or user.is_superuser

@user_passes_test(est_rh_ou_admin)
def valider_conges_list_view(request):
    # Iici, on ne cherche pas "request.user.employe". On s'en fiche, car on est admin !

    if request.method == 'POST':
        demande_id = request.POST.get('demande_id')
        action = request.POST.get('action')
        
        # Récupération de la demande de n'importe quel employé de la boîte
        demande = get_object_or_404(DemandeConge, id=demande_id)
        
        if action == 'approuver':
            demande.statut = 'Approuvé'
            messages.success(request, f"La demande de {demande.employe.utilisateur.first_name} a été approuvée.")
        elif action == 'refuser':
            demande.statut = 'Refusé'
            messages.warning(request, f"La demande de {demande.employe.utilisateur.first_name} a été refusée.")
        
        demande.save()
        return redirect('admin_validation_conges')

    # On récupère TOUTES les demandes de TOUT LE MONDE pour les afficher au RH
    demandes_en_attente = DemandeConge.objects.filter(statut='En attente').order_by('dateDebut')
    historique_demandes = DemandeConge.objects.exclude(statut='En attente').order_by('-id')[:15]

    context = {
        'demandes_en_attente': demandes_en_attente,
        'historique_demandes': historique_demandes,
    }
    return render(request, 'admin_validation_conges.html', context)