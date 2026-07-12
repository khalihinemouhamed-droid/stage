# payroll/models.py
from django.db import models
from employe.models import Employe

class FicheDePaie(models.Model):
    employe = models.ForeignKey(Employe, on_delete=models.CASCADE)
    mois = models.CharField(max_length=20)
    salaireBrut = models.FloatField()
    salaireNet = models.FloatField()
