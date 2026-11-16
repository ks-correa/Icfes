# Simulador FinOps ICFES — V4

Simulación nominal a 36 meses basada en Finanzas_ICFES_V4.xlsx. Las cifras de arquitectura y tarifas se consideran hipótesis presupuestarias, no resultados de un piloto. La línea base homologada es $504.000.000 COP. El perfil pesimista incorpora crecimiento de costos, por lo que su línea comparativa nominal es distinta.

## Origen de la interfaz

Adaptación del proyecto anterior [Ceroa](https://github.com/ks-correa/An-lisis-Ceroa-con-Streamlit): estilos de `dashboard_ui.py`, tarjetas de indicadores, gráficos Plotly, comparación de escenarios, desglose y guía de métricas. Los cálculos se implementan en `modelo.py` y las entradas se cargan desde `Finanzas_ICFES_V4.xlsx` mediante `lectura.py`.

## Ejecutar en Windows (PowerShell)

Abre esta carpeta en VS Code. Requiere Python 3.10 o superior y acceso a PyPI para instalar las dependencias.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Si `python` no está en PATH, utiliza `py -3 -m venv .venv`. No necesitas activar el entorno ni cambiar la política de ejecución de PowerShell. Abre la URL que muestra Streamlit (normalmente http://localhost:8501).

## Demostración
1. Selecciona Base, Optimista o Pesimista. El Excel incluido alimenta los tres perfiles; puedes cargar otra copia editada en la hoja «FinOps entradas».
2. Abre **Parámetros**, ajusta reenvíos To-Be, derivación a revisión, productividad, ahorro laboral realizado, inversión o tarifas y pulsa **Recalcular simulación**. Regresa a **Resultados** para consultar los cambios.
3. Revisa TCO económico, TCO caja, ROI y curva mensual de recuperación. El mes 0 es la inversión. Los períodos activos se distribuyen en el calendario anual; se acumula almacenamiento durante la retención.
4. Cambia páginas OCR, proporción de extracción avanzada y costo de mensajes; revisa costos por servicio y por recorrido. Los recorridos marginales no son sumables ni equivalen a costo total asignado.
5. Exporta parámetros y flujo mensual CSV. Los controles de la app no sobrescriben el Excel.

## Verificación

```powershell
.\.venv\Scripts\python.exe -m unittest -v test_modelo.py
```

Las 10 pruebas verifican los cálculos, validaciones, calendario, almacenamiento y correspondencia de los perfiles con el Excel V4.

`EVIDENCIA_FINOPS.txt` registra la ejecución de las pruebas y verificaciones de la interfaz. `CONTRASTE_EXCEL.csv` conserva el contraste histórico y añade los resultados actuales de V4, identificando las diferencias; no representa un recálculo independiente del Excel V4. El simulador calcula el primer cruce de recuperación, pero no ofrece un indicador independiente de payback sostenido.

### Comprobación local de CP-056 / CP-057

- Base: TCO manual $504.000.000; TCO económico $492.453.530,73; TCO caja $564.453.530,73. ROI económico 2,3447 %; ROI caja −10,7101 %. Sin recuperación de caja a 36 meses.
- Ajusta liberación efectiva de personal de 0,8 a 1,0: TCO caja = TCO económico (si no cambias otros parámetros); primer cruce económico/caja en el mes 26. El acumulado cae temporalmente por debajo de cero en mes 30.
- Cambia los reenvíos To-Be de 0,2 a 0,4: las cargas automáticas y el consumo aumentan; la línea manual no cambia.
- Cambia la productividad de revisión a 0,4: la dotación de revisión aumenta sin modificar la productividad de atención. Prueba una combinación inválida de ciclos y meses; debe mostrar error.
- Exporta ambos CSV y registra una captura de la interfaz, sus valores y la fecha de ejecución.

## Limitaciones

No es una cotización ni una plataforma tributaria productiva. RDS, conectividad, monitoreo, soporte y otros rubros agrupados son reservas de presupuesto; se deben cotizar para la región y la configuración aprobadas. Se utiliza una TRM presupuestaria y un recargo ilustrativo, no una tasa de cambio o impuesto oficial. El uso de software sin licencia incremental es una hipótesis que debe verificarse. No se proyectan costos de custodia posteriores al horizonte de 36 meses. La capacidad humana se calcula agregadamente; no acredita el cumplimiento de tiempos de espera.
