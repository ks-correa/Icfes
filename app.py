from pathlib import Path
import hashlib
import pandas as pd
import streamlit as st
import plotly.express as px
from dashboard_ui import aplicar_estilo, mostrar_grafica, mostrar_guia_metricas
from modelo import P,INTS,PROFILES,evaluate,validate
from lectura import read_profiles
st.set_page_config(page_title='FinOps ICFES',page_icon='📊',layout='wide',initial_sidebar_state='expanded')
aplicar_estilo()

def cop(v):return f'$ {v:,.0f}'.replace(',','.')
def m(v):return f'$ {v/1e6:,.2f} M'.replace(',',' ').replace('.',',')
def pct(v):return 'No aplica' if v is None else f'{v*100:.1f}%'.replace('.',',')
def pb(v):return 'No recupera en 36 meses' if v is None else f'Mes {v}'

st.title('ICFES | Simulador financiero FinOps')
st.caption('Propuesta de arquitectura empresarial · Simulación nominal a 36 meses · COP')
with st.sidebar:
    view=st.radio('Vista', ['Resultados', 'Parámetros'])
    st.header('Datos del escenario')
    upload=st.file_uploader('Modelo financiero actualizado (opcional)',type=['xlsx'])
    default_file=Path(__file__).parent/'Finanzas_ICFES.xlsx'
    try:
        data=upload.getvalue() if upload else (default_file.read_bytes() if default_file.exists() else None)
        profiles=read_profiles(data) if data is not None else {k:v.copy() for k,v in PROFILES.items()}
        token=hashlib.sha256(data).hexdigest()[:12] if data is not None else 'entrega-final'
        st.success('Entradas cargadas del Excel.' if data is not None else 'Perfiles actualizados integrados. Carga el nuevo Excel para contrastar.')
    except Exception as e:
        st.error(f'No se pudo leer el Excel financiero: {e}');st.stop()
    scenario=st.radio('Perfil',list(profiles),index=1)
    st.caption('Los controles modifican una copia del perfil; no sobrescriben el Excel.')
    st.markdown('---')
    st.caption('Horizonte: 36 meses · Serverless AWS · Escenarios financieros, no proveedores.')
    if st.button('Restaurar escenario'):
        for key in list(st.session_state):
            if key.startswith('fin_'):del st.session_state[key]
        st.rerun()
initial=profiles[scenario];state_key='fin_result_'+token+'_'+scenario
if state_key not in st.session_state:st.session_state[state_key]=dict(initial)
quick=['manual_re','re','review','min_r','peak','release','account_increment','shared_increment','trm','ocr_fraction','wa_marketing_n','wa_service_n','wa_auth_n','dev']
params={}

def widget(row):
    k,label,unit,b,source,group,o,pe,lo,hi=row
    v=st.session_state[state_key][k]
    if k in INTS:
        return st.number_input(label+f' ({unit})',min_value=int(lo),max_value=int(hi),value=int(v),step=1,key=f'fin_{token}_{scenario}_{k}',help=source)
    step=.01 if unit=='fracción' else .00000001 if 0<b<.01 else 1.0 if b>=1 else .01
    fmt='%.8f' if 0<b<.01 else '%.4f' if unit=='fracción' else '%.2f'
    return st.number_input(label+f' ({unit})',min_value=float(lo),max_value=float(hi),value=float(v),step=float(step),format=fmt,key=f'fin_{token}_{scenario}_{k}',help=source)

if view=='Parámetros':
    st.subheader(f'Parámetros · {scenario}')
    st.caption('Ajusta las entradas y pulsa Recalcular simulación para aplicar los cambios.')
    with st.form('ajustes_'+token+scenario):
        with st.expander('Ajustes principales · demanda, automatización y presupuesto',expanded=True):
            cols=st.columns(3)
            for i,k in enumerate(quick):
                with cols[i%3]:params[k]=widget(next(row for row in P if row[0]==k))
        for group in dict.fromkeys(row[5] for row in P):
            group_rows=[row for row in P if row[5]==group and row[0] not in quick]
            if not group_rows:continue
            with st.expander(group+' · parámetros detallados'):
                cols=st.columns(2)
                for i,row in enumerate(group_rows):
                    with cols[i%2]:params[row[0]]=widget(row)
        apply=st.form_submit_button('Recalcular simulación',type='primary')
    if apply:
        try:validate(params);st.session_state[state_key]=dict(params)
        except ValueError as e:st.error(str(e))
        else:st.success('Parámetros aplicados. Abre Resultados para consultar la simulación.')

    st.stop()
