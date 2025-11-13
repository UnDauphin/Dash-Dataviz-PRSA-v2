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
    """Pestaña de estacionariedad - Versión visual liviana"""
    return html.Div([
        html.H3("📊 Análisis Visual de Estacionariedad", style={'color': '#ffffff'}),
        html.P("🔍 Evaluación mediante gráficos y métricas simples", 
               style={'color': '#94a3b8', 'fontSize': '14px'}),
        
        html.Div([
            html.Label("Variable:", style={'color': '#ffffff', 'marginRight': '10px'}),
            dcc.Dropdown(
                id='stationarity-variable-selector',
                options=[{'label': col, 'value': col} for col in analysis_cols],
                value='PM2.5' if 'PM2.5' in analysis_cols else analysis_cols[0],
                style={'width': '300px', 'color': '#000000'}
            )
        ], style={'marginBottom': '20px'}),
        
        # Gráficos de análisis visual
        dcc.Graph(id='rolling-stats-plot'),
        dcc.Graph(id='seasonal-pattern-plot'),
        
        # Métricas visuales
        html.Div(id='visual-stationarity-metrics', style={'marginTop': '20px'})
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
    # Callback para análisis visual de estacionariedad
    @app.callback(
        [Output('rolling-stats-plot', 'figure'),
        Output('seasonal-pattern-plot', 'figure'),
        Output('visual-stationarity-metrics', 'children')],
        Input('stationarity-variable-selector', 'value')
    )
    def update_visual_stationarity(selected_var):
        if not selected_var:
            return {}, {}, ""
        
        df_orig, df_imp, _ = get_data()
        
        if df_imp.empty or selected_var not in df_imp.columns:
            return {}, {}, ""
        
        data = df_imp[selected_var].dropna()
        
        if len(data) < 100:
            empty_fig = go.Figure()
            empty_fig.update_layout(
                title="Datos insuficientes para análisis",
                template='plotly_dark',
                height=300
            )
            return empty_fig, empty_fig, "❌ Datos insuficientes para análisis"
        
        try:
            # Sample para hacerlo más liviano (máximo 5000 puntos)
            if len(data) > 5000:
                data = data.sample(5000, random_state=42)
            
            # --- GRÁFICO 1: Estadísticas Móviles ---
            fig_rolling = go.Figure()
            
            # Calcular ventana adaptativa
            window_size = min(168, len(data)//10)  # Máximo 1 semana, mínimo 10% de datos
            
            # Media móvil
            rolling_mean = data.rolling(window=window_size, center=True).mean()
            # Desviación estándar móvil
            rolling_std = data.rolling(window=window_size, center=True).std()
            
            # Serie original (muestreada para mejor visualización)
            if len(data) > 1000:
                display_data = data.iloc[::len(data)//1000]
            else:
                display_data = data
            
            fig_rolling.add_trace(go.Scatter(
                x=display_data.index,
                y=display_data,
                mode='lines',
                name='Serie Original',
                line=dict(color='#3b82f6', width=1),
                opacity=0.7
            ))
            
            fig_rolling.add_trace(go.Scatter(
                x=rolling_mean.index,
                y=rolling_mean,
                mode='lines',
                name=f'Media Móvil ({window_size} puntos)',
                line=dict(color='#ef4444', width=3)
            ))
            
            # Banda de desviación estándar
            fig_rolling.add_trace(go.Scatter(
                x=rolling_mean.index,
                y=rolling_mean + rolling_std,
                mode='lines',
                line=dict(width=0),
                showlegend=False
            ))
            
            fig_rolling.add_trace(go.Scatter(
                x=rolling_mean.index,
                y=rolling_mean - rolling_std,
                mode='lines',
                fill='tonexty',
                name='Desviación Estándar',
                line=dict(width=0),
                fillcolor='rgba(239, 68, 68, 0.2)'
            ))
            
            fig_rolling.update_layout(
                title=f'📈 Estadísticas Móviles - {selected_var}',
                xaxis_title='Tiempo',
                yaxis_title='Valor',
                template='plotly_dark',
                height=400,
                showlegend=True
            )
            
            # --- GRÁFICO 2: Patrones Estacionales ---
            fig_seasonal = go.Figure()
            
            # Extraer componentes temporales si existe datetime
            if 'datetime' in df_imp.columns:
                try:
                    # Agrupar por hora del día para ver patrón diario
                    df_temp = df_imp.copy()
                    df_temp['hour'] = pd.to_datetime(df_temp['datetime']).dt.hour
                    hourly_pattern = df_temp.groupby('hour')[selected_var].mean()
                    
                    fig_seasonal.add_trace(go.Scatter(
                        x=hourly_pattern.index,
                        y=hourly_pattern.values,
                        mode='lines+markers',
                        name='Patrón Horario',
                        line=dict(color='#10b981', width=3),
                        marker=dict(size=6)
                    ))
                    
                    # Agrupar por mes para ver patrón anual
                    df_temp['month'] = pd.to_datetime(df_temp['datetime']).dt.month
                    monthly_pattern = df_temp.groupby('month')[selected_var].mean()
                    
                    fig_seasonal.add_trace(go.Scatter(
                        x=monthly_pattern.index,
                        y=monthly_pattern.values,
                        mode='lines+markers',
                        name='Patrón Mensual',
                        line=dict(color='#f59e0b', width=3),
                        marker=dict(size=6)
                    ))
                    
                    fig_seasonal.update_layout(
                        title=f'🔄 Patrones Estacionales - {selected_var}',
                        xaxis_title='Período',
                        yaxis_title='Valor Promedio',
                        template='plotly_dark',
                        height=400
                    )
                    
                except Exception as e:
                    # Fallback: gráfico de distribución
                    fig_seasonal = px.histogram(
                        data, x=data, 
                        title=f'Distribución de {selected_var}',
                        template='plotly_dark'
                    )
                    fig_seasonal.update_layout(height=400)
            else:
                # Sin datos temporales, mostrar distribución
                fig_seasonal = px.histogram(
                    data, x=data, 
                    title=f'Distribución de {selected_var}',
                    template='plotly_dark'
                )
                fig_seasonal.update_layout(height=400)
            
            # --- MÉTRICAS VISUALES ---
            # Calcular métricas simples
            overall_mean = data.mean()
            overall_std = data.std()
            
            # Dividir datos en primeros y últimos 25% para comparar
            split_point = len(data) // 4
            first_quarter_mean = data.iloc[:split_point].mean()
            last_quarter_mean = data.iloc[-split_point:].mean()
            mean_change_pct = ((last_quarter_mean - first_quarter_mean) / first_quarter_mean) * 100
            
            # Volatilidad relativa
            volatility_ratio = overall_std / overall_mean if overall_mean != 0 else 0
            
            # Evaluación visual de estacionariedad
            if abs(mean_change_pct) < 10 and volatility_ratio < 1:
                stationarity_assessment = "✅ APARENTEMENTE ESTACIONARIA"
                assessment_color = "#10b981"
            elif abs(mean_change_pct) < 25:
                stationarity_assessment = "⚠️  POSIBLEMENTE ESTACIONARIA"
                assessment_color = "#f59e0b"
            else:
                stationarity_assessment = "❌ PROBABLEMENTE NO ESTACIONARIA"
                assessment_color = "#ef4444"
            
            metrics_content = html.Div([
                html.H4("📊 Evaluación Visual de Estacionariedad", style={'color': '#ffffff'}),
                
                html.Div([
                    # Columna 1: Métricas básicas
                    html.Div([
                        html.H5("📈 Métricas Básicas", style={'color': '#3b82f6'}),
                        html.P(f"Media global: {overall_mean:.2f}"),
                        html.P(f"Desviación estándar: {overall_std:.2f}"),
                        html.P(f"Volatilidad relativa: {volatility_ratio:.2f}"),
                    ], style={
                        'backgroundColor': '#1e293b',
                        'padding': '15px',
                        'borderRadius': '8px',
                        'flex': 1,
                        'margin': '5px'
                    }),
                    
                    # Columna 2: Cambio temporal
                    html.Div([
                        html.H5("🕒 Cambio Temporal", style={'color': '#3b82f6'}),
                        html.P(f"Media inicial: {first_quarter_mean:.2f}"),
                        html.P(f"Media final: {last_quarter_mean:.2f}"),
                        html.P(f"Cambio: {mean_change_pct:+.1f}%"),
                    ], style={
                        'backgroundColor': '#1e293b',
                        'padding': '15px',
                        'borderRadius': '8px',
                        'flex': 1,
                        'margin': '5px'
                    }),
                    
                    # Columna 3: Evaluación
                    html.Div([
                        html.H5("🔍 Evaluación", style={'color': '#3b82f6'}),
                        html.P(stationarity_assessment, 
                            style={'color': assessment_color, 'fontWeight': 'bold', 'fontSize': '16px'}),
                        html.P("Basado en análisis visual de tendencia y volatilidad", 
                            style={'color': '#94a3b8', 'fontSize': '12px'}),
                    ], style={
                        'backgroundColor': '#1e293b',
                        'padding': '15px',
                        'borderRadius': '8px',
                        'flex': 1,
                        'margin': '5px'
                    }),
                ], style={'display': 'flex', 'gap': '10px', 'marginBottom': '15px'}),
                
                # Guía de interpretación
                html.Div([
                    html.H5("📖 Guía de Interpretación", style={'color': '#f59e0b'}),
                    html.Ul([
                        html.Li("✅ Media móvil estable + Banda estrecha = Probable estacionariedad"),
                        html.Li("⚠️  Media móvil con pendiente + Banda ancha = Posible no estacionariedad"),
                        html.Li("❌ Cambio >25% en medias + Patrón claro = Probable no estacionariedad"),
                        html.Li("🔄 Patrones horarios/mensuales = Estacionalidad presente")
                    ])
                ], style={
                    'backgroundColor': '#1e293b',
                    'padding': '15px',
                    'borderRadius': '8px'
                })
            ])
            
            return fig_rolling, fig_seasonal, metrics_content
            
        except Exception as e:
            # Figuras de error
            error_fig = go.Figure()
            error_fig.update_layout(
                title=f"Error en análisis: {str(e)}",
                template='plotly_dark',
                height=300
            )
            return error_fig, error_fig, html.Div(f"❌ Error: {str(e)}", style={'color': '#ef4444'})
    
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