from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

class Utilisateur(AbstractUser):

    ROLE_CHOICES = (
        ('admin',  "Administrateur"), ('rh', "Ressources Humaines"), ('employe', "Employé")
        )
    # Email unique
    name= models.CharField(max_length=50)

    # Rôle de l'utilisateur
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="employe")

    

    def __str__(self):
        return f"{self.name} ({self.role})"
