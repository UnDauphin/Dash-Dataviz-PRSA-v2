import dash
from dash import dcc, html, Input, Output
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import os


def load_csv_safe(path, parse_dates=None, index_col=None):
    if os.path.exists(path):
        try:
            return pd.read_csv(path, parse_dates=parse_dates, index_col=index_col)
        except Exception:
            try:
                # fallback: read without parsing
                return pd.read_csv(path)
            except Exception:
                return None
    return None


# Cargar los CSVs que ahora generó el notebook (o el usuario)
pred_df = load_csv_safe('pred.csv', index_col=0, parse_dates=True)
df_cv = load_csv_safe('df_cv.csv')
df_p = load_csv_safe('df_p.csv')

from utils.data_loader import get_data
df_original, df_imputed, analysis_cols = get_data()


# --- Figura: Predicción vs Actual (igual que en el notebook) ---
def make_forecast_figure(agg='hourly'):
    if pred_df is None or getattr(pred_df, 'empty', True):
        return px.line(title='No se encontró `pred.pkl`')

    p = pred_df.copy()
    # Usar la primera columna numérica como predicción si el nombre varía
    num_cols = p.select_dtypes(include=[np.number]).columns.tolist()
    if not num_cols:
        return px.line(title='pred.pkl no contiene columnas numéricas de predicción')
    pred_col = num_cols[0]

    # Asegurar índice datetime
    if not isinstance(p.index, pd.DatetimeIndex):
        if 'Date' in p.columns:
            p.index = pd.to_datetime(p['Date'], errors='coerce')
        else:
            try:
                p.index = pd.to_datetime(p.index)
            except Exception:
                pass

    # Agregación: si daily, re-samplear por día (media)
    if agg == 'daily':
        p = p.resample('D').mean()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=p.index, y=p[pred_col], mode='lines', name='Predicción', line=dict(color='#f59e0b')))

    # Si hay datos reales, superponer (resample si daily)
    if df_imputed is not None and not getattr(df_imputed, 'empty', True):
        candidates = [c for c in df_imputed.columns if 'pm2' in c]
        if candidates:
            col = candidates[0]
            dff = df_imputed.set_index('datetime') if 'datetime' in df_imputed.columns else df_imputed.set_index(df_imputed.columns[0])
            dff.index = pd.to_datetime(dff.index, errors='coerce')
            if agg == 'daily':
                dff_plot = dff[[col]].resample('D').mean()
            else:
                dff_plot = dff[[col]]
            fig.add_trace(go.Scatter(x=dff_plot.index, y=dff_plot[col], mode='lines', name='Actual', line=dict(color='#3b82f6')))

    fig.update_layout(title=f'PM2.5 - Actual vs Predicción (Prophet) [{"Daily" if agg=="daily" else "Hourly"}]', template='plotly_dark', xaxis_title='Fecha', yaxis_title='PM2.5 (µg/m³)', hovermode='x unified', height=600)
    return fig


