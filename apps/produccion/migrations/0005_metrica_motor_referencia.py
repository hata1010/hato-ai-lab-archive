from django.db import migrations, models


def vincular_motores_globales(apps, schema_editor):
    Metrica = apps.get_model("produccion", "Metrica")
    Metrica.objects.filter(
        finca__isnull=True,
        codigo="PESO_PROMEDIO_GLOBAL",
    ).update(motor_referencia="PESO_PROMEDIO_FINCA")


def revertir_vinculo_peso_global(apps, schema_editor):
    Metrica = apps.get_model("produccion", "Metrica")
    Metrica.objects.filter(
        finca__isnull=True,
        codigo="PESO_PROMEDIO_GLOBAL",
        motor_referencia="PESO_PROMEDIO_FINCA",
    ).update(motor_referencia="")


class Migration(migrations.Migration):

    dependencies = [
        ("produccion", "0004_metrica_finca_alter_metrica_codigo_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="metrica",
            name="motor_referencia",
            field=models.CharField(
                blank=True,
                help_text="Código del motor V1 utilizado para evaluar esta métrica global.",
                max_length=50,
                verbose_name="Motor base de referencia",
            ),
        ),
        migrations.RunPython(
            vincular_motores_globales,
            revertir_vinculo_peso_global,
        ),
    ]
