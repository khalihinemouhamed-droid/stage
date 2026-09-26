import random
from datetime import date, datetime, time, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from account.decorators import role_required
from account.models import Utilisateur
from employe.models import Departement, Employe, Poste
from leave.models import DemandeConge
from paie.models import FicheDePaie
from .models import Presence


# --- OUTILS : ABSENCES ET CALCUL DES RETENUES ---
def verifier_et_generer_absences(date_cible=None):
    """
    Vérifie pour une date donnée (par défaut aujourd'hui) tous les employés enregistrés.
    Si un employé n'a aucun enregistrement de présence pour cette date,
    crée automatiquement un enregistrement de statut 'ABSENT' avec retenue sur salaire (1 journée de travail).
    """
    if date_cible is None:
        date_cible = date.today()

    employes = Employe.objects.all()
    for emp in employes:
        if emp.utilisateur.date_joined.date() > date_cible:
            continue
        if date_cible.weekday() >= 5:
            continue
        if DemandeConge.objects.filter(
            employe=emp,
            statut='Approuvé',
            dateDebut__lte=date_cible,
            dateFin__gte=date_cible,
        ).exists():
            continue
        presence_existante = Presence.objects.filter(employe=emp, date=date_cible).first()
        if not presence_existante:
            salaire_base_brut = getattr(emp, 'salaire_base', None)
            if salaire_base_brut is None or float(salaire_base_brut) == 0:
                salaire_base = 20000.0
            else:
                salaire_base = float(salaire_base_brut)

            # 1 jour de travail = 8h sur 160h mensuelles = 1/20ème du salaire de base
            taux_journalier = round(salaire_base / 20.0, 2)

            Presence.objects.create(
                employe=emp,
                date=date_cible,
                heure_arrivee=None,
                heure_depart=None,
                statut='ABSENT',
                minutes_retard=0,
                retenue_salaire=taux_journalier,
                note="Absence constatée (non pointé)"
            )


def generer_absences_du_mois():
    """Create absence records for missed workdays from this month through yesterday."""
    aujourd_hui = timezone.localdate()
    jour = aujourd_hui.replace(day=1)
    dernier_jour_a_verifier = aujourd_hui - timedelta(days=1)

    while jour <= dernier_jour_a_verifier:
        verifier_et_generer_absences(jour)
        jour += timedelta(days=1)


def calculer_retenues_employe_mois(employe, mois_str=""):
    """
    Calcule le total des retenues de salaire (retards + absences) pour un employé.
    Filtre par année/mois si mois_str contient une date (ex: YYYY-MM-DD ou YYYY-MM).
    """
    queryset = Presence.objects.filter(employe=employe)
    
    if mois_str:
        try:
            parts = str(mois_str).split('-')
            if len(parts) >= 2:
                annee = int(parts[0])
                mois_num = int(parts[1])
                queryset = queryset.filter(date__year=annee, date__month=mois_num)
        except (ValueError, IndexError):
            pass
            
    total_retenues = queryset.aggregate(total=Sum('retenue_salaire'))['total'] or 0.0
    nb_absences = queryset.filter(statut__icontains='ABSENT').count()
    nb_retards = queryset.filter(statut__icontains='RETARD').count()
    
    return float(total_retenues), nb_absences, nb_retards


