from django.db import models
from django.conf import settings  # Pour faire référence à votre modèle Utilisateur personnalisé

class Departement(models.Model):
    nom = models.CharField(max_length=100, unique=True)
    

    def __str__(self):
        return self.nom
    

class Poste(models.Model):
    titre = models.CharField(max_length=100)
    departement = models.ForeignKey(Departement, on_delete=models.CASCADE, related_name="postes")

    def __str__(self):
        return f"{self.titre} ({self.departement.nom})"

class Employe(models.Model):
    # Relation OneToOne avec votre modèle Utilisateur personnalisé de l'app 'account'
    utilisateur = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="employe")
    matricule = models.CharField(max_length=20, unique=True)
    telephone = models.CharField(max_length=20, blank=True, null=True)
    poste = models.ForeignKey(Poste, on_delete=models.SET_NULL, null=True, related_name="employes")
    departement = models.ForeignKey(Departement, on_delete=models.SET_NULL, null=True, blank=True)
    salaire_base = models.DecimalField(max_digits=12, decimal_places=2, default=20000.00)



    def __str__(self):
        return f"{self.utilisateur.first_name} {self.utilisateur.last_name} ({self.matricule})"