p=st.session_state[state_key];r=evaluate(p);d=r['calcs'];f=pd.DataFrame(r['flow']);
st.subheader(f'Escenario {scenario} · Resultados a tres años')
cols=st.columns(4)
for c,(label,v) in zip(cols,[('TCO manual',m(r['manual'])),('TCO económico',m(r['econ'])),('TCO de caja',m(r['cash'])),('Ahorro efectivo',m(r['cash_saving']))]):c.metric(label,v)
cols=st.columns(4)
for c,(label,v) in zip(cols,[('ROI económico',pct(r['roi'])),('ROI caja',pct(r['cash_roi'])),('Payback caja',pb(r['payback'])),('Personal residual',str(d['staff']))]):c.metric(label,v)
cols=st.columns(3)
for c,(label,v) in zip(cols,[('Inversión inicial',m(d['capex'])),('Ahorro económico',m(r['saving'])),('Payback económico',pb(r['payback_econ']))]):c.metric(label,v)
st.caption('WhatsApp principal · correo complementario · portal web seguro.')
cols=st.columns(4)
for col,(label,v) in zip(cols,[('Techo de inversión',m(p['budget'])),('Margen frente al techo',m(r['budget_margin'])),('Payback caja sostenido',pb(r['payback_sustained'])),('Custodia posterior a 36m',m(r['custody_tail']))]):col.metric(label,v)
if r['budget_ok']:st.success('Cumple el techo presupuestario bajo los supuestos seleccionados.')
else:st.warning('No cumple el techo presupuestario bajo los supuestos seleccionados.')
with st.expander('Metodología de indicadores'):
    st.markdown('TCO = inversión inicial + operación 36 meses. ROI comparativo = (manual − TCO) / TCO. Payback = primer mes en que el ahorro acumulado cubre la inversión; una caída posterior puede revertirlo. El ahorro de caja descuenta el personal que no se libera y contempla la absorción de costos por recursos existentes. No se imputa ingreso ni se aplican descuentos financieros.')
    st.write('ROI sobre inversión inicial (caja):',pct(r['investment_roi']),'· Payback económico:',pb(r['payback_econ']))

t1,t2,t3,t4,t5=st.tabs(['Recuperación y TCO','Costos y consumo','Recorridos documentales','Personal y escenarios','Exportación'])
with t1:
    st.subheader('Recuperación acumulada')
    chart=pd.concat([pd.DataFrame([{'month':0,'bal_e':-d['capex'],'bal_c':-d['capex']}]),f[['month','bal_e','bal_c']]],ignore_index=True).rename(columns={'month':'Mes','bal_e':'Económico','bal_c':'Caja'}).set_index('Mes')
    cumulative=pd.DataFrame({'Mes':[0]+f.month.tolist(),'Manual':[0]+f.manual.cumsum().tolist(),'Económico':[d['capex']]+(d['capex']+f.econ.cumsum()).tolist(),'Caja':[d['capex']]+(d['capex']+f.cash.cumsum()).tolist()})
    mostrar_grafica(px.line(cumulative,x='Mes',y=['Manual','Económico','Caja'],title='Costo total acumulado',color_discrete_map={'Manual':'#64748b','Económico':'#2563eb','Caja':'#d97706'}))
    fig=px.line(chart.reset_index(),x='Mes',y=['Económico','Caja'],title='Curva de recuperación de la inversión',color_discrete_map={'Económico':'#2563eb','Caja':'#d97706'})
    fig.add_hline(y=0,line_dash='dash',line_color='#64748b')
    mostrar_grafica(fig)
    mostrar_grafica(px.bar(pd.DataFrame({'Alternativa':['Manual','Económico','Caja'],'TCO':[r['manual'],r['econ'],r['cash']]}),x='Alternativa',y='TCO',color='Alternativa',title='TCO a 36 meses',color_discrete_sequence=['#64748b','#2563eb','#d97706']))
    st.caption('Mes 0: inversión inicial. Se cargan nómina y demanda durante los meses de convocatoria, mientras la infraestructura fija se mantiene 12 meses/año.')
    with st.expander('Ver detalle mensual'):
        st.dataframe(f.rename(columns={'month':'Mes','active':'Convocatoria activa','loads':'Cargas','stock':'GB custodiados','manual':'Manual','econ':'OpEx económico','cash':'OpEx caja','bal_e':'Acumulado económico','bal_c':'Acumulado caja'})[['Mes','Convocatoria activa','Cargas','GB custodiados','Manual','OpEx económico','OpEx caja','Acumulado económico','Acumulado caja']],hide_index=True,width='stretch')