# --- ESPACE EMPLOYÉ ---
@login_required
@role_required('employe')
def dashboard_employe_view(request):
    generer_absences_du_mois()
    try:
        employe = request.user.employe
    except (AttributeError, Employe.DoesNotExist):
        try:
            employe = request.user.employe_profil
        except (AttributeError, Employe.DoesNotExist):
            annee_actuelle = timezone.now().year
            numero_aleatoire = random.randint(1000, 9999)
            matricule_auto = f"EMP-{annee_actuelle}-{numero_aleatoire}"

            employe = Employe.objects.create(
                utilisateur=request.user,
                matricule=matricule_auto,
            )

    aujourdhui = timezone.now().date()
    maintenant_dt = timezone.now()
    maintenant = maintenant_dt.time()

    presence_du_jour = Presence.objects.filter(
        employe=employe, date=aujourdhui
    ).first()

    if request.method == "POST":
        if not presence_du_jour or not presence_du_jour.heure_arrivee:
            # --- POINTAGE ARRIVÉE ET RETARDS ---
            # Arrivals through 09:30 are considered on time.
            heure_limite = time(9, 30, 0)
            statut = 'Present'
            minutes_retard = 0
            retenue = 0.00

            if maintenant > heure_limite:
                statut = 'Retard'
                datetime_limite = timezone.make_aware(datetime.combine(aujourdhui, heure_limite))
                difference = maintenant_dt - datetime_limite
                minutes_retard = int(difference.total_seconds() / 60)

                salaire_base_brut = getattr(employe, 'salaire_base', None)
                if salaire_base_brut is None or float(salaire_base_brut) == 0:
                    salaire_base = 20000.0
                else:
                    salaire_base = float(salaire_base_brut)

                taux_horaire = salaire_base / 160.0
                taux_minute = taux_horaire / 60.0
                retenue = round(minutes_retard * taux_minute, 2)

            if presence_du_jour:
                # Si l'employé avait été pré-marqué ABSENT, on met à jour son arrivée
                presence_du_jour.heure_arrivee = maintenant
                presence_du_jour.statut = statut
                presence_du_jour.minutes_retard = minutes_retard
                presence_du_jour.retenue_salaire = retenue
                presence_du_jour.note = "Pointage enregistré tardivement"
                presence_du_jour.save()
            else:
                Presence.objects.create(
                    employe=employe,
                    date=aujourdhui,
                    heure_arrivee=maintenant,
                    statut=statut,
                    minutes_retard=minutes_retard,
                    retenue_salaire=retenue
                )
            
            if statut == 'Retard':
                heures_retard, minutes_restantes = divmod(minutes_retard, 60)
                duree_retard = f"{heures_retard}h{minutes_restantes:02d}min"
                messages.warning(
                    request, 
                    f"Arrivée en RETARD à {maintenant.strftime('%H:%M')}. "
                    f"Retard de {duree_retard}. Une retenue de {retenue} MRU a été appliquée."
                )
            else:
                messages.success(
                    request, 
                    f"Votre heure d'arrivée a été enregistrée : {maintenant.strftime('%H:%M')} !"
                )
        else:
            if not presence_du_jour.heure_depart:
                presence_du_jour.heure_depart = maintenant
                presence_du_jour.save()
                messages.success(
                    request,
                    f"Votre heure de départ a été enregistrée à {maintenant.strftime('%H:%M')}. Bonne soirée !"
                )
            else:
                messages.warning(request, "Vous avez déjà enregistré votre départ pour aujourd'hui.")

        return redirect("dashboard_employe")

    historique_presences = Presence.objects.filter(employe=employe).order_by("-date")
    total_heures = sum(p.calculer_heures() for p in historique_presences)
    mes_conges_recents = DemandeConge.objects.filter(employe=employe).order_by("-dateDebut")[:5]

    # RÉCUPÉRATION DU REGISTRE DE SES FICHES DE PAIE PERSONNELLES
    mes_fiches_paie = FicheDePaie.objects.filter(employe=employe).order_by("-id")

    context = {
        "employe": employe,
        "presence_du_jour": presence_du_jour,
        "historique_presences": historique_presences[:5],
        "total_heures": total_heures,
        "mes_conges_recents": mes_conges_recents,
        "mes_fiches_paie": mes_fiches_paie, # Envoyé au dashboard employé
    }
    return render(request, "dashboard_employe.html", context)
# def est_rh_ou_admin(user):
#     return user.is_staff or user.is_superuser

# # login_url='login' force Django à aller sur /login/ au lieu de /accounts/login/
# @user_passes_test(est_rh_ou_admin, login_url='login')


