#!/usr/bin/env python
# -*- coding: utf-8 -*-

# *********************************************************************************************************
# --------------------------- IMPORTO LIBRERÍAS -----------------------------------------------------------
# *********************************************************************************************************
import pandas as pd # Preprocesamiento de datos
import numpy as np 
import dash # Dashboard
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import plotly.express as px
from datetime import datetime, timedelta


# *********************************************************************************************************
# --------------------------- DEFINICIÓN DE CONSTANTES ----------------------------------------------------
# *********************************************************************************************************
TAMANIO_LETRA_KPIS=18
URL="https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv"
URL_FALLECIMIENTOS="https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv"
URL_RECUPERADOS="https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv"
CORTE_PAISES_MENOS_INFECTADOS = 100
CORTE_PAISES_MAS_INFECTADOS = 30000
PLANTILLA = 'ggplot2'
DIA_ACTUALIZACION = datetime.strftime(datetime.now() - timedelta(1), '%-d del %-m de %Y')
ESTILO_DASHBOARD = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
ESTILO_PESTANIAS = {'height': '50px'}
ESTILO_PESTANIA = {'borderBottom': '1px solid #d6d6d6','padding': '10px','fontWeight': 'bold','font-size':'20px'}
ESTILO_SELECCIONADA = {'borderTop': '1px solid #d6d6d6',
                       'borderBottom': '1px solid #d6d6d6',
                       'backgroundColor': '#1e1e1e',
                       'color': 'white','padding':'10px',
                       'font-size':'20px'}
EDADES = ['>80 años', '70-79 años', '60-69 años', '50-59 años', '40-49 años', 
          '30-39 años', '20-29 años', '10-19 años', '0-9 años']
RATIOS_EDADES = [14.8, 8, 3.6, 1.3, 0.4, 0.2, 0.2, 0.2, 0.0]
SEXO = ['Hombres', 'Mujeres']
RATIOS_SEXO = [4.7, 2.8]
PATOLOGIAS = ['Enfermedades cardiovasculares', 'Diabetes','Hipertensión', 
              'Enfermedades respiratorias crónicas', 'Cáncer', 
              'Sin patologías previas']
RATIOS_PATOLOGIAS = [13.2, 9.2, 8.4, 8.0, 7.6, 2.9]

# *********************************************************************************************************
# --------------------------- DEFINICIÓN DE FUNCIONES -----------------------------------------------------
# *********************************************************************************************************
# Funciones a utilizar
def a_tiempo_unix(dt):
    epoch =  datetime.utcfromtimestamp(0)
    return (dt - epoch).total_seconds() * 1000

# Funciones para filtrar el dataframe original por localizaciones
def devuelve_dfs_localizacion_pais(df, localizacion, flag_not=False):
    if flag_not:
        df_conf = df[df['Country/Region']!=localizacion].reset_index(drop=True)
        df_fall = df_fallecidos[df_fallecidos['Country/Region']!=localizacion].reset_index(drop=True)
        df_recup = df_recuperados[df_recuperados['Country/Region']!=localizacion].reset_index(drop=True)
    else:
        df_conf = df[df['Country/Region']==localizacion].reset_index(drop=True)
        df_fall = df_fallecidos[df_fallecidos['Country/Region']==localizacion].reset_index(drop=True)
        df_recup = df_recuperados[df_recuperados['Country/Region']==localizacion].reset_index(drop=True)
    df_conf.loc['fecha_infecciones'] = df_conf.sum()
    df_fall.loc['fecha_infecciones'] = df_fall.sum()
    df_recup.loc['fecha_infecciones'] = df_recup.sum()
    return df_conf, df_fall, df_recup

def devuelve_dfs_localizacion_estado(df, localizacion):
    df_conf = df[df['State']==localizacion].reset_index(drop=True)
    df_fall = df_fallecidos[df_fallecidos['State']==localizacion].reset_index(drop=True)
    df_recup = df_recuperados[df_recuperados['State']==localizacion].reset_index(drop=True)
    return df_conf, df_fall, df_recup 

