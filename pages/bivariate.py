# pages/bivariate.py - VERSIÓN COMPLETA CON MATRIZ DE CORRELACIONES
from dash import dcc, html, Input, Output, callback
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from utils.data_loader import get_data

# Obtener datos
df_original, df_imputed, analysis_cols = get_data()

# Layout de análisis bivariado
layout = html.Div([
    html.H2("🔗 Análisis Bivariado", 
            style={'color': '#ffffff', 'marginBottom': '20px'}),
    
    dcc.Tabs(id="bivariate-tabs", value='tab-scatter', children=[
        dcc.Tab(
            label='📊 Scatter Plots', 
            value='tab-scatter',
            style={'padding': '10px', 'fontWeight': 'bold'},
            selected_style={'backgroundColor': '#1e293b'}
        ),
        dcc.Tab(
            label='🔗 Matriz de Correlaciones', 
            value='tab-correlation',
            style={'padding': '10px', 'fontWeight': 'bold'},
            selected_style={'backgroundColor': '#1e293b'}
        ),
    ], style={'marginBottom': '20px'}),
    
    html.Div(id='bivariate-tab-content')
])

def render_scatter_plots():
    """Pestaña de scatter plots"""
    return html.Div([
        html.H3("📊 Análisis de Dispersión", style={'color': '#ffffff'}),
        html.P("Explora las relaciones entre dos variables:"),
        
        html.Div([
            html.Div([
                html.Label("Variable X:", style={'color': '#ffffff'}),
                dcc.Dropdown(
                    id='bivariate-x',
                    options=[{'label': col, 'value': col} for col in analysis_cols],
                    value=analysis_cols[0] if analysis_cols else None,
                    style={'color': '#000000'}
                ),
            ], style={'flex': '1', 'marginRight': '15px'}),
            
            html.Div([
                html.Label("Variable Y:", style={'color': '#ffffff'}),
                dcc.Dropdown(
                    id='bivariate-y',
                    options=[{'label': col, 'value': col} for col in analysis_cols],
                    value=analysis_cols[1] if len(analysis_cols) > 1 else analysis_cols[0],
                    style={'color': '#000000'}
                ),
            ], style={'flex': '1', 'marginRight': '15px'}),
            
            html.Div([
                html.Label("Tipo de Gráfico:", style={'color': '#ffffff'}),
                dcc.Dropdown(
                    id='bivariate-type',
                    options=[
                        {'label': 'Scatter Plot', 'value': 'scatter'},
                        {'label': 'Scatter + Trendline', 'value': 'scatter_trend'},
                        {'label': 'Heatmap de Densidad', 'value': 'density'}
                    ],
                    value='scatter',
                    style={'color': '#000000'}
                ),
            ], style={'flex': '1'}),
        ], style={'display': 'flex', 'marginBottom': '30px', 'alignItems': 'end'}),
        
        dcc.Graph(id='bivariate-plot'),
        
        html.Div(id='bivariate-correlation', style={'marginTop': '20px'})
    ])

