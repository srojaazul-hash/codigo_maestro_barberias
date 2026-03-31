# base_datos.py
import sqlite3

DB_NAME = "reservas_cliente.db"

def inicializar_db():
    # Se conecta al archivo (si no existe, lo crea automáticamente)
    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()

    # Tabla 1: Citas de clientes (Actualizada con duración y servicios)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS citas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_nombre TEXT NOT NULL,
            cliente_telefono TEXT NOT NULL,
            barbero TEXT NOT NULL,
            fecha TEXT NOT NULL,       -- Formato YYYY-MM-DD
            hora_inicio TEXT NOT NULL, -- Formato HH:MM
            hora_fin TEXT NOT NULL,    -- Fin exacto calculado por Python
            servicios_json TEXT NOT NULL, -- Lista de servicios adquiridos
            precio_total REAL NOT NULL,   -- Suma del carrito
            estado TEXT DEFAULT 'confirmada'
        )
    """)

    # Tabla 2: Bloqueos manuales del dueño (PWA)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bloqueos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            barbero TEXT NOT NULL,
            fecha TEXT NOT NULL,       -- Formato YYYY-MM-DD
            hora_inicio TEXT,          -- Si es NULL, bloquea el día entero
            hora_fin TEXT,
            motivo TEXT
        )
    """)

    conexion.commit()
    conexion.close()
    print(f"Base de datos '{DB_NAME}' inicializada con la nueva estructura de citas.")

if __name__ == '__main__':
    inicializar_db()