# from django.shortcuts import render, get_object_or_404, redirect
# from django.views.decorators.http import require_POST
# from .models import Employe, Departement, Poste
# from django.contrib import messages
# from django.views.decorators.http import require_POST

# # Liste des employés
# def liste_employes(request):
#     employes = Employe.objects.all()
#     return render(request, "liste.html", {"employes": employes})

# # Détail d’un employé
# def detail_employe(request, employe_id):
#     employe = get_object_or_404(Employe, id=employe_id)
#     return render(request, "detail.html", {"employe": employe})

# # Ajouter un employé
# def ajouter_employe(request):
#     if request.method == "POST":
#         matricule = request.POST.get("matricule")
#         date_embauche = request.POST.get("dateEmbauche")
#         poste_id = request.POST.get("poste")
#         departement_id = request.POST.get("departement")

#         poste = Poste.objects.get(id=poste_id) if poste_id else None
#         departement = Departement.objects.get(id=departement_id) if departement_id else None

#         Employe.objects.create(
#             matricule=matricule,
#             dateEmbauche=date_embauche,
#             poste=poste,
#             departement=departement
#         )
#         messages.success(request, "Employé ajouté avec succès !")
#         return redirect("liste_employes")

#     postes = Poste.objects.all()
#     departements = Departement.objects.all()
#     return render(request, "ajouter.html", {"postes": postes, "departements": departements})
# # Liste des postes
# def liste_postes(request):
#     postes = Poste.objects.all()
#     return render(request, "postes.html", {"postes": postes})

# # Ajouter un poste
# def ajouter_poste(request):
#     departements = Departement.objects.all()
#     if request.method == "POST":
#         titre = request.POST.get("titre")
#         description = request.POST.get("description")
#         departement_id = request.POST.get("departement")
#         departement = Departement.objects.get(id=departement_id)
#         Poste.objects.create(titre=titre, description=description, departement=departement)
#         messages.success(request, "Poste ajouté avec succès !")
#         return redirect("liste_postes")
#     return render(request, "ajouter_poste.html", {"departements": departements})


# # Supprimer un poste
# def supprimer_poste(request, poste_id):
#     poste = get_object_or_404(Poste, id=poste_id)
#     if request.method == "POST":
#         poste.delete()
#         messages.success(request, "Poste supprimé avec succès !")
#         return redirect("liste_postes")
#     return render(request, "supprimer_poste.html", {"poste": poste})


# # Liste des départements
# def liste_departements(request):
#     departements = Departement.objects.all()
#     return render(request, "departements.html", {"departements": departements})

# # Ajouter un département
# def ajouter_departement(request):
#     if request.method == "POST":
#         nom = request.POST.get("nom")
#         description = request.POST.get("description")
#         Departement.objects.create(nom=nom, description=description)
#         messages.success(request, "Département ajouté avec succès !")
#         return redirect("liste_departements")
#     return render(request, "ajouter_departement.html")

# # Supprimer un département
# def supprimer_departement(request, departement_id):
#     departement = get_object_or_404(Departement, id=departement_id)
#     if request.method == "POST":
#         departement.delete()
#         messages.success(request, "Département supprimé avec succès !")
#         return redirect("liste_departements")
#     return render(request, "supprimer_departement.html", {"departement": departement})

# def detail_departement(request, departement_id):
#     departement = get_object_or_404(Departement, id=departement_id)
#     postes = departement.postes.all()  # grâce au related_name
#     return render(request, "detail_departement.html", {
#         "departement": departement,
#         "postes": postes
#     })

# def modifier_employe(request, employe_id):
#     employe = get_object_or_404(Employe, id=employe_id)
#     if request.method == "POST":
#         employe.matricule = request.POST.get("matricule")
#         employe.dateEmbauche = request.POST.get("dateEmbauche")
#         poste_id = request.POST.get("poste")
#         departement_id = request.POST.get("departement")
#         employe.poste = Poste.objects.get(id=poste_id) if poste_id else None
#         employe.departement = Departement.objects.get(id=departement_id) if departement_id else None
#         employe.save()
#         messages.success(request, "Employé modifié avec succès !")
#         if request.user.is_authenticated and getattr(request.user, "role", None) == "rh":
#             return redirect("dashboard_rh")
#         return redirect("dashboard_admin")

#     postes = Poste.objects.all()
#     departements = Departement.objects.all()
#     return render(request, "modifier_employe.html", {"employe": employe, "postes": postes, "departements": departements})


# @require_POST
# def supprimer_employe(request, employe_id):
#     employe = get_object_or_404(Employe, id=employe_id)
#     employe.delete()
#     messages.success(request, "Employé supprimé avec succès !")
#     return redirect("liste_employes")