def render_correlation_matrix():
    """Pestaña de matriz de correlaciones"""
    df_orig, df_imp, analysis_cols = get_data()
    
    if len(analysis_cols) < 2:
        return html.Div([
            html.H3("🔗 Matriz de Correlaciones", style={'color': '#ffffff'}),
            html.P("❌ Se requieren al menos 2 variables para la matriz de correlaciones.")
        ])
    
    # Filtrar variables más relevantes
    important_vars = [col for col in analysis_cols if any(x in col for x in ['pm', 'temp', 'pres', 'dewp', 'wspm', 'so2', 'no2', 'co', 'o3'])]
    if len(important_vars) < 5:
        important_vars = analysis_cols[:min(10, len(analysis_cols))]
    
    return html.Div([
        html.H3("🔗 Matriz de Correlaciones", style={'color': '#ffffff'}),
        html.P("Selecciona las variables para la matriz de correlaciones:"),
        
        dcc.Dropdown(
            id='correlation-vars-selector',
            options=[{'label': col, 'value': col} for col in analysis_cols],
            value=important_vars,
            multi=True,
            style={
                'marginBottom': '20px', 
                'color': '#000000',
                'backgroundColor': '#1e293b'
            }
        ),
        
        html.Label("Método de correlación:", style={'color': '#ffffff', 'marginBottom': '10px'}),
        dcc.RadioItems(
            id='correlation-method',
            options=[
                {'label': ' Pearson', 'value': 'pearson'},
                {'label': ' Spearman', 'value': 'spearman'},
                {'label': ' Kendall', 'value': 'kendall'}
            ],
            value='pearson',
            style={'color': '#ffffff', 'marginBottom': '20px'}
        ),
        
        dcc.Graph(id='correlation-matrix-plot'),
        
        html.Div(id='correlation-stats', style={'marginTop': '20px'})
    ])

