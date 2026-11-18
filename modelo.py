"""Modelo FinOps ICFES. Las mismas expresiones generan fórmulas Excel y resultados Python.
Valores iniciales ilustrativos; no cotizaciones ni pruebas de producción.
"""
import math
from dataclasses import dataclass
@dataclass(frozen=True)
class X:
    s:str
    def __neg__(self):return X(f"(-{self.s})")
    def __add__(self,b):return X(f'({self.s}+{expr(b)})')
    def __radd__(self,b):return X(f'({expr(b)}+{self.s})')
    def __sub__(self,b):return X(f'({self.s}-{expr(b)})')
    def __rsub__(self,b):return X(f'({expr(b)}-{self.s})')
    def __mul__(self,b):return X(f'({self.s}*{expr(b)})')
    def __rmul__(self,b):return self*b
    def __truediv__(self,b):return X(f'({self.s}/{expr(b)})')
    def __rtruediv__(self,b):return X(f'({expr(b)}/{self.s})')
    def __pow__(self,b):return X(f'({self.s}^{expr(b)})')
    def __lt__(self,b):return X(f'({self.s}<{expr(b)})')
    def __le__(self,b):return X(f'({self.s}<={expr(b)})')
    def __gt__(self,b):return X(f'({self.s}>{expr(b)})')
    def __ge__(self,b):return X(f'({self.s}>={expr(b)})')