# --- Figuras de cross-validation (métricas) ---
def make_cv_metric_figures():
    # Preferir usar df_p.csv (performance metrics precomputadas)
    if df_p is not None and not getattr(df_p, 'empty', True):
        d = df_p.copy()
        # Determinar columna de horizon y convertir a horas si es timedelta-like
        if 'horizon' in d.columns:
            try:
                td = pd.to_timedelta(d['horizon'])
                d['h_hours'] = td.dt.total_seconds() / 3600
            except Exception:
                # Si no se pudo parsear, intentar como numérico
                try:
                    d['h_hours'] = d['horizon'].astype(float)
                except Exception:
                    d['h_hours'] = np.arange(len(d))
        elif 'horizon_days' in d.columns:
            try:
                d['h_hours'] = d['horizon_days'].astype(float) * 24
            except Exception:
                d['h_hours'] = np.arange(len(d))
        elif 'h_hours' in d.columns:
            d['h_hours'] = pd.to_numeric(d['h_hours'], errors='coerce').fillna(np.arange(len(d)))
        else:
            d['h_hours'] = np.arange(len(d))

        # Asegurar columnas de métricas
        for col in ['rmse', 'mae', 'mape']:
            if col not in d.columns:
                d[col] = np.nan

        fig_series = go.Figure()
        fig_series.add_trace(go.Scatter(x=d['h_hours'], y=d['rmse'], mode='lines+markers', name='RMSE', line=dict(color='#10b981')))
        fig_series.add_trace(go.Scatter(x=d['h_hours'], y=d['mae'], mode='lines+markers', name='MAE', line=dict(color='#3b82f6')))
        fig_series.add_trace(go.Scatter(x=d['h_hours'], y=d['mape'], mode='lines+markers', name='MAPE', line=dict(color='#f59e0b')))
        fig_series.update_layout(title='Métricas CV por Horizonte', template='plotly_dark', xaxis_title='Horizon (hours)', yaxis_title='Error')

        fig_scatter = px.scatter(d, x='h_hours', y='rmse', title='RMSE vs Horizon', labels={'h_hours': 'Horizon (hours)', 'rmse': 'RMSE'})
        fig_scatter.update_layout(template='plotly_dark')
        return fig_series, fig_scatter

    # Fallback: intentar reconstruir desde df_cv.csv si existe
    if df_cv is None or getattr(df_cv, 'empty', True):
        return px.line(title='No se encontró `df_p.csv` ni `df_cv.csv`'), px.line(title='No se encontró `df_p.csv` ni `df_cv.csv`')

    df = df_cv.copy()
    if all(c in df.columns for c in ['y', 'yhat', 'horizon']):
        try:
            try:
                df['h_hours'] = pd.to_timedelta(df['horizon']).dt.total_seconds() / 3600
            except Exception:
                df['h_hours'] = pd.to_numeric(df['horizon'], errors='coerce').fillna(np.arange(len(df)))

            metrics = df.groupby('h_hours').apply(lambda g: pd.Series({
                'rmse': np.sqrt(((g['y'] - g['yhat']) ** 2).mean()),
                'mae': (g['y'] - g['yhat']).abs().mean(),
                'mape': (g['y'] - g['yhat']).abs().div(g['y'].replace(0, np.nan)).dropna().mean() * 100
            }))
            metrics = metrics.reset_index()

            fig_series = go.Figure()
            fig_series.add_trace(go.Scatter(x=metrics['h_hours'], y=metrics['rmse'], mode='lines+markers', name='RMSE', line=dict(color='#10b981')))
            fig_series.add_trace(go.Scatter(x=metrics['h_hours'], y=metrics['mae'], mode='lines+markers', name='MAE', line=dict(color='#3b82f6')))
            fig_series.add_trace(go.Scatter(x=metrics['h_hours'], y=metrics['mape'], mode='lines+markers', name='MAPE', line=dict(color='#f59e0b')))
            fig_series.update_layout(title='Métricas CV por Horizonte', template='plotly_dark', xaxis_title='Horizon (hours)', yaxis_title='Error')

            fig_scatter = px.scatter(metrics, x='h_hours', y='rmse', title='RMSE vs Horizon', labels={'h_hours': 'Horizon (hours)', 'rmse': 'RMSE'})
            fig_scatter.update_layout(template='plotly_dark')
            return fig_series, fig_scatter
        except Exception as e:
            return px.line(title=f'Error generando métricas CV: {e}'), px.line(title=f'Error generando métricas CV: {e}')

    return px.line(title='df_cv.csv no contiene las columnas esperadas (y, yhat, horizon)'), px.line(title='df_cv.csv no contiene las columnas esperadas (y, yhat, horizon)')


forecast_fig = make_forecast_figure(agg='hourly')
cv_series_fig, cv_scatter_fig = make_cv_metric_figures()



