# utils/database.py
import pandas as pd
from sqlalchemy import create_engine
import os

def get_db_connection():
    """Obtener conexión a PostgreSQL"""
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL no está configurada")
    
    engine = create_engine(DATABASE_URL)
    return engine

def load_table(table_name):
    """Cargar una tabla completa desde PostgreSQL"""
    engine = get_db_connection()
    try:
        df = pd.read_sql_table(table_name, engine)
        return df
    except Exception as e:
        print(f"Error cargando tabla {table_name}: {e}")
        return pd.DataFrame()

def load_data_from_query(query):
    """Ejecutar una consulta SQL y retornar DataFrame"""
    engine = get_db_connection()
    try:
        df = pd.read_sql(query, engine)
        return df
    except Exception as e:
        print(f"Error ejecutando query: {e}")
        return pd.DataFrame()