def devuelve_evol_local(lista_df_localizacion, y, pais=False):
    if pais:
        y_conf = [lista_df_localizacion[0].copy().loc['fecha_infecciones'][str(d)] for d in y]
        y_fall = [lista_df_localizacion[1].copy().loc['fecha_infecciones'][str(d)] for d in y]
        y_recup=[lista_df_localizacion[2].copy().loc['fecha_infecciones'][str(d)] for d in y]
    else:
        y_conf=[lista_df_localizacion[0].copy()[str(d)].item() for d in y]
        y_fall=[lista_df_localizacion[1].copy()[str(d)].item() for d in y]
        y_recup=[lista_df_localizacion[2].copy()[str(d)].item() for d in y]
    return y_conf, y_fall, y_recup

def calculo_metricas_totales(df_conf, df_fall, df_recup):
    confirmados_totales = df_conf.loc['fecha_infecciones',:]['casos_totales']
    fallecidos_totales = df_fall.loc['fecha_infecciones',:]['casos_totales']
    recuperados_totales = df_recup.loc['fecha_infecciones',:]['casos_totales']
    return confirmados_totales, fallecidos_totales, recuperados_totales

def render_footer():
    """
    Generación del pie de página HTML para cada una de las páginas
    """
    return html.Footer(
        html.Div(
            id='footer-copyright',
            className='container-fluid text-center',
            children=[
                html.Div(children='''V 1.0 por: Álvaro Gonzalo''',
                        style = {'font-size':16,'font-family': "Helvetica Neue",
                                'color':'#ffffff'}),
                dcc.Link('MachineLearningParaTodos.com', href='https://machinelearningparatodos.com/',
                        style={'color':'#ffffff', 'fontWeight': 'bold'}),
                html.Br()]),
        className='page-footer',
        style={
            'textAlign': 'center',
            'width': '100%',
            'background-color': '#1e1e1e'}, )

def devuelve_figura_con_kpis(confirmados, fallecidos, recuperados):
    figura_aux = go.Figure()
    figura_aux.add_trace(go.Indicator(
        mode = "number",
        value = confirmados,
        number={"font":{"size":50, "color":'orange'}},
        domain = {'row': 1, 'column': 0},
        title = {"text": "Confirmados", "font":{"size":TAMANIO_LETRA_KPIS}}))
    figura_aux.add_trace(go.Indicator(
        mode = "number",
        value = fallecidos,
        number={"font":{"size":50, "color":'red'}},
        domain = {'row': 1, 'column': 1},
        title = {"text": "Fallecidos", "font":{"size":TAMANIO_LETRA_KPIS}}))
    figura_aux.add_trace(go.Indicator(
        mode = "number",
        value = recuperados,
        number={"font":{"size":50, "color":'green'}},
        domain = {'row': 1, 'column': 2},
        title = {"text": "Recuperados", "font":{"size":TAMANIO_LETRA_KPIS}}))
    figura_aux.add_trace(go.Indicator(
        mode = "number",
        value = recuperados/(recuperados+fallecidos),
        number={"font":{"size":50, "color":'black'}},
        domain = {'row': 1, 'column': 3},
        title = {"text": "Tasa de recuperación", "font":{"size":TAMANIO_LETRA_KPIS}}))
    figura_aux.update_layout(
        grid = {'rows': 1, 'columns': 4, 'pattern': "independent"}, 
        height=100)
    return figura_aux

