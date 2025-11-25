from dash import dcc, html
import dash
import plotly.express as px
import pandas as pd
from utils.data_loader import get_data


# --- Helpers / data ---
def load_data():
    try:
        df_original, df_imputed, analysis_cols = get_data()
        return df_original, df_imputed, analysis_cols
    except Exception as e:
        print(f"Error loading data: {e}")
        return pd.DataFrame(), pd.DataFrame(), []


def make_missing_fig(df):
    if df.empty:
        # Return empty figure if no data
        fig = px.bar(title='No data available')
        fig.update_layout(plot_bgcolor='#1e293b', paper_bgcolor='#1e293b', font_color='white', height=420)
        return fig
    
    # porcentaje faltantes por columna
    miss_pct = (df.isna().mean() * 100).reset_index()
    miss_pct.columns = ['variable', 'missing_pct']
    miss_pct = miss_pct.sort_values('missing_pct', ascending=False)

    fig = px.bar(
        miss_pct,
        x='variable',
        y='missing_pct',
        title='Porcentaje de valores faltantes por variable',
        labels={'missing_pct': '% faltantes', 'variable': 'Variable'},
        template='plotly_dark'
    )
    fig.update_layout(plot_bgcolor='#1e293b', paper_bgcolor='#1e293b', font_color='white', height=420)
    return fig


planteamiento_block = html.Div([
    html.H2("Planteamiento del problema", style={'color': '#ffffff'}),
    html.P("La contaminación atmosférica por partículas finas (PM2.5) constituye una amenaza importante para la salud pública en numerosas áreas urbanas. Estas partículas poseen un diámetro inferior a 2.5 micrómetros y pueden penetrar profundamente en el sistema respiratorio, incrementando el riesgo de enfermedades respiratorias y cardiovasculares. Este proyecto se centra en el análisis horario de las concentraciones de PM2.5 y su relación con variables meteorológicas (temperatura, presión, velocidad y dirección del viento) en la estación Dongsi de Beijing durante el periodo 2013-03-01 a 2017-02-28.", style={'color': '#e2e8f0'}),
    html.H3("Pregunta problema", style={'color': '#ffffff'}),
    html.P("¿Qué patrones temporales y relaciones con variables meteorológicas pueden identificarse en las concentraciones de PM2.5 registradas en la estación Dongsi, y hasta qué punto dichos patrones permiten caracterizar y predecir episodios de alta contaminación?", style={'color': '#e2e8f0'}),
    html.H2("Justificación", style={'color': '#ffffff', 'marginTop': 20}),
    html.P("Comprender la variabilidad de PM2.5 y su dependencia de condiciones meteorológicas tiene un impacto directo en la salud pública y en la toma de decisiones de gestión ambiental. El análisis y la visualización interactiva de estos datos facilitan la detección de episodios críticos y apoyan la planificación de medidas preventivas. El uso del conjunto de datos PRSA (estación Dongsi) permite replicabilidad y comparabilidad con estudios previos sobre contaminación en Beijing.", style={'color': '#e2e8f0'})
], style={'backgroundColor': '#1e293b', 'padding': '18px', 'borderRadius': '8px'})