def expr(a):return a.s if isinstance(a,X) else ('"'+a.replace('"','""')+'"' if isinstance(a,str) else str(int(a)) if isinstance(a,bool) else str(a))
def func(name,fn,*a):return X(name+'('+','.join(map(expr,a))+')') if any(isinstance(v,X) for v in a) else fn(*a)
def mx(*a):return func('MAX',max,*a)
def mn(*a):return func('MIN',min,*a)
def ceil(a):return func('ROUNDUP',lambda v,d:math.ceil(v),a,0)
def floor(a):return func('INT',math.floor,a)
def iff(c,a,b):return func('IF',lambda c,a,b:a if c else b,c,a,b)
# key,label,unit,base,source,group,optimistic,pessimistic,min,max
P=[]
def add(k,l,u,b,src,g,o=None,p=None,lo=0,hi=1e12):P.append((k,l,u,b,src,g,b if o is None else o,b if p is None else p,lo,hi))
S='Supuesto ilustrativo; validar con operador/piloto'; O='Pliego §2; referencia homologada'; A='Tarifa de referencia pública AWS; confirmar región, impuestos y contrato'; U='https://aws.amazon.com/'
add('n','Aspirantes por ciclo','personas',45000,O,'Demanda',lo=1,hi=45000)
add('cycles','Convocatorias/año','ciclos',2,O,'Demanda',lo=1,hi=12)
add('months','Meses/ciclo','meses',2,O,'Demanda',lo=1,hi=12)
add('days','Días laborales/ciclo','días',40,S,'Demanda',lo=1,hi=366)
add('hours','Horas/día','h',8,S,'Demanda',lo=1,hi=24)
add('manual_re','Reenvíos As-Is por aspirante','cargas',.6,'Profesor: 15% × 4 adicionales (hipótesis)','Demanda',hi=10)
add('re','Reenvíos To-Be por aspirante','cargas',.2,S,'Demanda',.1,.4,hi=2)
add('pre_pass','Fracción que supera prevalidación inmediata','fracción',.98,S,'Demanda',.99,.95,hi=1)
add('safe','Fracción técnicamente segura','fracción',.95,S,'Demanda',.97,.9,hi=1)
add('admit','Fracción admitida sobre cargas','fracción',.90,S,'Demanda',.93,.8,hi=1)
add('ocr_fraction','Fracción admitida con OCR externo','fracción',.8,S,'Demanda',.6,1,hi=1)
add('ocr_runs','Ejecuciones OCR por versión elegible','veces',1.1,S,'Demanda',1.03,1.3,lo=1,hi=3)
add('fiscal','Evaluaciones fiscales por versión','veces',1.1,S,'Demanda',1.03,1.3,lo=1,hi=5)
add('admin','Fracción admitida con evaluación administrativa','fracción',.8,S,'Demanda',hi=1)
add('alert','Aspirantes con responsabilidad 48','fracción',.10,'Profesor: 10% de aspirantes','Demanda',hi=1)
add('pages','Páginas promedio/versión','páginas',2,'Profesor: preferible 1, máximo 2; 2 conservador por casilla 89','Demanda',1.5,2,lo=1,hi=2)
add('advanced','Fracción páginas OCR con análisis avanzado adicional','fracción',.03,S,'Demanda',.01,.15,hi=1)
add('rounds','Rondas de aviso por carga (promedio)','rondas',1.1,S,'Demanda',1.03,1.4,hi=3)
add('mau','Meses de actividad por aspirante','MAU/persona',1.25,S,'Demanda',1,1.5,hi=12)
add('salary','Salario base homologado','COP/mes',2000000,O,'Personal',lo=1)
add('factor','Factor prestacional','factor',1.5,O,'Personal',lo=1,hi=3)
add('manual_v','Validadores manuales','personas',10,O,'Personal',hi=1000)
add('manual_a','Agentes manuales','personas',4,O,'Personal',hi=1000)
for k,l,b,o,p in [('review','Fracción cargas con revisión',.05,.03,.2),('attention','Fracción cargas con atención',.05,.03,.1),('prod_r','Productividad revisión',.8,.85,.7),('prod_a','Productividad atención',.8,.85,.7),('prod_c','Productividad Contabilidad',.8,.85,.7)]:add(k,l,'fracción',b,S,'Personal',o,p,lo=.01 if k.startswith('prod') else 0,hi=1)
add('review_count','Revisiones por caso derivado','veces',1,S,'Personal',hi=5)
add('attention_count','Gestiones por caso atendido','veces',1,S,'Personal',hi=5)
add('min_r','Minutos/revisión','min',8,S,'Personal',6,10,lo=.1,hi=600)
add('min_a','Minutos/atención','min',5,S,'Personal',4,7,lo=.1,hi=600)
add('min_c','Minutos/alerta 48','min',10,S,'Personal',8,12,lo=.1,hi=600)
add('peak','Factor de concentración laboral','factor',1.1,S,'Personal',1,1.6,lo=1,hi=10)
add('release','Fracción del ahorro de validación/atención realizada en caja','fracción',.8,S,'Personal',1,.5,hi=1)
add('account_increment','Fracción contable de gasto adicional','fracción',.5,S,'Personal',.25,1,hi=1)
add('support','Soporte TI y seguridad','COP/mes',1800000,'Supuesto: dedicación parcial; cotizar','Personal',1200000,3000000)
add('audit','Control interno y FinOps','COP/mes',800000,'Supuesto: dedicación parcial; cotizar','Personal',500000,1500000)
add('shared_increment','Fracción incremental soporte/auditoría','fracción',.5,S,'Personal',.25,1,hi=1)
add('trm','TRM de presupuesto','COP/USD',4000,'Supuesto de planeación, no TRM oficial','Finanzas',3800,4500,lo=1)
add('growth','Crecimiento anual de costos operativos (manual y automático)','fracción',0,S,'Finanzas',0,.06,hi=1)
add('tax','Recargo presupuestal sobre servicios USD','fracción',.19,'Reserva impuestos/cargos; no dictamen fiscal','Finanzas',.1,.25,hi=1)
add('dev','Desarrollo e integración','COP',36000000,'Supuesto: 2 desarrolladores × 3 meses × 6 M','Inversión',30000000,48000000)
add('arch','Arquitectura y gestión de proyecto','COP',18000000,'Supuesto: arquitectura 12 M + gestión 6 M','Inversión',15000000,24000000)
add('qa','Pruebas y piloto','COP',10000000,'Supuesto: 2 meses × 5 M','Inversión',8000000,15000000)
add('deploy','DevOps, despliegue y entorno piloto','COP',9000000,'Supuesto: 7 M trabajo + 2 M entorno','Inversión',7000000,12000000)
add('contingency','Contingencia inversión técnica','fracción',.1,S,'Inversión',.05,.2,hi=1)
add('teacher','Instructor','COP/h',80000,S,'Capacitación')
add('material','Material inicial','COP',300000,S,'Capacitación')
add('tech_people','Participantes TI/Seguridad/Control','personas',3,S,'Capacitación',hi=100)
add('training_initial_unpaid','Fracción horas iniciales fuera de nómina presupuestada','fracción',.65,S,'Capacitación',.4,1,hi=1)
add('training_rec_unpaid','Fracción horas recurrentes fuera de nómina','fracción',0,S,'Capacitación',0,.5,hi=1)
add('refresh','Rondas de refuerzo por año','rondas',1,S,'Capacitación',1,2,hi=12)
add('turnover','Rondas equivalentes adicionales por rotación/año','rondas',.25,S,'Capacitación',0,.75,hi=12)
add('lambda_gbs','Lambda ejecución','USD/GB-s',.0000166667,A+' '+U+'lambda/pricing/','Tarifas')
add('lambda_req','Lambda invocaciones','USD/millón',.2,A+' '+U+'lambda/pricing/','Tarifas')
add('ocr_text','Textract detección texto','USD/página',.0015,A+' '+U+'textract/pricing/ (ejemplo Oregón)','Tarifas')
add('ocr_adv','Textract formularios','USD/página',.05,A+' '+U+'textract/pricing/ (ejemplo)','Tarifas')
add('api','API Gateway REST','USD/millón',3.5,A+' '+U+'api-gateway/pricing/','Tarifas')
add('api_n','Solicitudes API por carga','solicitudes',6,S,'Consumo')
add('step','Step Functions Standard','USD/transición',.000025,A+' '+U+'step-functions/pricing/','Tarifas')
add('step_n','Transiciones por carga','transiciones',40,S,'Consumo')
add('sqs','SQS','USD/millón',.4,A+' '+U+'sqs/pricing/','Tarifas')
add('sqs_n','Peticiones SQS facturables/carga','peticiones',30,S,'Consumo')
add('sns','SNS','USD/millón',.5,A+' '+U+'sns/pricing/','Tarifas')
add('sns_n','Peticiones SNS/carga','peticiones',4,S,'Consumo')
add('ses','SES','USD/mensaje',.0001,A+' '+U+'ses/pricing/','Tarifas')
add('wa','WhatsApp utilidad (Colombia)','USD/mensaje',.0008,'Referencia lista Meta oct. 2026 publicada por Gupshup; confirmar categoría y contrato: https://www.gupshup.ai/resources/wp-content/uploads/2026/11/USD_Oct2026.pdf','Tarifas')
add('bsp','Recargo BSP/mensaje','USD/mensaje',0,'Supuesto API directa; cotizar si intermediario','Tarifas',0,.005)
add('cognito','Cognito Essentials','USD/MAU',.015,A+' '+U+'cognito/pricing/; sin descontar free tier','Tarifas')
add('s3_gb','S3 Standard','USD/GB-mes',.023,A+' '+U+'s3/pricing/','Tarifas')
add('s3_put','S3 escrituras','USD/1000',.005,A+' '+U+'s3/pricing/','Tarifas')
add('s3_get','S3 lecturas','USD/1000',.0004,A+' '+U+'s3/pricing/','Tarifas')
add('mb','Tamaño medio PDF','MB',3,'Profesor: 3 MB','Consumo',lo=.01,hi=4.999999)
add('copies','Copias custodiadas por versión (equiv. tamaño)','factor',2,S,'Consumo',lo=1,hi=10)
add('manifest_mb','Evidencia por carga','MB',.02,S,'Consumo',hi=10)
add('retention','Retención custodia','meses',60,'Profesor: cinco años','Consumo',lo=1,hi=120)
add('temp_days','Permanencia temporal','días',1,S,'Consumo',hi=30)
add('put_n','Escrituras temporales por carga','peticiones',1,S,'Consumo')
add('get_n','Lecturas base por carga','peticiones',3,S,'Consumo')
add('kms_req','KMS simétrico','USD/10000',.03,A+' '+U+'kms/pricing/','Tarifas')
add('kms_n','Solicitudes KMS simétricas por carga','peticiones',8,S,'Consumo')
add('sign','KMS firma RSA','USD/10000',.15,'Reserva ilustrativa; confirmar tarifa RSA-3072 '+U+'kms/pricing/','Tarifas')
add('sign_n','Firmas por carga admitida','firmas',2,S,'Consumo')
add('log_gb','Logs ingresados por carga','GB',.0002,S,'Consumo')
add('log_rate','CloudWatch ingestión','USD/GB',.5,A+' '+U+'cloudwatch/pricing/','Tarifas')
add('trail_n','CloudTrail eventos de datos/carga','eventos',10,S,'Consumo')
add('trail_rate','CloudTrail datos','USD/100000',.1,A+' '+U+'cloudtrail/pricing/','Tarifas')
add('transfer_gb','Egreso/NAT procesado por carga','GB',.005,S,'Consumo')
add('transfer','Egreso + procesamiento NAT','USD/GB',.135,'Reserva combinada; validar '+U+'vpc/pricing/','Tarifas')
add('rds','RDS PostgreSQL Multi-AZ cómputo','USD/mes',120,'Reserva presupuestaria, no tarifa confirmada '+U+'rds/postgresql/pricing/','Fijos cloud',100,180)
add('rds_storage','RDS almacenamiento y backups','USD/mes',25,'Reserva presupuestaria '+U+'rds/postgresql/pricing/','Fijos cloud',20,45)
add('proxy','RDS Proxy','USD/mes',22,'Reserva presupuestaria '+U+'rds/proxy/pricing/','Fijos cloud')
add('network','NAT redundante + endpoints / IPv4','USD/mes',85,'Reserva presupuestaria '+U+'vpc/pricing/','Fijos cloud',73,130)
add('keys','KMS claves activas/anteriores, promedio','USD/mes',6,'Reserva presupuestaria '+U+'kms/pricing/','Fijos cloud')
add('monitor','CloudWatch métricas, alarmas, retención logs','USD/mes',20,'Reserva presupuestaria '+U+'cloudwatch/pricing/','Fijos cloud',15,40)
add('portal','DNS, dominio, activos portal, secretos, seguridad y soporte cloud','USD/mes',40,'Reserva agrupada; cotizar DNS/WAF si aplica/Secrets Manager/soporte','Fijos cloud',25,75)
add('warm','Concurrencia preaprovisionada','entornos',4,'Supuesto prevalidación; cupos reservados no equivalen a capacidad caliente','Fijos cloud',2,8,hi=1000)
add('warm_gb','Memoria por entorno caliente','GB',.5,S,'Fijos cloud',lo=.128,hi=10)
add('warm_rate','Tarifa capacidad caliente','USD/GB-s',.0000041667,A+' '+U+'lambda/pricing/','Tarifas')
# Operaciones de V8: población se calcula explícitamente.
OPS=[('reg','Registro/autorización',2,.25,.3,'loads'),('pre','Prevalidación',1,.5,.5,'loads'),('sec','Seguridad',1,1,3,'pre_pass'),('class','Clasificación',1,2,15,'safe'),('cust','Custodia',1,.5,2,'admit'),('ocr','Inicio/lectura OCR',2,.5,1,'ocr'),('norm','Normalización',1,1,2,'norm'),('dmn','DMN Java',1,1,1.5,'dmn'),('notice','Despacho avisos',2,.5,1,'notice'),('query','Consulta',2,.5,.3,'loads'),('seal','Sellado y despacho',2,.5,1,'admit')]
for k,l,n,g,t,pop in OPS:
 for suf,label,val,unit in [('n','invocaciones',n,'inv./caso'),('g','memoria',g,'GB'),('t','duración',t,'s')]:add(k+'_'+suf,l+' · '+label,unit,val,'Presupuesto de consumo; supuesto','Funciones Lambda',lo=.001,hi=10000)
