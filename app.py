from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from datetime import datetime, timedelta
import sqlite3
from config import CONFIGURACION
from functools import wraps
import smtplib
from email.message import EmailMessage
import urllib.request
import urllib.parse

app = Flask(__name__)

# Obligatorio para usar sesiones en Flask. Cambia esto por una cadena aleatoria en producción.
app.secret_key = 'super_clave_secreta_barberia_2026'

def enviar_correo_cliente(destinatario, nombre, fecha, hora):
    remitente = "tu_correo@gmail.com" # Ya cambiaremos esto por tu correo real
    password = "tu_contraseña_de_aplicacion" # Ya cambiaremos esto luego
    
    msg = EmailMessage()
    msg.set_content(f"Hola {nombre},\n\nTu reserva en la barbería está confirmada.\n\n📅 Fecha: {fecha}\n⏰ Hora: {hora}\n\n¡Te esperamos!")
    msg['Subject'] = 'Confirmación de tu reserva'
    msg['From'] = remitente
    msg['To'] = destinatario

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(remitente, password)
        server.send_message(msg)
        server.quit()
        print("Correo enviado correctamente al cliente.")
    except Exception as e:
        print(f"Error enviando el correo: {e}")

def enviar_telegram_barbero(nombre, fecha, hora, servicios):
    # Tendrás que rellenar estos dos datos más adelante
    bot_token = '8520598678:AAHssHWMKlJBo8XOuzxMOy1nJuxPJb1hUC4' 
    chat_id = '1911923919'
    
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
        
        # Disparamos el correo si el cliente nos ha dejado uno
        if 'email' in d and d['email'] != '':
            enviar_correo_cliente(d['email'], d['nombre'], d['fecha'], d['hora_inicio'])
            # Disparamos el aviso al móvil del barbero
        enviar_telegram_barbero(d['nombre'], d['fecha'], d['hora_inicio'], d['servicios'])

        return jsonify({"status": "ok", "mensaje": "Reserva confirmada"})
    except Exception as e:
        return jsonify({"status": "error", "mensaje": str(e)})

@app.route('/admin')
@login_required
def admin():
    hoy = datetime.now().strftime('%Y-%m-%d')
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM citas WHERE fecha = ? ORDER BY hora_inicio ASC", (hoy,))
    citas_hoy = cursor.fetchall()
    conn.close()
    return render_template('admin.html', citas=citas_hoy, fecha=hoy, config=CONFIGURACION)

# --- ARRANQUE DEL SERVIDOR (SIEMPRE AL FINAL) ---
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)