# --- ESPACE RH ET ADMINISTRATION ---
@role_required('rh', 'admin')
def dashboard_rh(request):
    """
    Affiche le tableau de bord RH complet :
    - Génère automatiquement les absences des jours ouvrés passés du mois
    - Liste des présences du jour
    - Liste des demandes de congés en attente
    - Liste de tous les employés (pour le CRUD et suivi des salaires)
    - Liste de l'ensemble des fiches de paie émises
    - Départements et Postes pour alimenter les formulaires
    """
    # 0. Génération des absences des jours ouvrés déjà terminés.
    # Aujourd'hui is not marked absent until the day has passed.
    generer_absences_du_mois()

    # Filtres optionnels pour les présences (date, employé, statut)
    search_date = request.GET.get('date', '').strip()
    search_employe = request.GET.get('employe_id', '').strip()
    search_statut = request.GET.get('statut', '').strip()

    # 1. Présences du jour
    presences_du_jour = Presence.objects.filter(date=date.today()).select_related('employe__utilisateur')
    
    # 2. Historique complet des pointages (passé)
    toutes_les_presences = Presence.objects.all().select_related('employe__utilisateur')
    if search_date:
        toutes_les_presences = toutes_les_presences.filter(date=search_date)
    if search_employe:
        toutes_les_presences = toutes_les_presences.filter(employe_id=search_employe)
    if search_statut:
        toutes_les_presences = toutes_les_presences.filter(statut=search_statut)
    toutes_les_presences = toutes_les_presences.order_by('-date', 'employe__utilisateur__first_name')

    # 3. Demandes de congés en attente
    demandes_conges = DemandeConge.objects.filter(statut='En attente')
    
    # 4. Liste complète des employés
    employes = Employe.objects.all().select_related('utilisateur', 'poste', 'departement')
    
    # 5. Pour remplir les sélecteurs du formulaire
    departements = Departement.objects.all()
    postes = Poste.objects.all()

    # 6. Récupération de l'ensemble des bulletins de paie générés
    toutes_les_fiches = FicheDePaie.objects.all().select_related('employe__utilisateur').order_by('-id')
    
    context = {
        'presences_du_jour': presences_du_jour,
        'toutes_les_presences': toutes_les_presences,
        'demandes_conges': demandes_conges,
        'employes': employes,
        'departements': departements,
        'postes': postes,
        'toutes_les_fiches': toutes_les_fiches,
        'search_date': search_date,
        'search_employe': search_employe,
        'search_statut': search_statut,
    }
    return render(request, 'dashboard_rh.html', context)


@role_required('rh', 'admin')
def calculer_paie_ajax(request):
    """
    API AJAX pour calculer en temps réel le salaire brut, les déductions (absences/retards) et le net.
    """
    employe_id = request.GET.get('employe_id')
    mois = request.GET.get('mois', '').strip()

    if not employe_id:
        return JsonResponse({'success': False, 'error': 'Employé non spécifié'}, status=400)

    employe = get_object_or_404(Employe, id=employe_id)
    salaire_brut = float(employe.salaire_base or 20000.0)
    total_retenues, nb_absences, nb_retards = calculer_retenues_employe_mois(employe, mois)
    salaire_net = max(0.0, round(salaire_brut - total_retenues, 2))

    return JsonResponse({
        'success': True,
        'employe_nom': f"{employe.utilisateur.first_name} {employe.utilisateur.last_name}",
        'salaire_brut': salaire_brut,
        'total_retenues': total_retenues,
        'nb_absences': nb_absences,
        'nb_retards': nb_retards,
        'salaire_net': salaire_net,
    })


# Petite fonction d'aide pour générer un matricule unique
def generer_matricule_unique():
    while True:
        # Génère un matricule du type EMP-7249 (4 chiffres aléatoires)
        numero_aleatoire = random.randint(1000, 9999)
        matricule = f"EMP-{numero_aleatoire}"
        # On vérifie si ce matricule existe déjà dans la base
        if not Employe.objects.filter(matricule=matricule).exists():
            return matricule