add("alert_eligible","Fracción aspirantes 48 aprobados y elegibles","fracción",0.8,"Hipótesis piloto","Demanda",0.7,1,0,1)
add("wa_coverage","Fracción rondas con WhatsApp entregado (principal)","fracción",1,"Presupuesto conservador de entrega","Comunicaciones",1,1,0,1)
add("email_coverage","Fracción rondas con correo complementario","fracción",1,"Ambos canales presupuestados","Comunicaciones",1,1,0,1)
add("wa_auth_n","Autenticaciones WhatsApp por aspirante","mensajes",1,"Hipótesis piloto","Comunicaciones",0.5,2,0,20)
add("wa_marketing_n","Invitaciones marketing por aspirante (opcional)","mensajes",0,"Fuera del alcance base","Comunicaciones",0,1,0,20)
add("wa_service_n","Respuestas de servicio facturables por aspirante","mensajes",0.2,"No descuenta franquicias adicionales","Comunicaciones",0.1,0.5,0,100)
add("wa_auth","WhatsApp autenticación","USD/mensaje",0.0008,"Referencia Meta Colombia 01/10/2026; confirmar contrato","Tarifas",0.0008,0.0008,0,10)
add("wa_marketing","WhatsApp marketing","USD/mensaje",0.0125,"Referencia Meta Colombia 01/10/2026; confirmar contrato","Tarifas",0.0125,0.0125,0,10)
add("wa_service","WhatsApp servicio","USD/mensaje",0.0008,"Referencia Meta Colombia 01/10/2026; confirmar contrato","Tarifas",0.0008,0.0008,0,10)
add("review_min","Dotación mínima objetivo de revisores","personas",2,"Profesor: dos; refuerzo si capacidad insuficiente","Personal",2,2,0,1000)
add("budget","Techo referencia a 36 meses","COP",504000000,"Pliego: estrictamente inferior","Finanzas",504000000,504000000,1,1000000000000)
add("risk_asis","Pérdida esperada anual AS-IS (opcional)","COP/año",0,"Sin datos: no monetizada","Riesgos",0,0,0,1000000000000)
add("risk_tobe","Pérdida esperada anual TO-BE (opcional)","COP/año",0,"Sin datos: no monetizada","Riesgos",0,0,0,1000000000000)
add("first_share","Proporción primeras semanas","fracción",0.4,"Profesor","Demanda",0.4,0.4,0,1)
add("last_share","Proporción última semana","fracción",0.2,"Profesor","Demanda",0.2,0.2,0,1)
add("last_days","Días operativos última semana","días",5,"Supuesto","Demanda",5,5,1,7)
add("quickwin","Asignación Quick Win dentro de inversión técnica","COP",9640000,"Estimación 124 horas; no costo adicional","Inversión",9640000,9640000,0,1000000000000)
add("wrong_initial","Proporción RUT inicialmente incorrectos","fracción",0.15,"Profesor","Demanda",0.15,0.15,0,1)
add("wrong_resends","Reenvíos adicionales por afectado","reenvíos",4,"Profesor; interpretación por confirmar","Demanda",4,4,0,100)
DEFAULT={p[0]:p[3] for p in P}; PROFILES={'Optimista':{p[0]:p[6] for p in P},'Base':DEFAULT.copy(),'Pesimista':{p[0]:p[7] for p in P}}
INTS={'n','cycles','months','days','manual_v','manual_a','retention','tech_people','warm','review_min','last_days'}
def validate(p):
 for k,l,u,b,s,g,o,pe,lo,hi in P:
  v=p[k]
  if not isinstance(v,(int,float)) or not math.isfinite(v) or not lo<=v<=hi:raise ValueError(f'{l}: debe estar entre {lo} y {hi}')
  if k in INTS and v!=int(v):raise ValueError(f'{l}: debe ser entero')
 if p['cycles']*p['months']>12:raise ValueError('Convocatorias × meses no puede superar 12.')
 if not p['admit']<=p['safe']<=p['pre_pass']:raise ValueError('Admitidos ≤ seguros ≤ prevalidación superada.')
 if p['mau']>p['months']:raise ValueError('MAU/persona debe caber en meses de convocatoria.')
 if p['days']>31*p['months']:raise ValueError('Días laborables exceden ventana calendario.')
 if p['first_share']+p['last_share']>1:raise ValueError('Las proporciones inicial y final no pueden superar 100%.')
 if p['quickwin']>p['dev']+p['arch']+p['qa']+p['deploy']:raise ValueError('La asignación Quick Win debe estar incluida en la inversión técnica.')

