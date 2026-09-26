import datetime

from django.db import models

from employe.models import Employe

class Presence(models.Model):
    STATUT_CHOICES = [
        ('PRESENT', 'Présent'),
        ('ABSENT', 'Absent'),
        ('RETARD', 'En retard'),
    ]

    employe = models.ForeignKey(Employe, on_delete=models.CASCADE, related_name="presences")
    # Allows absences to be recorded against the actual missed date.
    date = models.DateField(default=datetime.date.today)
    heure_arrivee = models.TimeField(null=True, blank=True)
    heure_depart = models.TimeField(null=True, blank=True)
    statut = models.CharField(max_length=10, choices=STATUT_CHOICES, default='PRESENT')
    minutes_retard = models.PositiveIntegerField(default=0)
    retenue_salaire = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    note = models.TextField(blank=True, null=True)  # Exemple : Justification d'un retard

    class Meta:
        unique_together = ('employe', 'date')  # Un employé ne peut avoir qu'une ligne de présence par jour

    def __str__(self):
        return f"{self.employe.matricule} - {self.date} - {self.statut}"
    def calculer_heures(self):
        """Calcule la durée de travail en heures décimales (ex: 8.5 pour 8h30)"""
        if self.heure_arrivee and self.heure_depart:
            # Transformation en datetime combiné pour faire la soustraction
            start = datetime.datetime.combine(datetime.date.min, self.heure_arrivee)
            end = datetime.datetime.combine(datetime.date.min, self.heure_depart)
            if end > start:
                duree = end - start
                return round(duree.total_seconds() / 3600, 2)
        return 0.0