with t2:
    st.subheader('Desglose económico del horizonte')
    breakdown={'Inversión inicial':d['capex'],'Nómina residual':f.labor.sum(),'Fijos cloud y soporte humano':f.fixed.sum(),'Variables y capacidad caliente':f.variable.sum(),'Custodia acumulada':f.storage.sum(),'Capacitación recurrente':f.training.sum()}
    cost_df=pd.DataFrame({'Partida':list(breakdown),'COP':list(breakdown.values())})
    a,b=st.columns([3,2])
    with a:mostrar_grafica(px.bar(cost_df,x='COP',y='Partida',orientation='h',title='Costo económico por partida'),horizontal=True)
    with b:mostrar_grafica(px.pie(cost_df,names='Partida',values='COP',hole=.45,title='Composición del TCO económico'))
    st.dataframe(pd.DataFrame([{'Partida':k,'COP':round(v,2)} for k,v in breakdown.items()]),hide_index=True,width='stretch')
    st.subheader('Comparación operativa AS-IS / TO-BE')
    for col,(label,val) in zip(st.columns(4),[('Cargas AS-IS',d['manual_loads']),('Cargas TO-BE',d['loads']),('Cargas evitadas',d['manual_loads']-d['loads']),('Cargas/h última semana',p['n']*p['last_share']*(1+p['re'])/(p['last_days']*p['hours']))]):col.metric(label,f'{val:,.0f}')
    st.caption(f"AS-IS: 5 días hasta revisión, 5 minutos activos y 2 días hasta contacto. TO-BE: P95 ≤10 minutos automatizado, P95 ≤48 h excepción (metas). Reenvíos AS-IS informados: {p['wrong_initial']:.0%} × {p['wrong_resends']:g}; supuesto configurable {p['manual_re']:g}.")
    st.subheader('Demanda y procesamiento anual')
    for group in [[('Postulaciones',d['post']),('Cargas',d['loads']),('Archivos seguros',d['safe']),('RUT admitidos',d['admit'])],[('Ejecuciones OCR',d['ocr']),('Páginas OCR',d['pages']),('Evaluaciones fiscales',d['fiscal']),('Alertas 48',d['alerts'])]]:
        for col,(label,value) in zip(st.columns(4),group):col.metric(label,f'{value:,.0f}'.replace(',','.'))
    st.caption(f"Rondas de aviso: {d['notices']:,.0f} · Lambda: {d['lambda_gbs']:,.0f} GB-s / {d['lambda_calls']:,.0f} invocaciones.")
    services=pd.DataFrame([{'Servicio':name,'USD/año':d[k],'COP/año con recargo':d[k]*d['fx']} for k,name in [('lambda','Lambda'),('text','Textract texto'),('advanced','Textract avanzado adicional'),('api','API Gateway'),('step','Step Functions'),('sqs','SQS'),('sns','SNS'),('ses','SES'),('wa','WhatsApp'),('cognito','Cognito'),('s3_requests','Peticiones S3'),('kms','KMS'),('logs','CloudWatch ingestión'),('trail','CloudTrail'),('transfer','Transferencia'),('temp','S3 temporal')]])
    mostrar_grafica(px.bar(services.sort_values('COP/año con recargo',ascending=False),x='COP/año con recargo',y='Servicio',orientation='h',title='Consumo variable por servicio · año 1'),horizontal=True)
    st.dataframe(services,hide_index=True,width='stretch')
    st.subheader('Comunicaciones · WhatsApp principal')
    st.dataframe(pd.DataFrame([{'Categoría':label,'USD/año':d[k],'COP/año':d[k]*d['fx']} for k,label in [('wa_utility','Utilidad'),('wa_auth','Autenticación'),('wa_marketing','Marketing opcional'),('wa_service','Servicio facturable'),('wa','Total WhatsApp con BSP'),('ses','Correo complementario')]]),hide_index=True,width='stretch')
    st.write('Quick Win incluido en inversión técnica:',cop(p['quickwin']))
    st.caption(f'Custodia al mes 36: {f.stock.iloc[-1]:,.1f} GB. Los costos posteriores a los 36 meses no están incluidos; la obligación de retención puede continuar.')