def calc(p,emit=None):
 class Sink(dict):
  def __setitem__(self,k,v):
   super().__setitem__(k,emit(k,v) if emit else v)
 d=Sink(); q=lambda k:p[k]
 d['post']=q('n')*q('cycles'); d['active']=q('cycles')*q('months'); d['loads']=d['post']*(1+q('re')); d['manual_loads']=d['post']*(1+q('manual_re')); d['pre_pass']=d['loads']*q('pre_pass'); d['safe']=d['loads']*q('safe'); d['admit']=d['loads']*q('admit'); d['ocr']=d['admit']*q('ocr_fraction')*q('ocr_runs'); d['pages']=d['ocr']*q('pages'); d['fiscal']=d['admit']*q('fiscal'); d['admin']=d['admit']*q('admin'); d['alerts']=mn(d['admin'],d['post']*q('alert')*q('alert_eligible')); d['notices']=d['loads']*q('rounds'); d['norm']=d['ocr']+d['admit']*(1-q('ocr_fraction')); d['dmn']=d['fiscal']+d['admin']; d['notice']=d['notices']; d['salary']=q('salary')*q('factor'); d['manual']=d['salary']*d['active']*(q('manual_v')+q('manual_a'))
 for k,ratio,freq,t,prod in [('r','review','review_count','min_r','prod_r'),('a','attention','attention_count','min_a','prod_a')]:
  d['cases_'+k]=d['loads']/q('cycles')*q(ratio)*q(freq); d['staff_'+k]=ceil(d['cases_'+k]*q(t)*q('peak')/(q('days')*q('hours')*60*q(prod)))
 d['staff_r']=mx(q('review_min'),d['staff_r']);d['cases_c']=d['alerts']/q('cycles');d['staff_c']=ceil(d['cases_c']*q('min_c')*q('peak')/(q('days')*q('hours')*60*q('prod_c')))
 d['staff']=d['staff_r']+d['staff_a']+d['staff_c'];d['labor']=d['staff']*d['salary']*d['active'];d['ra_labor']=(d['staff_r']+d['staff_a'])*d['salary']*d['active'];d['c_labor']=d['staff_c']*d['salary']*d['active'];d['cash_labor']=d['manual']-mx(0,d['manual']-d['ra_labor'])*q('release')+mx(0,d['ra_labor']-d['manual'])+d['c_labor']*q('account_increment')
 gbs=0;calls=0;lc=0
 for k,l,n,g,t,pop in OPS:
  d[k+'_unit']=q(k+'_n')*(q(k+'_g')*q(k+'_t')*q('lambda_gbs')+q('lambda_req')/1e6);d[k+'_cost']=d[pop]*d[k+'_unit'];gbs+=d[pop]*q(k+'_n')*q(k+'_g')*q(k+'_t');calls+=d[pop]*q(k+'_n');lc+=d[k+'_cost']
 d['lambda_gbs']=gbs;d['lambda_calls']=calls;d['lambda']=lc
 d['text']=d['pages']*q('ocr_text');d['advanced']=d['pages']*q('advanced')*q('ocr_adv');d['api']=d['loads']*q('api_n')*q('api')/1e6;d['step']=d['loads']*q('step_n')*q('step');d['sqs']=d['loads']*q('sqs_n')*q('sqs')/1e6;d['sns']=d['loads']*q('sns_n')*q('sns')/1e6;d['ses']=d['notices']*q('email_coverage')*q('ses');d['wa_utility']=d['notices']*q('wa_coverage')*q('wa');d['wa_auth']=d['post']*q('wa_auth_n')*q('wa_auth');d['wa_marketing']=d['post']*q('wa_marketing_n')*q('wa_marketing');d['wa_service']=d['post']*q('wa_service_n')*q('wa_service');d['wa']=d['wa_utility']+d['wa_auth']+d['wa_marketing']+d['wa_service']+q('bsp')*(d['notices']*q('wa_coverage')+d['post']*(q('wa_auth_n')+q('wa_marketing_n')+q('wa_service_n')));d['cognito']=d['post']*q('mau')*q('cognito');d['s3_requests']=(d['loads']*q('put_n')+d['admit']*(q('copies')+1))*q('s3_put')/1000+(d['loads']*q('get_n')+d['ocr'])*q('s3_get')/1000;d['kms']=d['loads']*q('kms_n')*q('kms_req')/10000+d['admit']*q('sign_n')*q('sign')/10000;d['logs']=d['loads']*q('log_gb')*q('log_rate');d['trail']=d['loads']*q('trail_n')*q('trail_rate')/100000;d['transfer']=d['loads']*q('transfer_gb')*q('transfer');d['temp']=d['loads']*q('mb')/1000*q('temp_days')/30*q('s3_gb');d['gb_new']=d['admit']*q('mb')*q('copies')/1000+d['loads']*q('manifest_mb')/1000
 d['var_usd']=sum(d[k] for k in ['lambda','text','advanced','api','step','sqs','sns','ses','wa','cognito','s3_requests','kms','logs','trail','transfer','temp']);d['fixed_usd']=sum(q(k) for k in ['rds','rds_storage','proxy','network','keys','monitor','portal']);d['warm_month']=q('warm')*q('warm_gb')*730*3600*q('warm_rate');d['fx']=q('trm')*(1+q('tax'));d['variable']=d['var_usd']*d['fx'];d['fixed']=d['fixed_usd']*12*d['fx'];d['warm_cop']=d['warm_month']*d['active']*d['fx'];d['human_fixed']=(q('support')+q('audit'))*12
 d['train_initial_hours']=6*d['staff_r']+4*d['staff_a']+3*d['staff_c']+6*q('tech_people');d['train_refresh_hours']=2*d['staff_r']+2*d['staff_a']+d['staff_c']+2*q('tech_people');d['teach_initial']=6*iff(d['staff_r']>0,1,0)+4*iff(d['staff_a']>0,1,0)+3*iff(d['staff_c']>0,1,0)+6*iff(q('tech_people')>0,1,0);d['teach_refresh']=2*iff(d['staff_r']>0,1,0)+2*iff(d['staff_a']>0,1,0)+iff(d['staff_c']>0,1,0)+2*iff(q('tech_people')>0,1,0)
 d['train_initial_econ']=d['teach_initial']*q('teacher')+q('material')+d['train_initial_hours']*d['salary']/160;d['train_initial']=d['teach_initial']*q('teacher')+q('material')+d['train_initial_hours']*d['salary']/160*q('training_initial_unpaid');d['train_rec']=(d['teach_refresh']*q('refresh')+d['teach_initial']*q('turnover'))*q('teacher')+q('material')*q('turnover')+(d['train_refresh_hours']*q('refresh')+d['train_initial_hours']*q('turnover'))*d['salary']/160*q('training_rec_unpaid');d['capex_tech']=sum(q(k) for k in ['dev','arch','qa','deploy'])*(1+q('contingency'));d['capex']=d['capex_tech']+d['train_initial'];d['cost_load']=d['variable']/d['loads'];d['cost_post']=d['variable']/d['post']
 return d

