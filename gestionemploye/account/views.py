from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from employe.models import Departement, Employe, Poste
from .models import Utilisateur
from attendance.models import Presence
from leave.models import DemandeConge
from paie.models import FicheDePaie
from django.contrib.auth.models import User
from datetime import date, datetime, time
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

# Connexion
def login_view(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]
        user = authenticate(request, email=email, password=password)
        print(f"Authenticating user: {email} {password}, Result: {user}")  # Debugging line
        if user is not None:
            login(request, user)
            print(f"User logged in: {user.role}")  # Debugging line
            # Vérifie si l'utilisateur est lié à Administrateur ou RH
            if user.role == "admin":
                return redirect("dashboard_admin")
            elif user.role == "rh":
                return redirect("dashboard_rh")
            elif user.role == "employe":
                return redirect("dashboard_employe")
        else:
            messages.error(request,"Nom d’utilisateur ou mot de passe incorrect.")
    return render(request, "login.html")
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required

User = get_user_model()
from account.decorators import role_required


def password_reset_step1(request):
    if request.method == "POST":
        username = request.POST.get('username', '').strip()
        
        # On cherche l'utilisateur dans la base
        try:
            user = User.objects.get(username__iexact=username)
            # On stocke l'ID de l'utilisateur en session pour l'étape suivante
            request.session['reset_user_id'] = user.id
            return redirect('password_reset_step2')
        except User.DoesNotExist:
            messages.error(request, "Cet identifiant est introuvable.")
            
    return render(request, 'password_reset_username.html')
def password_reset_step2(request):
    user_id = request.session.get('reset_user_id')
    if not user_id:
        return redirect('password_reset_step1') # Si pas d'étape 1, on renvoie au début
        
    if request.method == "POST":
        new_password = request.POST.get('password')
        user = User.objects.get(id=user_id)
        
        # Enregistrement du nouveau mot de passe
        user.set_password(new_password)
        user.save()
        
        # Nettoyage de la session
        del request.session['reset_user_id']
        messages.success(request, "Votre mot de passe a été modifié avec succès.")
        return redirect('login')
            
    return render(request, 'password_reset_password.html')
# Déconnexion
def logout_view(request):
    logout(request)
    return redirect("login")

from django.contrib.auth import get_user_model

# Récupération de votre modèle Utilisateur personnalisé
Utilisateur = get_user_model()

# --- FONCTION COMPAGNON : RECHERCHE D'IDENTIFIANT UNIQUE ---
# Cette fonction regarde si le "username" est déjà pris.
# Si oui, elle ajoute un numéro à la fin (ex: sidi -> sidi1 -> sidi2) pour éviter le blocage.
def generer_username_unique(username):
    username = username.strip().lower() # Enlève les espaces et met en minuscules
    username_de_base = username
    compteur = 1
    
    # Boucle tant que l'identifiant existe déjà dans la base
    while Utilisateur.objects.filter(username=username).exists():
        username = f"{username_de_base}{compteur}"
        compteur += 1
        
    return username





# ... existing code ...

# --- DASHBOARD ADMIN : SUIVI CENTRALISÉ DES SALAIRES ET DES BULLETINS ---
@login_required
@role_required('admin')
def dashboard_admin(request):
    responsables_rh = Utilisateur.objects.filter(role='rh')
    departements = Departement.objects.all()
    postes = Poste.objects.all().select_related('departement')
    employes = Employe.objects.all().select_related('utilisateur', 'departement', 'poste')
    
    # Récupération de l'ensemble des fiches de paie générées par l'entreprise
    toutes_les_fiches = FicheDePaie.objects.all().select_related('employe__utilisateur').order_by('-id')

    context = {
        'responsables_rh': responsables_rh,
        'departements': departements,
        'postes': postes,
        'employes': employes,
        'toutes_les_fiches': toutes_les_fiches,
    }
    return render(request, 'dashboard_admin.html', context)


# --- ACTION : ATTRIBUER OU ÉDITER LE SALAIRE DE BASE D'UN EMPLOYÉ ---
def modifier_salaire_employe(request, employe_id):
    if request.method == 'POST':
        employe = get_object_or_404(Employe, id=employe_id)
        nouveau_salaire = request.POST.get('salaire_base')
        try:
            employe.salaire_base = float(nouveau_salaire)
            employe.save()
            messages.success(
                request, 
                f"Le salaire de base de {employe.utilisateur.first_name} a été mis à jour à {employe.salaire_base} MRU !"
            )
        except (ValueError, TypeError):
            messages.error(request, "Veuillez entrer un montant numérique valide.")
            
    return redirect('dashboard_admin')





