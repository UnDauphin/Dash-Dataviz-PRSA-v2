# utils/data_loader.py - Manejo centralizado de datos
import pandas as pd
import numpy as np
from scipy.stats import ks_2samp
from utils.database import load_table, load_data_from_query
import os

# Variables globales para los datasets
df_original = None
df_imputed = None
analysis_cols = []

def initialize_data():
    """Inicializa y carga todos los datos desde PostgreSQL"""
    global df_original, df_imputed, analysis_cols
    try:
        print("📂 Cargando datos desde PostgreSQL...")
        
        # Cargar los datos principales desde la tabla PRSA
        df_original = load_data()
        
        if df_original.empty:
            print("❌ No se pudieron cargar datos desde PostgreSQL")
            return
            
        print(f"✅ Datos cargados. Dimensiones: {df_original.shape}")
        
        # Procesar los datos (el resto del código se mantiene igual)
        df_imputed = impute_dataframe(df_original)
        analysis_cols = get_analysis_columns(df_imputed)
        
        print(f"🔢 Variables de análisis: {len(analysis_cols)}")
        print("🎯 Inicialización completada exitosamente")
        
    except Exception as e:
        print(f"❌ Error durante la inicialización: {str(e)}")
        import traceback
        traceback.print_exc()

def load_data():
    """Cargar y preparar el dataset desde PostgreSQL"""
    df = load_table('prsa_data_dongsi')
    
    if df.empty:
        print("❌ No se pudieron cargar datos desde PostgreSQL")
        return df
    
    # Normalizar nombres de columnas
    df.columns = df.columns.str.strip().str.lower().str.replace('.', '_', regex=False).str.replace(' ', '_', regex=False)
    
    # Construir datetime si existen las columnas temporales
    cols = df.columns
    if set(['year','month','day','hour']).issubset(cols):
        try:
            df['datetime'] = pd.to_datetime(dict(
                year=df['year'].astype(int),
                month=df['month'].astype(int),
                day=df['day'].astype(int),
                hour=df['hour'].astype(int)
            ))
        except Exception:
            # Fallback: intentar combinar como string
            df['datetime'] = pd.to_datetime(
                df[['year','month','day','hour']].astype(str).agg(' '.join, axis=1), 
                errors='coerce'
            )
    else:
        # Si hay columnas de fecha, intentar parsearlas
        date_cols = [c for c in cols if 'date' in c]
        if date_cols:
            df['datetime'] = pd.to_datetime(df[date_cols[0]], errors='coerce')
    
    return df

def get_analysis_columns(df, exclude_datetime_components=True):
    """Retorna columnas para análisis, excluyendo componentes de datetime"""
    base_exclude = ['station', 'no']  # Columnas identificadoras
    
    if exclude_datetime_components:
        datetime_components = ['year', 'month', 'day', 'hour']
        base_exclude.extend(datetime_components)
    
    all_numeric = df.select_dtypes(include=[np.number]).columns.tolist()
    analysis_cols = [col for col in all_numeric if col not in base_exclude]
    
    return analysis_cols

def impute_dataframe(df_in):
    """Aplica imputación inteligente según el tipo de variable"""
    if df_in.empty:
        return df_in
    
    df_out = df_in.copy()
    
    if 'datetime' not in df_out.columns or df_out['datetime'].isna().all():
        print("⚠️  No hay columna datetime válida, usando métodos básicos")
        return impute_fallback(df_out)
    
    df_out = df_out.sort_values('datetime').set_index('datetime')
    
    # ESTRATEGIAS ESPECÍFICAS POR TIPO DE VARIABLE
    if 'pm2_5' in df_out.columns:
        df_out['pm2_5'] = df_out['pm2_5'].interpolate(method='time').ffill().bfill()
    
    if 'pm10' in df_out.columns:
        df_out['pm10'] = df_out['pm10'].interpolate(method='time').ffill().bfill()
    
    # Para gases (SO2, NO2, CO, O3) - interpolación temporal
    gases = ['so2', 'no2', 'co', 'o3']
    for gas in gases:
        if gas in df_out.columns:
            df_out[gas] = df_out[gas].interpolate(method='time').ffill().bfill()
    
    # Variables meteorológicas - estrategias específicas
    if 'temp' in df_out.columns:
        df_out['temp'] = df_out['temp'].interpolate(method='time')
    
    if 'pres' in df_out.columns:
        df_out['pres'] = df_out['pres'].interpolate(method='time')
    
    if 'dewp' in df_out.columns:
        df_out['dewp'] = df_out['dewp'].interpolate(method='time')
    
    if 'wspm' in df_out.columns:
        df_out['wspm'] = df_out['wspm'].fillna(0)
    
    if 'wd' in df_out.columns:
        df_out['wd'] = df_out['wd'].ffill().bfill()
    
    if 'rain' in df_out.columns:
        df_out['rain'] = df_out['rain'].fillna(0)
    
    # Para cualquier otra variable numérica no cubierta
    remaining_numeric = df_out.select_dtypes(include=[np.number]).columns.difference(
        ['pm2_5', 'pm10', 'so2', 'no2', 'co', 'o3', 'temp', 'pres', 'dewp', 'wspm', 'rain']
    )
    for col in remaining_numeric:
        df_out[col] = df_out[col].interpolate(method='time').ffill().bfill()
    
    df_out = df_out.reset_index()
    return df_out

