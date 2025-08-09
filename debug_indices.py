import sqlite3
import os

# Cambiar al directorio database
os.chdir('d:/UDC 2025 -1/CHAMBA/interrapidisimo/database')

# Conectar a la base de datos
conn = sqlite3.connect('data.db')
c = conn.cursor()

# Verificar la estructura actual de la tabla
c.execute("PRAGMA table_info(rastreos)")
columns = c.fetchall()

print("Índices y columnas en la tabla rastreos:")
for i, col in enumerate(columns):
    print(f"  Índice {i}: {col[1]} ({col[2]})")

print("\nEjemplo de mapeo en server.py debería ser:")
print("row[0] = id")
for i, col in enumerate(columns[1:], 1):
    print(f"row[{i}] = {col[1]}")

# Obtener un registro de ejemplo
c.execute("SELECT * FROM rastreos LIMIT 1")
row = c.fetchone()
if row:
    print(f"\nEjemplo de datos reales:")
    for i, (col, value) in enumerate(zip(columns, row)):
        print(f"  row[{i}] ({col[1]}): {repr(value)}")

conn.close()
