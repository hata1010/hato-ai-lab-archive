from django.db import models
from apps.core.models import Finca


# ============================================================
# MÉTRICA
# ============================================================

class Metrica(models.Model):

    # ========================================================
    # CATEGORÍAS
    # ========================================================

    CATEGORIA_CHOICES = [
        ("productividad", "Productividad"),
        ("peso", "Peso"),
        ("ganado", "Ganado"),
        ("potreros", "Potreros"),
        ("alimentacion", "Alimentación"),
        ("reproduccion", "Reproducción"),
        ("salud", "Salud"),
        ("economia", "Economía"),
        ("sostenibilidad", "Sostenibilidad"),
        ("otro", "Otro"),
    ]

    PERIODICIDAD_CHOICES = [
        ("diaria", "Diaria"),
        ("semanal", "Semanal"),
        ("mensual", "Mensual"),
        ("trimestral", "Trimestral"),
        ("semestral", "Semestral"),
        ("anual", "Anual"),
        ("variable", "Variable"),
    ]

    TIPO_RESULTADO_CHOICES = [
        ("numero", "Número"),
        ("cantidad", "Cantidad"),
        ("peso", "Peso"),
        ("porcentaje", "Porcentaje"),
        ("volumen", "Volumen"),
        ("moneda", "Moneda"),
        ("indice", "Índice"),
        ("booleano", "Verdadero / Falso"),
    ]

    finca = models.ForeignKey(
        Finca,
        on_delete=models.PROTECT,
        related_name="metricas",
        null=True,
        blank=True,
        verbose_name="Finca",
        help_text="Finca propietaria de esta definición de métrica.",
    )

    nombre = models.CharField(max_length=200, verbose_name="Nombre")

    codigo = models.CharField(
        max_length=50,
        verbose_name="Código",
        help_text="Identificador utilizado por el motor de métricas. Ejemplo: GDP",
    )

    descripcion = models.TextField(blank=True, verbose_name="Descripción")

    categoria = models.CharField(
        max_length=30,
        choices=CATEGORIA_CHOICES,
        default="productividad",
        verbose_name="Categoría",
    )

    unidad_resultado = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Unidad del resultado",
        help_text="Ejemplo: kg/animal/día, litros, %, animales, COP.",
    )

    periodicidad = models.CharField(
        max_length=20,
        choices=PERIODICIDAD_CHOICES,
        default="variable",
        verbose_name="Periodicidad",
    )

    tipo_resultado = models.CharField(
        max_length=20,
        choices=TIPO_RESULTADO_CHOICES,
        default="numero",
        verbose_name="Tipo de resultado",
    )

    formula = models.TextField(
        blank=True,
        verbose_name="Fórmula",
        help_text="Expresión que define el cálculo de la métrica. Ejemplo: (PESO_FINAL - PESO_INICIAL) / DIAS",
    )

    # Código del motor V1 que debe ejecutar esta definición global.
    # Se persiste explícitamente porque el código global (p. ej.
    # PESO_PROMEDIO_GLOBAL) no tiene por qué existir como función V1.
    motor_referencia = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Motor base de referencia",
        help_text="Código del motor V1 utilizado para evaluar esta métrica global.",
    )

    activa = models.BooleanField(default=True, verbose_name="Activa")

    version = models.PositiveIntegerField(default=1, verbose_name="Versión")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última actualización")

    class Meta:
        ordering = ["categoria", "nombre"]
        verbose_name = "Métrica"
        verbose_name_plural = "Métricas"
        constraints = [
            models.UniqueConstraint(fields=["finca", "codigo"], name="metrica_codigo_unico_por_finca"),
            models.UniqueConstraint(fields=["finca", "nombre"], name="metrica_nombre_unico_por_finca"),
        ]

    def __str__(self):
        if self.finca:
            return f"{self.finca.nombre} → {self.codigo} - {self.nombre}"
        return f"{self.codigo} - {self.nombre}"


# ============================================================
# VARIABLES DE LA MÉTRICA
# ============================================================

class VariableMetrica(models.Model):
    TIPO_CHOICES = [
        ("dato", "Dato"),
        ("calculada", "Calculada"),
        ("parametro", "Parámetro"),
    ]

    REGLA_CHOICES = [
        ("directo", "Valor directo"),
        ("primero", "Primer valor del período"),
        ("ultimo", "Último valor del período"),
        ("promedio", "Promedio"),
        ("suma", "Suma"),
        ("minimo", "Mínimo"),
        ("maximo", "Máximo"),
        ("diferencia_fechas", "Diferencia entre fechas"),
    ]

    metrica = models.ForeignKey(
        Metrica,
        on_delete=models.CASCADE,
        related_name="variables",
        verbose_name="Métrica",
    )

    nombre = models.CharField(max_length=100, verbose_name="Nombre")

    codigo = models.CharField(
        max_length=50,
        verbose_name="Código",
        help_text="Nombre utilizado dentro de la fórmula. Ejemplo: PESO_INICIAL",
    )

    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default="dato", verbose_name="Tipo")

    fuente = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Fuente",
        help_text="Modelo o fuente de donde se obtiene el dato. Ejemplo: PesajeAnimal",
    )

    campo = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Campo",
        help_text="Campo de la fuente utilizado. Ejemplo: peso_kg",
    )

    regla = models.CharField(max_length=30, choices=REGLA_CHOICES, default="directo", verbose_name="Regla")

    orden = models.PositiveIntegerField(default=0, verbose_name="Orden")

    activa = models.BooleanField(default=True, verbose_name="Activa")

    class Meta:
        ordering = ["orden", "codigo"]
        verbose_name = "Variable de Métrica"
        verbose_name_plural = "Variables de Métrica"
        constraints = [
            models.UniqueConstraint(fields=["metrica", "codigo"], name="variable_codigo_unico_por_metrica")
        ]

    def __str__(self):
        return f"{self.metrica.codigo} → {self.codigo}"