def flow(p,d,emit=None):
 rows=[]; bal_e=-d['capex'];bal_c=-d['capex']; stocks=[]
 for i in range(1,37):
  m=(i-1)%12+1;y=(i-1)//12;start=floor(floor((m*p['cycles']-1)/12)*12/p['cycles'])+1;active=iff(m-start<p['months'],1,0);g=(1+p['growth'])**y
  new=d['gb_new']/d['active']*active;stocks.append(new)
  # Stock fin de mes; cada cohorte permanece exactamente retención meses. No se imputa disposición fuera horizonte.
  stock=sum(iff(i-j<p['retention'],v,0) for j,v in enumerate(stocks,1)); storage=stock*p['s3_gb']*d['fx']*g
  manual=d['manual']/d['active']*active*g;labor=d['labor']/d['active']*active*g;cashlabor=d['cash_labor']/d['active']*active*g;fixed=(d['fixed']/12+d['human_fixed']/12)*g;cashfixed=(d['fixed']/12+d['human_fixed']/12*p['shared_increment'])*g;variable=(d['variable']/d['active']+d['warm_month']*d['fx'])*active*g;training=d['train_rec']/p['cycles']*iff(m-start<1,1,0)*g
  econ=labor+fixed+variable+storage+training;cash=cashlabor+cashfixed+variable+storage+training;bal_e+=manual-econ;bal_c+=manual-cash
  row=dict(month=i,active=active,loads=d['loads']/d['active']*active,new=new,stock=stock,manual=manual,labor=labor,cashlabor=cashlabor,fixed=fixed,variable=variable,storage=storage,training=training,econ=econ,cash=cash,net_e=manual-econ,net_c=manual-cash,bal_e=bal_e,bal_c=bal_c)
  if emit:
   row=emit(i,row);stocks[-1]=row['new'];bal_e=row['bal_e'];bal_c=row['bal_c']
  rows.append(row)
 return rows