def devuelve_figura_con_kpis_doble(confirmados, fallecidos, recuperados):
    figura_aux = go.Figure()
    figura_aux.add_trace(go.Indicator(
        mode = "number",
        value = confirmados[0],
        number={"font":{"size":50, "color":'orange'}},
        domain = {'row': 0, 'column': 0},
        title = {"text": "Confirmados totales", "font":{"size":TAMANIO_LETRA_KPIS}}))
    figura_aux.add_trace(go.Indicator(
        mode = "number",
        value = fallecidos[0],
        number={"font":{"size":50, "color":'red'}},
        domain = {'row': 0, 'column': 1},
        title = {"text": "Fallecidos totales", "font":{"size":TAMANIO_LETRA_KPIS}}))
    figura_aux.add_trace(go.Indicator(
        mode = "number",
        value = recuperados[0],
        number={"font":{"size":50, "color":'green'}},
        domain = {'row': 0, 'column': 2},
        title = {"text": "Recuperados totales", "font":{"size":TAMANIO_LETRA_KPIS}}))
    figura_aux.add_trace(go.Indicator(
        mode = "number",
        value = confirmados[1],
        number={"font":{"size":50, "color":'orange'}},
        domain = {'row': 1, 'column': 0},
        title = {"text": "Confirmados en España", "font":{"size":TAMANIO_LETRA_KPIS}}))
    figura_aux.add_trace(go.Indicator(
        mode = "number",
        value = fallecidos[1],
        number={"font":{"size":50, "color":'red'}},
        domain = {'row': 1, 'column': 1},
        title = {"text": "Fallecidos en España", "font":{"size":TAMANIO_LETRA_KPIS}}))
    figura_aux.add_trace(go.Indicator(
        mode = "number",
        value = recuperados[1],
        number={"font":{"size":50, "color":'green'}},
        domain = {'row': 1, 'column': 2},
        title = {"text": "Recuperados en España", "font":{"size":TAMANIO_LETRA_KPIS}}))
    figura_aux.update_layout(
        grid = {'rows': 2, 'columns': 3, 'pattern': "independent"}, 
        height=200, width=800,margin=dict(t=20, b=0, l=5, r=5))
    return figura_aux

# *********************************************************************************************************
# --------------------------- GENERACIÓN DEL SERVIDOR CON DASH --------------------------------------------
# *********************************************************************************************************
# Genero servidor dash
# Las apps hechas con Dash son aplicaciones web. Dash usa flask como framework web.
app = dash.Dash(__name__, external_stylesheets = ESTILO_DASHBOARD)
app.title = 'Infecciones por el coronavirus'
server = app.server # Flask app 

# *********************************************************************************************************
# --------------------------- LECTURA Y PREPARACIÓN DE DATOS ----------------------------------------------
# *********************************************************************************************************
df=pd.read_csv(URL)
df_fallecidos=pd.read_csv(URL_FALLECIMIENTOS)
df_recuperados=pd.read_csv(URL_RECUPERADOS)

# Defino la variable 
df['casos_totales'] = df[df.columns[-1]]
df_recuperados['casos_totales'] = df_recuperados[df_recuperados.columns[-1]]
df_fallecidos['casos_totales'] = df_fallecidos[df_fallecidos.columns[-1]]

# Renombro columnas
df.rename(columns = {'Province/State':'State'}, inplace = True)
df_fallecidos.rename(columns = {'Province/State':'State'}, inplace = True)
df_recuperados.rename(columns = {'Province/State':'State'}, inplace = True)

confirmados_totales = df['casos_totales'].sum()
fallecidos_totales = df_fallecidos['casos_totales'].sum()
recuperados_totales = df_recuperados['casos_totales'].sum()

# Análisis de Hubei
df_H, df_H_fall, df_H_recup = devuelve_dfs_localizacion_estado(df, 'Hubei')
# Obtengo infecciones de USA
df_USA, df_USA_fall, df_USA_recup = devuelve_dfs_localizacion_pais(df, 'US')
# Obtengo infecciones de España
df_ITALY, df_ITALY_fall, df_ITALY_recup = devuelve_dfs_localizacion_pais(df, 'Italy')
# Obtengo infecciones de China
df_CHINA, df_CHINA_d, df_CHINA_r = devuelve_dfs_localizacion_pais(df, 'China')
confirmados_china_totales, fallecidos_china_totales, recuperados_china_totales = calculo_metricas_totales(df_CHINA, df_CHINA_d, df_CHINA_r)
# Obtengo infecciones de España
df_ESP, df_ESP_d, df_ESP_r = devuelve_dfs_localizacion_pais(df, 'Spain')
confirmados_esp_totales, fallecidos_esp_totales, recuperados_esp_totales = calculo_metricas_totales(df_ESP, df_ESP_d, df_ESP_r)
# Obtengo infecciones de fuera de China
df_OTROS, df_OTROS_d, df_OTROS_r =  devuelve_dfs_localizacion_pais(df, 'China', flag_not=True)
confirmados_otros_totales, fallecidos_otros_totales, recuperados_otros_totales = calculo_metricas_totales(df_OTROS, df_OTROS_d, df_OTROS_r)


