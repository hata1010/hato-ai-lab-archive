from django.shortcuts import render, get_object_or_404, redirect
from django.core.exceptions import PermissionDenied
from django.views.decorators.http import require_POST
from django.db.models import Q

from apps.core.models import Finca, Potrero
from apps.ganado.models import Animal
from apps.core.tenant import (
    obtener_finca_activa,
    obtener_fincas_usuario,
    verificar_acceso_finca,
)
from apps.produccion.models import Metrica
from apps.produccion.forms import MetricaForm
from apps.produccion.services.indicadores import obtener_indicadores_finca
from apps.produccion.engine.plan import PlanMetrica
from apps.produccion.engine import (
    EjecutorMotorV1,
    obtener_metrica_v1,
    METRICAS_V1,
    DefinicionMetrica,
)
from apps.produccion.global_views import (
    metricas_globales_lista,
    crear_editar_metrica_global,
    contraste_global_metrica,
    toggle_metrica_global,
)


def dashboard(request):
    finca = obtener_finca_activa(request)
    contexto = {
        "titulo": "Administración de la Finca",
        "finca": finca,
        "fincas_disponibles": obtener_fincas_usuario(request.user),
    }
    return render(request, "administrador/dashboard.html", contexto)


def indicadores(request):
    finca = obtener_finca_activa(request)
    indicadores_list = []
    if finca:
        indicadores_list = obtener_indicadores_finca(finca=finca)
    contexto = {
        "finca": finca,
        "fincas_disponibles": obtener_fincas_usuario(request.user),
        "indicadores": indicadores_list,
    }
    return render(request, "administrador/indicadores.html", contexto)


def lista_metricas(request):
    """Muestra el listado de métricas de la finca activa y globales."""
    finca = obtener_finca_activa(request)
    fincas_disponibles = obtener_fincas_usuario(request.user)
    if getattr(request.user, "is_superuser", False):
        if finca:
            metricas = Metrica.objects.filter(Q(finca=finca) | Q(finca__isnull=True))
        else:
            metricas = Metrica.objects.all()
    else:
        if finca:
            metricas = Metrica.objects.filter(Q(finca=finca) | Q(finca__isnull=True))
        else:
            metricas = Metrica.objects.filter(finca__isnull=True)
    contexto = {
        "finca": finca,
        "fincas_disponibles": fincas_disponibles,
        "metricas": metricas.order_by("-finca_id", "categoria", "nombre"),
        "catalogo_v1": METRICAS_V1,
    }
    return render(request, "produccion/metricas_lista.html", contexto)


def crear_editar_metrica(request, metrica_id=None):
    finca = obtener_finca_activa(request)
    fincas_disponibles = obtener_fincas_usuario(request.user)
    instancia = None
    if metrica_id:
        instancia = get_object_or_404(Metrica, id=metrica_id)
        if instancia.finca and not verificar_acceso_finca(request.user, instancia.finca):
            raise PermissionDenied("No tienes autorización para editar métricas de esta finca.")
        if instancia.finca is None and not getattr(request.user, "is_superuser", False):
            raise PermissionDenied("Solo el superusuario puede editar métricas globales del sistema.")
    if request.method == "POST":
        form = MetricaForm(request.POST, instance=instancia)
        if form.is_valid():
            metrica = form.save(commit=False)
            if not instancia and finca:
                metrica.finca = finca
            metrica.save()
            return redirect("produccion:lista_metricas")
    else:
        form = MetricaForm(instance=instancia)
    contexto = {
        "form": form,
        "metrica": instancia,
        "finca": finca,
        "fincas_disponibles": fincas_disponibles,
        "es_edicion": instancia is not None,
    }
    return render(request, "produccion/metrica_form_y_prueba.html", contexto)


