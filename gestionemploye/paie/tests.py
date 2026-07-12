from django.test import TestCase
from django.urls import reverse

from account.models import Utilisateur
from employe.models import Departement, Employe, Poste
from paie.models import FicheDePaie


class ModifierSalaireTests(TestCase):
    def setUp(self):
        self.utilisateur = Utilisateur.objects.create_user(
            username="rh",
            email="rh@example.com",
            password="secret123",
            role="rh",
        )
        self.departement = Departement.objects.create(
            nom="RH",
            description="Ressources humaines",
        )
        self.poste = Poste.objects.create(
            titre="Responsable RH",
            description="Gestion RH",
            departement=self.departement,
        )
        self.employe = Employe.objects.create(
            matricule="R001",
            dateEmbauche="2024-01-01",
            poste=self.poste,
            departement=self.departement,
        )
        self.salaire = FicheDePaie.objects.create(
            employe=self.employe,
            mois="Janvier",
            salaireBrut=1000,
            salaireNet=800,
        )

    def test_modifier_salaire_updates_fields(self):
        response = self.client.post(
            reverse("modifier_salaire", args=[self.salaire.id]),
            {
                "mois": "Février",
                "salaireBrut": "1200",
                "salaireNet": "1000",
            },
        )

        self.assertRedirects(response, reverse("liste_salaires"))
        self.salaire.refresh_from_db()
        self.assertEqual(self.salaire.mois, "Février")
        self.assertEqual(self.salaire.salaireBrut, 1200.0)
        self.assertEqual(self.salaire.salaireNet, 1000.0)
