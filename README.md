# FinOps ICFES — entrega final

Simulador de arquitectura empresarial. WhatsApp Cloud API principal; Amazon SES complementario; portal web responsivo.

## Ejecución

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
.\.venv\Scripts\python -m unittest -v
.\.venv\Scripts\python -m streamlit run app.py
```

Copia **Finanzas_ICFES.xlsx** actualizado junto a app.py o cárgalo en la interfaz. Sin él, se utilizan los perfiles integrados corregidos. El Excel anterior y sus evidencias son históricos, no compatibles con las nuevas entradas. Sustituye el archivo de esta rama por el Excel definitivo antes de validar.

## Línea base y supuestos

90.000 aspirantes/año; 144.000 cargas AS-IS estimadas suponiendo 15% × cuatro reenvíos adicionales; 108.000 cargas TO-BE base como meta; 3 MB; cinco años de retención; 10% responsabilidad 48, 80% elegible en base; dos revisores objetivo. Techo de $504 M COP. El escenario base presupone 80% de ahorro laboral liberado, 50% incremental de Contabilidad y soporte/auditoría, y 5% revisión humana. Validar en piloto.

WhatsApp: utilidad, autenticación, servicio facturable y marketing opcional con tarifas de referencia Colombia 01/10/2026. Correo presupuestado en todas las rondas. Quick Win de $9,64 M incluido en CapEx. Custodia posterior al mes 36 separada. ROI de riesgos es una sensibilidad sin pérdidas inventadas.

## Validación final

1. Copiar el Excel definitivo junto a app.py con el nombre Finanzas_ICFES.xlsx.
2. Si se modificó el libro, recalcular todas las fórmulas en Excel (Ctrl+Alt+F9) y guardar.
3. Ejecutar `python validar_finops.py` en el entorno virtual. Genera EVIDENCIA_FINOPS.txt y CONTRASTE_EXCEL.csv con las pruebas unitarias, el contraste de los tres escenarios y los 36 meses de cada uno, y AppTest. Un resultado REVISAR no acredita aceptación.

CapEx económico incluye la capacitación inicial completa; CapEx caja incluye únicamente capacitación incremental. El flujo y TCO económico parten del primero; caja del segundo. Las evidencias históricas quedan en el historial de Git. La verificación debe realizarse con el libro definitivo.
