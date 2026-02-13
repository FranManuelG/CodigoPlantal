#!/usr/bin/env python3
"""
Script para migrar datos de SQLite a PostgreSQL (Supabase)
Ejecutar solo una vez después de configurar Supabase
"""

import sqlite3
import os
import sys
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    print("❌ Error: DATABASE_URL no está configurada en el archivo .env")
    print("Por favor, añade la URL de Supabase en el archivo .env")
    sys.exit(1)

try:
    import psycopg2
except ImportError:
    print("❌ Error: psycopg2 no está instalado")
    print("Ejecuta: pip install psycopg2-binary")
    sys.exit(1)

SQLITE_DB = 'plants.db'

if not os.path.exists(SQLITE_DB):
    print(f"❌ Error: No se encuentra el archivo {SQLITE_DB}")
    print("No hay datos para migrar. Puedes empezar a usar Supabase directamente.")
    sys.exit(0)

print("🌱 Iniciando migración de SQLite a PostgreSQL (Supabase)...")
print(f"📂 Origen: {SQLITE_DB}")
print(f"🔗 Destino: Supabase PostgreSQL\n")

sqlite_conn = sqlite3.connect(SQLITE_DB)
sqlite_cursor = sqlite_conn.cursor()

pg_conn = psycopg2.connect(DATABASE_URL)
pg_cursor = pg_conn.cursor()

print("✅ Conexiones establecidas\n")

print("📋 Migrando plantas...")
sqlite_cursor.execute('SELECT id, user_id, name, watering_frequency_days, group_id, photo_file_id, created_at FROM plants')
plants = sqlite_cursor.fetchall()

for plant in plants:
    plant_id, user_id, name, freq, group_id, photo_id, created_at = plant
    pg_cursor.execute('''
        INSERT INTO plants (id, user_id, name, watering_frequency_days, group_id, photo_file_id, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (id) DO NOTHING
    ''', (plant_id, user_id, name, freq, group_id, photo_id, created_at))

print(f"   ✓ {len(plants)} plantas migradas")

print("💧 Migrando historial de riego...")
sqlite_cursor.execute('SELECT id, plant_id, watered_at FROM watering_log')
waterings = sqlite_cursor.fetchall()

for watering in waterings:
    watering_id, plant_id, watered_at = watering
    pg_cursor.execute('''
        INSERT INTO watering_log (id, plant_id, watered_at)
        VALUES (%s, %s, %s)
        ON CONFLICT (id) DO NOTHING
    ''', (watering_id, plant_id, watered_at))

print(f"   ✓ {len(waterings)} registros de riego migrados")

print("📸 Migrando fotos de plantas...")
sqlite_cursor.execute('SELECT id, plant_id, file_id, caption, uploaded_at FROM plant_photos')
photos = sqlite_cursor.fetchall()

for photo in photos:
    photo_id, plant_id, file_id, caption, uploaded_at = photo
    pg_cursor.execute('''
        INSERT INTO plant_photos (id, plant_id, file_id, caption, uploaded_at)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (id) DO NOTHING
    ''', (photo_id, plant_id, file_id, caption, uploaded_at))

print(f"   ✓ {len(photos)} fotos migradas")

print("📁 Migrando grupos de plantas...")
sqlite_cursor.execute('SELECT id, user_id, name, created_at FROM plant_groups')
groups = sqlite_cursor.fetchall()

for group in groups:
    group_id, user_id, name, created_at = group
    pg_cursor.execute('''
        INSERT INTO plant_groups (id, user_id, name, created_at)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (id) DO NOTHING
    ''', (group_id, user_id, name, created_at))

print(f"   ✓ {len(groups)} grupos migrados")

print("⚙️  Migrando configuración de usuarios...")
sqlite_cursor.execute('SELECT user_id, notifications_enabled, notification_time, timezone FROM user_settings')
settings = sqlite_cursor.fetchall()

for setting in settings:
    user_id, notif_enabled, notif_time, timezone = setting
    pg_cursor.execute('''
        INSERT INTO user_settings (user_id, notifications_enabled, notification_time, timezone)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (user_id) DO UPDATE 
        SET notifications_enabled = %s, notification_time = %s, timezone = %s
    ''', (user_id, notif_enabled, notif_time, timezone, notif_enabled, notif_time, timezone))

print(f"   ✓ {len(settings)} configuraciones migradas")

print("\n🔄 Actualizando secuencias de IDs...")
pg_cursor.execute("SELECT setval('plants_id_seq', (SELECT MAX(id) FROM plants))")
pg_cursor.execute("SELECT setval('watering_log_id_seq', (SELECT MAX(id) FROM watering_log))")
pg_cursor.execute("SELECT setval('plant_photos_id_seq', (SELECT MAX(id) FROM plant_photos))")
pg_cursor.execute("SELECT setval('plant_groups_id_seq', (SELECT MAX(id) FROM plant_groups))")
print("   ✓ Secuencias actualizadas")

pg_conn.commit()

sqlite_conn.close()
pg_conn.close()

print("\n✅ ¡Migración completada exitosamente!")
print("\n📊 Resumen:")
print(f"   • {len(plants)} plantas")
print(f"   • {len(waterings)} registros de riego")
print(f"   • {len(photos)} fotos")
print(f"   • {len(groups)} grupos")
print(f"   • {len(settings)} configuraciones de usuario")

print("\n🎉 Ahora puedes:")
print("   1. Verificar los datos en el dashboard de Supabase")
print("   2. Desplegar el bot en Render con la variable DATABASE_URL configurada")
print("   3. Opcionalmente, hacer backup de plants.db y eliminarlo")
