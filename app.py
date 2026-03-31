from flask import Flask, render_template, request, jsonify
from datetime import datetime, timedelta
import sqlite3
from config import CONFIGURACION

app = Flask(__name__)

# --- FUNCIONES DE APOYO ---
def obtener_conexion():
    conn = sqlite3.connect('reservas_cliente.db')
    conn.row_factory = sqlite3.Row
    return conn

def calcular_huecos_disponibles(fecha_str: str, barbero: str, duracion_total_minutos: int) -> list:
    horario = CONFIGURACION["horario"]
    intervalo = CONFIGURACION["intervalo_calendario"]
    cortesia = CONFIGURACION["tiempo_cortesia"]
    formato = "%H:%M"
    
    tiempo_necesario = duracion_total_minutos + cortesia
    
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

# --- RUTAS DE LA WEB ---

@app.route('/')
def inicio():
    return render_template('index.html', config=CONFIGURACION)

@app.route('/obtener_horas', methods=['POST'])
def obtener_horas():
    datos = request.json
    horas = calcular_huecos_disponibles(datos['fecha'], datos['barbero'], int(datos['duracion']))
    return jsonify({"horas": horas})

@app.route('/reservar', methods=['POST'])
def reservar():
    d = request.json
    try:
        inicio_dt = datetime.strptime(d['hora_inicio'], "%H:%M")
        fin_dt = inicio_dt + timedelta(minutes=int(d['duracion']) + CONFIGURACION["tiempo_cortesia"])
        hora_fin_str = fin_dt.strftime("%H:%M")

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

@app.route('/admin')
def admin():
    password_query = request.args.get('pass')
    if password_query != CONFIGURACION["admin_password"]:
        return "Acceso denegado. Contraseña incorrecta.", 403
        
    hoy = datetime.now().strftime('%Y-%m-%d')
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM citas WHERE fecha = ? ORDER BY hora_inicio ASC", (hoy,))
    citas_hoy = cursor.fetchall()
    conn.close()
    return render_template('admin.html', citas=citas_hoy, fecha=hoy, config=CONFIGURACION)

# --- ARRANQUE DEL SERVIDOR (SIEMPRE AL FINAL) ---
if __name__ == '__main__':
    app.run(debug=True)