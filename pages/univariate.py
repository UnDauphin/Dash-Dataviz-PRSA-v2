# pages/univariate.py - VERSIÓN CORREGIDA
from dash import dcc, html, Input, Output, callback, dash_table
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from statsmodels.tsa.stattools import adfuller, kpss
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
import matplotlib.pyplot as plt
import io
import base64

from utils.data_loader import get_data

# Obtener datos
df_original, df_imputed, analysis_cols = get_data()

# Layout principal de análisis univariado
layout = html.Div([
    html.H2("📈 Análisis Univariado", 
            style={'color': '#ffffff', 'marginBottom': '20px'}),
    
    dcc.Tabs(id="univariate-tabs", value='tab-distributions', children=[
        dcc.Tab(
            label='📊 Distribuciones', 
            value='tab-distributions',
            style={'padding': '10px', 'fontWeight': 'bold'},
            selected_style={'backgroundColor': '#1e293b'}
        ),
        dcc.Tab(
            label='📈 Series Temporales', 
            value='tab-timeseries',
            style={'padding': '10px', 'fontWeight': 'bold'},
            selected_style={'backgroundColor': '#1e293b'}
        ),
        dcc.Tab(
            label='⚖️ Estacionariedad', 
            value='tab-stationarity',
            style={'padding': '10px', 'fontWeight': 'bold'},
            selected_style={'backgroundColor': '#1e293b'}
        ),
        dcc.Tab(
            label='🔄 Autocorrelación', 
            value='tab-autocorrelation',
            style={'padding': '10px', 'fontWeight': 'bold'},
            selected_style={'backgroundColor': '#1e293b'}
        ),
    ]),
    
    html.Div(id='univariate-tab-content', style={'marginTop': '20px'})
])

def render_distributions():
    """Pestaña de distribuciones"""
    return html.Div([
        html.H3("📊 Distribuciones de Variables", style={'color': '#ffffff'}),
        html.P("Selecciona una variable para ver su distribución:"),
        
        html.Div([
            html.Label("Variable:", style={'color': '#ffffff', 'marginRight': '10px'}),
            dcc.Dropdown(
                id='dist-variable-selector',
                options=[{'label': col, 'value': col} for col in analysis_cols],
                value=analysis_cols[0] if analysis_cols else None,
                style={'width': '300px', 'color': '#000000'}
            )
        ], style={'marginBottom': '20px'}),
        
        dcc.Graph(id='distribution-plot'),
        
        html.Div(id='distribution-stats', style={'marginTop': '20px'})
    ])

def render_timeseries():
    """Pestaña de series temporales univariadas"""
    if 'datetime' not in df_imputed.columns or df_imputed.empty:
        return html.Div([
            html.H3("📈 Series Temporales Individuales", style={'color': '#ffffff'}),
            html.P("❌ No se detectó columna de fecha/hora (datetime) o no hay datos disponibles.")
        ])
    
    return html.Div([
        html.H3("📈 Series Temporales Individuales", style={'color': '#ffffff'}),
        html.P("Selecciona una variable para ver su serie temporal:"),
        
        html.Div([
            html.Label("Variable:", style={'color': '#ffffff', 'marginRight': '10px'}),
            dcc.Dropdown(
                id='ts-variable-selector',
                options=[{'label': col, 'value': col} for col in analysis_cols],
                value=analysis_cols[0] if analysis_cols else None,
                style={'width': '300px', 'color': '#000000'}
            )
        ], style={'marginBottom': '20px'}),
        
        dcc.Graph(id='timeseries-plot')
    ])

