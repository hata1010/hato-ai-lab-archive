"""Sincronización idempotente del catálogo oficial con la BD operativa."""

from typing import Dict

from .catalogo_v1 import METRICAS_V1


def sincronizar_catalogo_oficial() -> Dict[str, int]:
    """Sincroniza las métricas oficiales sin tocar las métricas de las fincas.

    La versión actual del modelo Metrica mantiene la estrategia V1 en Python y
    utiliza la BD como catálogo operativo. Por eso solo persistimos los campos
    que existen realmente en el modelo; no inventamos un campo ``estrategia``.
    """
    from apps.produccion.models import Metrica

    creadas = 0
    actualizadas = 0

    for codigo, definicion in METRICAS_V1.items():
        try:
            version = int(str(definicion.version).split(".")[0])
        except (TypeError, ValueError):
            version = 1

        _, fue_creada = Metrica.objects.update_or_create(
            codigo=codigo,
            finca=None,
            defaults={
                "nombre": definicion.nombre,
                "categoria": definicion.familia,
                "unidad_resultado": definicion.unidad,
                "formula": definicion.formula or "",
                "descripcion": definicion.descripcion,
                "version": version,
                "activa": True,
            },
        )

        if fue_creada:
            creadas += 1
        else:
            actualizadas += 1

    return {
        "creadas": creadas,
        "actualizadas": actualizadas,
        "total_oficiales": len(METRICAS_V1),
    }
