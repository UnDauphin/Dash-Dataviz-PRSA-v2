# pages/summary.py
from dash import dcc, html, dash_table, Input, Output, callback
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from utils.data_loader import get_data
from utils.database import load_data_from_query

# Obtener datos
df_original, df_imputed, analysis_cols = get_data()

# Cargar datos de estaciones (asumiendo que el archivo está en la raíz del proyecto)
try:
    stations_df = pd.read_csv('stations_coordinates.csv')
except:
    # Datos de ejemplo en caso de que no encuentre el archivo
    stations_df = pd.DataFrame({
        'station': ['Dongsi', 'Nongzhanguan', 'Wanshouxigong', 'Aotizhongxin', 
                   'Dingling', 'Changping', 'Gucheng', 'Huairou', 'Shunyi', 
                   'Tiantan', 'Wanliu', 'Guanyuan'],
        'lat': [39.929, 39.938, 39.878, 39.983, 40.292, 40.217, 39.914, 
               40.413, 40.129, 39.886, 39.987, 39.929],
        'lon': [116.417, 116.467, 116.367, 116.417, 116.217, 116.233, 
               116.184, 116.634, 116.655, 116.407, 116.306, 116.357]
    })

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

QUERIES = {
    'pm25_stats': {
        'name': '🌫️ Estadísticas PM2.5',
        'query': """
        SELECT 
            COUNT(*) as total_filas,
            COUNT("PM2.5") as filas_con_pm25,
            AVG("PM2.5") as pm25_promedio,
            MIN("PM2.5") as pm25_minimo,
            MAX("PM2.5") as pm25_maximo,
            STDDEV("PM2.5") as pm25_desviacion,
            SUM(CASE WHEN "PM2.5" IS NULL THEN 1 ELSE 0 END) as nulos,
            100.0 * SUM(CASE WHEN "PM2.5" IS NULL THEN 1 ELSE 0 END) / COUNT(*) as porcentaje_nulos
        FROM prsa_data_dongsi
        """
    },
    'pollution_by_year': {
        'name': '📅 Contaminación por Año',
        'query': """
        SELECT 
            year as año,
            COUNT(*) as total_mediciones,
            COUNT("PM2.5") as mediciones_pm25,
            AVG("PM2.5") as pm25_promedio,
            AVG("PM10") as pm10_promedio,
            AVG("SO2") as so2_promedio,
            AVG("NO2") as no2_promedio
        FROM prsa_data_dongsi
        GROUP BY year
        HAVING COUNT("PM2.5") > 0
        ORDER BY year
        """
    },
    'seasonal_analysis': {
        'name': '🌤️ Análisis Estacional',
        'query': """
        SELECT 
            month as mes,
            COUNT(*) as total_mediciones,
            AVG("PM2.5") as pm25_promedio,
            AVG("PM10") as pm10_promedio,
            AVG("TEMP") as temperatura_promedio,
            AVG("RAIN") as lluvia_promedio
        FROM prsa_data_dongsi
        WHERE "PM2.5" IS NOT NULL AND "TEMP" IS NOT NULL
        GROUP BY month
        ORDER BY month
        """
    },
    'daily_pattern': {
        'name': '🕐 Patrón Diario por Hora',
        'query': """
        SELECT 
            hour as hora,
            COUNT(*) as mediciones,
            AVG("PM2.5") as pm25_promedio,
            AVG("PM10") as pm10_promedio,
            AVG("TEMP") as temperatura_promedio
        FROM prsa_data_dongsi
        WHERE "PM2.5" IS NOT NULL AND "TEMP" IS NOT NULL
        GROUP BY hour
        ORDER BY hour
        """
    },
    'wind_analysis': {
        'name': '💨 Análisis por Dirección del Viento',
        'query': """
        SELECT 
            wd as direccion_viento,
            COUNT(*) as mediciones,
            AVG("PM2.5") as pm25_promedio,
            AVG("PM10") as pm10_promedio,
            AVG("WSPM") as velocidad_viento_promedio
        FROM prsa_data_dongsi
        WHERE wd IS NOT NULL AND "PM2.5" IS NOT NULL
        GROUP BY wd
        HAVING COUNT(*) >= 10
        ORDER BY pm25_promedio DESC
        LIMIT 10
        """
    },
    'top_polluted_days': {
        'name': '⚠️ Días Más Contaminados',
        'query': """
        SELECT 
            year, month, day,
            COUNT(*) as mediciones_dia,
            AVG("PM2.5") as pm25_promedio,
            AVG("PM10") as pm10_promedio,
            AVG("TEMP") as temperatura_promedio,
            AVG("RAIN") as lluvia_promedio
        FROM prsa_data_dongsi
        WHERE "PM2.5" IS NOT NULL
        GROUP BY year, month, day
        HAVING COUNT(*) >= 18
        ORDER BY pm25_promedio DESC
        LIMIT 10
        """
    },
    'meteorology_correlation': {
        'name': '🔗 Correlaciones Meteorológicas',
        'query': """
        SELECT 
            COUNT(*) as pares_completos,
            CORR("PM2.5", "TEMP") as corr_pm25_temperatura,
            CORR("PM2.5", "PRES") as corr_pm25_presion,
            CORR("PM2.5", "DEWP") as corr_pm25_punto_rocio,
            CORR("PM2.5", "RAIN") as corr_pm25_lluvia,
            CORR("PM2.5", "WSPM") as corr_pm25_viento
        FROM prsa_data_dongsi
        WHERE "PM2.5" IS NOT NULL 
          AND "TEMP" IS NOT NULL 
          AND "PRES" IS NOT NULL
          AND "DEWP" IS NOT NULL
          AND "RAIN" IS NOT NULL
          AND "WSPM" IS NOT NULL
        """
    },
}

