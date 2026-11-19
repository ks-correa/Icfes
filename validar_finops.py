"""Contrasta resultados Python con fórmulas calculadas y guardadas en Excel.
Ejecutar después de copiar Finanzas_ICFES.xlsx definitivo junto a app.py.
No regenera ni modifica el libro: utilizar una copia recalculada y guardada.
"""
from pathlib import Path
from zipfile import ZipFile
from xml.etree import ElementTree as ET
from datetime import datetime, timezone
import csv, hashlib, math, posixpath, subprocess, sys
from modelo import evaluate
from lectura import read_profiles

ROOT = Path(__file__).resolve().parent
BOOK = ROOT / "Finanzas_ICFES.xlsx"
NS = {"s":"http://schemas.openxmlformats.org/spreadsheetml/2006/main",
      "r":"http://schemas.openxmlformats.org/officeDocument/2006/relationships"}
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def cached_sheets(path):
    with ZipFile(path) as z:
        workbook = ET.fromstring(z.read("xl/workbook.xml"))
        rels = {x.get("Id"):x.get("Target") for x in ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))}
        shared = []
        if "xl/sharedStrings.xml" in z.namelist():
            shared = ["".join(t.text or "" for t in x.findall(".//s:t",NS))
                      for x in ET.fromstring(z.read("xl/sharedStrings.xml"))]
        sheets = {}
        for s in workbook.findall("s:sheets/s:sheet",NS):
            target = rels[s.get("{"+NS["r"]+"}id")]
            target = target.lstrip("/") if target.startswith("/") else posixpath.normpath("xl/"+target)
            cells = {}
            for c in ET.fromstring(z.read(target)).findall(".//s:sheetData/s:row/s:c",NS):
                t = c.get("t"); v = c.findtext("s:v",None,NS)
                if t == "e": raise ValueError(f"Error de Excel: {s.get('name')}!{c.get('r')}: {v}")
                if t == "s": v = shared[int(v)] if v is not None else None
                elif t == "inlineStr": v = "".join(x.text or "" for x in c.findall(".//s:t",NS))
                elif t == "b": v = v == "1"
                elif t not in ("str","d") and v is not None: v = float(v)
                cells[c.get("r")] = (v,c.findtext("s:f",None,NS))
            sheets[s.get("name")] = cells
        return sheets

def compare():
    profiles = read_profiles(BOOK)
    sheets = cached_sheets(BOOK)
    rows = []
    def check(profile,sheet,cell,key,python_value,tol=0.01):
        excel_value,formula = sheets[sheet].get(cell,(None,None))
        if formula is None: raise ValueError(f"Se esperaba fórmula: {sheet}!{cell}")
        if python_value is None: python_value = "No recupera en 36 meses"
        ok = (math.isclose(float(excel_value),float(python_value),rel_tol=0,abs_tol=tol)
              if isinstance(excel_value,(int,float)) and isinstance(python_value,(int,float))
              else excel_value == python_value)
        rows.append([profile,sheet,cell,key,excel_value,python_value,ok])
    for i,(profile,p) in enumerate(profiles.items()):
        r=evaluate(p); d=r["calcs"]; flow=r["flow"]; tc="BCD"[i]; cc="CDE"[i]
        for row,key in [(3,"manual"),(7,"econ"),(8,"cash"),(9,"saving"),(10,"cash_saving"),
                        (11,"roi"),(12,"cash_roi"),(13,"investment_roi"),(14,"payback_econ"),
                        (15,"payback"),(33,"payback_econ_sustained"),(34,"payback_sustained")]:
            check(profile,"TCO y rentabilidad",f"{tc}{row}",key,r[key],1e-9 if row in (11,12,13) else .01)
        for row,key in [(4,"capex"),(16,"cost_load"),(17,"cost_post"),(20,"staff"),(26,"capex_econ")]:
            check(profile,"TCO y rentabilidad",f"{tc}{row}",key,d[key])
        for row,key in [(24,"budget_margin"),(28,"custody_tail"),(29,"risk_avoided"),(30,"risk_roi")]:
            check(profile,"Decisión empresarial",f"{tc}{row}",key,r[key],1e-9 if row==30 else .01)
        for row,key in [(13,"alerts"),(84,"train_initial_econ"),(85,"train_initial"),(88,"capex"),(91,"capex_econ")]:
            check(profile,"FinOps cálculo",f"{cc}{row}",key,d[key])
        for j,(name,value) in enumerate(r["routes"].items(),2):
            check(profile,"Costo por recorrido",f"{tc}{j}",name,value)
        for j,f in enumerate(flow,2+36*i):
            for col,key in zip("BCDEFGHIJKLMNOPQRS",("month","active","loads","new","stock","manual","labor","cashlabor","fixed","variable","storage","training","econ","cash","net_e","net_c","bal_e","bal_c")):
                check(profile,"Flujo 36m",f"{col}{j}",key,f[key])
    with (ROOT/"CONTRASTE_EXCEL.csv").open("w",encoding="utf-8-sig",newline="") as f:
        w=csv.writer(f); w.writerow(["Escenario","Hoja","Celda","Indicador","Excel calculado","Python","Coincide"]); w.writerows(rows)
    failures=[row for row in rows if not row[-1]]
    return len(rows),failures

def main():
    if not BOOK.is_file(): raise SystemExit("Copia el Excel definitivo como Finanzas_ICFES.xlsx.")
    log=[f"Fecha UTC: {datetime.now(timezone.utc).isoformat()}",f"Excel SHA-256: {sha(BOOK)}",
         f"modelo.py SHA-256: {sha(ROOT/'modelo.py')}",f"app.py SHA-256: {sha(ROOT/'app.py')}",
         "Contraste: fórmulas calculadas y guardadas en el libro frente a evaluación Python; no solo entradas."]
    run=subprocess.run([sys.executable,"-m","unittest","-v"],cwd=ROOT,capture_output=True,text=True,encoding="utf-8",errors="replace")
    log.extend([run.stdout,run.stderr])
    ok=run.returncode==0 and "skipped=" not in run.stderr
    try:
        count,bad=compare(); log.append(f"Contraste Excel-Python: {count-len(bad)}/{count} coincidencias; {len(bad)} diferencias.")
        log.extend(map(str,bad[:20])); ok=ok and not bad
    except Exception as exc:
        log.append(f"Contraste NO COMPLETADO: {exc}"); ok=False
    try:
        from streamlit.testing.v1 import AppTest
        at=AppTest.from_file(str(ROOT/"app.py"),default_timeout=60).run()
        for name in ("Optimista","Base","Pesimista"):
            at.radio[1].set_value(name).run()
            if len(at.exception): raise RuntimeError(str(at.exception))
            if not len(at.metric): raise RuntimeError("No aparecen indicadores.")
            log.append(f"AppTest perfil {name}: OK, {len(at.metric)} indicadores.")
        at.radio[0].set_value("Parámetros").run()
        if len(at.exception): raise RuntimeError(str(at.exception))
        if not len(at.number_input): raise RuntimeError("No aparecen parámetros.")
        log.append("AppTest vista Parámetros: OK.")
    except Exception as exc:
        log.append(f"AppTest NO COMPLETADO: {exc}"); ok=False
    log.append("RESULTADO: "+("APROBADO" if ok else "REVISAR"))
    result="\n".join(log)+"\n"
    (ROOT/"EVIDENCIA_FINOPS.txt").write_text(result,encoding="utf-8")
    print(result)
    return 0 if ok else 1

if __name__=="__main__":
    raise SystemExit(main())
