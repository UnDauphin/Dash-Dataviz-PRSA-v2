# pages/summary.py
from dash import dcc, html, dash_table
import plotly.express as px
from utils.data_loader import get_data

# Obtener datos
df_original, df_imputed, analysis_cols = get_data()

# Diccionario de explicación de variables
variable_descriptions = {
    'year': 'Año de la medición',
    'month': 'Mes de la medición (1-12)',
    'day': 'Día del mes',
    'hour': 'Hora del día (0-23)',
    'PM2.5': 'Material particulado fino (μg/m³) - partículas de menos de 2.5 micrómetros',
    'PM10': 'Material particulado (μg/m³) - partículas de menos de 10 micrómetros', 
    'SO2': 'Dióxido de azufre (μg/m³) - gas contaminante de combustión',
    'NO2': 'Dióxido de nitrógeno (μg/m³) - gas de vehículos e industria',
    'CO': 'Monóxido de carbono (μg/m³) - gas de combustión incompleta',
    'O3': 'Ozono (μg/m³) - contaminante secundario formado por reacciones químicas',
    'TEMP': 'Temperatura (°C) - medida meteorológica',
    'PRES': 'Presión atmosférica (hPa) - influye en dispersión de contaminantes',
    'DEWP': 'Punto de rocío (°C) - medida de humedad atmosférica',
    'RAIN': 'Precipitación (mm) - ayuda a limpiar contaminantes del aire',
    'wd': 'Dirección del viento - afecta transporte de contaminantes',
    'WSPM': 'Velocidad del viento (m/s) - influye en dispersión de contaminantes',
    'station': 'Estación de monitoreo - Dongsi en Beijing',
    'datetime': 'Fecha y hora completa de la medición'
}

