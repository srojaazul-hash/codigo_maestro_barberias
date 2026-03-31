# app.py
from flask import Flask, render_template
from datetime import datetime, timedelta
from config import CONFIGURACION

app = Flask(__name__)

def calcular_huecos_disponibles(fecha_str: str, barbero: str, duracion_total_minutos: int) -> list:
    """
    Busca huecos libres donde quepa la 'duracion_total_minutos' + cortesía
    sin chocar con otras citas o el horario de cierre.
    """
    # 1. Variables de configuración
    horario = CONFIGURACION["horario"]
    intervalo = CONFIGURACION["intervalo_calendario"]
    cortesia = CONFIGURACION["tiempo_cortesia"]
    formato = "%H:%M"
    
    # El tiempo real que necesitamos bloquear en la agenda
    tiempo_necesario = duracion_total_minutos + cortesia
    
    # (Futura conexión con SQLite) Citas simuladas para que el motor no de error
    citas_ocupadas = [
        {"inicio": "10:00", "fin": "10:30"} 
    ]
    
    # SOLUCIÓN: Declaramos la lista vacía antes de procesar los turnos
    huecos_libres = []
    
    # Función interna para procesar un turno (mañana o tarde)
    def procesar_turno(hora_apertura, hora_cierre):
        if not hora_apertura or not hora_cierre:
            return
            
        inicio_turno = datetime.strptime(hora_apertura, formato)
        fin_turno = datetime.strptime(hora_cierre, formato)
        
        hora_actual = inicio_turno
        
        # Mientras el bloque de tiempo no supere el cierre
        while hora_actual + timedelta(minutes=tiempo_necesario) <= fin_turno:
            hora_fin_estimada = hora_actual + timedelta(minutes=tiempo_necesario)
            
            solapamiento = False
            
            # Comprobamos si choca con alguna cita ya reservada
            for cita in citas_ocupadas:
                cita_inicio = datetime.strptime(cita["inicio"], formato)
                cita_fin = datetime.strptime(cita["fin"], formato)
                
                if hora_actual < cita_fin and hora_fin_estimada > cita_inicio:
                    solapamiento = True
                    break
            
            # Si no hay solapamiento, guardamos la hora en la lista
            if not solapamiento:
                huecos_libres.append(hora_actual.strftime(formato))
                
            # Avanzamos el reloj según el intervalo elegido (ej: 15 min)
            hora_actual += timedelta(minutes=intervalo)

    # 2. Ejecutamos el cálculo para mañana y tarde
    procesar_turno(horario["apertura_manana"], horario["cierre_manana"])
    procesar_turno(horario["apertura_tarde"], horario["cierre_tarde"])
    
    return huecos_libres

@app.route('/')
def inicio():
    # Enviamos los datos de configuración al HTML para que pinte los servicios
    return render_template('index.html', config=CONFIGURACION)

if __name__ == '__main__':
    app.run(debug=True)