marco_block = html.Div([
    html.H2("Marco Teórico – Antecedentes", style={'color': '#ffffff'}),
    html.H4("Conceptos clave", style={'color': '#ffffff'}),
    html.Ul([
        html.Li([html.B("PM2.5 (material particulado fino): "), html.Span("Partículas en suspensión con diámetro aerodinámico inferior a 2.5 μm. Su inhalación está asociada a efectos adversos en la salud respiratoria y cardiovascular, y a una mayor mortalidad prematura (The Lancet Commission on Pollution and Health, 2018; Huang et al., 2024).", style={'color': '#e2e8f0'})]),
        html.Li([html.B("Series de tiempo ambientales: "), html.Span("Las concentraciones horarias de contaminantes constituyen series de tiempo con posibles componentes de tendencia, estacionalidad y autocorrelación; por ello, su análisis requiere técnicas específicas.", style={'color': '#e2e8f0'})]),
        html.Li([html.B("Facebook Prophet: "), html.Span("Modelo de forecasting desarrollado por Facebook que maneja automáticamente estacionalidades, efectos de días festivos, y es robusto frente a datos faltantes y outliers. Está basado en un modelo aditivo que descompone la serie temporal en tendencia, estacionalidad y efectos de regresores.", style={'color': '#e2e8f0'})]),
    ]),

    html.H4("Prophet: Funcionamiento y Ventajas", style={'color': '#ffffff', 'marginTop': 10}),
    html.Ul([
        html.Li([html.B("Modelo aditivo: "), html.Span("y(t) = g(t) + s(t) + h(t) + εₜ, donde g(t) es la tendencia, s(t) la estacionalidad, h(t) efectos de festivos, y εₜ el error.")]),
        html.Li([html.B("Tendencia no lineal: "), html.Span("Se modela con crecimiento logístico o lineal por partes, permitiendo capturar cambios en la tendencia.")]),
        html.Li([html.B("Estacionalidad múltiple: "), html.Span("Maneja estacionalidad diaria, semanal y anual automáticamente mediante series de Fourier.")]),
        html.Li([html.B("Robustez: "), html.Span("Funciona bien con datos faltantes y outliers sin necesidad de preprocesamiento extensivo.")]),
    ], style={'color': '#e2e8f0'}),

    html.H4("Validación Cruzada en Prophet", style={'color': '#ffffff', 'marginTop': 10}),
    html.P("Prophet implementa una validación cruzada temporal específica para series de tiempo:", style={'color': '#e2e8f0'}),
    html.Ul([
        html.Li([html.B("Rolling origin: "), html.Span("Se entrena el modelo en un período inicial y se evalúa en un horizonte futuro, luego se expande la ventana de entrenamiento.")]),
        html.Li([html.B("Métricas: "), html.Span("Se calculan MSE, RMSE y SMAPE para diferentes horizontes de predicción.")]),
        html.Li([html.B("Parámetros: "), html.Span("initial: tamaño inicial de entrenamiento, period: espaciado entre cortes, horizon: longitud del período de prueba.")]),
    ], style={'color': '#e2e8f0'}),

    html.H4("Referencias (seleccionadas)", style={'color': '#ffffff', 'marginTop': 10}),
    html.Ul([
        html.Li("Taylor, S. J., & Letham, B. (2018). Forecasting at scale. The American Statistician, 72(1), 37-45."),
        html.Li("Beijing PM2.5 dataset. (2020). Zenodo. https://zenodo.org/records/3902671"),
        html.Li("Facebook Prophet Documentation. https://facebook.github.io/prophet/"),
        html.Li("Huang, F., et al. (2024). Visualization and analysis of PM2.5 health effects, 2013 to 2023. International Journal of Environmental Research and Public Health, 21, Article 11630982."),
    ], style={'color': '#e2e8f0'})
], style={'backgroundColor': '#1e293b', 'padding': '18px', 'borderRadius': '8px'})