def compute_kpis():
    # Simplified: assume necessary columns exist in df_p or df_cv as requested
    k = {'mse': np.nan, 'rmse': np.nan, 'mape': np.nan, 'smape': np.nan}
    if df_p is not None and not getattr(df_p, 'empty', True):
        d = df_p
        k['mse'] = float(d['mse'].mean())
        k['rmse'] = float(d['rmse'].mean())
        k['mape'] = float(d['mape'].mean())
        k['smape'] = float(d['smape'].mean())
        return k

    # Otherwise compute basic global metrics from df_cv (assume y and yhat present)
    df = df_cv
    errs = df['y'] - df['yhat']
    k['mse'] = float((errs ** 2).mean())
    k['rmse'] = float(np.sqrt((errs ** 2).mean()))
    k['mape'] = float((errs.abs() / df['y']).dropna().mean() * 100)
    k['smape'] = float((2 * errs.abs() / (df['y'].abs() + df['yhat'].abs())).dropna().mean() * 100)
    return k


kpis = compute_kpis()

layout = html.Div([
    html.H2("🔮 Predicciones Prophet - PM2.5", style={'textAlign': 'center', 'marginBottom': 20}),

    # KPI cards
    html.Div([
        html.Div([
            html.H4(f"{kpis['mse']:.2f}" if not np.isnan(kpis['mse']) else "N/A", style={'color': '#ffffff', 'margin': 0}),
            html.P("MSE", style={'margin': 0, 'color': '#94a3b8'})
        ], style={'backgroundColor': '#111827', 'padding': '12px', 'borderRadius': '8px', 'flex': 1, 'margin': '6px', 'textAlign': 'center'}),
        html.Div([
            html.H4(f"{kpis['rmse']:.2f}" if not np.isnan(kpis['rmse']) else "N/A", style={'color': '#ffffff', 'margin': 0}),
            html.P("RMSE", style={'margin': 0, 'color': '#94a3b8'})
        ], style={'backgroundColor': '#111827', 'padding': '12px', 'borderRadius': '8px', 'flex': 1, 'margin': '6px', 'textAlign': 'center'}),
        html.Div([
            html.H4(f"{kpis['mape']:.2f}%" if not np.isnan(kpis['mape']) else "N/A", style={'color': '#ffffff', 'margin': 0}),
            html.P("MAPE", style={'margin': 0, 'color': '#94a3b8'})
        ], style={'backgroundColor': '#111827', 'padding': '12px', 'borderRadius': '8px', 'flex': 1, 'margin': '6px', 'textAlign': 'center'}),
        html.Div([
            html.H4(f"{kpis['smape']:.2f}%" if not np.isnan(kpis['smape']) else "N/A", style={'color': '#ffffff', 'margin': 0}),
            html.P("SMAPE", style={'margin': 0, 'color': '#94a3b8'})
        ], style={'backgroundColor': '#111827', 'padding': '12px', 'borderRadius': '8px', 'flex': 1, 'margin': '6px', 'textAlign': 'center'})
    ], style={'display': 'flex', 'justifyContent': 'space-between', 'marginBottom': 20}),

    # Selector de agregación: hourly o daily
    html.Div([
        html.Label('Agrupar por:', style={'color': '#94a3b8', 'marginRight': '8px'}),
        dcc.RadioItems(
            id='time-agg',
            options=[
                {'label': 'Hourly', 'value': 'hourly'},
                {'label': 'Daily (mean)', 'value': 'daily'}
            ],
            value='hourly',
            labelStyle={'display': 'inline-block', 'marginRight': '12px', 'color': '#ffffff'}
        )
    ], style={'marginBottom': 10}),

    dcc.Graph(figure=forecast_fig, id='prophet-forecast-plot'),
    html.H4("📈 Métricas de Cross-Validation", style={'marginTop': 20}),
    dcc.Graph(figure=cv_series_fig, id='cv-metrics-series'),
    dcc.Graph(figure=cv_scatter_fig, id='cv-rmse-horizon')
], style={'backgroundColor': '#0f1720', 'color': '#ffffff', 'padding': '10px'})


def register_callbacks(app):
    # Callback para actualizar la figura principal según agregación horaria/diaria
    @app.callback(
        Output('prophet-forecast-plot', 'figure'),
        Input('time-agg', 'value')
    )
    def update_forecast_agg(agg_value):
        try:
            return make_forecast_figure(agg=agg_value)
        except Exception as e:
            return px.line(title=f'Error generando figura: {e}')