def routes(p,d):
 # Costo marginal de camino, no TCO asignado. Base por carga + incrementos; rutas no sumables.
 q=lambda k:p[k]; common=d['reg_unit']+d['pre_unit']+d['query_unit']+d['notice_unit']*q('rounds')+q('api_n')*q('api')/1e6+q('step_n')*q('step')+q('sqs_n')*q('sqs')/1e6+q('sns_n')*q('sns')/1e6+q('rounds')*(q('email_coverage')*q('ses')+q('wa_coverage')*(q('wa')+q('bsp')))+q('put_n')*q('s3_put')/1000+q('get_n')*q('s3_get')/1000+q('kms_n')*q('kms_req')/10000+q('log_gb')*q('log_rate')+q('trail_n')*q('trail_rate')/100000+q('transfer_gb')*q('transfer')+q('mb')/1000*q('temp_days')/30*q('s3_gb')
 cl=common+d['sec_unit']+d['class_unit'];ocr=d['ocr_unit']+d['norm_unit']+q('pages')*(q('ocr_text')+q('advanced')*q('ocr_adv'))+q('s3_get')/1000; admitted=cl+d['cust_unit']+d['seal_unit']+(q('copies')+1)*q('s3_put')/1000+q('sign_n')*q('sign')/10000+q('ocr_fraction')*ocr+(1-q('ocr_fraction'))*d['norm_unit']+d['dmn_unit']*(1+q('admin')); storage=(q('mb')*q('copies')+q('manifest_mb'))/1000*q('s3_gb')*q('retention'); hourly=d['salary']/160/60
 return {'PDF rechazado en prevalidación':common*d['fx'],'PDF rechazado en seguridad posterior':(common+d['sec_unit'])*d['fx'],'PDF no RUT (seguro)':cl*d['fx'],'RUT ordinario (1 ejecución, sin revisión)':(admitted+storage)*d['fx'],'RUT con 1 reintento OCR adicional':(admitted+storage+ocr)*d['fx'],'Subsanación: 1 carga no RUT + 1 RUT':(cl+admitted+storage)*d['fx'],'RUT con alerta 48':(admitted+storage)*d['fx']+hourly*q('min_c'),'RUT con revisión humana y reevaluación':(admitted+storage+d['dmn_unit'])*d['fx']+hourly*q('min_r')}