# Crear mapa de estaciones
def create_stations_map():
    # Agregar columna para resaltar Dongsi
    stations_df['current_station'] = stations_df['station'] == 'Dongsi Beijing'
    stations_df['size'] = stations_df['current_station'].apply(lambda x: 20 if x else 10)
    stations_df['color'] = stations_df['current_station'].apply(lambda x: '#ef4444' if x else '#3b82f6')
    
    fig = go.Figure()
    
    # Añadir todas las estaciones
    for _, row in stations_df.iterrows():
        fig.add_trace(go.Scattermapbox(
            lat=[row['lat']],
            lon=[row['lon']],
            mode='markers+text',
            marker=dict(
                size=row['size'],
                color=row['color'],
                opacity=0.8
            ),
            text=[row['station']],
            textposition="top right",
            name=row['station'],
            hovertemplate=(
                f"<b>{row['station']}</b><br>" +
                f"Lat: {row['lat']:.3f}<br>" +
                f"Lon: {row['lon']:.3f}<br>" +
                f"{'📍 Estación actual' if row['current_station'] else '📍 Otra estación'}" +
                "<extra></extra>"
            )
        ))
    
    fig.update_layout(
        mapbox=dict(
            style='open-street-map',
            center=dict(lat=39.9, lon=116.4),  # Centro en Beijing
            zoom=10
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        height=400,
        showlegend=False,
        paper_bgcolor='#1e293b',
        plot_bgcolor='#1e293b'
    )
    
    return fig

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
        html.P(f"Estación: {df_original['station'].iloc[0] if 'station' in df_original.columns else 'No disponible'}", 
               style={'color': '#e2e8f0'}),
        html.P(f"Rango temporal: {df_original['datetime'].min().strftime('%Y-%m-%d') if 'datetime' in df_original.columns else 'N/A'} a {df_original['datetime'].max().strftime('%Y-%m-%d') if 'datetime' in df_original.columns else 'N/A'}", 
               style={'color': '#e2e8f0'}),
    ], style={
        'backgroundColor': '#1e293b', 
        'padding': '20px', 
        'borderRadius': '10px',
        'marginBottom': '20px'
    }),

    # Mapa de estaciones
    html.Div([
        html.H3("🗺️ Red de Estaciones de Monitoreo - Beijing", style={'color': '#ffffff', 'marginBottom': '15px'}),
        html.P("Ubicación de las 12 estaciones de monitoreo de calidad del aire en Beijing", 
               style={'color': '#94a3b8', 'marginBottom': '15px'}),
        
        # Leyenda del mapa
        html.Div([
            html.Div([
                html.Span("🔴", style={'fontSize': '20px', 'marginRight': '8px'}),
                html.Span("Dongsi (Estación actual)", style={'color': '#ffffff'})
            ], style={'display': 'flex', 'alignItems': 'center', 'marginRight': '20px'}),
            html.Div([
                html.Span("🔵", style={'fontSize': '20px', 'marginRight': '8px'}),
                html.Span("Otras estaciones", style={'color': '#ffffff'})
            ], style={'display': 'flex', 'alignItems': 'center'})
        ], style={'display': 'flex', 'marginBottom': '15px'}),
        
        dcc.Graph(
            id='stations-map',
            figure=create_stations_map(),
            config={'displayModeBar': True, 'scrollZoom': True}
        ),
    ], style={
        'backgroundColor': '#1e293b', 
        'padding': '25px', 
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

    # Sección de consultas interactivas
    html.Div([
        html.H3("🔍 Consultas Interactivas de la Base de Datos", 
                style={'color': '#ffffff', 'marginBottom': '15px'}),
        html.P("Selecciona una consulta para explorar los datos:", 
               style={'color': '#94a3b8', 'marginBottom': '15px'}),
        
        # Selector de consultas
        html.Div([
            dcc.Dropdown(
                id='query-selector',
                options=[{'label': query_info['name'], 'value': query_id} 
                        for query_id, query_info in QUERIES.items()],
                placeholder='Selecciona una consulta...',
                style={'color': '#000000', 'marginBottom': '15px'}
            ),
        ]),
        
        # Resultados de la consulta
        html.Div(id='query-results', style={'marginTop': '20px'})
        
    ], style={
        'backgroundColor': '#1e293b', 
        'padding': '25px', 
        'borderRadius': '10px',
        'marginBottom': '20px'
    }),
])