def impute_fallback(df_out):
    """Fallback cuando no hay datetime"""
    if df_out.empty:
        return df_out
        
    numeric_cols = df_out.select_dtypes(include=[np.number]).columns
    
    # Estrategias básicas sin información temporal
    for col in numeric_cols:
        if col in ['rain', 'wspm']:
            df_out[col] = df_out[col].fillna(0)
        elif col == 'wd':
            df_out[col] = df_out[col].ffill().bfill()
        else:
            df_out[col] = df_out[col].fillna(df_out[col].median())
    
    return df_out

def classify_missing_type(col_name, df_obj):
    """Clasifica el tipo de valores faltantes (MCAR, MAR, MNAR)"""
    if df_obj.empty:
        return "Sin datos"
        
    p = df_obj[col_name].isna().mean()
    if p == 0:
        return "Sin faltantes"
    
    numeric = df_obj.select_dtypes(include=[np.number])
    
    if col_name in numeric.columns:
        numeric = numeric.drop(columns=[col_name])
    
    if numeric.shape[1] == 0:
        return "MCAR" if p < 0.2 else "MNAR"
    
    indicator = df_obj[col_name].isna().astype(int)
    cors = numeric.apply(lambda x: indicator.corr(x) if x.notna().any() else np.nan)
    max_abs_corr = cors.abs().max(skipna=True)
    
    if pd.isna(max_abs_corr):
        return "MCAR"
    if max_abs_corr > 0.3:
        return "MAR"
    if p > 0.20:
        return "MNAR"
    return "MCAR"

def get_data():
    """Retorna los datasets para usar en otras páginas"""
    return df_original, df_imputed, analysis_cols

def get_missing_analysis():
    """Análisis de valores faltantes"""
    df_orig, df_imp, _ = get_data()
    
    if df_orig.empty:
        return None, None, None
    
    # Before imputation
    miss_before = df_orig.isna().sum()
    miss_before = miss_before[miss_before > 0].sort_values(ascending=False)
    
    # After imputation
    miss_after = df_imp.isna().sum()
    miss_after = miss_after[miss_after > 0].sort_values(ascending=False)
    
    # Classification types
    types = {col: classify_missing_type(col, df_orig) for col in df_orig.columns if df_orig[col].isna().sum() > 0}
    
    return miss_before, miss_after, types

def get_ks_test_results():
    """Prueba KS para variables que tuvieron NA originalmente"""
    df_orig, df_imp, _ = get_data()
    
    if df_orig.empty:
        return []
    
    had_na = [c for c in df_orig.columns if df_orig[c].isna().sum() > 0 and c in get_analysis_columns(df_orig)]
    ks_rows = []
    
    for c in had_na:
        orig_vals = df_orig[c].dropna().values
        new_vals = df_imp[c].dropna().values
        if len(orig_vals) < 2 or len(new_vals) < 2:
            ks_rows.append((c, np.nan, np.nan, "insuficientes datos"))
            continue
        try:
            stat, p = ks_2samp(orig_vals, new_vals)
            note = "No cambio significativo" if p > 0.05 else "Cambio significativo"
            ks_rows.append((c, float(stat), float(p), note))
        except Exception as e:
            ks_rows.append((c, np.nan, np.nan, f"error: {e}"))
    
    return ks_rows