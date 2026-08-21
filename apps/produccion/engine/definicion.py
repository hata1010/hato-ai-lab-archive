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
        """Construye una definición ejecutable desde cualquier instancia de Metrica.

        Prioridad de resolución:
        1. Código oficial del catálogo V1.
        2. Motor de referencia V1 explícito.
        3. Fórmula almacenada en BD.
        4. Fallback por categoría para métricas personalizadas.
        """
        from .catalogo_v1 import METRICAS_V1

        codigo = (getattr(metrica_db, "codigo", "") or "").strip().upper()
        nombre = getattr(metrica_db, "nombre", codigo)
        categoria = (getattr(metrica_db, "categoria", "poblacion") or "poblacion").strip().lower()
        unidad = getattr(metrica_db, "unidad_resultado", "") or ""
        descripcion = getattr(metrica_db, "descripcion", "") or ""
        formula = (getattr(metrica_db, "formula", "") or "").strip()

        # 1. Código oficial del catálogo V1.
        oficial = METRICAS_V1.get(codigo)
        if oficial is not None:
            return cls(
                codigo=codigo,
                nombre=nombre,
                version=str(getattr(metrica_db, "version", "1.0")),
                tipo=oficial.tipo,
                familia=oficial.familia,
                unidad=unidad or oficial.unidad,
                precision_decimales=oficial.precision_decimales,
                estrategia=oficial.estrategia,
                descripcion=descripcion or oficial.descripcion,
            )

        # 2. Motor de referencia V1 explícito.
        referencia = (getattr(metrica_db, "motor_referencia", "") or "").strip().upper()
        if referencia:
            motor_base = METRICAS_V1.get(referencia)
            if motor_base is not None:
                return cls(
                    codigo=codigo,
                    nombre=nombre,
                    version=str(getattr(metrica_db, "version", "1.0")),
                    tipo=motor_base.tipo,
                    familia=motor_base.familia,
                    unidad=unidad or motor_base.unidad,
                    precision_decimales=motor_base.precision_decimales,
                    estrategia=motor_base.estrategia,
                    descripcion=descripcion or motor_base.descripcion,
                )

        # 3. Fórmula matemática definida en BD.
        if formula:
            return cls(
                codigo=codigo,
                nombre=nombre,
                version=str(getattr(metrica_db, "version", "1.0")),
                tipo="derivada",
                familia=categoria,
                unidad=unidad or "numero",
                precision_decimales=2,
                estrategia={"modo": "formula", "formula": formula},
                descripcion=descripcion,
            )

        # 4. Fallback por categoría para códigos personalizados.
        mapa_categoria = {
            "peso": "PESO_PROMEDIO_FINCA",
            "productividad": "PESO_TOTAL_FINCA",
            "ganado": "CANT_ANIMALES_TOTAL",
            "poblacion": "CANT_ANIMALES_TOTAL",
            "potreros": "SUP_TOTAL_POTREROS",
            "territorial": "SUP_TOTAL_POTREROS",
            "crecimiento": "GMD_INDIVIDUAL",
            "salud": "CANT_ANIMALES_TOTAL",
            "economia": "CARGA_ANIMAL_HA",
            "sostenibilidad": "CARGA_ANIMAL_HA",
            "otro": "CANT_ANIMALES_TOTAL",
        }
        codigo_base = mapa_categoria.get(categoria, "CANT_ANIMALES_TOTAL")
        base = METRICAS_V1[codigo_base]

        return cls(
            codigo=codigo,
            nombre=nombre,
            version=str(getattr(metrica_db, "version", "1.0")),
            tipo=base.tipo,
            familia=base.familia,
            unidad=unidad or base.unidad,
            precision_decimales=base.precision_decimales,
            estrategia=base.estrategia,
            descripcion=descripcion or base.descripcion,
        )
