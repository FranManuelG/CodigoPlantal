#!/usr/bin/env python3
"""
Script de migración para añadir tipos de planta y ajuste estacional
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

if DATABASE_URL:
    import psycopg2
    
    print("Conectando a PostgreSQL...")
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    print("Añadiendo columnas a la tabla plants...")
    
    # Añadir columna plant_type
    try:
        cursor.execute("""
            ALTER TABLE plants 
            ADD COLUMN IF NOT EXISTS plant_type TEXT DEFAULT 'moderada'
        """)
        print("✓ Columna plant_type añadida")
    except Exception as e:
        print(f"⚠ plant_type: {e}")
    
    # Añadir columna seasonal_adjustment
    try:
        cursor.execute("""
            ALTER TABLE plants 
            ADD COLUMN IF NOT EXISTS seasonal_adjustment BOOLEAN DEFAULT TRUE
        """)
        print("✓ Columna seasonal_adjustment añadida")
    except Exception as e:
        print(f"⚠ seasonal_adjustment: {e}")
    
    # Añadir columna custom_dryness_level (para tipo personalizado)
    try:
        cursor.execute("""
            ALTER TABLE plants 
            ADD COLUMN IF NOT EXISTS custom_dryness_level INTEGER DEFAULT 50
        """)
        print("✓ Columna custom_dryness_level añadida")
    except Exception as e:
        print(f"⚠ custom_dryness_level: {e}")
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print("\n✅ Migración completada exitosamente!")
    
else:
    import sqlite3
    
    print("Conectando a SQLite...")
    conn = sqlite3.connect('plants.db')
    cursor = conn.cursor()
    
    print("Añadiendo columnas a la tabla plants...")
    
    # Verificar qué columnas existen
    cursor.execute("PRAGMA table_info(plants)")
    existing_columns = [col[1] for col in cursor.fetchall()]
    
    # Añadir plant_type si no existe
    if 'plant_type' not in existing_columns:
        cursor.execute("""
            ALTER TABLE plants 
            ADD COLUMN plant_type TEXT DEFAULT 'moderada'
        """)
        print("✓ Columna plant_type añadida")
    else:
        print("⚠ plant_type ya existe")
    
    # Añadir seasonal_adjustment si no existe
    if 'seasonal_adjustment' not in existing_columns:
        cursor.execute("""
            ALTER TABLE plants 
            ADD COLUMN seasonal_adjustment INTEGER DEFAULT 1
        """)
        print("✓ Columna seasonal_adjustment añadida")
    else:
        print("⚠ seasonal_adjustment ya existe")
    
    # Añadir custom_dryness_level si no existe
    if 'custom_dryness_level' not in existing_columns:
        cursor.execute("""
            ALTER TABLE plants 
            ADD COLUMN custom_dryness_level INTEGER DEFAULT 50
        """)
        print("✓ Columna custom_dryness_level añadida")
    else:
        print("⚠ custom_dryness_level ya existe")
    
    conn.commit()
    conn.close()
    
    print("\n✅ Migración completada exitosamente!")
