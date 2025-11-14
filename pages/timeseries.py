# pages/timeseries.py - MODIFICADO para incluir descomposición y estacionalidad
from dash import dcc, html, Input, Output, callback
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from statsmodels.tsa.seasonal import seasonal_decompose
from utils.data_loader import get_data

# Obtener datos
df_original, df_imputed, analysis_cols = get_data()

# Layout de análisis de series de tiempo
layout = html.Div([
    html.H2("🕒 Análisis de Series de Tiempo", 
            style={'color': '#ffffff', 'marginBottom': '20px'}),
    
    dcc.Tabs(id="timeseries-tabs", value='tab-decomposition', children=[
        dcc.Tab(
            label='🧩 Descomposición', 
            value='tab-decomposition',
            style={'padding': '10px', 'fontWeight': 'bold'},
            selected_style={'backgroundColor': '#1e293b'}
        ),
        dcc.Tab(
            label='📅 Estacionalidad', 
            value='tab-seasonality',
            style={'padding': '10px', 'fontWeight': 'bold'},
            selected_style={'backgroundColor': '#1e293b'}
        ),
        dcc.Tab(
            label='📊 Análisis de Volatilidad', 
            value='tab-volatility',
            style={'padding': '10px', 'fontWeight': 'bold'},
            selected_style={'backgroundColor': '#1e293b'}
        ),
    ]),
    
    html.Div(id='timeseries-tab-content', style={'marginTop': '20px'})
])

def render_decomposition():
    """Pestaña de descomposición de series temporales"""
    return html.Div([
        html.H3("🧩 Descomposición de Series Temporales", style={'color': '#ffffff'}),
        html.P("Selecciona una variable para descomponer en tendencia, estacionalidad y residual:"),
        
        html.Div([
            html.Label("Variable:", style={'color': '#ffffff', 'marginRight': '10px'}),
            dcc.Dropdown(
                id='decomposition-variable-selector',
                options=[{'label': col, 'value': col} for col in analysis_cols],
                value=analysis_cols[0] if analysis_cols else None,
                style={'width': '300px', 'color': '#000000'}
            ),
            html.Label("Modelo:", style={'color': '#ffffff', 'marginLeft': '20px', 'marginRight': '10px'}),
            dcc.RadioItems(
                id='decomposition-model',
                options=[
                    {'label': 'Aditivo', 'value': 'additive'},
                    {'label': 'Multiplicativo', 'value': 'multiplicative'}
                ],
                value='additive',
                inline=True,
                style={'color': '#ffffff'}
            ),
            html.Label("Período Estacional:", style={'color': '#ffffff', 'marginLeft': '20px', 'marginRight': '10px'}),
            dcc.Input(
                id='seasonal-period',
                type='number',
                value=24,  # Por defecto 24 horas para datos horarios
                min=1,
                max=365,
                style={'width': '100px', 'color': '#000000'}
            )
        ], style={'marginBottom': '20px'}),
        
        dcc.Graph(id='decomposition-plot')
    ])

def render_seasonality():
    """Pestaña de análisis de estacionalidad"""
    return html.Div([
        html.H3("📅 Análisis de Estacionalidad", style={'color': '#ffffff'}),
        html.P("Selecciona una variable para analizar sus patrones estacionales:"),
        
        html.Div([
            html.Label("Variable:", style={'color': '#ffffff', 'marginRight': '10px'}),
            dcc.Dropdown(
                id='seasonality-variable-selector',
                options=[{'label': col, 'value': col} for col in analysis_cols],
                value=analysis_cols[0] if analysis_cols else None,
                style={'width': '300px', 'color': '#000000'}
            ),
            html.Label("Tipo de Estacionalidad:", style={'color': '#ffffff', 'marginLeft': '20px', 'marginRight': '10px'}),
            dcc.Dropdown(
                id='seasonality-type',
                options=[
                    {'label': 'Por Hora del Día', 'value': 'hour'},
                    {'label': 'Por Día de la Semana', 'value': 'dayofweek'},
                    {'label': 'Por Mes', 'value': 'month'},
                    {'label': 'Por Estación del Año', 'value': 'season'}
                ],
                value='hour',
                style={'width': '200px', 'color': '#000000'}
            )
        ], style={'marginBottom': '20px'}),
        
        dcc.Graph(id='seasonality-plot')
    ])

