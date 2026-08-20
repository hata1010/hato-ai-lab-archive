"""Pruebas del Super Motor: extensibilidad sin regresión de V1."""

import sys
import types
import unittest
from unittest.mock import patch

from apps.produccion.engine import (
    DefinicionMetrica,
    EjecutorMotorV1,
    METRICAS_V1,
    ErrorCalculoMetrica,
    ErrorComposicion,
    sincronizar_catalogo_oficial,
    validar_estrategia_dsl,
)


class TestSuperMotorMetricas(unittest.TestCase):
    def test_catalogo_oficial_conserva_las_8_metricas(self):
        self.assertEqual(len(METRICAS_V1), 8)
        for definicion in METRICAS_V1.values():
            self.assertEqual(definicion.version, "1.0")
            self.assertTrue(definicion.nombre)

    def test_pipeline_usa_whitelist_y_contrato_del_compositor(self):
        estrategia = {
            "modo": "pipeline",
            "pasos": [
                {"funcion": "FILTRO", "parametros": {"campo": "sexo", "valor": "H"}},
                {"funcion": "CONTEO"},
            ],
        }
        self.assertTrue(validar_estrategia_dsl(estrategia))

    def test_pipeline_rechaza_funcion_no_registrada(self):
        with self.assertRaises(ErrorComposicion):
            validar_estrategia_dsl({
                "modo": "pipeline",
                "pasos": [{"funcion": "os.system"}],
            })

    def test_formula_rechaza_llamadas_de_codigo(self):
        with self.assertRaises(ErrorCalculoMetrica):
            validar_estrategia_dsl({
                "modo": "formula",
                "formula": "__import__('os').system('ls')",
            })

    def test_formula_aritmetica_valida(self):
        self.assertTrue(validar_estrategia_dsl({
            "modo": "formula",
            "formula": "(peso_total / total_animales) * 1.05",
        }))

    def test_definicion_desde_modelo_oficial_no_rompe_catalogo(self):
        modelo = types.SimpleNamespace(
            codigo="PESO_TOTAL_FINCA",
            nombre="Peso Total Hato",
            version=1,
            categoria="peso",
            unidad_resultado="kg",
            descripcion="Prueba",
            formula="",
        )
        definicion = DefinicionMetrica.desde_modelo(modelo)
        self.assertEqual(definicion.codigo, "PESO_TOTAL_FINCA")
        self.assertEqual(len(definicion.pasos), 3)

    def test_definicion_desde_modelo_personalizada_usa_formula(self):
        modelo = types.SimpleNamespace(
            codigo="MI_METRICA",
            nombre="Mi métrica",
            version=1,
            categoria="productividad",
            unidad_resultado="kg",
            descripcion="Personalizada",
            formula="peso_total / animales",
        )
        definicion = DefinicionMetrica.desde_modelo(modelo)
        resultado = EjecutorMotorV1().ejecutar(
            definicion,
            {"peso_total": "1200", "animales": "3"},
        )
        self.assertTrue(resultado.es_valido)
        self.assertEqual(resultado.valor, 400)

    def test_sincronizador_solo_trabaja_con_catalogo_global(self):
        registros = []

        class Manager:
            def update_or_create(self, **kwargs):
                self.last = kwargs
                registros.append(kwargs)
                return object(), len(registros) == 1

        fake_models = types.ModuleType("apps.produccion.models")
        fake_models.Metrica = types.SimpleNamespace(objects=Manager())

        with patch.dict(sys.modules, {"apps.produccion.models": fake_models}):
            resultado = sincronizar_catalogo_oficial()

        self.assertEqual(resultado["total_oficiales"], 8)
        self.assertEqual(len(registros), 8)
        self.assertTrue(all(r["codigo"] in METRICAS_V1 for r in registros))
        self.assertTrue(all(r["finca"] is None for r in registros))


if __name__ == "__main__":
    unittest.main()