@role_required('rh', 'admin')
def crud_employe(request):
    if request.method == 'POST':
        employe_id = request.POST.get('employe_id')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email', '').strip()  # <--- Récupération de l'email
        username = request.POST.get('username').strip().lower()
        password = request.POST.get('password')
        departement_id = request.POST.get('departement')
        poste_id = request.POST.get('poste')
        
        # Récupération du salaire saisi (optionnel, 20000.00 par défaut)
        salaire_base_saisi = request.POST.get('salaire_base', '').strip()
        try:
            salaire_base = float(salaire_base_saisi) if salaire_base_saisi else 20000.00
        except (ValueError, TypeError):
            salaire_base = 20000.00

        # Récupération éventuelle d'un matricule envoyé par le formulaire
        matricule = request.POST.get('matricule', '').strip()

        try:
            dept = Departement.objects.get(id=departement_id)
            poste = Poste.objects.get(id=poste_id)
        except (Departement.DoesNotExist, Poste.DoesNotExist):
            messages.error(request, "Département ou Poste sélectionné invalide.")
            return redirect('dashboard_rh')

        # ================= MODE MODIFICATION =================
        if employe_id:
            try:
                emp = Employe.objects.get(id=employe_id)
                user = emp.utilisateur
                
                if Utilisateur.objects.filter(username=username).exclude(id=user.id).exists():
                    messages.error(request, f"L'identifiant @{username} est déjà utilisé par un autre employé.")
                    return redirect('dashboard_rh')
                
                # Vérification de l'unicité de l'email (si modifié)
                if email and Utilisateur.objects.filter(email=email).exclude(id=user.id).exists():
                    messages.error(request, f"L'adresse email {email} est déjà utilisée par un autre utilisateur.")
                    return redirect('dashboard_rh')
                
                # Si un matricule est saisi à la modification, on vérifie son unicité
                if matricule and Employe.objects.filter(matricule=matricule).exclude(id=emp.id).exists():
                    messages.error(request, f"Le matricule {matricule} est déjà attribué.")
                    return redirect('dashboard_rh')

                user.first_name = first_name
                user.last_name = last_name
                user.username = username
                user.email = email  # <--- Mise à jour de l'email
                if password:
                    user.set_password(password)
                user.save()
                
                emp.departement = dept
                emp.poste = poste
                emp.salaire_base = salaire_base
                if matricule:
                    emp.matricule = matricule
                emp.save()
                
                messages.success(request, f"L'employé {first_name} {last_name} a été mis à jour.")
            except Employe.DoesNotExist:
                messages.error(request, "Employé introuvable.")

        # ================= MODE CRÉATION =================
        else:
            username_original = username
            compteur = 1
            while Utilisateur.objects.filter(username=username).exists():
                username = f"{username_original}{compteur}"
                compteur += 1

            if username != username_original:
                messages.warning(request, f"L'identifiant @{username_original} était déjà pris. @{username} a été attribué automatiquement.")

            # Vérification de l'unicité de l'email à la création
            if email and Utilisateur.objects.filter(email=email).exists():
                messages.error(request, f"L'adresse email {email} est déjà utilisée.")
                return redirect('dashboard_rh')

            # Génération d'un matricule unique s'il n'est pas fourni dans le formulaire
            if not matricule:
                matricule = generer_matricule_unique()
            elif Employe.objects.filter(matricule=matricule).exists():
                messages.error(request, f"Le matricule fourni ({matricule}) existe déjà. Un matricule automatique va être généré.")
                matricule = generer_matricule_unique()

            # Création de l'utilisateur avec l'email
            user = Utilisateur.objects.create_user(
                username=username,
                first_name=first_name,
                last_name=last_name,
                email=email,  # <--- Ajout de l'email ici
                password=password if password else '123456'
            )

            # Création du profil Employé lié avec le matricule et le salaire de base
            Employe.objects.create(
                utilisateur=user,
                departement=dept,
                poste=poste,
                matricule=matricule,
                salaire_base=salaire_base
            )
            
            messages.success(request, f"L'employé {first_name} {last_name} a été créé avec le matricule {matricule}.")

    return redirect('dashboard_rh')