def metricas_block():
    return html.Div([
        html.H3("Métricas de Evaluación", style={'color': '#ffffff'}),
        
        html.Div([
            html.H4("MSE (Mean Squared Error)", style={'color': '#ffffff'}),
            html.P("Error Cuadrático Medio - Promedia los errores al cuadrado:", style={'color': '#e2e8f0'}),
            html.P("MSE = (1/n) × Σ(yᵢ - ŷᵢ)²", style={
                'color': '#3b82f6', 
                'fontFamily': 'monospace', 
                'fontSize': '18px',
                'textAlign': 'center',
                'padding': '10px',
                'backgroundColor': '#334155',
                'borderRadius': '5px'
            }),
            html.P("Donde yᵢ son los valores reales, ŷᵢ las predicciones, y n el número de observaciones.", style={'color': '#94a3b8', 'fontSize': '14px'}),
            html.P("▪ Penaliza más los errores grandes ▪ Sensible a outliers ▪ En unidades cuadradas", style={'color': '#e2e8f0'}),
        ], style={'marginBottom': '20px'}),
        
        html.Div([
            html.H4("RMSE (Root Mean Squared Error)", style={'color': '#ffffff'}),
            html.P("Raíz del Error Cuadrático Medio - En las mismas unidades que la variable original:", style={'color': '#e2e8f0'}),
            html.P("RMSE = √MSE", style={
                'color': '#3b82f6', 
                'fontFamily': 'monospace', 
                'fontSize': '18px',
                'textAlign': 'center',
                'padding': '10px',
                'backgroundColor': '#334155',
                'borderRadius': '5px'
            }),
            html.P("Interpretación directa en la escala original de PM2.5 (μg/m³).", style={'color': '#94a3b8', 'fontSize': '14px'}),
            html.P("▪ Misma escala que los datos ▪ Fácil interpretación ▪ También sensible a outliers", style={'color': '#e2e8f0'}),
        ], style={'marginBottom': '20px'}),
        
        html.Div([
            html.H4("SMAPE (Symmetric Mean Absolute Percentage Error)", style={'color': '#ffffff'}),
            html.P("Error Porcentual Absoluto Medio Simétrico - Error porcentual simétrico:", style={'color': '#e2e8f0'}),
            html.P("SMAPE = (100%/n) × Σ(|yᵢ - ŷᵢ| / (|yᵢ| + |ŷᵢ|)/2)", style={
                'color': '#3b82f6', 
                'fontFamily': 'monospace', 
                'fontSize': '18px',
                'textAlign': 'center',
                'padding': '10px',
                'backgroundColor': '#334155',
                'borderRadius': '5px'
            }),
            html.P("Versión simétrica del MAPE, evita división por cero y es más estable.", style={'color': '#94a3b8', 'fontSize': '14px'}),
            html.P("▪ Escala porcentual ▪ Simétrico ▪ Robustez frente a valores cero", style={'color': '#e2e8f0'}),
        ]),
    ], style={'backgroundColor': '#334155', 'padding': '15px', 'borderRadius': '8px', 'marginTop': '15px'})