def render_volatility_analysis():
    """Pestaña de análisis de volatilidad"""
    if 'datetime' not in df_imputed.columns or df_imputed.empty:
        return html.Div([
            html.H3("📊 Análisis de Volatilidad", style={'color': '#ffffff'}),
            html.P("❌ No hay datos temporales disponibles.")
        ])
    
    # Variables recomendadas para análisis de volatilidad
    volatility_vars = [col for col in analysis_cols if any(x in col for x in ['pm', 'so2', 'no2', 'co', 'o3', 'wspm'])]
    if not volatility_vars:
        volatility_vars = analysis_cols[:3] if len(analysis_cols) >= 3 else analysis_cols
    
    return html.Div([
        html.H3("📊 Análisis de Volatilidad en Series Temporales", style={'color': '#ffffff'}),
        html.P("Identifica periodos de alta variabilidad y eventos extremos en los datos."),
        
        html.Div([
            html.Div([
                html.Label("Variable para análisis:", style={'color': '#ffffff'}),
                dcc.Dropdown(
                    id='volatility-variable',
                    options=[{'label': col, 'value': col} for col in analysis_cols],
                    value=volatility_vars[0] if volatility_vars else None,
                    style={'color': '#000000'}
                ),
            ], style={'flex': '1', 'marginRight': '15px'}),
            
            html.Div([
                html.Label("Ventana para volatilidad (días):", style={'color': '#ffffff'}),
                dcc.Slider(
                    id='volatility-window',
                    min=1,
                    max=30,
                    step=1,
                    value=7,
                    marks={1: '1d', 7: '7d', 14: '14d', 30: '30d'},
                ),
            ], style={'flex': '1', 'marginRight': '15px'}),
            
            html.Div([
                html.Label("Umbral de outliers (σ):", style={'color': '#ffffff'}),
                dcc.Slider(
                    id='outlier-threshold',
                    min=1,
                    max=3,
                    step=0.5,
                    value=2,
                    marks={1: '1σ', 2: '2σ', 3: '3σ'},
                ),
            ], style={'flex': '1'}),
        ], style={'display': 'flex', 'marginBottom': '20px', 'alignItems': 'end'}),
        
        html.H4("📈 Serie Temporal con Volatilidad", style={'color': '#ffffff', 'marginTop': '30px'}),
        dcc.Graph(id='volatility-plot'),
        
        html.H4("🎯 Detección de Eventos Extremos", style={'color': '#ffffff', 'marginTop': '30px'}),
        dcc.Graph(id='outliers-plot'),
        
        html.H4("📊 Estadísticas de Volatilidad", style={'color': '#ffffff', 'marginTop': '30px'}),
        html.Div(id='volatility-stats')
    ])