def render_stationarity():
    """Pestaña de estacionariedad"""
    if 'datetime' not in df_imputed.columns or df_imputed.empty:
        return html.Div([
            html.H3("⚖️ Análisis de Estacionariedad", style={'color': '#ffffff'}),
            html.P("❌ No hay datos temporales disponibles para análisis de estacionariedad.")
        ])
    
    return html.Div([
        html.H3("⚖️ Análisis de Estacionariedad", style={'color': '#ffffff'}),
        html.P("Selecciona una variable para realizar tests de estacionariedad:"),
        
        html.Div([
            html.Label("Variable:", style={'color': '#ffffff', 'marginRight': '10px'}),
            dcc.Dropdown(
                id='stationarity-variable-selector',
                options=[{'label': col, 'value': col} for col in analysis_cols],
                value=analysis_cols[0] if analysis_cols else None,
                style={'width': '300px', 'color': '#000000'}
            )
        ], style={'marginBottom': '20px'}),
        
        html.Button('Ejecutar Tests de Estacionariedad', 
                   id='run-stationarity-tests',
                   style={'backgroundColor': '#3b82f6', 
                          'color': 'white', 
                          'padding': '10px 20px',
                          'border': 'none',
                          'borderRadius': '5px',
                          'cursor': 'pointer'}),
        
        html.Div(id='stationarity-results', style={'marginTop': '20px'})
    ])

def render_autocorrelation():
    """Pestaña de autocorrelación"""
    if 'datetime' not in df_imputed.columns or df_imputed.empty:
        return html.Div([
            html.H3("🔄 Análisis de Autocorrelación", style={'color': '#ffffff'}),
            html.P("❌ No hay datos temporales disponibles para análisis de autocorrelación.")
        ])
    
    return html.Div([
        html.H3("🔄 Análisis de Autocorrelación", style={'color': '#ffffff'}),
        html.P("Selecciona una variable para ver sus funciones de autocorrelación:"),
        
        html.Div([
            html.Label("Variable:", style={'color': '#ffffff', 'marginRight': '10px'}),
            dcc.Dropdown(
                id='acf-variable-selector',
                options=[{'label': col, 'value': col} for col in analysis_cols],
                value=analysis_cols[0] if analysis_cols else None,
                style={'width': '300px', 'color': '#000000'}
            )
        ], style={'marginBottom': '20px'}),
        
        html.Label("Número de Lags:", style={'color': '#ffffff', 'marginRight': '10px'}),
        dcc.Slider(
            id='acf-lags-slider',
            min=10,
            max=100,
            step=5,
            value=40,
            marks={i: str(i) for i in range(10, 101, 10)},
        ),
        
        html.Div([
            dcc.Graph(id='acf-plot'),
            dcc.Graph(id='pacf-plot')
        ], style={'display': 'flex', 'flexDirection': 'column', 'gap': '20px'})
    ])