def metodologia_block(df_original):
    try:
        # Safe calculations with empty DataFrame check
        if df_original.empty:
            total = 0
            missing_cells = 0
            missing_pct = 0.0
        else:
            total = df_original.shape[0] * df_original.shape[1]
            missing_cells = int(df_original.isna().sum().sum())
            missing_pct = (missing_cells / total * 100) if total > 0 else 0.0

        return html.Div([
            html.H2("Metodología", style={'color': '#ffffff'}),

            html.H4("a) Definición del problema a resolver", style={'color': '#ffffff'}),
            html.P("Tipo de problema: Predicción de series temporales univariada con Prophet. Variable objetivo: Concentración horaria de PM2.5 (columna `pm2.5` en el dataset). Horizonte de predicción: corto y mediano plazo (predicciones horarias).", style={'color': '#e2e8f0'}),

            html.H4("b) Preparación de los datos", style={'color': '#ffffff', 'marginTop': 10}),
            html.Ol([
                html.Li("Carga y combinación de archivos (PRSA csv, estaciones, parámetros adicionales). Conversión de fecha y hora a formato datetime para indexación temporal."),
                html.Li("Limpieza: tratamiento de valores faltantes mediante imputación con mediana para variables continuas."),
                html.Li([html.B("Transformación logarítmica: "), "Aplicación de logaritmo natural a los datos de PM2.5 para manejar la asimetría (cola derecha) y mejorar la estabilidad del modelo. Basado en literatura especializada que reporta mejor desempeño con esta transformación."]),
                html.Li("Formato Prophet: la serie temporal se prepara con dos columnas: `ds` (fechas) y `y` (valores de PM2.5 transformados)."),
                html.Li("División temporal: 80% para entrenamiento (2013-2015) y 20% para prueba (2016-2017), respetando la naturaleza temporal de los datos."),
            ], style={'color': '#e2e8f0'}),

            html.H4("c) Configuración del modelo Prophet", style={'color': '#ffffff', 'marginTop': 10}),
            html.Ul([
                html.Li([html.B("Estacionalidades: "), "Configuradas para patrones diarios, semanales y anuales."]),
                html.Li([html.B("Puntos de cambio (Changepoints): "), "Usamos changepoint_prior_scale=0.01. Los changepoints son puntos donde la tendencia puede cambiar abruptamente. Una escala baja (0.01) significa que el modelo es más conservador y evita sobreajuste, suavizando las transiciones de tendencia."]),
                html.Li([html.B("Crecimiento: "), "Crecimiento logístico para capturar saturación en niveles de contaminación."]),
                html.Li([html.B("Intervalos de confianza: "), "Se calculan intervalos de predicción del 95%."]),
            ], style={'color': '#e2e8f0'}),

            html.H4("d) Entrenamiento y evaluación", style={'color': '#ffffff', 'marginTop': 10}),
            html.Ol([
                html.Li("Entrenamiento del modelo Prophet con datos de 2013-2015 (transformados logarítmicamente)."),
                html.Li("Validación cruzada temporal con parámetros: initial='365 days', period='90 days', horizon='180 days'."),
                html.Li("Cálculo de métricas de performance: MSE, RMSE y SMAPE en conjunto de prueba."),
                html.Li("Análisis de residuales y patrones de error temporales."),
            ], style={'color': '#e2e8f0'}),

            html.H4("e) Interpretación de resultados", style={'color': '#ffffff', 'marginTop': 10}),
            html.P("Análisis de componentes: tendencia, estacionalidades y puntos de cambio identificados por el modelo. Evaluación de capacidad predictiva para episodios de alta contaminación. Transformación inversa de predicciones para interpretación en escala original.", style={'color': '#e2e8f0'}),

            # Bloque de métricas
            metricas_block(),

            html.P(["Porcentaje global de valores faltantes en el dataset: ", html.B(f"{missing_pct:.2f}%")], style={'color': '#e2e8f0', 'marginTop': '20px'}),
            html.Div(dcc.Graph(figure=make_missing_fig(df_original)), style={'marginTop': '12px'})
        ], style={'backgroundColor': '#1e293b', 'padding': '18px', 'borderRadius': '8px'})
    
    except Exception as e:
        print(f"Error in metodologia_block: {e}")
        return html.Div([
            html.H2("Error al cargar la metodología", style={'color': 'red'}),
            html.P(f"Error: {str(e)}", style={'color': 'white'})
        ], style={'backgroundColor': '#1e293b', 'padding': '18px', 'borderRadius': '8px'})


# --- Layout principal ---
layout = html.Div([
    dcc.Tabs(id='desarrollo-subtabs', value='tab-planteamiento', children=[
        dcc.Tab(label='Planteamiento y Justificación', value='tab-planteamiento'),
        dcc.Tab(label='Marco Teórico', value='tab-marco'),
        dcc.Tab(label='Metodología', value='tab-metodologia')
    ], colors={"border": "#475569", "primary": "#3b82f6", "background": "#1e293b"}),

    html.Div(id='desarrollo-subtab-content', style={'paddingTop': '18px'})
], style={'backgroundColor': '#0f1720', 'color': '#ffffff', 'padding': '16px'})


def register_callbacks(app: dash.Dash):
    from dash import Input, Output

    @app.callback(
        Output('desarrollo-subtab-content', 'children'),
        Input('desarrollo-subtabs', 'value')
    )
    def render_subtab(tab):
        try:
            df_original, df_imputed, analysis_cols = load_data()

            if tab == 'tab-planteamiento':
                return planteamiento_block
            elif tab == 'tab-marco':
                return marco_block
            elif tab == 'tab-metodologia':
                return metodologia_block(df_original)
            return html.Div()
        except Exception as e:
            print(f"Error in render_subtab: {e}")
            return html.Div(f"Error: {str(e)}", style={'color': 'red'})