def register_callbacks(app):
    # Callback para cambiar sub-pestañas
    @app.callback(
        Output('timeseries-tab-content', 'children'),
        Input('timeseries-tabs', 'value')
    )
    def render_timeseries_tab(tab):
        if tab == 'tab-decomposition':
            return render_decomposition()
        elif tab == 'tab-seasonality':
            return render_seasonality()
        elif tab == 'tab-volatility':
            return render_volatility_analysis()
        return html.Div("Selecciona una sub-pestaña")
    
    # Callback para descomposición
    @app.callback(
        Output('decomposition-plot', 'figure'),
        [Input('decomposition-variable-selector', 'value'),
         Input('decomposition-model', 'value'),
         Input('seasonal-period', 'value')]
    )
    def update_decomposition(selected_var, model, period):
        if not selected_var or not period:
            return {}
            
        df_orig, df_imp, _ = get_data()
        
        if 'datetime' not in df_imp.columns:
            return {}
            
        series = df_imp.set_index('datetime')[selected_var].dropna()
        
        if series.empty:
            return {}
        
        try:
            # Realizar descomposición estacional
            decomposition = seasonal_decompose(series, model=model, period=period)
            
            # Crear subplots
            fig = make_subplots(
                rows=4, cols=1,
                subplot_titles=('Serie Original', 'Tendencia', 'Estacionalidad', 'Residual'),
                vertical_spacing=0.05
            )
            
            # Serie original
            fig.add_trace(
                go.Scatter(x=series.index, y=series, name='Original', line=dict(color='#3b82f6')),
                row=1, col=1
            )
            
            # Tendencia
            fig.add_trace(
                go.Scatter(x=decomposition.trend.index, y=decomposition.trend, name='Tendencia', line=dict(color='#10b981')),
                row=2, col=1
            )
            
            # Estacionalidad
            fig.add_trace(
                go.Scatter(x=decomposition.seasonal.index, y=decomposition.seasonal, name='Estacionalidad', line=dict(color='#f59e0b')),
                row=3, col=1
            )
            
            # Residual
            fig.add_trace(
                go.Scatter(x=decomposition.resid.index, y=decomposition.resid, name='Residual', line=dict(color='#ef4444')),
                row=4, col=1
            )
            
            fig.update_layout(
                height=800,
                title_text=f"Descomposición {model.capitalize()} - {selected_var}",
                template='plotly_dark',
                plot_bgcolor='#1e293b',
                paper_bgcolor='#1e293b',
                font_color='white',
                showlegend=False
            )
            
            return fig
            
        except Exception as e:
            return go.Figure().add_annotation(
                text=f"Error en descomposición: {str(e)}",
                xref="paper", yref="paper",
                x=0.5, y=0.5, xanchor='center', yanchor='middle',
                showarrow=False
            )
    
    # Callback para estacionalidad
    @app.callback(
        Output('seasonality-plot', 'figure'),
        [Input('seasonality-variable-selector', 'value'),
         Input('seasonality-type', 'value')]
    )
    def update_seasonality(selected_var, seasonality_type):
        if not selected_var:
            return {}
            
        df_orig, df_imp, _ = get_data()
        
        if 'datetime' not in df_imp.columns:
            return {}
            
        df = df_imp.copy()
        series = df.set_index('datetime')[selected_var].dropna()
        
        if series.empty:
            return {}
        
        # Extraer componentes temporales según el tipo de estacionalidad
        if seasonality_type == 'hour':
            df['time_unit'] = df['datetime'].dt.hour
            x_label = 'Hora del Día'
        elif seasonality_type == 'dayofweek':
            df['time_unit'] = df['datetime'].dt.dayofweek
            x_label = 'Día de la Semana (0=Lunes, 6=Domingo)'
        elif seasonality_type == 'month':
            df['time_unit'] = df['datetime'].dt.month
            x_label = 'Mes del Año'
        elif seasonality_type == 'season':
            # Definir estaciones: 1=Invierno, 2=Primavera, 3=Verano, 4=Otoño
            df['month'] = df['datetime'].dt.month
            conditions = [
                (df['month'].isin([12, 1, 2])),
                (df['month'].isin([3, 4, 5])),
                (df['month'].isin([6, 7, 8])),
                (df['month'].isin([9, 10, 11]))
            ]
            choices = ['Invierno', 'Primavera', 'Verano', 'Otoño']
            df['time_unit'] = np.select(conditions, choices)
            x_label = 'Estación del Año'
        
        # Crear boxplot para mostrar la distribución por unidad temporal
        if seasonality_type == 'season':
            fig = px.box(df, x='time_unit', y=selected_var, 
                        title=f"Distribución de {selected_var} por {x_label}",
                        category_orders={'time_unit': ['Invierno', 'Primavera', 'Verano', 'Otoño']})
        else:
            fig = px.box(df, x='time_unit', y=selected_var, 
                        title=f"Distribución de {selected_var} por {x_label}")
        
        fig.update_layout(
            template='plotly_dark',
            plot_bgcolor='#1e293b',
            paper_bgcolor='#1e293b',
            font_color='white',
            height=500,
            xaxis_title=x_label,
            yaxis_title=selected_var
        )
        
        return fig
    
    # Callback para análisis de volatilidad
    @app.callback(
        [Output('volatility-plot', 'figure'),
        Output('outliers-plot', 'figure'),
        Output('volatility-stats', 'children')],
        [Input('volatility-variable', 'value'),
        Input('volatility-window', 'value'),
        Input('outlier-threshold', 'value')]
    )
    def update_volatility_analysis(selected_var, window, threshold):
        if not selected_var:
            return {}, {}, ""
        
        df_orig, df_imp, _ = get_data()
        
        if df_imp.empty or selected_var not in df_imp.columns or 'datetime' not in df_imp.columns:
            return {}, {}, html.Div("❌ Variable no disponible.")
        
        try:
            # Preparar datos
            df_temp = df_imp[['datetime', selected_var]].copy()
            df_temp = df_temp.set_index('datetime').sort_index()
            
            # Resample diario para mejor visualización
            df_daily = df_temp.resample('D').mean().reset_index()
            
            # Calcular volatilidad (desviación estándar rolling)
            df_daily['volatility'] = df_daily[selected_var].rolling(window=window).std()
            
            # Calcular z-score para outliers
            mean_val = df_daily[selected_var].mean()
            std_val = df_daily[selected_var].std()
            df_daily['z_score'] = (df_daily[selected_var] - mean_val) / std_val
            
            # Identificar outliers
            df_daily['is_outlier'] = abs(df_daily['z_score']) > threshold
            
            # GRÁFICO 1: Serie con volatilidad
            fig_volatility = go.Figure()
            
            # Serie principal
            fig_volatility.add_trace(go.Scatter(
                x=df_daily['datetime'],
                y=df_daily[selected_var],
                mode='lines',
                name=selected_var,
                line=dict(color='#3b82f6', width=1),
                opacity=0.7
            ))
            
            # Banda de volatilidad (mean ± std)
            fig_volatility.add_trace(go.Scatter(
                x=df_daily['datetime'],
                y=df_daily[selected_var].mean() + df_daily['volatility'],
                mode='lines',
                name='Volatilidad +',
                line=dict(color='#ef4444', width=1, dash='dash'),
                opacity=0.5
            ))
            
            fig_volatility.add_trace(go.Scatter(
                x=df_daily['datetime'],
                y=df_daily[selected_var].mean() - df_daily['volatility'],
                mode='lines',
                name='Volatilidad -',
                line=dict(color='#ef4444', width=1, dash='dash'),
                opacity=0.5,
                fill='tonexty'
            ))
            
            fig_volatility.update_layout(
                title=f'Serie de {selected_var} con Volatilidad ({window} días)',
                template='plotly_dark',
                plot_bgcolor='#1e293b',
                paper_bgcolor='#1e293b',
                font_color='white',
                height=400
            )
            
            # GRÁFICO 2: Eventos extremos
            fig_outliers = go.Figure()
            
            # Puntos normales
            normal_data = df_daily[~df_daily['is_outlier']]
            fig_outliers.add_trace(go.Scatter(
                x=normal_data['datetime'],
                y=normal_data[selected_var],
                mode='markers',
                name='Valores normales',
                marker=dict(color='#3b82f6', size=4),
                opacity=0.6
            ))
            
            # Outliers
            outlier_data = df_daily[df_daily['is_outlier']]
            fig_outliers.add_trace(go.Scatter(
                x=outlier_data['datetime'],
                y=outlier_data[selected_var],
                mode='markers',
                name=f'Outliers (> {threshold}σ)',
                marker=dict(color='#ef4444', size=8, line=dict(width=2, color='white')),
                opacity=0.8
            ))
            
            fig_outliers.update_layout(
                title=f'Eventos Extremos en {selected_var}',
                template='plotly_dark',
                plot_bgcolor='#1e293b',
                paper_bgcolor='#1e293b',
                font_color='white',
                height=400
            )
            
            # ESTADÍSTICAS
            outliers_count = df_daily['is_outlier'].sum()
            total_count = len(df_daily)
            outlier_percentage = (outliers_count / total_count) * 100
            
            max_volatility = df_daily['volatility'].max()
            avg_volatility = df_daily['volatility'].mean()
            
            stats_content = html.Div([
                html.Div([
                    html.Div([
                        html.H5("📈 Estadísticas de Volatilidad", style={'color': '#3b82f6'}),
                        html.P(f"Volatilidad promedio: {avg_volatility:.2f}"),
                        html.P(f"Volatilidad máxima: {max_volatility:.2f}"),
                        html.P(f"Ventana de análisis: {window} días"),
                    ], style={
                        'backgroundColor': '#1e293b',
                        'padding': '15px',
                        'borderRadius': '8px',
                        'flex': '1',
                        'marginRight': '10px'
                    }),
                    
                    html.Div([
                        html.H5("🎯 Detección de Outliers", style={'color': '#ef4444'}),
                        html.P(f"Outliers detectados: {outliers_count}"),
                        html.P(f"Total de puntos: {total_count}"),
                        html.P(f"Porcentaje de outliers: {outlier_percentage:.1f}%"),
                        html.P(f"Umbral: {threshold} desviaciones estándar"),
                    ], style={
                        'backgroundColor': '#1e293b',
                        'padding': '15px',
                        'borderRadius': '8px',
                        'flex': '1',
                        'marginLeft': '10px'
                    }),
                ], style={'display': 'flex', 'marginBottom': '15px'}),
                
                # Periodos de alta volatilidad
                html.Div([
                    html.H5("🔄 Periodos de Alta Volatilidad", style={'color': '#f59e0b'}),
                    html.P("Los periodos de alta volatilidad pueden indicar:"),
                    html.Ul([
                        html.Li("Cambios abruptos en condiciones meteorológicas"),
                        html.Li("Eventos de contaminación extraordinarios"),
                        html.Li("Problemas en la medición de datos"),
                        html.Li("Transiciones estacionales")
                    ])
                ], style={
                    'backgroundColor': '#1e293b',
                    'padding': '15px',
                    'borderRadius': '8px'
                })
            ])
            
            return fig_volatility, fig_outliers, stats_content
            
        except Exception as e:
            error_fig = go.Figure()
            error_fig.update_layout(
                title=f"Error en análisis: {str(e)}",
                template='plotly_dark',
                height=400
            )
            return error_fig, error_fig, html.Div(f"❌ Error: {str(e)}")