def probar_metrica(request, metrica_id=None):
    """Laboratorio interactivo de prueba en vivo con resolución robusta de métricas."""
    finca = obtener_finca_activa(request)
    fincas_disponibles = obtener_fincas_usuario(request.user)
    if getattr(request.user, "is_superuser", False):
        if finca:
            metricas_disponibles = Metrica.objects.filter(Q(finca=finca) | Q(finca__isnull=True), activa=True)
        else:
            metricas_disponibles = Metrica.objects.filter(activa=True)
    else:
        if finca:
            metricas_disponibles = Metrica.objects.filter(Q(finca=finca) | Q(finca__isnull=True), activa=True)
        else:
            metricas_disponibles = Metrica.objects.filter(finca__isnull=True, activa=True)

    id_seleccionada = request.GET.get("metrica_id") or metrica_id
    metrica_db = None
    if id_seleccionada:
        metrica_db = metricas_disponibles.filter(id=id_seleccionada).first()
    if not metrica_db:
        metrica_db = metricas_disponibles.first()

    if metrica_db and metrica_db.finca and not finca:
        if verificar_acceso_finca(request.user, metrica_db.finca):
            finca = metrica_db.finca

    sexo = request.GET.get("sexo", "")
    nombres_filtro = {"": "Todos", "H": "Hembras (H)", "M": "Machos (M)"}
    filtro_nombre = nombres_filtro.get(sexo, "Todos")
    contexto_eval = {"sexo": sexo} if sexo in ("H", "M") else {}
    resultado = None
    error = None
    def_v1 = None

    if metrica_db and finca:
        def_v1 = DefinicionMetrica.desde_modelo(metrica_db)
        ejecutor = EjecutorMotorV1()

        if def_v1.familia in ("poblacion", "peso", "ganado"):
            datos_fuente = Animal.objects.filter(finca=finca)
            if sexo in ("H", "M"):
                datos_fuente = datos_fuente.filter(sexo=sexo)
        elif def_v1.familia in ("territorial", "potreros"):
            datos_fuente = [p.area_hectareas for p in Potrero.objects.filter(finca=finca, is_active=True)]
        elif def_v1.familia == "crecimiento":
            datos_fuente = Animal.objects.filter(finca=finca, pesajes__isnull=False).distinct().first()
        elif def_v1.familia in ("capacidad_carga", "productividad", "sostenibilidad"):
            total_anim = Animal.objects.filter(finca=finca, estado="activo").count()
            total_ha = sum(p.area_hectareas for p in Potrero.objects.filter(finca=finca, is_active=True) if p.area_hectareas)
            datos_fuente = {"animales": total_anim, "hectareas": total_ha}
        else:
            datos_fuente = Animal.objects.filter(finca=finca)

        resultado = ejecutor.ejecutar(def_v1, datos_fuente, contexto=contexto_eval)
    elif not metrica_db:
        error = "No existen métricas activas para evaluar en esta finca."

    contexto = {
        "finca": finca,
        "fincas_disponibles": fincas_disponibles,
        "metricas_disponibles": metricas_disponibles,
        "metrica": metrica_db,
        "definicion_v1": def_v1,
        "sexo": sexo,
        "filtro_nombre": filtro_nombre,
        "resultado": resultado,
        "error": error,
    }
    return render(request, "produccion/metrica_probar.html", contexto)


@require_POST
def toggle_metrica_activa(request, metrica_id):
    metrica = get_object_or_404(Metrica, id=metrica_id)
    if metrica.finca and not verificar_acceso_finca(request.user, metrica.finca):
        raise PermissionDenied("No tienes autorización para modificar esta métrica.")
    if metrica.finca is None and not getattr(request.user, "is_superuser", False):
        raise PermissionDenied("Solo el superusuario puede modificar métricas globales.")
    metrica.activa = not metrica.activa
    metrica.save()
    return redirect(request.META.get("HTTP_REFERER") or "produccion:lista_metricas")


def prueba_motor(request):
    finca = obtener_finca_activa(request)
    fincas_disponibles = obtener_fincas_usuario(request.user)
    sexo = request.GET.get("sexo", "")
    metrica = request.GET.get("metrica", "peso_promedio")
    animales = Animal.objects.filter(finca=finca) if finca else Animal.objects.none()
    pasos = []
    if sexo in ("H", "M"):
        pasos.append({"funcion": "FILTRO", "parametros": {"campo": "sexo", "valor": sexo}})
    nombre_metrica = ""
    unidad = ""
    if metrica == "peso_promedio":
        pasos.extend([{"funcion": "MAPEAR", "parametros": {"funcion": "PESO_ACTUAL"}}, {"funcion": "PROMEDIO"}])
        nombre_metrica, unidad = "Peso promedio", "kg"
    elif metrica == "peso_total":
        pasos.extend([{"funcion": "MAPEAR", "parametros": {"funcion": "PESO_ACTUAL"}}, {"funcion": "SUMA"}])
        nombre_metrica, unidad = "Peso total", "kg"
    elif metrica == "cantidad":
        pasos.append({"funcion": "CONTEO"})
        nombre_metrica, unidad = "Cantidad de animales", "animales"
    else:
        metrica = "peso_promedio"
        pasos.extend([{"funcion": "MAPEAR", "parametros": {"funcion": "PESO_ACTUAL"}}, {"funcion": "PROMEDIO"}])
        nombre_metrica, unidad = "Peso promedio", "kg"
    plan = PlanMetrica(nombre=nombre_metrica, pasos=pasos)
    validacion = plan.validar()
    resultado = None
    error = None
    if validacion.get("valido", False) and animales.exists():
        try:
            resultado = plan.ejecutar(animales)
        except Exception as exc:
            error = str(exc)
    explicacion = plan.explicar()
    sexo_nombre = {"": "Todos", "H": "Hembras", "M": "Machos"}.get(sexo, "Todos")
    contexto = {
        "fincas": fincas_disponibles, "finca": finca, "sexo": sexo, "sexo_nombre": sexo_nombre,
        "metrica": metrica, "nombre_metrica": nombre_metrica, "unidad": unidad,
        "resultado": resultado, "error": error, "validacion": validacion,
        "explicacion": explicacion, "animales_count": animales.count(),
    }
    return render(request, "produccion/prueba_motor.html", contexto)