@role_required('rh', 'admin')
def supprimer_employe(request, employe_id):
    # 1. On récupère le profil de l'employé
    employe = get_object_or_404(Employe, id=employe_id)
    user_associe = employe.utilisateur  # Instance de account.Utilisateur
    nom_complet = f"{user_associe.first_name} {user_associe.last_name}"

    # Ne jamais supprimer son propre compte
    if user_associe.id == request.user.id:
        messages.error(request, "Vous ne pouvez pas supprimer votre propre compte depuis le tableau de bord.")
        return redirect('dashboard_rh')
    
    try:
        # On ouvre un bloc atomique pour s'assurer que tout est supprimé ensemble
        with transaction.atomic():
            # Suppression en cascade : utilisateur -> employé et données liées.
            user_associe.delete()
            
        messages.success(request, f"Le compte de {nom_complet} et toutes ses données associées ont été supprimés.")
        
    except Exception as e:
        messages.error(request, f"Impossible de supprimer cet employé : {str(e)}")
        
    return redirect('dashboard_rh')

@role_required('rh', 'admin')
# --- ACTION : CRÉATION DU BULLETIN DE PAIE (FICHE DE PAIE) PAR UN RH OU ADMIN ---
def emettre_fiche_paie(request):
    if request.method == 'POST':
        employe_id = (request.POST.get('employe_id') or '').strip()
        mois = request.POST.get('mois') # Format: "2026-08-04" ou "2026-08" ou texte
        salaire_brut_saisi = request.POST.get('salaire_brut')
        salaire_net_saisi = request.POST.get('salaire_net')

        if not employe_id.isdigit():
            messages.error(request, "Veuillez sélectionner un employé avant d'émettre le bulletin.")
            return redirect(request.META.get('HTTP_REFERER', 'dashboard_rh'))

        employe = get_object_or_404(Employe, id=employe_id)

        try:
            brut = float(salaire_brut_saisi) if (salaire_brut_saisi and float(salaire_brut_saisi) > 0) else float(employe.salaire_base or 20000.0)
            
            # Calcul automatique des retenues d'absence ET de retard du mois
            total_retenues, nb_absences, nb_retards = calculer_retenues_employe_mois(employe, mois)

            if salaire_net_saisi and float(salaire_net_saisi) > 0 and float(salaire_net_saisi) != brut:
                net = float(salaire_net_saisi)
            else:
                net = max(0.0, round(brut - total_retenues, 2))

            fiche, created = FicheDePaie.objects.update_or_create(
                employe=employe,
                mois=mois,
                defaults={
                    'salaireBrut': brut,
                    'salaireNet': net
                }
            )

            msg = (
                f"Fiche de paie de {mois} émise avec succès pour {employe.utilisateur.first_name} {employe.utilisateur.last_name}. "
                f"Brut: {brut} MRU | Déductions ({nb_absences} absence(s), {nb_retards} retard(s)): -{total_retenues} MRU | Net: {net} MRU."
            )
            messages.success(request, msg)

        except (ValueError, TypeError) as e:
            messages.error(request, f"Erreur lors du calcul de la paie : {str(e)}")

    return redirect(request.META.get('HTTP_REFERER', 'dashboard_rh'))


@role_required('rh', 'admin')
@require_POST
def supprimer_fiche_paie(request, fiche_id):
    fiche = get_object_or_404(FicheDePaie, id=fiche_id)
    nom_employe = f"{fiche.employe.utilisateur.first_name} {fiche.employe.utilisateur.last_name}".strip()
    periode = fiche.mois
    fiche.delete()
    messages.success(request, f"Le bulletin de {periode} pour {nom_employe} a été supprimé.")
    return redirect('dashboard_rh')
