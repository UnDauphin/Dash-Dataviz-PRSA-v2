# pages/summary.py
from dash import dcc, html, dash_table
import plotly.express as px
from utils.data_loader import get_data

# Obtener datos
df_original, df_imputed, analysis_cols = get_data()

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
        Input('main-tabs', 'value')  # Se activa cuando se carga la pestaña
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