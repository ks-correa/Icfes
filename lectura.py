"""Lee únicamente las entradas editables del Excel (sin ejecutar macros ni fórmulas)."""
from zipfile import ZipFile
from io import BytesIO
from pathlib import PurePosixPath
from xml.etree import ElementTree as ET
from modelo import P,PROFILES,validate
NS={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main','r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships','p':'http://schemas.openxmlformats.org/package/2006/relationships'}
def read_profiles(data):
    z=ZipFile(BytesIO(data) if isinstance(data,bytes) else data)
    with z:
        workbook=ET.fromstring(z.read('xl/workbook.xml'))
        rels=ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))
        targets={x.attrib['Id']:x.attrib['Target'] for x in rels}
        sheet=next((x for x in workbook.findall('s:sheets/s:sheet',NS) if x.attrib['name']=='FinOps entradas'),None)
        if sheet is None:raise ValueError('No se encuentra la hoja FinOps entradas.')
        target=targets[sheet.attrib['{'+NS['r']+'}id']];target=target.lstrip('/') if target.startswith('/') else str(PurePosixPath('xl')/target)
        shared=[]
        if 'xl/sharedStrings.xml' in z.namelist():shared=[''.join(t.text or '' for t in x.findall('.//s:t',NS)) for x in ET.fromstring(z.read('xl/sharedStrings.xml'))]
        def value(c):
            if c.find('s:f',NS) is not None:raise ValueError(f'La entrada {c.get("r")} debe ser numérica y no una fórmula.')
            v=c.findtext('s:v',None,NS)
            if c.get('t')=='s':return shared[int(v)]
            if c.get('t')=='inlineStr':return ''.join(t.text or '' for t in c.findall('.//s:t',NS))
            if c.get('t')=='str':return v
            return float(v) if v is not None else None
        results={n:{} for n in PROFILES}
        for row in ET.fromstring(z.read(target)).findall('s:sheetData/s:row',NS):
            cells={''.join(x for x in c.get('r','') if x.isalpha()):c for c in row}
            if 'A' not in cells:continue
            k=value(cells['A'])
            if k not in {p[0] for p in P}:continue
            for col,n in zip('DEF',PROFILES):
                if col not in cells:raise ValueError(f'Falta {n}: {k}')
                results[n][k]=value(cells[col])
        for n,p in results.items():
            if set(p)!={v[0] for v in P}:raise ValueError(f'Faltan entradas en {n}.')
            validate(p)
        return results
