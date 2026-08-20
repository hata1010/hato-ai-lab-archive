"""Validador seguro de estrategias declarativas del motor de métricas.

Acepta únicamente los dos formatos soportados por el motor:
- pipeline: pasos compuestos exclusivamente por funciones de la whitelist.
- formula: expresión aritmética evaluable por el evaluador AST seguro.
"""

import ast
from typing import Any, Dict

from .compositor import Compositor
from .evaluador import OPERADORES
from .excepciones import ErrorCalculoMetrica, ErrorComposicion
from .funciones import FUNCIONES


_ALLOWED_AST_NODES = (
    ast.Expression,
    ast.BinOp,
    ast.UnaryOp,
    ast.Constant,
    ast.Name,
    ast.Load,
    ast.operator,
    ast.unaryop,
)


def validar_estrategia_dsl(estrategia: Dict[str, Any]) -> bool:
    """Valida una estrategia sin ejecutar código proporcionado por el usuario."""
    if not isinstance(estrategia, dict):
        raise ErrorComposicion("La estrategia debe ser un objeto JSON/Diccionario.")

    modo = estrategia.get("modo")
    if modo not in ("pipeline", "formula"):
        raise ErrorComposicion(
            f"Modo de estrategia inválido: '{modo}'. Debe ser 'pipeline' o 'formula'."
        )

    if modo == "pipeline":
        pasos = estrategia.get("pasos")
        if not isinstance(pasos, list) or not pasos:
            raise ErrorComposicion("El modo pipeline requiere una lista no vacía de pasos.")

        for idx, paso in enumerate(pasos, start=1):
            if not isinstance(paso, dict):
                raise ErrorComposicion(f"El paso {idx} debe ser un objeto/diccionario.")
            codigo_fn = paso.get("funcion")
            if not codigo_fn:
                raise ErrorComposicion(f"El paso {idx} no especifica la clave 'funcion'.")
            if codigo_fn not in FUNCIONES:
                raise ErrorComposicion(
                    f"Función no autorizada o no registrada en la Whitelist: '{codigo_fn}' en paso {idx}."
                )

        resultado = Compositor().validar(pasos)
        if not resultado.get("valido", False):
            raise ErrorComposicion(f"La composición del pipeline es incompatible: {resultado}")
        return True

    formula = estrategia.get("formula")
    if not isinstance(formula, str) or not formula.strip():
        raise ErrorCalculoMetrica(
            "El modo formula requiere un texto de fórmula matemática no vacío."
        )

    try:
        arbol = ast.parse(formula, mode="eval")
    except SyntaxError as exc:
        raise ErrorCalculoMetrica(f"Sintaxis de fórmula inválida: {exc}") from exc

    for nodo in ast.walk(arbol):
        if not isinstance(nodo, _ALLOWED_AST_NODES):
            raise ErrorCalculoMetrica(
                f"Elemento no permitido en fórmula: '{type(nodo).__name__}'. "
                "Solo se admiten operaciones matemáticas básicas."
            )
        if isinstance(nodo, ast.BinOp) and type(nodo.op) not in OPERADORES:
            raise ErrorCalculoMetrica(
                f"Operador binario no permitido: {type(nodo.op).__name__}"
            )
        if isinstance(nodo, ast.UnaryOp) and type(nodo.op) not in OPERADORES:
            raise ErrorCalculoMetrica(
                f"Operador unario no permitido: {type(nodo.op).__name__}"
            )

    return True
