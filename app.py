from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from datetime import datetime, timedelta
import sqlite3
from config import CONFIGURACION
import os
from dotenv import load_dotenv
from functools import wraps
import urllib.request
import urllib.parse

load_dotenv() # Carga las variables del archivo .env
app = Flask(__name__)

# Obligatorio para usar sesiones en Flask. Cambia esto por una cadena aleatoria en producción.
app.secret_key = 'super_clave_secreta_barberia_2026'

def enviar_telegram_barbero(nombre, fecha, hora, servicios):
    # Tendrás que rellenar estos dos datos más adelante
    bot_token = os.getenv("TELEGRAM_TOKEN") 
    chat_id = os.getenv("TELEGRAM_ID")
    
    mensaje = f"💈 ¡NUEVA RESERVA!\n\n👤 Cliente: {nombre}\n📅 Fecha: {fecha}\n⏰ Hora: {hora}\n✂️ Servicios: {servicios}"
    
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = urllib.parse.urlencode({'chat_id': chat_id, 'text': mensaje}).encode('utf-8')
    
    try:
        urllib.request.urlopen(url, data=data)
        print("Aviso enviado por Telegram al barbero.")
    except Exception as e:
        print(f"Error enviando Telegram: {e}")

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
    cursor.execute("SELECT hora_inicio, hora_fin FROM citas WHERE fecha = ? AND barbero = ?", (fecha_str, barbero))
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

# --- DECORADOR DE SEGURIDAD ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# --- RUTAS DE AUTENTICACIÓN ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == CONFIGURACION["admin_password"]:
            session['admin_logged_in'] = True
            return redirect(url_for('admin'))
        else:
            return "Contraseña incorrecta", 401
    
    return '''
        <!DOCTYPE html>
        <html>
        <head>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Login Admin</title>
        </head>
        <body style="display:flex; justify-content:center; align-items:center; height:100vh; font-family:sans-serif;">
            <form method="post" style="display:flex; flex-direction:column; gap:10px; padding:20px; border:1px solid #ccc; border-radius:8px;">
                <h3>Acceso Barbería</h3>
                <input type="password" name="password" placeholder="Contraseña" required style="padding:10px;">
                <button type="submit" style="padding:10px; background:black; color:white; border:none; border-radius:4px; cursor:pointer;">Entrar</button>
            </form>
        </body>
        </html>
    '''

@app.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('login'))

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
            INSERT INTO citas (cliente_nombre, cliente_telefono, cliente_email, barbero, fecha, hora_inicio, hora_fin, servicios_json, precio_total)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (d['nombre'], d['telefono'], d.get('email', ''), d['barbero'], d['fecha'], d['hora_inicio'], hora_fin_str, d['servicios'], d['precio']))
        conn.commit()
        conn.close()
        
            # Disparamos el aviso al móvil del barbero
        enviar_telegram_barbero(d['nombre'], d['fecha'], d['hora_inicio'], d['servicios'])

        return jsonify({"status": "ok", "mensaje": "Reserva confirmada"})
    except Exception as e:
        return jsonify({"status": "error", "mensaje": str(e)})

@app.route('/admin')
@login_required
def admin():
    fecha_seleccionada = request.args.get('fecha', datetime.now().strftime('%Y-%m-%d'))
    barbero_seleccionado = request.args.get('barbero', 'Todos')
    
    conn = obtener_conexion()
    cursor = conn.cursor()
    
    if barbero_seleccionado == 'Todos':
        cursor.execute("SELECT * FROM citas WHERE fecha = ? ORDER BY hora_inicio ASC", (fecha_seleccionada,))
    else:
        cursor.execute("SELECT * FROM citas WHERE fecha = ? AND barbero = ? ORDER BY hora_inicio ASC", (fecha_seleccionada, barbero_seleccionado))
        
    citas_hoy = cursor.fetchall()
    conn.close()
    
    return render_template('admin.html', citas=citas_hoy, fecha=fecha_seleccionada, barbero_seleccionado=barbero_seleccionado, config=CONFIGURACION)

@app.route('/cancelar/<int:id>', methods=['POST'])
@login_required
def cancelar_cita(id):
    fecha_actual = request.form.get('fecha_actual')
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM citas WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    # Recargamos la misma fecha que el barbero estaba mirando
    return redirect(url_for('admin', fecha=fecha_actual))

@app.route('/admin_reservar', methods=['POST'])
@login_required
def admin_reservar():
    nombre = request.form.get('nombre')
    telefono = request.form.get('telefono', '')
    if not telefono:
        telefono = "ADMIN"
    fecha = request.form.get('fecha')
    hora_inicio = request.form.get('hora_inicio')
    duracion = int(request.form.get('duracion', 30))
    barbero = request.form.get('barbero')
    # Capturamos los servicios reales, si no hay, ponemos "Manual"
    servicios = request.form.get('servicios', 'Reserva Manual') 
    
    inicio_dt = datetime.strptime(hora_inicio, "%H:%M")
    fin_dt = inicio_dt + timedelta(minutes=duracion)
    hora_fin_str = fin_dt.strftime("%H:%M")

    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO citas (cliente_nombre, cliente_telefono, cliente_email, barbero, fecha, hora_inicio, hora_fin, servicios_json, precio_total)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (nombre, telefono, "", barbero, fecha, hora_inicio, hora_fin_str, servicios, "0"))
    conn.commit()
    conn.close()
    
    return redirect(url_for('admin', fecha=fecha))

