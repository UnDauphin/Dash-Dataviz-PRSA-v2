# pages/conclusions.py
from dash import dcc, html
from utils.data_loader import get_data

# Obtener datos para el resumen
df_original, df_imputed, analysis_cols = get_data()

# Layout de conclusiones
layout = html.Div([
    html.H2("📋 Conclusiones del Análisis EDA", 
            style={'color': '#ffffff', 'marginBottom': '20px'}),
    
    html.Div([
        dcc.Markdown("""
        ## 🎯 Resumen Ejecutivo

        Este análisis exploratorio de datos (EDA) comprende datos de calidad del aire de la estación Dongsi 
        (Marzo 2013 - Febrero 2017), con el objetivo de caracterizar patrones de contaminación, 
        identificar valores faltantes, y establecer relaciones entre variables ambientales.
        """, style={'color': '#ffffff', 'lineHeight': '1.6'}),
        
        html.Ul([
            html.Li(f"Período analizado: {df_original['datetime'].min().strftime('%Y-%m-%d') if 'datetime' in df_original.columns else 'N/A'} a {df_original['datetime'].max().strftime('%Y-%m-%d') if 'datetime' in df_original.columns else 'N/A'}"),
            html.Li(f"Total de observaciones: {len(df_original):,}"),
            html.Li(f"Variables de análisis: {len(analysis_cols)}"),
            html.Li(f"Contaminantes principales: PM2.5, PM10, SO2, NO2, CO, O3"),
        ], style={'color': '#e2e8f0', 'marginBottom': '20px'}),
        
        dcc.Markdown("""
        ## 📈 Hallazgos Principales

        ### 1. Patrones Temporales
        - **Estacionalidad marcada** en contaminantes (mayores niveles en invierno)
        - **Ciclos diarios** evidentes en PM2.5 y O3
        - **Tendencias interanales** que sugieren efectividad de políticas ambientales

        ### 2. Relaciones entre Variables
        - **Correlación positiva** entre PM2.5-PM10 (origen común de combustión)
        - **Relación inversa** temperatura-contaminantes (inversión térmica invernal)
        - **Patrón complejo** viento-contaminación (dispersión vs transporte)

        ### 3. Calidad de Datos
        - **Tasa de faltantes:** Variable según parámetro (5-15% típico)
        - **Distribución de faltantes:** Principalmente MCAR
        - **Integridad temporal:** Brechas concentradas en periodos específicos
        """, style={'color': '#e2e8f0', 'lineHeight': '1.6'}),

        dcc.Markdown("""
        ## ⚠️ Limitaciones Técnicas

        ### Restricciones de Render
        - **Memoria RAM limitada** en el plan gratuito impide ejecutar tests estadísticos avanzados
        - **Imposibilidad de cargar el modelo SARIMA completo** debido al tamaño del archivo
        - **Análisis de estacionariedad** se realiza mediante métodos visuales por limitaciones de recursos

        ### Resultados del Modelo SARIMA
        - **Rendimiento subóptimo:** El modelo muestra métricas bajas (R² = 0.009)
        - **Falta de experiencia:** Poco dominio en selección de hiperparámetros óptimos
        - **Complejidad no capturada:** El modelo no logra capturar adecuadamente la variabilidad de los datos
        """, style={'color': '#e2e8f0', 'lineHeight': '1.6'}),

        dcc.Markdown("""
        ## 🚀 Mejoras Futuras

        ### Para el Modelo Predictivo
        - **Búsqueda en grid** para encontrar parámetros SARIMA óptimos
        - **Incorporar variables exógenas** (temperatura, presión, viento) en modelo SARIMAX
        - **Probar modelos alternativos** como LSTM o XGBoost para series temporales
        - **Validación cruzada temporal** para evaluación robusta del rendimiento

        ### Para el Análisis
        - **Transformaciones** para estabilizar varianza en series temporales
        - **Detección avanzada de outliers** y patrones estacionales
        - **Análisis de múltiples estaciones** para comprender patrones espaciales
        """, style={'color': '#e2e8f0', 'lineHeight': '1.6'})
    ], style={
        'backgroundColor': '#1e293b', 
        'padding': '30px', 
        'borderRadius': '10px',
        'border': '1px solid #334155'
    })
])

def register_callbacks(app):
    # No se necesitan callbacks para las conclusiones
    pass