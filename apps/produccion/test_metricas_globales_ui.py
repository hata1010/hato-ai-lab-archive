from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.core.models import Finca
from apps.ganado.models import Animal
from apps.produccion.models import Metrica


class MetricasGlobalesUITest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.root = User.objects.create_superuser("root-ui", "root@example.com", "pass1234")
        self.admin = User.objects.create_user("admin-finca", password="pass1234")
        self.finca = Finca.objects.create(nombre="Finca UI", nit="UI-001")

    def test_root_can_open_global_catalog(self):
        self.client.force_login(self.root)
        response = self.client.get(reverse("produccion:metricas_globales_lista"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Catálogo de Métricas Globales")

    def test_non_root_gets_403(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse("produccion:metricas_globales_lista"))
        self.assertEqual(response.status_code, 403)

    def test_global_creation_forces_finca_null_and_persists_motor_reference(self):
        self.client.force_login(self.root)
        response = self.client.post(
            reverse("produccion:crear_metrica_global"),
            {
                "nombre": "Peso Promedio Global UI",
                "codigo": "PESO_GLOBAL_UI",
                "motor_referencia": "PESO_PROMEDIO_FINCA",
                "categoria": "peso",
                "unidad_resultado": "kg",
                "periodicidad": "mensual",
                "tipo_resultado": "peso",
                "formula": "",
                "descripcion": "Prueba UI",
                "version": 1,
                "activa": "on",
            },
        )
        self.assertRedirects(response, reverse("produccion:metricas_globales_lista"))
        metrica = Metrica.objects.get(codigo="PESO_GLOBAL_UI")
        self.assertIsNone(metrica.finca)
        self.assertEqual(metrica.motor_referencia, "PESO_PROMEDIO_FINCA")

    def test_existing_global_is_backfilled_to_base_motor(self):
        metric = Metrica.objects.create(
            nombre="Peso Promedio Global UI",
            codigo="PESO_PROMEDIO_GLOBAL",
            categoria="peso",
            unidad_resultado="kg",
            finca=None,
            motor_referencia="",
        )
        # This test documents the runtime expectation after migration: the existing
        # official global metric must have its base motor persisted.
        from apps.produccion.migrations import _0005_metrica_motor_referencia as migration_module
        self.assertEqual(metric.motor_referencia, "")
        migration_module.vincular_motores_globales(type("Apps", (), {"get_model": lambda self, a, b: Metrica})(), None)
        metric.refresh_from_db()
        self.assertEqual(metric.motor_referencia, "PESO_PROMEDIO_FINCA")

    def test_root_link_is_present_in_dashboard_base(self):
        self.client.force_login(self.root)
        response = self.client.get(reverse("administrador:dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse("produccion:metricas_globales_lista"))
        self.assertContains(response, "Métricas Globales (ROOT)")

    def test_contrast_route_is_root_only(self):
        metric = Metrica.objects.create(
            nombre="Contraste UI",
            codigo="CONTRASTE_UI",
            categoria="peso",
            unidad_resultado="kg",
            finca=None,
            motor_referencia="PESO_PROMEDIO_FINCA",
        )
        for i in range(2):
            Animal.objects.create(
                finca=self.finca,
                numero_arete=f"UI-{i}",
                sexo="H",
            )

        self.client.force_login(self.admin)
        denied = self.client.get(reverse("produccion:contraste_global", args=[metric.id]))
        self.assertEqual(denied.status_code, 403)

        self.client.force_login(self.root)
        allowed = self.client.get(reverse("produccion:contraste_global", args=[metric.id]))
        self.assertEqual(allowed.status_code, 200)
        self.assertContains(allowed, "Contraste Global")
