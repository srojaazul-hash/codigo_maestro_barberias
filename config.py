# config.py

CONFIGURACION = {
    "nombre_negocio": "Barberia Ejemplo",
    "color_principal": "#1a1a1a",
    
    "servicios": {
        "Corte clásico": {"duracion": 30, "precio": 12},
        "Degradado (Fade)": {"duracion": 45, "precio": 14},
        "Arreglo de barba": {"duracion": 20, "precio": 8},
        "Cejas": {"duracion": 10, "precio": 3},
        "Masaje Facial": {"duracion": 15, "precio": 10}
    },
    
    # Tiempo extra de limpieza/descanso tras cada servicio (en minutos)
    "tiempo_cortesia": 0, 
    
    # Flexibilidad del calendario (5, 10, 15...)
    "intervalo_calendario": 15, 
    
    "horario": {
        "apertura_manana": "10:00",
        "cierre_manana": "14:00",
        "apertura_tarde": "16:00",
        "cierre_tarde": "20:00"
    },
    
    "barberos": ["Armando", "Lujan", "Ruben"],
    "activar_eleccion_barbero": True, 
    "telefono_bizum": "+34600000000",
    "admin_password": "admin123", # Dile al cliente que la cambie luego
}
# Modifica solo los valores de este diccionario para cada cliente nuevo.
