from django.shortcuts import render, redirect, get_object_or_404
from .models import FicheDePaie
from account.decorators import role_required

# Liste des salaires (admin ou RH)
@role_required('rh', 'admin')
def liste_salaires(request):
    salaires = FicheDePaie.objects.select_related("employe").all()
    return render(request, "liste_salaires.html", {"salaires": salaires})

# Ajouter un salaire
@role_required('rh', 'admin')
def ajouter_salaire(request):
    if request.method == "POST":
        mois = request.POST.get("mois")
        salaireBrut = request.POST.get("salaireBrut")
        salaireNet = request.POST.get("salaireNet")

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
@role_required('rh', 'admin')
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
@role_required('rh', 'admin')
def supprimer_salaire(request, salaire_id):
    salaire = get_object_or_404(FicheDePaie, id=salaire_id)
    salaire.delete()
    return redirect("liste_salaires")

# Espace Employé : Consultation de ses fiches de paie personnelles
@role_required('employe')
def mes_fiches_paie_view(request):
    employe = None
    try:
        employe = request.user.employe
    except Exception:
        try:
            employe = request.user.employe_profil
        except Exception:
            pass

    if employe:
        fiches = FicheDePaie.objects.filter(employe=employe).order_by("-id")
    else:
        fiches = []

    return render(request, "mes_fiches_paie.html", {
        "employe": employe,
        "fiches": fiches
    })
