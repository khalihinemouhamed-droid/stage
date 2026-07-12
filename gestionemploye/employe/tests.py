from django.test import TestCase
from django.urls import reverse

from account.models import Utilisateur
from employe.models import Departement, Employe, Poste


class ModifierEmployeTests(TestCase):
    def setUp(self):
        self.utilisateur = Utilisateur.objects.create_user(
            username="admin",
            email="admin@example.com",
            password="secret123",
            role="admin",
        )
        self.departement = Departement.objects.create(
            nom="Informatique",
            description="Équipe technique",
        )
        self.poste = Poste.objects.create(
            titre="Développeur",
            description="Développement",
            departement=self.departement,
        )
        self.employe = Employe.objects.create(
            matricule="E001",
            dateEmbauche="2024-01-01",
            poste=self.poste,
            departement=self.departement,
        )

    def test_modifier_employe_updates_fields(self):
        response = self.client.post(
            reverse("modifier_employe", args=[self.employe.id]),
            {
                "matricule": "E002",
                "dateEmbauche": "2024-02-02",
                "poste": self.poste.id,
                "departement": self.departement.id,
            },
        )

        self.assertRedirects(response, reverse("dashboard_admin"))
        self.employe.refresh_from_db()
        self.assertEqual(self.employe.matricule, "E002")
        self.assertEqual(str(self.employe.dateEmbauche), "2024-02-02")
