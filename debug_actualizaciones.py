import sqlite3
import os

# Cambiar al directorio database
os.chdir('d:/UDC 2025 -1/CHAMBA/interrapidisimo/database')

# Conectar a la base de datos
conn = sqlite3.connect('data.db')
c = conn.cursor()

# Verificar los datos existentes y el campo actualizaciones
c.execute("SELECT numero_guia, actualizaciones FROM rastreos LIMIT 10")
rows = c.fetchall()

print("Datos de actualizaciones en la base de datos:")
for i, row in enumerate(rows):
    guia = row[0]
    actualizaciones = row[1]
    print(f"\nRegistro {i+1}:")
    print(f"  Guía: {guia}")
    print(f"  Actualizaciones (raw): {repr(actualizaciones)}")
    print(f"  Tipo: {type(actualizaciones)}")
    
    # Intentar parsear JSON
    if actualizaciones:
        try:
            import json
            parsed = json.loads(actualizaciones)
            print(f"  JSON parseado: {parsed}")
            print(f"  Tipo parseado: {type(parsed)}")
        except Exception as e:
            print(f"  Error al parsear JSON: {e}")
    else:
        print(f"  Actualizaciones está vacío o es None")

conn.close()