def register_callbacks(app):
    from utils.data_loader import get_data
    
    # Callback para cambiar sub-pestañas
    @app.callback(
        Output('bivariate-tab-content', 'children'),
        Input('bivariate-tabs', 'value')
    )
    def render_bivariate_tab(tab):
        if tab == 'tab-scatter':
            return render_scatter_plots()
        elif tab == 'tab-correlation':
            return render_correlation_matrix()
        return html.Div("Selecciona una sub-pestaña")
    
    # Callback para scatter plots
    @app.callback(
        [Output('bivariate-plot', 'figure'),
         Output('bivariate-correlation', 'children')],
        [Input('bivariate-x', 'value'),
         Input('bivariate-y', 'value'),
         Input('bivariate-type', 'value')]
    )
    def update_bivariate(x, y, plot_type):
        if not x or not y:
            return {}, ""
            
        df_orig, df_imp, _ = get_data()
        
        if df_imp.empty or x not in df_imp.columns or y not in df_imp.columns:
            return {}, html.Div("❌ Variables no disponibles en el dataset.")
        
        # Calcular correlación
        corr_val = df_imp[x].corr(df_imp[y])
        
        # Crear gráfico según tipo
        if plot_type == 'scatter':
            fig = px.scatter(
                df_imp, x=x, y=y, 
                opacity=0.6, 
                title=f"{x} vs {y}",
                template='plotly_dark'
            )
        elif plot_type == 'scatter_trend':
            fig = px.scatter(
                df_imp, x=x, y=y, 
                trendline="lowess", 
                opacity=0.5, 
                title=f"{x} vs {y} (Suavizado LOWESS)",
                template='plotly_dark'
            )
            # Cambiar color del trendline para que resalte más
            fig.update_traces(
                line=dict(color='red', width=3, dash='solid'),
                selector=dict(mode='lines')
            )
        else:  # density
            fig = px.density_heatmap(
                df_imp, x=x, y=y, 
                nbinsx=40, nbinsy=40,
                title=f"Densidad {x} vs {y}",
                template='plotly_dark'
            )
        
        fig.update_layout(
            plot_bgcolor='#1e293b',
            paper_bgcolor='#1e293b',
            font_color='white',
            height=500
        )
        
        # Interpretación de correlación
        if abs(corr_val) >= 0.7:
            strength = "FUERTE"
            color = "#ef4444" if corr_val > 0 else "#3b82f6"
        elif abs(corr_val) >= 0.3:
            strength = "MODERADA"
            color = "#f59e0b"
        else:
            strength = "DÉBIL"
            color = "#10b981"
        
        direction = "POSITIVA" if corr_val > 0 else "NEGATIVA"
        
        correlation_text = html.Div([
            html.H4("📈 Correlación entre Variables", style={'color': '#ffffff'}),
            html.P(f"Coeficiente de correlación (Pearson) entre **{x}** y **{y}**:", 
                  style={'color': '#ffffff'}),
            html.P(f"{corr_val:.3f}", 
                  style={'color': color, 'fontSize': '24px', 'fontWeight': 'bold'}),
            html.P(f"Relación {strength} {direction}", 
                  style={'color': color, 'fontWeight': 'bold'})
        ], style={
            'backgroundColor': '#1e293b',
            'padding': '20px',
            'borderRadius': '10px',
            'textAlign': 'center'
        })
        
        return fig, correlation_text
    
    # Callback para matriz de correlaciones
    @app.callback(
        [Output('correlation-matrix-plot', 'figure'),
         Output('correlation-stats', 'children')],
        [Input('correlation-vars-selector', 'value'),
         Input('correlation-method', 'value')]
    )
    def update_correlation_matrix(selected_vars, method):
        if not selected_vars or len(selected_vars) < 2:
            empty_fig = go.Figure()
            empty_fig.update_layout(
                title="Selecciona al menos 2 variables",
                template='plotly_dark',
                plot_bgcolor='#1e293b',
                paper_bgcolor='#1e293b',
                font_color='white',
                height=400
            )
            return empty_fig, ""
        
        df_orig, df_imp, _ = get_data()
        
        # Verificar que las variables seleccionadas existen
        available_vars = [var for var in selected_vars if var in df_imp.columns]
        if len(available_vars) < 2:
            empty_fig = go.Figure()
            empty_fig.update_layout(
                title="Variables seleccionadas no disponibles",
                template='plotly_dark',
                plot_bgcolor='#1e293b',
                paper_bgcolor='#1e293b',
                font_color='white',
                height=400
            )
            return empty_fig, ""
        
        try:
            # Calcular matriz de correlación
            corr_matrix = df_imp[available_vars].corr(method=method)
            
            # Crear heatmap
            fig = px.imshow(
                corr_matrix,
                text_auto=True,
                aspect="auto",
                color_continuous_scale='RdBu_r',
                title=f"Matriz de Correlación ({method.capitalize()})",
                template='plotly_dark'
            )
            
            fig.update_layout(
                plot_bgcolor='#1e293b',
                paper_bgcolor='#1e293b',
                font_color='white',
                height=600,
                xaxis_title="Variables",
                yaxis_title="Variables"
            )
            
            # Estadísticas de correlaciones fuertes
            strong_correlations = []
            for i in range(len(corr_matrix.columns)):
                for j in range(i+1, len(corr_matrix.columns)):
                    corr_val = corr_matrix.iloc[i, j]
                    if abs(corr_val) > 0.7:
                        strong_correlations.append((
                            corr_matrix.columns[i],
                            corr_matrix.columns[j],
                            corr_val
                        ))
            
            # Ordenar por magnitud de correlación
            strong_correlations.sort(key=lambda x: abs(x[2]), reverse=True)
            
            stats_content = html.Div([
                html.H4("🔍 Correlaciones Fuertes (|r| > 0.7)", style={'color': '#ffffff'}),
                html.Ul([
                    html.Li(
                        f"{var1} ↔ {var2}: {corr_val:.3f}",
                        style={'color': '#ef4444' if abs(corr_val) > 0.8 else '#f59e0b'}
                    ) 
                    for var1, var2, corr_val in strong_correlations
                ]) if strong_correlations else html.P(
                    "No hay correlaciones fuertes (> 0.7)", 
                    style={'color': '#94a3b8'}
                )
            ], style={
                'backgroundColor': '#1e293b',
                'padding': '20px',
                'borderRadius': '10px'
            })
            
            return fig, stats_content
            
        except Exception as e:
            error_fig = go.Figure()
            error_fig.update_layout(
                title=f"Error al calcular correlaciones: {str(e)}",
                template='plotly_dark',
                plot_bgcolor='#1e293b',
                paper_bgcolor='#1e293b',
                font_color='white',
                height=400
            )
            return error_fig, ""