# Callbacks para las consultas interactivas
@callback(
    Output('query-results', 'children'),
    Input('query-selector', 'value')
)
def update_query_results(selected_query):
    if not selected_query:
        return html.Div("Selecciona una consulta para ver los resultados.", 
                       style={'color': '#94a3b8', 'textAlign': 'center', 'padding': '20px'})
    
    try:
        # Ejecutar la consulta
        query_info = QUERIES[selected_query]
        df = load_data_from_query(query_info['query'])
        
        if df.empty:
            return html.Div("No se encontraron resultados para esta consulta.", 
                           style={'color': '#ef4444', 'padding': '20px'})
        
        # Formatear números decimales
        for col in df.columns:
            if df[col].dtype in ['float64', 'float32']:
                df[col] = df[col].round(2)

        # Para porcentajes, formatear como string con %
        percentage_cols = [col for col in df.columns if 'porcentaje' in col.lower() or 'percentage' in col.lower()]
        for col in percentage_cols:
            df[col] = df[col].apply(lambda x: f"{x}%" if pd.notnull(x) else x)
        
        # Crear tabla de resultados
        return html.Div([
            html.H4(f"📊 {query_info['name']}", 
                   style={'color': '#ffffff', 'marginBottom': '15px'}),
            dash_table.DataTable(
                data=df.to_dict('records'),
                columns=[{"name": col, "id": col} for col in df.columns],
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
                style_data={
                    'whiteSpace': 'normal',
                    'height': 'auto',
                },
            )
        ])
        
    except Exception as e:
        return html.Div([
            html.H4("❌ Error en la consulta", style={'color': '#ef4444'}),
            html.P(f"Error: {str(e)}", style={'color': '#94a3b8'})
        ], style={'padding': '20px'})

def register_callbacks(app):
    # Este callback ya está definido arriba con el decorator @callback
    # Solo mantenemos la función para compatibilidad si es necesaria
    pass