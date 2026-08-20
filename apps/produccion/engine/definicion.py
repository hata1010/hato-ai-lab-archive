"""Estructura de definición para el catálogo de métricas V1 y resolución operativa."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class DefinicionMetrica:
    """Especificación declarativa de una métrica en Hato AI."""

    codigo: str
    nombre: str
    version: str = "1.0"
    tipo: str = "atomica"
    familia: str = "poblacion"
    unidad: str = ""
    precision_decimales: int = 2
    estrategia: Dict[str, Any] = field(default_factory=dict)
    descripcion: str = ""

    @property
    def pasos(self) -> List[Dict[str, Any]]:
        return self.estrategia.get("pasos", [])

    @property
    def formula(self) -> Optional[str]:
        return self.estrategia.get("formula")

    @property
    def dependencias(self) -> List[str]:
        return self.estrategia.get("dependencias", [])

    @classmethod
    def desde_modelo(cls, metrica_db: Any) -> "DefinicionMetrica":
        """Resuelve una métrica operativa desde el modelo Django sin romper V1.

        Prioridad de estrategia:
        1. estrategia declarativa si el modelo ya la expone.
        2. definición oficial V1 cuando el código pertenece al catálogo.
        3. fórmula almacenada en BD para métricas personalizadas.

        Así el motor conserva el catálogo oficial como semilla técnica y permite
        que una métrica local pueda evolucionar independientemente.
        """
        from .catalogo_v1 import METRICAS_V1

        codigo = getattr(metrica_db, "codigo", "")
        oficial = METRICAS_V1.get(codigo)

        estrategia_modelo = getattr(metrica_db, "estrategia", None)
        if estrategia_modelo:
            estrategia = estrategia_modelo
        elif oficial is not None:
            estrategia = oficial.estrategia
        else:
            formula_db = getattr(metrica_db, "formula", "") or ""
            estrategia = {"modo": "formula", "formula": formula_db} if formula_db else {}

        return cls(
            codigo=codigo,
            nombre=getattr(metrica_db, "nombre", codigo),
            version=str(getattr(metrica_db, "version", "1.0")),
            tipo=oficial.tipo if oficial else "derivada",
            familia=oficial.familia if oficial else getattr(metrica_db, "categoria", "otro"),
            unidad=getattr(metrica_db, "unidad_resultado", "") or (oficial.unidad if oficial else ""),
            precision_decimales=oficial.precision_decimales if oficial else 2,
            estrategia=estrategia,
            descripcion=getattr(metrica_db, "descripcion", ""),
        )