with t3:
    st.subheader('Costos por recorrido')
    routes=pd.DataFrame([{'Recorrido':k,'Costo marginal COP':v} for k,v in r['routes'].items()])
    mostrar_grafica(px.bar(routes,x='Costo marginal COP',y='Recorrido',orientation='h',title='Costo marginal por recorrido documental'),horizontal=True)
    st.dataframe(routes,hide_index=True,width='stretch')
    st.caption('Recorridos ilustrativos no sumables. Incluyen consumos y, donde corresponde, valor del tiempo humano y custodia durante toda la retención. Excluyen CapEx, fijos y autenticación por postulante. Los agregados se obtienen por población, no multiplicando todos los recorridos.')
    c1,c2,c3,c4=st.columns(4);c4.metric('TCO caja por postulante',cop(r['cash']/(3*d['post'])));c1.metric('Consumo variable por carga',f"$ {d['cost_load']:,.2f} COP");c2.metric('Consumo variable por postulante',f"$ {d['cost_post']:,.2f} COP");c3.metric('TCO económico por postulante',cop(r['econ']/(3*d['post'])))
with t4:
    st.subheader('Capacidad residual')
    if d['staff_r']>p['review_min']:st.warning(f"Se requieren {d['staff_r']} revisores, por encima del objetivo de {p['review_min']}.")
    else:st.success(f"Dotación objetivo de {p['review_min']} revisores suficiente bajo los supuestos agregados; validar colas en piloto.")
    st.write('Riesgo evitado a tres años (sensibilidad):',cop(r['risk_avoided']),'· ROI ajustado:',pct(r['risk_roi']))
    st.dataframe(pd.DataFrame([{'Función':name,'Casos/ciclo':d['cases_'+k],'Personas mínimas':d['staff_'+k]} for k,name in [('r','Revisión'),('a','Atención'),('c','Contabilidad')]]),hide_index=True,width='stretch')
    st.write('Nómina económica anual:',cop(d['labor']),'· Nómina atribuible en caja:',cop(d['cash_labor']))
    st.write('Capacitación inicial total de referencia:',cop(d['train_initial_econ']),'· Incremental presupuestada:',cop(d['train_initial']),'· Recurrente anual:',cop(d['train_rec']))
    st.subheader('Comparación de perfiles')
    st.caption('El perfil seleccionado refleja los ajustes aplicados; los otros dos muestran sus valores originales del Excel.')
    comp=[]
    for name,profile in profiles.items():
        e=evaluate(p if name==scenario else profile);comp.append({'Perfil':name,'Manual':e['manual'],'TCO económico':e['econ'],'TCO caja':e['cash'],'Ahorro caja':e['cash_saving'],'ROI caja':pct(e['cash_roi']),'Payback':pb(e['payback'])})
    st.dataframe(pd.DataFrame(comp),hide_index=True,width='stretch')
    mostrar_grafica(px.bar(pd.DataFrame(comp),x='Perfil',y=['Manual','TCO económico','TCO caja'],barmode='group',title='Comparación de escenarios a 36 meses'))
    mostrar_grafica(px.bar(pd.DataFrame({'Función':['Validación / revisión','Atención','Contabilidad*'],'As-Is':[p['manual_v'],p['manual_a'],0],'To-Be':[d['staff_r'],d['staff_a'],d['staff_c']]}),x='Función',y=['As-Is','To-Be'],barmode='group',title='Dotación por función'),tipo='personas')
    st.caption('*El personal contable no está incluido en la línea base laboral del pliego; cero no significa que el operador carezca de Contabilidad.')
with t5:
    st.download_button('Descargar flujo mensual CSV',f.to_csv(index=False).encode('utf-8-sig'),file_name='Flujo_ICFES.csv',mime='text/csv')
    st.download_button('Descargar parámetros CSV',pd.DataFrame([{'Clave':k,'Valor':v} for k,v in p.items()]).to_csv(index=False).encode('utf-8-sig'),file_name='Parametros_ICFES.csv',mime='text/csv')
    if data is not None:st.download_button('Descargar Excel de entrada',data,file_name=upload.name if upload else default_file.name,mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
mostrar_guia_metricas()