# Layout de la pestaña de resumen
layout = html.Div([
    html.H2("📊 Resumen General del Dataset", 
            style={'color': '#ffffff', 'marginBottom': '20px'}),
    
    # Tarjetas de información
    html.Div([
        html.Div([
            html.H3(f"{df_original.shape[0]:,}", style={'color': '#3b82f6', 'margin': '0'}),
            html.P("Total de Filas", style={'color': '#94a3b8', 'margin': '0'})
        ], style={
            'backgroundColor': '#1e293b', 
            'padding': '20px', 
            'borderRadius': '10px',
            'textAlign': 'center',
            'flex': '1',
            'margin': '0 10px'
        }),
        html.Div([
            html.H3(f"{df_original.shape[1]}", style={'color': '#10b981', 'margin': '0'}),
            html.P("Total de Columnas", style={'color': '#94a3b8', 'margin': '0'})
        ], style={
            'backgroundColor': '#1e293b', 
            'padding': '20px', 
            'borderRadius': '10px',
            'textAlign': 'center',
            'flex': '1',
            'margin': '0 10px'
        }),
        html.Div([
            html.H3(f"{len(analysis_cols)}", style={'color': '#f59e0b', 'margin': '0'}),
            html.P("Variables de Análisis", style={'color': '#94a3b8', 'margin': '0'})
        ], style={
            'backgroundColor': '#1e293b', 
            'padding': '20px', 
            'borderRadius': '10px',
            'textAlign': 'center',
            'flex': '1',
            'margin': '0 10px'
        }),
    ], style={'display': 'flex', 'marginBottom': '30px', 'justifyContent': 'space-between'}),
    
    # Información de la estación
    html.Div([
        html.H3("🏢 Información de la Estación", style={'color': '#ffffff'}),
        html.P(f"Estación: {df_original['station'].iloc[0] if 'station' in df_original.columns else 'No disponible'}"),
        html.P(f"Rango temporal: {df_original['datetime'].min().strftime('%Y-%m-%d') if 'datetime' in df_original.columns else 'N/A'} a {df_original['datetime'].max().strftime('%Y-%m-%d') if 'datetime' in df_original.columns else 'N/A'}"),
    ], style={
        'backgroundColor': '#1e293b', 
        'padding': '20px', 
        'borderRadius': '10px',
        'marginBottom': '20px'
    }),

    # Explicación de variables
    html.Div([
        html.H3("📖 Diccionario de Variables", style={'color': '#ffffff', 'marginBottom': '15px'}),
        html.P("Descripción de cada variable en el dataset:", style={'color': '#94a3b8', 'marginBottom': '15px'}),
        
        html.Div([
            html.Div([
                html.H4("🕒 Variables Temporales", style={'color': '#3b82f6', 'marginBottom': '10px'}),
                html.Ul([
                    html.Li([html.Strong("year: "), variable_descriptions.get('year', 'No disponible')]),
                    html.Li([html.Strong("month: "), variable_descriptions.get('month', 'No disponible')]),
                    html.Li([html.Strong("day: "), variable_descriptions.get('day', 'No disponible')]),
                    html.Li([html.Strong("hour: "), variable_descriptions.get('hour', 'No disponible')]),
                    html.Li([html.Strong("datetime: "), variable_descriptions.get('datetime', 'No disponible')]),
                ], style={'color': '#e2e8f0'})
            ], style={'flex': '1', 'marginRight': '15px'}),
            
            html.Div([
                html.H4("🌫️ Contaminantes", style={'color': '#ef4444', 'marginBottom': '10px'}),
                html.Ul([
                    html.Li([html.Strong("PM2.5: "), variable_descriptions.get('PM2.5', 'No disponible')]),
                    html.Li([html.Strong("PM10: "), variable_descriptions.get('PM10', 'No disponible')]),
                    html.Li([html.Strong("SO2: "), variable_descriptions.get('SO2', 'No disponible')]),
                    html.Li([html.Strong("NO2: "), variable_descriptions.get('NO2', 'No disponible')]),
                    html.Li([html.Strong("CO: "), variable_descriptions.get('CO', 'No disponible')]),
                    html.Li([html.Strong("O3: "), variable_descriptions.get('O3', 'No disponible')]),
                ], style={'color': '#e2e8f0'})
            ], style={'flex': '1', 'marginRight': '15px'}),
            
            html.Div([
                html.H4("🌤️ Variables Meteorológicas", style={'color': '#10b981', 'marginBottom': '10px'}),
                html.Ul([
                    html.Li([html.Strong("TEMP: "), variable_descriptions.get('TEMP', 'No disponible')]),
                    html.Li([html.Strong("PRES: "), variable_descriptions.get('PRES', 'No disponible')]),
                    html.Li([html.Strong("DEWP: "), variable_descriptions.get('DEWP', 'No disponible')]),
                    html.Li([html.Strong("RAIN: "), variable_descriptions.get('RAIN', 'No disponible')]),
                    html.Li([html.Strong("wd: "), variable_descriptions.get('wd', 'No disponible')]),
                    html.Li([html.Strong("WSPM: "), variable_descriptions.get('WSPM', 'No disponible')]),
                ], style={'color': '#e2e8f0'})
            ], style={'flex': '1'})
        ], style={'display': 'flex', 'justifyContent': 'space-between', 'marginBottom': '20px'}),
        
        html.Div([
            html.H4("📍 Información de Estación", style={'color': '#f59e0b', 'marginBottom': '10px'}),
            html.Ul([
                html.Li([html.Strong("station: "), variable_descriptions.get('station', 'No disponible')]),
            ], style={'color': '#e2e8f0'})
        ])
    ], style={
        'backgroundColor': '#1e293b', 
        'padding': '25px', 
        'borderRadius': '10px',
        'marginBottom': '20px'
    }),
    
    # Primeras filas
    html.Div([
        html.H3("📋 Primeras Filas del Dataset", style={'color': '#ffffff'}),
        dash_table.DataTable(
            data=df_original.head(10).to_dict('records'),
            columns=[{"name": col, "id": col} for col in df_original.columns],
            page_size=10,
            style_table={'overflowX': 'auto', 'borderRadius': '10px'},
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
                'fontWeight': 'bold',
                'border': '1px solid #475569'
            },
        )
    ], style={'marginBottom': '30px'}),
    
    # Gráfico de tendencias (si hay datos temporales)
    html.Div(id='trends-section')
])

def register_callbacks(app):
    from dash import Input, Output
    from utils.data_loader import get_data
    
    @app.callback(
        Output('trends-section', 'children'),
        Input('main-tabs', 'value')
    )
    def render_trends(tab):
        if tab != 'tab-summary':
            return ""
            
        df_original, _, analysis_cols = get_data()
        
        if 'datetime' not in df_original.columns or not analysis_cols:
            return html.Div("No hay datos temporales disponibles para mostrar tendencias.")
        
        # Filtrar solo contaminantes para el gráfico
        pollutants = [col for col in analysis_cols if col in ['pm2_5', 'pm10', 'so2', 'no2', 'co', 'o3']]
        if not pollutants:
            return html.Div("No se detectaron contaminantes para mostrar tendencias.")
        
        try:
            # Resample mensual
            dfm = df_original.set_index('datetime').resample('M')[pollutants].mean().reset_index()
            
            fig = px.line(dfm, x='datetime', y=pollutants, 
                         title="📈 Tendencias Mensuales - Contaminantes Principales",
                         labels={'value': 'Concentración', 'datetime': 'Fecha'},
                         template='plotly_dark')
            
            fig.update_layout(
                plot_bgcolor='#1e293b',
                paper_bgcolor='#1e293b',
                font_color='white',
                height=400
            )
            
            return html.Div([
                html.H3("📈 Tendencias Temporales", style={'color': '#ffffff', 'marginBottom': '15px'}),
                dcc.Graph(figure=fig)
            ])
        except Exception as e:
            return html.Div(f"Error al generar gráfico de tendencias: {str(e)}")