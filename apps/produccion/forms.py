"""Formularios para la administración de definiciones de métricas en Hato V1 y Globales."""

from django import forms
from apps.produccion.models import Metrica
from apps.produccion.engine.catalogo_v1 import METRICAS_V1

CODIGO_CALCULO_CHOICES = [
    (m.codigo, f"{m.nombre} ({m.codigo}) — {m.unidad}")
    for m in METRICAS_V1.values()
]


class MetricaForm(forms.ModelForm):
    """Formulario para métricas locales pertenecientes a una finca."""
    codigo = forms.ChoiceField(
        choices=CODIGO_CALCULO_CHOICES,
        label="Motor de Cálculo (Catálogo V1)",
        help_text="Seleccione la fórmula/motor del catálogo oficial V1 que ejecutará esta métrica.",
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    class Meta:
        model = Metrica
        fields = [
            "nombre", "codigo", "categoria", "unidad_resultado", "periodicidad",
            "tipo_resultado", "descripcion", "activa",
        ]
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej. Ganancia Media Diaria Lote Ceba"}),
            "categoria": forms.Select(attrs={"class": "form-select"}),
            "unidad_resultado": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej. kg/día, cab/ha, animales"}),
            "periodicidad": forms.Select(attrs={"class": "form-select"}),
            "tipo_resultado": forms.Select(attrs={"class": "form-select"}),
            "descripcion": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Describa el objetivo zootécnico o productivo de esta métrica."}),
            "activa": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.codigo:
            codigos_actuales = [c[0] for c in CODIGO_CALCULO_CHOICES]
            if self.instance.codigo not in codigos_actuales:
                self.fields["codigo"].choices = [(self.instance.codigo, self.instance.codigo)] + CODIGO_CALCULO_CHOICES


class MetricaGlobalForm(forms.ModelForm):
    """Formulario exclusivo para ROOT. Nunca asigna una finca."""

    motor_referencia = forms.ChoiceField(
        choices=[("", "--- Personalizada / Fórmula directa ---")] + CODIGO_CALCULO_CHOICES,
        required=False,
        label="Motor Base de Referencia (Opcional)",
        help_text="Seleccione un cálculo V1 si la métrica global reutiliza un pipeline oficial.",
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    codigo = forms.CharField(
        max_length=50,
        label="Código Único del Sistema",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej. GMD_GLOBAL"}),
    )

    class Meta:
        model = Metrica
        fields = [
            "nombre", "codigo", "categoria", "unidad_resultado", "periodicidad",
            "tipo_resultado", "formula", "descripcion", "version", "activa",
        ]
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej. Ganancia Media Diaria Global"}),
            "categoria": forms.Select(attrs={"class": "form-select"}),
            "unidad_resultado": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej. kg/día"}),
            "periodicidad": forms.Select(attrs={"class": "form-select"}),
            "tipo_resultado": forms.Select(attrs={"class": "form-select"}),
            "formula": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Ej. (peso_final - peso_inicial) / dias"}),
            "descripcion": forms.Textarea(attrs={"class": "form-control", "rows": 4, "placeholder": "Especificación oficial de la métrica global."}),
            "version": forms.NumberInput(attrs={"class": "form-control", "min": 1}),
            "activa": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Al editar una global existente, mostrar la relación persistida.
        if self.instance and self.instance.motor_referencia:
            self.fields["motor_referencia"].initial = self.instance.motor_referencia

    def clean_codigo(self):
        codigo = self.cleaned_data.get("codigo", "").strip().upper()
        if not codigo:
            raise forms.ValidationError("El código es obligatorio.")
        qs = Metrica.objects.filter(finca__isnull=True, codigo=codigo)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError(f"Ya existe una métrica global oficial con el código '{codigo}'.")
        return codigo

    def save(self, commit=True):
        """Persiste también el motor V1 seleccionado en el registro global."""
        metrica = super().save(commit=False)
        metrica.motor_referencia = self.cleaned_data.get("motor_referencia", "") or ""
        if commit:
            metrica.save()
            self.save_m2m()
        return metrica
