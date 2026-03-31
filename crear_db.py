import sqlite3

conn = sqlite3.connect('reservas_cliente.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS citas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente_nombre TEXT NOT NULL,
        cliente_telefono TEXT NOT NULL,
        cliente_email TEXT,
        barbero TEXT NOT NULL,
        fecha TEXT NOT NULL,
        hora_inicio TEXT NOT NULL,
        hora_fin TEXT NOT NULL,
        servicios_json TEXT,
        precio_total TEXT
    )
''')

conn.commit()
conn.close()
print("Base de datos creada con éxito. Ya puedes arrancar la app.")