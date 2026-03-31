# app.py
from flask import Flask, render_template, request, jsonify
from datetime import datetime, timedelta
import sqlite3
from config import CONFIGURACION

app = Flask(__name__)

def obtener_conexion():
    conn = sqlite3.connect('reservas_cliente.db')
    conn.row_factory = sqlite3.Row # Permite acceder a columnas por nombre
    return conn

def calcular_huecos_disponibles(fecha_str: str, barbero: str, duracion_total_minutos: int) -> list:
    horario = CONFIGURACION["horario"]
    intervalo = CONFIGURACION["intervalo_calendario"]
    cortesia = CONFIGURACION["tiempo_cortesia"]
    formato = "%H:%M"
    
    tiempo_necesario = duracion_total_minutos + cortesia
    
    # CONEXIÓN REAL: Buscamos citas existentes para ese barbero y fecha
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT hora_inicio, hora_fin FROM citas WHERE fecha = ? AND barbero = ? AND estado != 'cancelada'", (fecha_str, barbero))
    citas_reales = cursor.fetchall()
    conn.close()

    huecos_libres = []

    def procesar_turno(hora_apertura, hora_cierre):
        if not hora_apertura or not hora_cierre: return
        inicio_turno = datetime.strptime(hora_apertura, formato)
        fin_turno = datetime.strptime(hora_cierre, formato)
        hora_actual = inicio_turno

        while hora_actual + timedelta(minutes=tiempo_necesario) <= fin_turno:
            hora_fin_estimada = hora_actual + timedelta(minutes=tiempo_necesario)
            solapamiento = False
            
            for cita in citas_reales:
                c_ini = datetime.strptime(cita["hora_inicio"], formato)
                c_fin = datetime.strptime(cita["hora_fin"], formato)
                if hora_actual < c_fin and hora_fin_estimada > c_ini:
                    solapamiento = True
                    break
            
            if not solapamiento:
                huecos_libres.append(hora_actual.strftime(formato))
            hora_actual += timedelta(minutes=intervalo)

    procesar_turno(horario["apertura_manana"], horario["cierre_manana"])
    procesar_turno(horario["apertura_tarde"], horario["cierre_tarde"])
    return huecos_libres

@app.route('/')
def inicio():
    return render_template('index.html', config=CONFIGURACION)

# RUTA 1: Buscar horas libres (se llama vía JavaScript)
@app.route('/obtener_horas', methods=['POST'])
def obtener_horas():
    datos = request.json
    horas = calcular_huecos_disponibles(datos['fecha'], datos['barbero'], int(datos['duracion']))
    return jsonify({"horas": horas})

# RUTA 2: Guardar la reserva final
@app.route('/reservar', methods=['POST'])
def reservar():
    d = request.json
    # Calculamos hora_fin para la base de datos
    inicio = datetime.strptime(d['hora_inicio'], "%H:%M")
    fin = inicio + timedelta(minutes=int(d['duracion']) + CONFIGURACION["tiempo_cortesia"])
    hora_fin_str = fin.strftime("%H:%M")

    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO citas (cliente_nombre, cliente_telefono, barbero, fecha, hora_inicio, hora_fin, servicios_json, precio_total)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (d['nombre'], d['telefono'], d['barbero'], d['fecha'], d['hora_inicio'], hora_fin_str, d['servicios'], d['precio']))
        conn.commit()
        conn.close()
        return jsonify({"status": "ok", "mensaje": "Reserva confirmada"})
    except Exception as e:
        return jsonify({"status": "error", "mensaje": str(e)})

if __name__ == '__main__':
    app.run(debug=True)