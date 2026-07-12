from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from employe.models import Departement, Employe, Poste

from .models import Utilisateur

from django.contrib.auth.decorators import login_required
from employe.models import Employe
from employe.models import Poste
from employe.models import Departement
from attendance.models import Presence
from leave.models import DemandeConge
from paie.models import FicheDePaie


# Connexion
def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        print(f"Authenticating user: {username} {password}, Result: {user}")  # Debugging line
        if user is not None:
            login(request, user)
            print(f"User logged in: {user.role}")  # Debugging line
            # Vérifie si l'utilisateur est lié à Administrateur ou RH
            if user.role == "administrateur":
                return redirect("dashboard_admin")
            elif user.role == "rh":
                return redirect("dashboard_rh")
            elif user.role == "employe":
                return redirect("dashboard_employe")
        else:
            messages.error(request,"Nom d’utilisateur ou mot de passe incorrect.")
    return render(request, "login.html")

# Déconnexion
def logout_view(request):
    logout(request)
    return redirect("login")

# Dashboards
@login_required


@login_required
def dashboard_admin(request):
    employes = Employe.objects.select_related("poste", "departement").all()
    postes = Poste.objects.select_related("departement").all()
    departements = Departement.objects.prefetch_related("postes").all()
    presences = Presence.objects.select_related("employe").all()
    conges = DemandeConge.objects.select_related("employe").all()
    return render(request, "dashboard_admin.html", {
        "employes": employes,
        "postes": postes,
        "departements": departements,
        "presences": presences,
        "conges": conges,
        "total_employes": employes.count(),
        "total_postes": postes.count(),
        "total_departements": departements.count(),
        "total_conges": conges.filter(statut="En attente").count(),
    })