@app.route('/api/estado_mes')
def estado_mes():
    import calendar
    anio = int(request.args.get('anio'))
    mes = int(request.args.get('mes'))
    barbero_seleccionado = request.args.get('barbero', 'Todos')

    # 1. Calculamos los minutos totales de trabajo de un día normal
    fmt = '%H:%M'
    ap_m = datetime.strptime(CONFIGURACION['horario']['apertura_manana'], fmt)
    ci_m = datetime.strptime(CONFIGURACION['horario']['cierre_manana'], fmt)
    ap_t = datetime.strptime(CONFIGURACION['horario']['apertura_tarde'], fmt)
    ci_t = datetime.strptime(CONFIGURACION['horario']['cierre_tarde'], fmt)

    minutos_jornada = ((ci_m - ap_m).seconds + (ci_t - ap_t).seconds) / 60
    if barbero_seleccionado == 'Todos':
        minutos_jornada *= len(CONFIGURACION['barberos'])

    # 2. Buscamos todas las citas de ese mes de golpe
    mes_str = f"{anio}-{mes:02d}-"
    conn = obtener_conexion()
    cursor = conn.cursor()
    if barbero_seleccionado == 'Todos':
        cursor.execute("SELECT fecha, hora_inicio, hora_fin FROM citas WHERE fecha LIKE ?", (f"{mes_str}%",))
    else:
        cursor.execute("SELECT fecha, hora_inicio, hora_fin FROM citas WHERE fecha LIKE ? AND barbero = ?", (f"{mes_str}%", barbero_seleccionado))
    citas_mes = cursor.fetchall()
    conn.close()

    # 3. Sumamos los minutos ocupados de cada día
    ocupacion_por_dia = {}
    for cita in citas_mes:
        fecha_cita = cita['fecha']
        try:
            h_in = datetime.strptime(cita['hora_inicio'], fmt)
            h_out = datetime.strptime(cita['hora_fin'], fmt)
            minutos_ocupados = (h_out - h_in).seconds / 60
            
            if fecha_cita not in ocupacion_por_dia:
                ocupacion_por_dia[fecha_cita] = 0
            ocupacion_por_dia[fecha_cita] += minutos_ocupados
        except:
            pass 

    # 4. Asignamos el color matemático
    _, num_dias = calendar.monthrange(anio, mes)
    resultado = {}

    for dia in range(1, num_dias + 1):
        fecha_str = f"{anio}-{mes:02d}-{dia:02d}"
        min_ocupados = ocupacion_por_dia.get(fecha_str, 0)
        
        porcentaje_libre = ((minutos_jornada - min_ocupados) / minutos_jornada) * 100

        if porcentaje_libre > 50:
            resultado[fecha_str] = "verde"
        elif porcentaje_libre > 0:
            resultado[fecha_str] = "amarillo"
        else:
            resultado[fecha_str] = "rojo"

    return jsonify(resultado)

@app.route('/admin_bloquear', methods=['POST'])
@login_required
def admin_bloquear():
    barbero = request.form.get('barbero')
    concepto = request.form.get('concepto')
    fecha_inicio_str = request.form.get('fecha_inicio')
    fecha_fin_str = request.form.get('fecha_fin')
    hora_inicio = request.form.get('hora_inicio')
    hora_fin = request.form.get('hora_fin')

    # Convertimos los textos de fecha a objetos matemáticos de Python
    fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date()
    fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d').date()

    conn = obtener_conexion()
    cursor = conn.cursor()

    # Bucle: Mientras la fecha que estamos procesando sea menor o igual a la fecha final
    delta = timedelta(days=1)
    fecha_actual = fecha_inicio
    
    while fecha_actual <= fecha_fin:
        cursor.execute("""
            INSERT INTO citas (cliente_nombre, cliente_telefono, cliente_email, barbero, fecha, hora_inicio, hora_fin, servicios_json, precio_total)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (concepto, "ADMIN_BLOCK", "", barbero, fecha_actual.strftime('%Y-%m-%d'), hora_inicio, hora_fin, "Bloqueo de agenda", "0"))
        
        fecha_actual += delta # Avanzamos un día en el calendario

    conn.commit()
    conn.close()

    # Devolvemos al admin al día en el que empezó el bloqueo
    return redirect(url_for('admin', fecha=fecha_inicio_str))

# --- ARRANQUE DEL SERVIDOR (SIEMPRE AL FINAL) ---
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)