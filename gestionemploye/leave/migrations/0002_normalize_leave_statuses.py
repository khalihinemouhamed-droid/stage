from django.db import migrations


def normalize_leave_statuses(apps, schema_editor):
    DemandeConge = apps.get_model("leave", "DemandeConge")
    DemandeConge.objects.filter(statut__in=["Accepte", "Accepté"]).update(
        statut="Approuvé"
    )
    DemandeConge.objects.filter(statut__in=["Refuse", "Refusé"]).update(
        statut="Refusé"
    )


class Migration(migrations.Migration):
    dependencies = [
        ("leave", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(normalize_leave_statuses, migrations.RunPython.noop),
    ]
