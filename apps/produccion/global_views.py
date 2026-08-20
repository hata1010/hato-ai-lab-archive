"""Vistas de Métricas Globales Oficiales, exclusivas para ROOT."""

from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.core.models import Finca
from apps.ganado.models import Animal
from apps.produccion.engine import EjecutorMotorV1, obtener_metrica_v1
from apps.produccion.forms import MetricaGlobalForm
from apps.produccion.models import Metrica


def _exigir_root(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        raise PermissionDenied("Solo ROOT puede administrar Métricas Globales Oficiales.")


def metricas_globales_lista(request):
    _exigir_root(request)
    metricas_globales = Metrica.objects.filter(finca__isnull=True).order_by("categoria", "nombre")
    contexto = {
        "metricas_globales": metricas_globales,
        "fincas_activas_count": Finca.objects.filter(is_active=True).count(),
    }
    return render(request, "produccion/metricas_globales_lista.html", contexto)


def crear_editar_metrica_global(request, metrica_id=None):
    _exigir_root(request)
    instancia = None
    if metrica_id is not None:
        instancia = get_object_or_404(Metrica, id=metrica_id, finca__isnull=True)

    if request.method == "POST":
        form = MetricaGlobalForm(request.POST, instance=instancia)
        if form.is_valid():
            metrica = form.save(commit=False)
            # Inviolable: una métrica administrada por esta vista nunca pertenece a una finca.
            metrica.finca = None
            # El formulario ya persistió motor_referencia en la instancia.
            metrica.save()
            return redirect("produccion:metricas_globales_lista")
    else:
        form = MetricaGlobalForm(instance=instancia)

    return render(
        request,
        "produccion/metrica_global_form.html",
        {"form": form, "metrica": instancia, "es_edicion": instancia is not None},
    )


def _evaluar_global_en_finca(metrica, finca):
    """Evalúa una métrica global mediante su motor V1 de referencia persistido."""
    codigo_motor = metrica.motor_referencia or metrica.codigo

    try:
        definicion = obtener_metrica_v1(codigo_motor)
    except ValueError:
        return {
            "es_valido": False,
            "valor": None,
            "unidad": metrica.unidad_resultado,
            "error": f"El motor de referencia '{codigo_motor}' no está registrado en el catálogo Motor V1.",
        }

    if definicion.familia in ("poblacion", "peso"):
        datos = Animal.objects.filter(finca=finca)
    else:
        return {
            "es_valido": False,
            "valor": None,
            "unidad": metrica.unidad_resultado,
            "error": "Familia V1 no conectada al contraste global.",
        }

    try:
        resultado = EjecutorMotorV1().ejecutar(definicion, datos, contexto={})
        return {
            "es_valido": getattr(resultado, "es_valido", False),
            "valor": getattr(resultado, "valor", None),
            "unidad": getattr(resultado, "unidad", None) or metrica.unidad_resultado,
            "error": getattr(resultado, "error", None),
        }
    except Exception as exc:
        return {
            "es_valido": False,
            "valor": None,
            "unidad": metrica.unidad_resultado,
            "error": str(exc),
        }


def contraste_global_metrica(request, metrica_id):
    _exigir_root(request)
    metrica = get_object_or_404(Metrica, id=metrica_id, finca__isnull=True)
    resultados_fincas = []
    fincas = Finca.objects.filter(is_active=True).order_by("nombre")

    for finca in fincas:
        resultados_fincas.append({
            "finca": finca,
            "total_animales": Animal.objects.filter(finca=finca).count(),
            "resultado": _evaluar_global_en_finca(metrica, finca),
        })

    return render(
        request,
        "produccion/metrica_global_contraste.html",
        {"metrica": metrica, "total_fincas": len(resultados_fincas), "resultados_fincas": resultados_fincas},
    )


@require_POST
def toggle_metrica_global(request, metrica_id):
    _exigir_root(request)
    metrica = get_object_or_404(Metrica, id=metrica_id, finca__isnull=True)
    metrica.activa = not metrica.activa
    metrica.save(update_fields=["activa", "updated_at"])
    return redirect("produccion:metricas_globales_lista")