# --- AUTRES ACTIONS D'ADMINISTRATION ---
def crud_rh(request):
    if request.method == 'POST':
        rh_id = request.POST.get('rh_id')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password')

        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, "Veuillez saisir une adresse e-mail valide pour le responsable RH.")
            return redirect('dashboard_admin')

        email_query = Utilisateur.objects.filter(email__iexact=email)
        if rh_id:
            email_query = email_query.exclude(id=rh_id)
        if email_query.exists():
            messages.error(request, f"L'adresse e-mail {email} est déjà utilisée.")
            return redirect('dashboard_admin')

        if rh_id:
            user_rh = get_object_or_404(Utilisateur, id=rh_id)
            if Utilisateur.objects.filter(username=username).exclude(id=user_rh.id).exists():
                messages.error(request, f"L'identifiant {username} est déjà pris.")
                return redirect('dashboard_admin')
            
            user_rh.first_name = first_name
            user_rh.last_name = last_name
            user_rh.username = username
            user_rh.email = email
            if password:
                user_rh.set_password(password)
            user_rh.save()
            messages.success(request, f"Le compte RH de {first_name} a été mis à jour.")
        else:
            # Génération automatique d'un username unique si doublon de nom
            base_username = username
            counter = 1
            while Utilisateur.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1
                
            Utilisateur.objects.create_user(
                username=username,
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=password if password else "rh123456",
                is_staff=True,
                role='rh'
            )
            messages.success(request, f"Compte RH créé avec l'identifiant unique : @{username}")

    return redirect('dashboard_admin')


def supprimer_rh(request, rh_id):
    if request.method == 'POST':
        rh = get_object_or_404(Utilisateur, id=rh_id)
        rh.delete()
        messages.success(request, "Le compte RH a été supprimé.")
    return redirect('dashboard_admin')


def ajouter_departement(request):
    if request.method == 'POST':
        nom = request.POST.get('nom_departement')
        if nom:
            Departement.objects.create(nom=nom)
            messages.success(request, f"Département '{nom}' ajouté avec succès.")
    return redirect('dashboard_admin')


def ajouter_poste(request):
    if request.method == 'POST':
        titre = request.POST.get('titre_poste')
        dept_id = request.POST.get('departement_id')
        if titre and dept_id:
            dept = get_object_or_404(Departement, id=dept_id)
            Poste.objects.create(titre=titre, departement=dept)
            messages.success(request, f"Poste '{titre}' ajouté au département {dept.nom}.")
    return redirect('dashboard_admin')
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.shortcuts import render
from django.db.models import Q
from django.conf import settings
from django.template.loader import render_to_string

User = get_user_model() # Récupère votre modèle personnalisé (Utilisateur)

def password_reset_request(request):
    if request.method == "POST":
        email = request.POST.get('email', '').strip()
        
        if email:
            # Recherche l'utilisateur uniquement par son adresse e-mail (insensible à la casse)
            users = User.objects.filter(email__iexact=email)
            
            if not users.exists():
                messages.error(request, f"Aucun utilisateur n'est enregistré avec l'adresse e-mail : {email}")
                return render(request, 'password_reset_username.html')

            for user in users:
                if user.email:
                    # Générer un jeton unique
                    token = default_token_generator.make_token(user)
                    uid = urlsafe_base64_encode(force_bytes(user.pk))
                    
                    # Créer le lien de réinitialisation
                    reset_link = request.build_absolute_uri(
                        reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
                    )
                    
                    # Rendu du template HTML de l'email
                    context = {
                        'user': user,
                        'reset_link': reset_link,
                    }
                    html_content = render_to_string('password_reset_email.html', context)
                    
                    text_content = (
                        f"Bonjour {user.first_name or user.username},\n\n"
                        f"Vous avez demandé la réinitialisation de votre mot de passe sur la plateforme Smart RH.\n\n"
                        f"Veuillez cliquer sur le lien ci-dessous pour définir un nouveau mot de passe :\n"
                        f"{reset_link}\n\n"
                        f"Si vous n'avez pas effectué cette demande, vous pouvez ignorer cet e-mail en toute sécurité.\n\n"
                        f"Cordialement,\n"
                        f"L'équipe Smart RH"
                    )
                    
                    # Envoyer l'email avec le template HTML
                    try:
                        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', getattr(settings, 'EMAIL_HOST_USER', 'noreply@smartrh.com'))
                        send_mail(
                            subject='Réinitialisation de votre mot de passe Smart RH',
                            message=text_content,
                            from_email=from_email,
                            recipient_list=[user.email],
                            html_message=html_content,
                            fail_silently=False,
                        )
                    except Exception as e:
                        print(f"Erreur d'envoi SMTP: {e}")
                        messages.error(request, f"Erreur lors de l'envoi de l'e-mail (problème de connexion SMTP/Mot de passe d'application) : {e}")
                        return render(request, 'password_reset_username.html')
            
            return render(request, 'password_reset_sent.html')
            
    return render(request, 'password_reset_username.html')
