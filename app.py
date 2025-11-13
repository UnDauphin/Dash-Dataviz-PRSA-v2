# app.py - VERSIÓN PARA DOCKER
import dash
from dash import dcc, html, Input, Output, callback
import warnings
warnings.filterwarnings('ignore')

# -------------------------
# INICIALIZAR DATOS PRIMERO
# -------------------------
from utils.data_loader import initialize_data
print("🔄 Inicializando datos...")
initialize_data()
print("✅ Datos inicializados correctamente")

# -------------------------
# IMPORTAR PÁGINAS DESPUÉS de inicializar datos
# -------------------------
from pages import (
    summary, missing, univariate, bivariate, timeseries, conclusions, sarima
)

# Inicializar la app
app = dash.Dash(
    __name__, 
    suppress_callback_exceptions=True,
    external_stylesheets=[
        'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css'
    ]
)
app.title = "EDA PRSA - Análisis de Calidad del Aire"

# Layout principal con tema oscuro
app.layout = html.Div([
    # Header
    html.Div([
        html.H1("EDA PRSA - Análisis de Calidad del Aire", 
                style={
                    'textAlign': 'center', 
                    'color': '#ffffff', 
                    'marginBottom': 30,
                    'fontFamily': 'Arial, sans-serif'
                }),
    ], style={
        'backgroundColor': '#0f1720', 
        'padding': '20px',
        'borderBottom': '2px solid #334155'
    }),
    
    # Tabs principales
    html.Div([
        dcc.Tabs(
            id="main-tabs", 
            value='tab-summary',
            children=[
                dcc.Tab(
                    label='📊 Resumen General', 
                    value='tab-summary',
                    style={'padding': '10px', 'fontWeight': 'bold'},
                    selected_style={'backgroundColor': '#1e293b', 'border': '1px solid #475569'}
                ),
                dcc.Tab(
                    label='❓ Valores Faltantes', 
                    value='tab-missing',
                    style={'padding': '10px', 'fontWeight': 'bold'},
                    selected_style={'backgroundColor': '#1e293b', 'border': '1px solid #475569'}
                ),
                dcc.Tab(
                    label='📈 Análisis Univariado', 
                    value='tab-univariate',
                    style={'padding': '10px', 'fontWeight': 'bold'},
                    selected_style={'backgroundColor': '#1e293b', 'border': '1px solid #475569'}
                ),
                dcc.Tab(
                    label='🔗 Análisis Bivariado', 
                    value='tab-bivariate',
                    style={'padding': '10px', 'fontWeight': 'bold'},
                    selected_style={'backgroundColor': '#1e293b', 'border': '1px solid #475569'}
                ),
                dcc.Tab(
                    label='🕒 Análisis Series Tiempo', 
                    value='tab-timeseries',
                    style={'padding': '10px', 'fontWeight': 'bold'},
                    selected_style={'backgroundColor': '#1e293b', 'border': '1px solid #475569'}
                ),
                dcc.Tab(
                    label='🔮 Predicciones SARIMA', 
                    value='tab-sarima',
                    style={'padding': '10px', 'fontWeight': 'bold'},
                    selected_style={'backgroundColor': '#1e293b', 'border': '1px solid #475569'}
                ),
                dcc.Tab(
                    label='📋 Conclusiones', 
                    value='tab-conclusions',
                    style={'padding': '10px', 'fontWeight': 'bold'},
                    selected_style={'backgroundColor': '#1e293b', 'border': '1px solid #475569'}
                ),
            ],
            colors={
                "border": "#475569",
                "primary": "#3b82f6",
                "background": "#1e293b"
            }
        ),
    ], style={'backgroundColor': '#0f1720', 'padding': '0px 20px'}),
    
    # Contenido de las pestañas
    html.Div(
        id='tab-content', 
        style={
            'padding': '20px', 
            'backgroundColor': '#0f1720', 
            'color': '#ffffff',
            'minHeight': '80vh'
        }
    )
], style={'backgroundColor': '#0f1720', 'minHeight': '100vh'})

# Callback principal para cambiar pestañas
@app.callback(
    Output('tab-content', 'children'),
    Input('main-tabs', 'value')
)
def render_content(tab):
    if tab == 'tab-summary':
        return summary.layout
    elif tab == 'tab-missing':
        return missing.layout
    elif tab == 'tab-univariate':
        return univariate.layout
    elif tab == 'tab-bivariate':
        return bivariate.layout
    elif tab == 'tab-timeseries':
        return timeseries.layout
    elif tab == 'tab-conclusions':
        return conclusions.layout
    elif tab == 'tab-sarima':
        return sarima.layout
    return html.Div("Selecciona una pestaña")

# Registrar callbacks de cada página
summary.register_callbacks(app)
missing.register_callbacks(app)
univariate.register_callbacks(app)
bivariate.register_callbacks(app)
timeseries.register_callbacks(app)
conclusions.register_callbacks(app)
sarima.register_callbacks(app)

# Servir para producción
if __name__ == '__main__':
    import os
    debug_mode = os.environ.get('DEBUG', 'False').lower() == 'true'
    app.run(
        debug=debug_mode, 
        host='0.0.0.0', 
        port=8050,
        dev_tools_ui=debug_mode,
        dev_tools_props_check=debug_mode
    )