df_agrupado=df.groupby(['Country/Region']).sum()
df_agrupado.reset_index(inplace=True)

# Países más infectados después de China
df_mas_infectados = df_agrupado.loc[(df_agrupado['casos_totales']>CORTE_PAISES_MAS_INFECTADOS) 
                                    & (df_agrupado['Country/Region']!='China')]
df_mas_infectados.reset_index(inplace=True)
# Países menos infectados
df_menos_infectados = df_agrupado.loc[(df_agrupado['casos_totales']<CORTE_PAISES_MENOS_INFECTADOS)]
df_menos_infectados.reset_index(inplace=True)
# China
df_china=df.loc[df['Country/Region']=='China']
df_china.reset_index(inplace=True)

# Escalas para las series temporales
x = pd.date_range(start = "2020-01-22", end = datetime.now(), freq = "D")
x = [pd.to_datetime(date, format='%Y-%m-%d').date() for date in x]

y_index = pd.date_range(start = datetime.strftime(datetime(2020, 1, 22),'%-m/%-d/%y'), 
                        end = df.columns[-2], freq = "D")
y_index = [datetime.strftime(date,'%-m/%-d/%y') for date in y_index]

# Evolución para Hubei
y_hubei, y_hubei_d, y_hubei_r = devuelve_evol_local([df_H, df_H_fall, df_H_recup], y_index, pais=False)
# Evolución para USA
y_usa, y_usa_d, y_usa_r = devuelve_evol_local([df_USA, df_USA_fall, df_USA_recup], y_index, pais=True)
# Evolución para Italia
y_italy, y_italy_d, y_italy_r = devuelve_evol_local([df_ITALY, df_ITALY_fall, df_ITALY_recup], y_index, pais=True)
# Evolución para España
y_esp, y_esp_d, y_esp_r = devuelve_evol_local([df_ESP, df_ESP_d, df_ESP_r], y_index, pais=True)


figura_kpis = devuelve_figura_con_kpis_doble([confirmados_totales, confirmados_esp_totales], 
                                             [fallecidos_totales,fallecidos_esp_totales], 
                                             [recuperados_totales,recuperados_esp_totales])

figura_kpis_china = devuelve_figura_con_kpis(confirmados_china_totales, 
                                             fallecidos_china_totales, 
                                             recuperados_china_totales)

figura_kpis_esp = devuelve_figura_con_kpis(confirmados_esp_totales, 
                                             fallecidos_esp_totales, 
                                             recuperados_esp_totales)

figura_kpis_otros = devuelve_figura_con_kpis(confirmados_otros_totales, 
                                             fallecidos_otros_totales, 
                                             recuperados_otros_totales)

