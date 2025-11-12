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
            label='📈 Preparación Modelado', 
            value='tab-model-prep',
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

def render_model_prep():
    """Pestaña de preparación para modelado (por implementar)"""
    return html.Div([
        html.H3("📈 Preparación para Modelado", style={'color': '#ffffff'}),
        html.P("🔨 Esta funcionalidad está en desarrollo..."),
        html.P("Próximamente: Diferenciación, transformaciones, split temporal")
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
        elif tab == 'tab-model-prep':
            return render_model_prep()
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