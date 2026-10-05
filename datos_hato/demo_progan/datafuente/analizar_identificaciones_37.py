import csv
from pathlib import Path
from collections import defaultdict

BASE=Path(".")
OUT=BASE/"analisis_37"/"paso_01_inventario"
OUT.mkdir(parents=True,exist_ok=True)

targets={
    "arete":["arete"],
    "nro_chip":["nro_chip"],
    "id_cowpro":["id_cowpro"],
    "hierro":["hierro"],
}
animal_fields={"nro_animal","idem","idem_vaca","id_animal","nro_de_animal"}

files=sorted(p for p in BASE.glob("*.csv") if p.name not in {
    "sqlite_sequence.csv","inventario_37.csv","estructura_37.csv",
    "perfil_datos_37.csv","mapa_funcional_37.csv"
})

values={k:defaultdict(list) for k in targets}
coexist=[]

for path in files:
    with path.open("r",encoding="utf-8-sig",errors="replace",newline="") as f:
        reader=csv.DictReader(f)
        headers=reader.fieldnames or []
        cols={k:[h for h in hs if h in headers] for k,hs in targets.items()}
        cols={k:v for k,v in cols.items() if v}
        if not cols: continue

        for rn,row in enumerate(reader,start=2):
            refs={h:str(row.get(h,"") or "").strip() for h in headers if h in animal_fields}
            present={}
            for kind,hs in cols.items():
                for h in hs:
                    v=str(row.get(h,"") or "").strip()
                    if v:
                        present[kind]=v
                        values[kind][v].append((path.name,rn,refs))
            if present:
                coexist.append((path.name,rn,present,refs))

with (OUT/"identificaciones_37_resumen.csv").open("w",encoding="utf-8-sig",newline="") as f:
    w=csv.writer(f); w.writerow(["dispositivo","valores_distintos","registros_con_valor","ejemplos"])
    for k in targets:
        w.writerow([k,len(values[k]),sum(map(len,values[k].values())),
                     " | ".join(list(values[k])[:10])])

with (OUT/"identificaciones_37_detalle.csv").open("w",encoding="utf-8-sig",newline="") as f:
    w=csv.writer(f); w.writerow(["dispositivo","valor","apariciones","archivos","referencias_animal"])
    for k,vs in values.items():
        for v,occ in sorted(vs.items()):
            refs=[]
            for _,_,r in occ:
                refs += [f"{a}={b}" for a,b in r.items() if b]
            w.writerow([k,v,len(occ)," | ".join(sorted(set(x[0] for x in occ))),
                        " | ".join(list(dict.fromkeys(refs))[:20])])

with (OUT/"identificaciones_37_coexistencias.csv").open("w",encoding="utf-8-sig",newline="") as f:
    w=csv.writer(f); w.writerow(["archivo","fila","arete","nro_chip","id_cowpro","hierro","referencias_animal"])
    for fn,rn,p,r in coexist:
        w.writerow([fn,rn,p.get("arete",""),p.get("nro_chip",""),p.get("id_cowpro",""),
                    p.get("hierro","")," | ".join(f"{a}={b}" for a,b in r.items() if b)])

combo=defaultdict(int)
for _,_,p,_ in coexist:
    combo[" + ".join(k for k in targets if k in p)]+=1
with (OUT/"identificaciones_37_combinaciones.csv").open("w",encoding="utf-8-sig",newline="") as f:
    w=csv.writer(f); w.writerow(["combinacion_observada","filas"])
    for k,n in sorted(combo.items(),key=lambda x:-x[1]): w.writerow([k,n])

print("==============================================")
print(" ANALISIS DE IDENTIFICACIONES GENERADO")
print("==============================================")
print("Archivos fuente revisados:",len(files))
print("Resultados en:",OUT)
print("  identificaciones_37_resumen.csv")
print("  identificaciones_37_detalle.csv")
print("  identificaciones_37_coexistencias.csv")
print("  identificaciones_37_combinaciones.csv")
print("==============================================")