# *********************************************************************************************************
# --------------------------- PLANTILLA PRINCIPAL DE DASH -------------------------------------------------
# *********************************************************************************************************
app.layout = html.Div([
    # Inserto títulos
    html.Div([
        html.Br(),
        html.H1(children='Dashboard de seguimiento del coronavirus'),
        html.Div(children=''''''),
        html.Div(children='''Visualizaciones del incremento de infectados desde el 22 de enero de 2020''',
                 style = {'font-size':16,'font-family': "Helvetica Neue"}),
        html.Div(children='''Datos actualizados a día {0}'''.format(DIA_ACTUALIZACION),
                 style = {'font-size':16,'font-family': "Helvetica Neue"}),
        html.Br(),
        ],style = {'textAlign':'center','font-family': "Helvetica Neue", 
                   'background-color': '#1e1e1e', 'width': '100%','color':'#ffffff'}),
    # Inserto figura con kpis
    html.Br(),
    html.Div([
    dcc.Graph(id='kpis',figure=figura_kpis,)], 
        style = {'width': '100%', 'display': 'flex', 'align-items': 'center', 'justify-content': 'center'}),
    
    # Inserto el mapa de infectados general
    html.H3(children='Mapa de infectados por coronavirus desde el 22 de enero de 2020', 
            style = {'textAlign':'center','font-family': "Helvetica Neue"}),
    dcc.Graph(
        id='mapa-principal',
        figure= go.Figure(data=go.Scattergeo(
        locationmode = 'ISO-3',
        lon = df.loc[df['casos_totales']>0]['Long'],
        lat = df.loc[df['casos_totales']>0]['Lat'],
        text = 'Estado: ' + df.loc[df['casos_totales']>0]['State'].astype(str) \
                + ' <br> Pais: ' + df.loc[df['casos_totales']>0]['Country/Region'].astype(str) \
                + ' <br> Casos: ' + df.loc[df['casos_totales']>0]['casos_totales'].astype(str),
        mode = 'markers',
        marker = dict(
            # Tamanio de los circulos en el mapa principal de contagios
            size = np.sqrt(df.loc[df['casos_totales']>0]['casos_totales']/30)+10,
            opacity = 0.8,
            reversescale = True,
            autocolorscale = False,
            color='red',
            line = dict(width=1,color='rgba(102, 102, 102)'))),
                          layout=dict(geo = dict(showcountries = True), 
                                      height=800, template=PLANTILLA, margin=dict(t=10)))),
    # Inserto saltos de líneas
    html.Br(),
    html.Div(children=''''''),
    html.Div(children=''''''),
    
    # Inserto pestañas de selección
    dcc.Tabs(id="menu-pestanias", value='pestania-consejos',
             children=[
                 dcc.Tab(label='China', id='tab1', value='pestania-china', style=ESTILO_PESTANIA, 
                         selected_style=ESTILO_SELECCIONADA),
                 dcc.Tab(label=u'España', id='tab3', value='pestania-espania', style=ESTILO_PESTANIA, 
                         selected_style=ESTILO_SELECCIONADA),
                 dcc.Tab(label='Fuera de China', id='tab2',value='pestania-out-china', style=ESTILO_PESTANIA,
                         selected_style=ESTILO_SELECCIONADA),
                 dcc.Tab(label='Edad y patologías', id='tab4',value='pestania-edad-patologias', style=ESTILO_PESTANIA,
                         selected_style=ESTILO_SELECCIONADA),
                 dcc.Tab(label='Consejos básicos', id='tab5',value='pestania-consejos', style=ESTILO_PESTANIA,
                         selected_style=ESTILO_SELECCIONADA),
                 dcc.Tab(label='Análisis 5/5/2020', id='tab6',value='pestania-analisis', style=ESTILO_PESTANIA,
                         selected_style=ESTILO_SELECCIONADA),
             ], style=ESTILO_PESTANIAS),
    # Inserto el contenido de la pestaña seleccionada
    html.Div(id='contenido-pestanias'),
    # Inserto footer
    render_footer()])


