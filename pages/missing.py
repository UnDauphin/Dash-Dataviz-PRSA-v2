# pages/missing.py
from dash import dcc, html, dash_table
import plotly.express as px
import pandas as pd
from utils.data_loader import get_missing_analysis, get_ks_test_results

# Obtener análisis de faltantes
miss_before, miss_after, types = get_missing_analysis()
ks_results = get_ks_test_results()

# Layout de la pestaña de valores faltantes
layout = html.Div([
    html.H2("❓ Análisis de Valores Faltantes", 
            style={'color': '#ffffff', 'marginBottom': '20px'}),
    
    # Resumen ejecutivo
    html.Div([
        html.H3("📋 Resumen Ejecutivo", style={'color': '#ffffff'}),
        html.P("Esta sección analiza los valores faltantes en el dataset, su clasificación y el impacto de la imputación."),
    ], style={
        'backgroundColor': '#1e293b', 
        'padding': '20px', 
        'borderRadius': '10px',
        'marginBottom': '20px'
    }),
    
    # Antes de imputar
    html.Div([
        html.H3("🔍 Antes de la Imputación", style={'color': '#ffffff'}),
        html.P("Distribución de valores faltantes en el dataset original:"),
    ], style={'marginBottom': '15px'}),
    
    html.Div(id='missing-before-section'),
    
    # Clasificación de tipos
    html.Div([
        html.H3("🎯 Clasificación de Tipos de Ausencia", style={'color': '#ffffff', 'marginTop': '30px'}),
        html.P("Heurística para clasificar los valores faltantes (MCAR, MAR, MNAR):"),
    ], style={'marginBottom': '15px'}),
    
    html.Div(id='missing-types-section'),
    
    # Después de imputar
    html.Div([
        html.H3("✅ Después de la Imputación", style={'color': '#ffffff', 'marginTop': '30px'}),
        html.P("Estado del dataset después de aplicar las estrategias de imputación:"),
    ], style={'marginBottom': '15px'}),
    
    html.Div(id='missing-after-section'),
    
    # Validación estadística
    html.Div([
        html.H3("📊 Validación Estadística (Prueba KS)", style={'color': '#ffffff', 'marginTop': '30px'}),
        html.P("Comparación de distribuciones antes y después de la imputación:"),
    ], style={'marginBottom': '15px'}),
    
    html.Div(id='ks-test-section'),
])

def register_callbacks(app):
    from dash import Input, Output
    from utils.data_loader import get_missing_analysis, get_ks_test_results
    
    @app.callback(
        [Output('missing-before-section', 'children'),
         Output('missing-types-section', 'children'),
         Output('missing-after-section', 'children'),
         Output('ks-test-section', 'children')],
        Input('main-tabs', 'value')
    )
    def update_missing_analysis(tab):
        if tab != 'tab-missing':
            return "", "", "", ""
            
        miss_before, miss_after, types = get_missing_analysis()
        ks_results = get_ks_test_results()
        
        # Sección: Antes de imputar
        if miss_before is not None and not miss_before.empty:
            miss_before_df = miss_before.reset_index()
            miss_before_df.columns = ['Variable', 'Valores Faltantes']
            
            fig_before = px.bar(miss_before_df, x='Variable', y='Valores Faltantes',
                              title="Valores Faltantes Antes de Imputar",
                              template='plotly_dark')
            fig_before.update_layout(
                plot_bgcolor='#1e293b',
                paper_bgcolor='#1e293b',
                font_color='white'
            )
            
            before_section = html.Div([
                dash_table.DataTable(
                    data=miss_before_df.to_dict('records'),
                    columns=[{"name": col, "id": col} for col in miss_before_df.columns],
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
                ),
                dcc.Graph(figure=fig_before)
            ])
        else:
            before_section = html.Div([
                html.P("✅ No hay valores faltantes en el dataset original.", 
                      style={'color': '#10b981', 'fontWeight': 'bold'})
            ])
        
        # Sección: Tipos de ausencia
        if types:
            types_df = pd.DataFrame(list(types.items()), columns=['Variable', 'Tipo'])
            types_section = dash_table.DataTable(
                data=types_df.to_dict('records'),
                columns=[{"name": col, "id": col} for col in types_df.columns],
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
        else:
            types_section = html.P("No hay columnas con faltantes para clasificar.")
        
        # Sección: Después de imputar
        if miss_after is not None and not miss_after.empty:
            miss_after_df = miss_after.reset_index()
            miss_after_df.columns = ['Variable', 'Valores Faltantes']
            
            fig_after = px.bar(miss_after_df, x='Variable', y='Valores Faltantes',
                             title="Valores Faltantes Después de Imputar",
                             template='plotly_dark')
            fig_after.update_layout(
                plot_bgcolor='#1e293b',
                paper_bgcolor='#1e293b',
                font_color='white'
            )
            
            after_section = html.Div([
                dash_table.DataTable(
                    data=miss_after_df.to_dict('records'),
                    columns=[{"name": col, "id": col} for col in miss_after_df.columns],
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
                ),
                dcc.Graph(figure=fig_after)
            ])
        else:
            after_section = html.Div([
                html.P("✅ No quedan valores faltantes después de la imputación.", 
                      style={'color': '#10b981', 'fontWeight': 'bold'})
            ])
        
        # Sección: Prueba KS
        if ks_results:
            ks_df = pd.DataFrame(ks_results, columns=['Variable', 'Estadístico KS', 'Valor p', 'Nota'])
            ks_section = dash_table.DataTable(
                data=ks_df.to_dict('records'),
                columns=[{"name": col, "id": col} for col in ks_df.columns],
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
        else:
            ks_section = html.P("No hay variables numéricas con valores faltantes para comparar.")
        
        return before_section, types_section, after_section, ks_section