def register_callbacks(app):
    from utils.data_loader import get_data
    
    # Callback para cambiar sub-pestañas
    @app.callback(
        Output('univariate-tab-content', 'children'),
        Input('univariate-tabs', 'value')
    )
    def render_univariate_tab(tab):
        if tab == 'tab-distributions':
            return render_distributions()
        elif tab == 'tab-timeseries':
            return render_timeseries()
        elif tab == 'tab-stationarity':
            return render_stationarity()
        elif tab == 'tab-autocorrelation':
            return render_autocorrelation()
        return html.Div("Selecciona una sub-pestaña")
    
    # Callback para actualizar distribuciones
    @app.callback(
        [Output('distribution-plot', 'figure'),
         Output('distribution-stats', 'children')],
        Input('dist-variable-selector', 'value')
    )
    def update_distribution(selected_var):
        if not selected_var:
            return {}, ""
            
        df_orig, df_imp, _ = get_data()
        
        if df_imp.empty or selected_var not in df_imp.columns:
            return {}, ""
            
        data = df_imp[selected_var].dropna()
        
        if len(data) == 0:
            return {}, html.Div("No hay datos disponibles para esta variable.")
        
        # Crear histograma
        fig = px.histogram(
            data, x=data, nbins=40, 
            title=f"Distribución de {selected_var}",
            marginal="box",
            template='plotly_dark'
        )
        fig.update_layout(
            plot_bgcolor='#1e293b',
            paper_bgcolor='#1e293b',
            font_color='white',
            height=500
        )
        
        # Estadísticas
        stats_df = df_imp[selected_var].describe().reset_index()
        stats_df.columns = ['Estadístico', 'Valor']
        
        stats_table = dash_table.DataTable(
            data=stats_df.to_dict('records'),
            columns=[{"name": i, "id": i} for i in stats_df.columns],
            style_cell={
                'backgroundColor': '#1e293b',
                'color': 'white',
                'textAlign': 'left',
                'padding': '10px',
                'border': '1px solid #334155'
            },
            style_header={
                'backgroundColor': '#334155',
                'color': 'white',
                'fontWeight': 'bold'
            },
        )
        
        return fig, html.Div([
            html.H4("📊 Estadísticas Descriptivas", style={'color': '#ffffff'}),
            stats_table
        ])
    
    # Callback para actualizar series temporales
    @app.callback(
        Output('timeseries-plot', 'figure'),
        Input('ts-variable-selector', 'value')
    )
    def update_timeseries(selected_var):
        if not selected_var:
            return {}
            
        df_orig, df_imp, _ = get_data()
        
        if df_imp.empty or selected_var not in df_imp.columns or 'datetime' not in df_imp.columns:
            return {}
        
        try:
            # Resample diario para mejor visualización
            dfts = df_imp.set_index('datetime').resample('D')[selected_var].mean().reset_index()
            
            fig = px.line(
                dfts, x='datetime', y=selected_var, 
                title=f"Serie Temporal Diaria de {selected_var}",
                template='plotly_dark'
            )
            fig.update_layout(
                plot_bgcolor='#1e293b',
                paper_bgcolor='#1e293b',
                font_color='white',
                height=500
            )
            
            return fig
        except Exception as e:
            print(f"Error en update_timeseries: {e}")
            return {}
    
    # Callback para tests de estacionariedad
    @app.callback(
        Output('stationarity-results', 'children'),
        [Input('run-stationarity-tests', 'n_clicks'),
         Input('stationarity-variable-selector', 'value')]
    )
    def update_stationarity(n_clicks, selected_var):
        if not n_clicks or not selected_var:
            return html.Div("Haz clic en 'Ejecutar Tests' para analizar la estacionariedad.")
        
        df_orig, df_imp, _ = get_data()
        
        if df_imp.empty or selected_var not in df_imp.columns:
            return html.Div("❌ Variable no disponible.")
        
        data = df_imp[selected_var].dropna()
        
        if len(data) < 2:
            return html.Div("❌ Datos insuficientes para el análisis.")
        
        try:
            # Test ADF
            adf_result = adfuller(data)
            adf_statistic = adf_result[0]
            adf_pvalue = adf_result[1]
            adf_critical_values = adf_result[4]
            
            # Test KPSS
            kpss_result = kpss(data, regression='c')
            kpss_statistic = kpss_result[0]
            kpss_pvalue = kpss_result[1]
            kpss_critical_values = kpss_result[3]
            
            # Interpretación
            is_stationary_adf = adf_pvalue < 0.05
            is_stationary_kpss = kpss_pvalue > 0.05
            
            conclusion = ""
            if is_stationary_adf and is_stationary_kpss:
                conclusion = "✅ La serie es ESTACIONARIA"
                color = "#10b981"
            elif not is_stationary_adf and not is_stationary_kpss:
                conclusion = "❌ La serie es NO ESTACIONARIA"
                color = "#ef4444"
            else:
                conclusion = "⚠️  Resultados contradictorios - se requiere análisis adicional"
                color = "#f59e0b"
            
            return html.Div([
                html.H4(f"Resultados para {selected_var}", style={'color': '#ffffff'}),
                
                html.Div([
                    html.H5("Test de Dickey-Fuller Aumentado (ADF)", style={'color': '#3b82f6'}),
                    html.P(f"Estadístico: {adf_statistic:.4f}"),
                    html.P(f"Valor p: {adf_pvalue:.4f}"),
                    html.P("Hipótesis nula: La serie tiene raíz unitaria (no estacionaria)"),
                    html.P(f"Conclusión: {'RECHAZAR H0 - Serie estacionaria' if is_stationary_adf else 'NO RECHAZAR H0 - Serie no estacionaria'}"),
                    
                    html.H5("Valores Críticos ADF:", style={'marginTop': '15px'}),
                    html.Ul([
                        html.Li(f"1%: {adf_critical_values['1%']:.4f}"),
                        html.Li(f"5%: {adf_critical_values['5%']:.4f}"),
                        html.Li(f"10%: {adf_critical_values['10%']:.4f}")
                    ])
                ], style={
                    'backgroundColor': '#1e293b',
                    'padding': '15px',
                    'borderRadius': '8px',
                    'marginBottom': '15px'
                }),
                
                html.Div([
                    html.H5("Test KPSS", style={'color': '#3b82f6'}),
                    html.P(f"Estadístico: {kpss_statistic:.4f}"),
                    html.P(f"Valor p: {kpss_pvalue:.4f}"),
                    html.P("Hipótesis nula: La serie es estacionaria"),
                    html.P(f"Conclusión: {'NO RECHAZAR H0 - Serie estacionaria' if is_stationary_kpss else 'RECHAZAR H0 - Serie no estacionaria'}"),
                    
                    html.H5("Valores Críticos KPSS:", style={'marginTop': '15px'}),
                    html.Ul([
                        html.Li(f"1%: {kpss_critical_values['1%']:.4f}"),
                        html.Li(f"5%: {kpss_critical_values['5%']:.4f}"),
                        html.Li(f"10%: {kpss_critical_values['10%']:.4f}")
                    ])
                ], style={
                    'backgroundColor': '#1e293b',
                    'padding': '15px',
                    'borderRadius': '8px',
                    'marginBottom': '15px'
                }),
                
                html.Div([
                    html.H4("Conclusión General", style={'color': color}),
                    html.P(conclusion, style={'color': color, 'fontWeight': 'bold', 'fontSize': '18px'})
                ], style={
                    'backgroundColor': '#1e293b',
                    'padding': '15px',
                    'borderRadius': '8px',
                    'textAlign': 'center'
                })
            ])
            
        except Exception as e:
            return html.Div([
                html.H4("❌ Error en el análisis", style={'color': '#ef4444'}),
                html.P(f"Error: {str(e)}")
            ])
    
    # Callback para autocorrelación
    @app.callback(
        [Output('acf-plot', 'figure'),
         Output('pacf-plot', 'figure')],
        [Input('acf-variable-selector', 'value'),
         Input('acf-lags-slider', 'value')]
    )
    def update_autocorrelation(selected_var, lags):
        if not selected_var:
            return {}, {}
            
        df_orig, df_imp, _ = get_data()
        
        if df_imp.empty or selected_var not in df_imp.columns:
            return {}, {}
        
        data = df_imp[selected_var].dropna()
        
        if len(data) < lags:
            return {}, {}
        
        try:
            # Crear figura ACF con Plotly
            from statsmodels.tsa.stattools import acf, pacf
            
            # Calcular ACF y PACF
            acf_values = acf(data, nlags=lags)
            pacf_values = pacf(data, nlags=lags)
            
            lags_range = list(range(len(acf_values)))
            
            # Crear gráfico ACF
            acf_fig = go.Figure()
            acf_fig.add_trace(go.Bar(
                x=lags_range,
                y=acf_values,
                name='ACF',
                marker_color='#3b82f6'
            ))
            acf_fig.update_layout(
                title=f'Función de Autocorrelación (ACF) - {selected_var}',
                xaxis_title='Lag',
                yaxis_title='Autocorrelación',
                template='plotly_dark',
                plot_bgcolor='#1e293b',
                paper_bgcolor='#1e293b',
                font_color='white',
                height=400
            )
            
            # Crear gráfico PACF
            pacf_fig = go.Figure()
            pacf_fig.add_trace(go.Bar(
                x=lags_range,
                y=pacf_values,
                name='PACF',
                marker_color='#10b981'
            ))
            pacf_fig.update_layout(
                title=f'Función de Autocorrelación Parcial (PACF) - {selected_var}',
                xaxis_title='Lag',
                yaxis_title='Autocorrelación Parcial',
                template='plotly_dark',
                plot_bgcolor='#1e293b',
                paper_bgcolor='#1e293b',
                font_color='white',
                height=400
            )
            
            return acf_fig, pacf_fig
            
        except Exception as e:
            print(f"Error en autocorrelación: {e}")
            # Figuras vacías en caso de error
            empty_fig = go.Figure()
            empty_fig.update_layout(
                title=f"Error: {str(e)}",
                template='plotly_dark',
                plot_bgcolor='#1e293b',
                paper_bgcolor='#1e293b',
                font_color='white',
                height=400
            )
            return empty_fig, empty_fig