# *********************************************************************************************************
# --------------------------- CALLBACK DE LA PESTAÑA DE SELECCIÓN -----------------------------------------
# *********************************************************************************************************
@app.callback(Output('contenido-pestanias', 'children'),[Input('menu-pestanias', 'value')])
def render_content(tab):
    # Pestaña China
    if tab == 'pestania-china':
        return html.Div(children=[
            # Inserto saltos de línea
            html.Br(),
            html.Br(),
            # Inserto figuras con kpis de china
            dcc.Graph(id='kpis', figure=figura_kpis_china),
            html.Div(children=''''''),
            # Inserto la tendencia de infectados
            html.H4(children='Tendencia de infectados en Hubei (estado con más casos)', 
                    style = {'textAlign':'center','font-family': "Helvetica Neue"}),
            dcc.Graph(
                id='example-scatter',
                figure=go.Figure(data = [
                    go.Scatter(
                        x=x, y=y_hubei, mode='lines+markers',name='Casos confirmados',
                        marker_color='rgba(152, 0, 0, .8)'),
                    go.Scatter(x=x,y=y_hubei_d, name='Fallecimientos', 
                               mode='lines+markers',
                               marker_color='rgb(231, 99, 250)'),
                    go.Scatter(x=x,y=y_hubei_r, name='Casos sanados',
                               mode='lines+markers',
                               marker_color='rgb(17, 157, 255)')],
                 layout = go.Layout(margin=dict(t=10),height=600,
                                    xaxis = dict(range = [a_tiempo_unix(datetime(2020, 1, 21)),
                                                          a_tiempo_unix(datetime.now())]),
                                    template=PLANTILLA, yaxis_title="Población acumulada (en miles)"))),

            # Inserto separación
            html.Div(children=''''''),
            # Inserto infectados por estado en China
            html.H4(children='Infectados por coronavirus en estados de China', 
                    style = {'textAlign':'center','font-family': "Helvetica Neue"}),
            dcc.Graph(id='example-graph1',
                      figure=go.Figure(data=[go.Bar(
                          x=df_china['State'].tolist(), y=df_china['casos_totales'].tolist(),
                          text=df_china['casos_totales'].tolist(),textposition='auto',)],
                                       layout=go.Layout(height=600,margin=dict(t=10),
                                                        template=PLANTILLA))),])
    # Pestaña fuera de China
    elif tab == 'pestania-out-china':
        return html.Div(children=[
        html.Br(),
        html.Br(),
        # Inserto figura con kpis de otros países
        dcc.Graph(id='kpis', figure=figura_kpis_otros),
        html.Div(children=''''''),
            
        # Inserto infectados en otros países del mundo
        html.H4(children='Infectados en otros países del mundo', 
                style = {'textAlign':'center','font-family': "Helvetica Neue"}),
        dcc.Graph(
        id='example-graph3',
        figure=go.Figure(data=[go.Bar(
            x=df_mas_infectados['Country/Region'].tolist(), 
            y=df_mas_infectados['casos_totales'].tolist(),
            text=df_mas_infectados['casos_totales'].tolist(),
            textposition='auto',
        )],layout=go.Layout(height=600,margin=dict(t=10),
                            template=PLANTILLA, yaxis_title="Población total infectada"))),
        html.Div(children=''''''),
            
        # Inserto tendencia en Italia
        html.H4(children='Tendencia de infectados por coronavirus en Italia', 
                style = {'textAlign':'center','font-family': "Helvetica Neue"}),
        dcc.Graph(
            id='example-scatter2',
            figure=go.Figure(data = [go.Scatter(
            x=x,
            y=y_italy,
            name='Casos confirmados',
            mode='lines+markers',
            marker_color='rgba(152, 0, 0, .8)'), go.Scatter(
            x=x,
            y=y_italy_d,
            name='Fallecimientos',
            mode='lines+markers',
            marker_color='rgb(231, 99, 250)'),go.Scatter(
            x=x,
            y=y_italy_r,
            name='Casos sanados',
            mode='lines+markers',
            marker_color='rgb(17, 157, 255)')],
            layout = go.Layout(yaxis_title="Población acumulada", height=600,xaxis = dict(
                    range = [a_tiempo_unix(datetime(2020, 1, 21)),
                                a_tiempo_unix(datetime.now())]
                                ), template=PLANTILLA, margin=dict(t=10)))),
            # Inserto separación
            html.Div(children=''''''),
            html.Div(children=[
            # Inserto tarta paises más infectados
            html.Div(dcc.Graph(
                id='example-graph4',
                figure={
                    'data': [
                        go.Pie(
                            labels=list(df_mas_infectados['Country/Region']),
                            values=list(df_mas_infectados['casos_totales']),
                            hoverinfo='label+value+percent')],
                    'layout':{
                        'showlegend':True,
                        'title':'Países más infectados después de China',
                        'height':700, 
                        'width':800,
                        'annotations':[],
                        'template':PLANTILLA}}
            ), style={'display': 'inline-block'}),
            
            # Inserto tarta países menos infectados
            html.Div(
                dcc.Graph(
                    id='example-graph5',
                    figure={
                        'data': [
                            go.Pie(
                                labels=list(df_menos_infectados['Country/Region']),
                                values=list(df_menos_infectados['casos_totales']),
                                hoverinfo='label+value+percent'
                            )
                        ],
                        'layout':{
                            'showlegend':True,
                            'title':'Países menos infectados pero con algún caso',
                            'height':700,
                            'width':800,
                            'annotations':[],
                            'template':PLANTILLA}}), 
                 style={'display': 'inline-block'})
            ], style={'width': '100%', 'display': 'inline-block', 'Align':'center'})
        ])
    
    # Pestaña España
    elif tab == 'pestania-espania':
        return html.Div(children=[
            # Inserto saltos de línea
            html.Br(),
            html.Br(),
            # Inserto kpis para España
            dcc.Graph(id='kpis',figure=figura_kpis_esp),
            # Inserto tendencia de infectados en España
            html.Div(children=''''''),
            html.H4(children='Tendencia de infectados en España', 
                    style = {'textAlign':'center','font-family': "Helvetica Neue"}),
            dcc.Graph(
                id='example-scatter3',
                figure=go.Figure(data = [
                    go.Scatter(
                        x=x,y=y_esp,mode='lines+markers',name='Casos confirmados',
                        marker_color='rgba(152, 0, 0, .8)'),
                    go.Scatter(
                        x=x,y=y_esp_d,name='Fallecimientos',mode='lines+markers',
                        marker_color='rgb(231, 99, 250)'),
                    go.Scatter(
                        x=x,y=y_esp_r,name='Casos sanados',mode='lines+markers',
                        marker_color='rgb(17, 157, 255)')],
                 layout = go.Layout(margin=dict(t=10),height=600,
                        xaxis = dict(range = [a_tiempo_unix(datetime(2020, 1, 21)),
                                              a_tiempo_unix(datetime.now())]),
                        template=PLANTILLA, yaxis_title="Población acumulada"))),
            html.Div(children=''''''),
            
            # Inserto mapa de infectados por comunidad autónoma en html
            html.H4(children='Infectados en España por comunidad autónoma (actualizado el 16 de abril de 2020)', 
                    style = {'textAlign':'center','font-family': "Helvetica Neue"}),
            html.Iframe(srcDoc = open('infectados_espania.html', 'r').read(),
                        style={'width': '80%', 'height':800, 'padding-left':'10%', 'border': 'white'}),  
            html.Br(),
        ])
    
    # Pestaña Edad y patologías
    elif tab == 'pestania-edad-patologias':
        return html.Div(children=[            
            html.Br(),
            html.Br(),
            html.Div(children='''Los datos por edades y patologías previas provienen del gobierno chino y están actualizados a día 29 de febrero de 2020''', 
                    style = {'font-size':17,'font-family': "Helvetica Neue"}),
            html.Div(children='''- Tasa de mortalidad: número de muertes/casos confirmados''', 
                     style = {'font-size':20,'font-family': "Helvetica Neue"}),
            html.H4(children='Tasa de mortalidad por edad (COVID-19 confirmado y personas con síntomas...)', 
                    style = {'textAlign':'center','font-family': "Helvetica Neue"}),
            # Gráfico de tasa de mortalidad por edad
            dcc.Graph(
                id='example-scatter4',
                figure=go.Figure([go.Bar(x=EDADES, y=RATIOS_EDADES, marker={'color': RATIOS_EDADES,
                                                                            'colorscale': 'Reds'}), 
                                  go.Scatter(x=EDADES,y=RATIOS_EDADES)],
                                 layout = go.Layout(margin=dict(t=10), template=PLANTILLA, 
                                                    width=600, yaxis_title="Tasa de mortalidad (%)",
                                                    showlegend=False))), 
            # Gráfico de tasa de mortalidad por sexo
            html.H4(children='Tasa de mortalidad por sexo (COVID-19 confirmado)', 
                    style = {'textAlign':'center','font-family': "Helvetica Neue"}),
            dcc.Graph(
                id='example-scatter5',
                figure=go.Figure([go.Bar(x=SEXO, y=RATIOS_SEXO, marker={'color': RATIOS_EDADES,
                                                                        'colorscale': 'Reds'}), 
                                  go.Scatter(x=SEXO,y=RATIOS_SEXO)],
                                 layout = go.Layout(margin=dict(t=10), template=PLANTILLA,
                                                    width=600, yaxis_title="Tasa de mortalidad (%)",
                                                    showlegend=False))), 
            
            # Gráfico de tasa de mortalidad por patologías previas
            html.H4(children='Tasa de mortalidad según la patología previa', 
                    style = {'textAlign':'center','font-family': "Helvetica Neue"}),
            dcc.Graph(
                id='example-scatter6',
                figure=go.Figure([go.Bar(x=PATOLOGIAS, y=RATIOS_PATOLOGIAS, marker={'color': RATIOS_EDADES,
                                                                                    'colorscale': 'Reds'}), 
                                  go.Scatter(x=PATOLOGIAS,y=RATIOS_PATOLOGIAS)],
                                 layout = go.Layout(margin=dict(t=10), template=PLANTILLA,
                                                    yaxis_title="Tasa de mortalidad (%)",showlegend=False))),])
    elif tab == 'pestania-analisis':
        return html.Div(children=[
            html.Br(),
            html.Div(children='''Este es un análisis que hice para la asociación Women in Big Data Madrid''', style = {'font-size':20,'font-family': "Helvetica Neue"}),
            html.Br(),
            html.Div(html.Iframe(id="embedded-pdf", src="assets/covid19_5_mayo_2020.pdf",style={'width': '80%', 'height':800, 'padding-left':'10%', 'border': 'white'}))])
    elif tab == 'pestania-consejos':
        return html.Div(children=[
            html.Br(),
            html.Div(children='''Consejos obtenidos de la web de la Organización Mundial de la salud.''', 
                    style = {'font-size':20,'font-family': "Helvetica Neue"}),
            html.Br(),
            html.H4(children='Lávese las manos frecuentemente', 
                    style = {'font-weight': 'bold','font-family': "Helvetica Neue"}),

            html.Br(),
            html.Div(children='''Lávese las manos con frecuencia con un desinfectante de manos a base de alcohol o con agua y jabón.''', 
                    style = {'font-size':20,'font-family': "Helvetica Neue"}),
            html.Br(),
            html.H4(children='Adopte medidas de higiene respiratoria', 
                    style = {'font-weight': 'bold','font-family': "Helvetica Neue"}),
            html.Br(),
            html.Div(children='''Al toser o estornudar, cúbrase la boca y la nariz con el codo flexionado o con un pañuelo; tire el pañuelo inmediatamente y lávese las manos con un desinfectante de manos a base de alcohol, o con agua y jabón.''', 
                    style = {'font-size':20,'font-family': "Helvetica Neue"}),
            html.Br(),
            html.H4(children='Mantenga el distanciamiento social', 
                    style = {'font-weight': 'bold','font-family': "Helvetica Neue"}),
            html.Br(),
            html.Div(children='''Mantenga al menos 1 metro (3 pies) de distancia entre usted y las demás personas, particularmente aquellas que tosan, estornuden y tengan fiebre.''', 
                    style = {'font-size':20,'font-family': "Helvetica Neue"}),
            
            html.Br(),
            html.H4(children='Evite tocarse los ojos, la nariz y la boca', 
                    style = {'font-weight': 'bold','font-family': "Helvetica Neue"}),
            html.Br(),
            html.Div(children='''Las manos tocan muchas superficies que pueden estar contaminadas con el virus. Si se toca los ojos, la nariz o la boca con las manos contaminadas, puedes transferir el virus de la superficie a si mismo.''', 
                    style = {'font-size':20,'font-family': "Helvetica Neue"}),
            
            html.Br(),
            html.H4(children='Si tiene fiebre, tos y dificultad para respirar, solicite atención médica a tiempo', 
                    style = {'font-weight': 'bold','font-family': "Helvetica Neue"}),

            html.Br(),
            html.Div(children='''Indique a su prestador de atención de salud si ha viajado a una zona de China en la que se haya notificado la presencia del 2019-nCoV, o si ha tenido un contacto cercano con alguien que haya viajado desde China y tenga síntomas respiratorios.''', 
                    style = {'font-size':20,'font-family': "Helvetica Neue"}),
            html.Br(),])

# *********************************************************************************************************
# ---------------------- MAIN -----------------------------------------------------------------------------
# *********************************************************************************************************
if __name__ == '__main__':
    # Opción en local
    # app.run_server(debug=True, host='0.0.0.0', use_reloader=False)
    # Opción en Heroku
    app.run_server(debug=True) 