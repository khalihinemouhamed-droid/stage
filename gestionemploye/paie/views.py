from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import FicheDePaie

# Liste des salaires (admin ou RH)
@login_required
def liste_salaires(request):
    salaires = FicheDePaie.objects.select_related("employe").all()
    return render(request, "liste_salaires.html", {"salaires": salaires})

# Ajouter un salaire (employé connecté → pas de sélection)
@login_required
def ajouter_salaire(request):
    if request.method == "POST":
        mois = request.POST.get("mois")
        salaireBrut = request.POST.get("salaireBrut")
        salaireNet = request.POST.get("salaireNet")

        # ⚠️ Récupération automatique de l'employé lié au user connecté
        employe = request.user.employe  

        FicheDePaie.objects.create(
            employe=employe,
            mois=mois,
            salaireBrut=salaireBrut,
            salaireNet=salaireNet
        )
        return redirect("liste_salaires")

    return render(request, "ajouter_salaire.html")

# Modifier un salaire
@login_required
def modifier_salaire(request, salaire_id):
    salaire = get_object_or_404(FicheDePaie, id=salaire_id)
    if request.method == "POST":
        salaire.mois = request.POST.get("mois")
        salaire.salaireBrut = float(request.POST.get("salaireBrut") or 0)
        salaire.salaireNet = float(request.POST.get("salaireNet") or 0)
        salaire.save()
        if request.user.is_authenticated and getattr(request.user, "role", None) == "rh":
            return redirect("dashboard_rh")
        return redirect("liste_salaires")
    return render(request, "modifier_salaire.html", {"salaire": salaire})

# Supprimer un salaire
@login_required
def supprimer_salaire(request, salaire_id):
    salaire = get_object_or_404(FicheDePaie, id=salaire_id)
    salaire.delete()
    return redirect("liste_salaires")
