from django.db import models
from employe.models import Employe

class Presence(models.Model):
    STATUT_CHOICES = [
        ('PRESENT', 'Présent'),
        ('ABSENT', 'Absent'),
        ('RETARD', 'En retard'),
    ]

    employe = models.ForeignKey(Employe, on_delete=models.CASCADE, related_name="presences")
    date = models.DateField(auto_now_add=True)
    heure_arrivee = models.TimeField(null=True, blank=True)
    heure_depart = models.TimeField(null=True, blank=True)
    statut = models.CharField(max_length=10, choices=STATUT_CHOICES, default='PRESENT')
    note = models.TextField(blank=True, null=True)  # Exemple : Justification d'un retard

    class Meta:
        unique_together = ('employe', 'date')  # Un employé ne peut avoir qu'une ligne de présence par jour

    def __str__(self):
        return f"{self.employe.matricule} - {self.date} - {self.statut}"