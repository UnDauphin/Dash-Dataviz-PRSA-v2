import dash
from dash import dcc, html, Input, Output, callback
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

# Cargar tus datos existentes
forecast_df = pd.read_csv('forecast.csv', index_col=0, parse_dates=True)
params_df = pd.read_csv('params.csv', index_col=0)

# Calcular métricas básicas desde tus datos
mae = 63.92  # Del output de tu notebook
rmse = 90.66  # Del output de tu notebook
r2 = 0.009    # Del output de tu notebook

# Layout de la página SARIMA
layout = html.Div([
    html.H2("🔮 Predicciones SARIMA - PM2.5", 
            style={'textAlign': 'center', 'marginBottom': 30}),
    
    # Métricas en tarjetas
    html.Div([
        html.Div([
            html.H4(f"{mae:.2f}", style={'color': '#3b82f6', 'margin': 0}),
            html.P("MAE", style={'margin': 0, 'color': '#94a3b8'})
        ], className="card", style={
            'backgroundColor': '#1e293b', 
            'padding': '20px', 
            'borderRadius': '10px',
            'textAlign': 'center',
            'flex': 1,
            'margin': '5px'
        }),
        html.Div([
            html.H4(f"{rmse:.2f}", style={'color': '#10b981', 'margin': 0}),
            html.P("RMSE", style={'margin': 0, 'color': '#94a3b8'})
        ], className="card", style={
            'backgroundColor': '#1e293b', 
            'padding': '20px', 
            'borderRadius': '10px',
            'textAlign': 'center',
            'flex': 1,
            'margin': '5px'
        }),
        html.Div([
            html.H4(f"{r2:.3f}", style={'color': '#f59e0b', 'margin': 0}),
            html.P("R²", style={'margin': 0, 'color': '#94a3b8'})
        ], className="card", style={
            'backgroundColor': '#1e293b', 
            'padding': '20px', 
            'borderRadius': '10px',
            'textAlign': 'center',
            'flex': 1,
            'margin': '5px'
        }),
    ], style={'display': 'flex', 'justifyContent': 'space-between', 'marginBottom': 30}),
    
    # Información del modelo
    html.Div([
        html.H4("📊 Parámetros del Modelo SARIMA", style={'marginBottom': 15}),
        html.Div([
            html.P(f"🔹 AR Lag 1: {params_df.loc['ar.L1', 'params']:.4f}"),
            html.P(f"🔹 MA Lag 1: {params_df.loc['ma.L1', 'params']:.4f}"),
            html.P(f"🔹 Seasonal AR: {params_df.loc['ar.S.L24', 'params']:.4f}"),
            html.P(f"🔹 Seasonal MA: {params_df.loc['ma.S.L24', 'params']:.4f}"),
            html.P(f"🔹 Sigma²: {params_df.loc['sigma2', 'params']:.2f}"),
        ], style={
            'backgroundColor': '#1e293b',
            'padding': '15px',
            'borderRadius': '10px',
            'marginBottom': '20px'
        })
    ]),
    
    # Gráfico de predicciones
    dcc.Graph(id='sarima-forecast-plot'),
    
    # Selector de número de predicciones a mostrar
    html.Div([
        html.Label("Mostrar próximas:", style={'marginRight': '10px', 'color': '#94a3b8'}),
        dcc.Slider(
            id='forecast-horizon',
            min=6,
            max=48,
            step=6,
            value=24,
            marks={i: f'{i}h' for i in range(6, 49, 6)},
        )
    ], style={'margin': '30px 0'}),
    
    # Tabla de predicciones
    html.Div([
        html.H4("📋 Próximas Predicciones", style={'marginBottom': 15}),
        html.Div(id='forecast-table')
    ])
])

# Callbacks para SARIMA
def register_callbacks(app):
    @app.callback(
        [Output('sarima-forecast-plot', 'figure'),
         Output('forecast-table', 'children')],
        Input('forecast-horizon', 'value')
    )
    def update_sarima_forecast(horizon):
        try:
            # Usar tus datos reales del forecast.csv
            display_df = forecast_df.head(horizon).copy()
            
            # Crear gráfico interactivo
            fig = go.Figure()
            
            # Línea de predicción
            fig.add_trace(go.Scatter(
                x=display_df.index, 
                y=display_df['forecast'],
                mode='lines+markers',
                name='Predicción SARIMA',
                line=dict(color='#f59e0b', width=3),
                marker=dict(size=6)
            ))
            
            # Intervalo de confianza
            fig.add_trace(go.Scatter(
                x=display_df.index,
                y=display_df['upper'],
                fill=None,
                mode='lines',
                line=dict(width=0),
                showlegend=False
            ))
            fig.add_trace(go.Scatter(
                x=display_df.index,
                y=display_df['lower'],
                fill='tonexty',
                mode='lines',
                name='Intervalo de Confianza (95%)',
                line=dict(width=0),
                fillcolor='rgba(245, 158, 11, 0.2)'
            ))
            
            fig.update_layout(
                title=f"Predicción SARIMA - Próximas {horizon} horas",
                template='plotly_dark',
                xaxis_title="Fecha y Hora",
                yaxis_title="PM2.5 (µg/m³)",
                hovermode='x unified',
                height=500
            )
            
            # Crear tabla de predicciones
            table_data = []
            for idx, row in display_df.iterrows():
                table_data.append(
                    html.Tr([
                        html.Td(idx.strftime('%Y-%m-%d %H:%M'), 
                               style={'padding': '8px', 'borderBottom': '1px solid #334155'}),
                        html.Td(f"{row['forecast']:.1f} µg/m³", 
                               style={'padding': '8px', 'borderBottom': '1px solid #334155'}),
                        html.Td(f"[{row['lower']:.1f}, {row['upper']:.1f}]", 
                               style={'padding': '8px', 'borderBottom': '1px solid #334155',
                                     'color': '#94a3b8', 'fontSize': '0.9em'})
                    ])
                )
            
            table = html.Table([
                html.Thead([
                    html.Tr([
                        html.Th("Fecha/Hora", style={'padding': '10px', 'textAlign': 'left'}),
                        html.Th("PM2.5 Predicho", style={'padding': '10px', 'textAlign': 'left'}),
                        html.Th("Intervalo Confianza", style={'padding': '10px', 'textAlign': 'left'})
                    ])
                ], style={'backgroundColor': '#1e293b'}),
                html.Tbody(table_data)
            ], style={
                'width': '100%', 
                'borderCollapse': 'collapse',
                'backgroundColor': '#0f1720'
            })
            
            return fig, table
            
        except Exception as e:
            error_fig = px.line(title=f"Error cargando datos: {str(e)}")
            error_msg = html.P(f"Error: {str(e)}", style={'color': '#ef4444'})
            return error_fig, error_msg