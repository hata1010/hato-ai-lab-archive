"""Hato Metrics Engine: núcleo oficial de evaluación y composición V1/V2."""

from .compositor import Compositor
from .plan import PlanMetrica
from .evaluador import evaluar_expresion, evaluar_metrica
from .definicion import DefinicionMetrica
from .resultado import ResultadoMetrica
from .catalogo_v1 import METRICAS_V1, obtener_metrica_v1
from .ejecutor import EjecutorMotorV1
from .validador_dsl import validar_estrategia_dsl
from .sincronizador import sincronizar_catalogo_oficial
from .excepciones import (
    ErrorMotorMetrica,
    ErrorComposicion,
    ErrorCalculoMetrica,
    ErrorDatosInsuficientes,
    ErrorDivisionPorCero,
)

__all__ = [
    "Compositor",
    "PlanMetrica",
    "evaluar_expresion",
    "evaluar_metrica",
    "DefinicionMetrica",
    "ResultadoMetrica",
    "METRICAS_V1",
    "obtener_metrica_v1",
    "EjecutorMotorV1",
    "validar_estrategia_dsl",
    "sincronizar_catalogo_oficial",
    "ErrorMotorMetrica",
    "ErrorComposicion",
    "ErrorCalculoMetrica",
    "ErrorDatosInsuficientes",
    "ErrorDivisionPorCero",
]
