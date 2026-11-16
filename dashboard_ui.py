"""Adaptación de dashboard_ui.py de Ceroa al simulador FinOps ICFES."""
from pathlib import Path
import streamlit as st


def mostrar_guia_metricas():
    with st.expander('Qué significa cada métrica y cada gráfica'):
        st.markdown((Path(__file__).parent / 'GUIA_METRICAS.md').read_text(encoding='utf-8'))


def aplicar_estilo():
    st.markdown('''<style>
    .block-container {max-width: 1440px; padding-top: 2rem; padding-bottom: 3rem;}
    h1 {font-size: 2rem !important; letter-spacing: -.04em;}
    h2, h3 {letter-spacing: -.025em;}
    [data-testid="stMetric"] {border: 1px solid #dbe3ed; border-radius: 12px;
        padding: 16px; min-height: 100px;}
    [data-testid="stMetricValue"] {font-size: clamp(1.1rem, 1.7vw, 1.8rem);}
    [data-testid="stMetricLabel"] {font-weight: 600;}
    [data-testid="stPlotlyChart"] {border: 1px solid #dbe3ed; border-radius: 12px;
        padding: 8px; margin-bottom: 16px; overflow: hidden;}
    [data-testid="stSidebar"] {border-right: 1px solid #dbe3ed;}
    </style>''', unsafe_allow_html=True)


def mostrar_grafica(fig, tipo='dinero', horizontal=False):
    """Formato común inspirado en Ceroa, con unidades propias de ICFES."""
    temporal=any(t.type=='scatter' and 'lines' in (t.mode or '') for t in fig.data)
    pie=any(t.type=='pie' for t in fig.data)
    rows=max((len(t.y) for t in fig.data if t.type=='bar' and t.y is not None),default=0)
    height=max(460, rows*38+140) if horizontal else 510 if temporal else 460
    fig.update_layout(template='plotly_white', height=height,
        font=dict(family='Arial, sans-serif', size=12, color='#334155'),
        title=dict(font=dict(size=17, color='#0f172a'), x=0, xanchor='left'),
        margin=dict(l=24, r=32, t=75, b=105 if pie else 75), hovermode='x unified' if temporal else 'closest',
        hoverlabel=dict(bgcolor='#ffffff', bordercolor='#cbd5e1', font=dict(size=13, color='#0f172a'), namelength=-1),
        legend=dict(title_text='', orientation='h', y=-.22 if pie else 1.09, x=0, font=dict(size=12)),
        colorway=['#2563eb','#d97706','#64748b','#0d9488','#8b5cf6','#db2777'],
        separators=',.', dragmode='zoom', hoverdistance=50, spikedistance=-1)
    unit={'dinero':'COP','personas':'personas','cargas':'cargas','GB':'GB'}[tipo]
    fmt='$%{'+('x' if horizontal else 'y')+':,.2f} COP' if tipo=='dinero' else '%{'+('x' if horizontal else 'y')+':,.0f} '+unit
    for trace in fig.data:
        if trace.type=='pie':
            trace.update(textinfo='percent', textposition='inside', hovertemplate='<b>%{label}</b><br>$%{value:,.2f} COP<br>Participación: %{percent}<extra></extra>')
        elif trace.type in ('scatter','bar'):
            category='%{y}' if horizontal else '%{x}'
            trace.update(hovertemplate='<b>'+category+'</b><br>'+fmt+'<extra>%{fullData.name}</extra>')
            if temporal:
                trace.update(line=dict(width=3), hovertemplate=fmt+'<extra>%{fullData.name}</extra>')
    if not any(t.type=='pie' for t in fig.data):
        if horizontal:
            fig.update_xaxes(title_text=unit, gridcolor='#edf2f7', automargin=True, tickformat='~s')
            fig.update_yaxes(title_text=None, automargin=True, autorange='reversed')
        else:
            fig.update_xaxes(title_text=None, showgrid=False, automargin=True)
            fig.update_yaxes(title_text=unit, gridcolor='#edf2f7', automargin=True, tickformat='~s')
    if temporal:
        fig.update_xaxes(title_text='Mes', dtick=3, range=[0,36], showspikes=True,
            spikemode='across', spikesnap='cursor', spikecolor='#64748b', spikethickness=1, spikedash='solid')
        fig.update_yaxes(zeroline=True, zerolinecolor='#94a3b8')
    st.plotly_chart(fig, width='stretch', config={'displayModeBar':True,'scrollZoom':False,'displaylogo':False,
        'modeBarButtonsToRemove':['lasso2d','select2d'], 'toImageButtonOptions':{'format':'png','scale':2}})