def evaluate(p):
 validate(p);d=calc(p);f=flow(p,d);manual=sum(x['manual'] for x in f);econ=d['capex']+sum(x['econ'] for x in f);cash=d['capex']+sum(x['cash'] for x in f)
 def pb(k):return next((x['month'] for x in f if x[k]>=0),None) if d['capex']>0 else 0
 def sustained(k):return next((x['month'] for i,x in enumerate(f) if all(y[k]>=0 for y in f[i:])),None) if d['capex']>0 else (0 if all(y[k]>=0 for y in f) else next((x['month'] for i,x in enumerate(f) if all(y[k]>=0 for y in f[i:])),None))
 tail=sum(x['new']*max(0,p['retention']-(37-x['month']))*p['s3_gb']*d['fx']*(1+p['growth'])**2 for x in f)
 avoided=3*(p['risk_asis']-p['risk_tobe'])
 return dict(payback_sustained=sustained('bal_c'),payback_econ_sustained=sustained('bal_e'),custody_tail=tail,budget_margin=p['budget']-cash,budget_ok=cash<p['budget'],risk_avoided=avoided,risk_roi=(manual-cash+avoided)/cash if cash else None,calcs=d,flow=f,routes=routes(p,d),manual=manual,econ=econ,cash=cash,saving=manual-econ,cash_saving=manual-cash,roi=(manual-econ)/econ if econ else None,cash_roi=(manual-cash)/cash if cash else None,investment_roi=(manual-cash)/d['capex'] if d['capex'] else None,payback=pb('bal_c'),payback_econ=pb('bal_e'))
