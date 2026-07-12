# account/admin.py
from django.contrib import admin
from .models import Utilisateur

admin.site.register(Utilisateur)

