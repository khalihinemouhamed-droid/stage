# leave/models.py
from django.db import models
from employe.models import Employe

class DemandeConge(models.Model):
    STATUT_CHOICES = [
        ('En attente', 'En attente'),
        ('Approuvé', 'Approuvé'),
        ('Refusé', 'Refusé'),
    ]
    employe = models.ForeignKey(Employe, on_delete=models.CASCADE)
    dateDebut = models.DateField()
    dateFin = models.DateField()
    statut = models.CharField(max_length=20, default="En attente")
    motif = models.TextField()
def __str__(self):
        return f"Congé de {self.employe.utilisateur.last_name} - Du {self.dateDebut} au {self.dateFin}"