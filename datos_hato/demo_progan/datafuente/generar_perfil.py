import csv
from pathlib import Path

FUENTE = Path(".")
SALIDA = Path("analisis_37/paso_01_inventario")
SALIDA.mkdir(parents=True, exist_ok=True)

EXCLUIR = {
    "sqlite_sequence.csv",
    "inventario_37.csv",
    "estructura_37.csv",
    "perfil_datos_37.csv",
}

archivos = sorted(
    x for x in FUENTE.glob("*.csv")
    if x.name not in EXCLUIR
)

salida = SALIDA / "perfil_datos_37.csv"

with open(salida, "w", newline="", encoding="utf-8-sig") as out:
    writer = csv.writer(out)

    writer.writerow([
        "archivo",
        "campo",
        "filas",
        "vacios",
        "no_vacios",
        "distintos",
        "tipo_observado",
        "ejemplos"
    ])

    for archivo in archivos:

        with open(
            archivo,
            encoding="utf-8-sig",
            errors="replace",
            newline=""
        ) as f:
            reader = csv.DictReader(f)
            filas = list(reader)

        if not filas:
            continue

        campos = filas[0].keys()

        for campo in campos:

            valores = [
                str(fila.get(campo, "")).strip()
                for fila in filas
            ]

            no_vacios = [
                valor for valor in valores
                if valor != ""
            ]

            distintos = list(dict.fromkeys(no_vacios))

            numeros = []

            for valor in no_vacios:
                try:
                    float(valor)
                    numeros.append(valor)
                except ValueError:
                    pass

            if no_vacios and len(numeros) == len(no_vacios):

                if all("." not in valor for valor in no_vacios):
                    tipo = "ENTERO"
                else:
                    tipo = "DECIMAL"

            else:
                tipo = "TEXTO"

            ejemplos = " | ".join(distintos[:5])

            writer.writerow([
                archivo.name,
                campo,
                len(valores),
                len(valores) - len(no_vacios),
                len(no_vacios),
                len(distintos),
                tipo,
                ejemplos
            ])

print()
print("==============================================")
print(" PERFIL DE DATOS GENERADO")
print("==============================================")
print(f"Archivos fuente analizados: {len(archivos)}")
print(f"Resultado: {salida}")
print("==============================================")