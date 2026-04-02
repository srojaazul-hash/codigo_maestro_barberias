# config.py

CONFIGURACION = {
    "nombre_negocio": "Barbería Premium",
    
    # --- NUEVO BLOQUE DE ESTÉTICA ---
    "estetica": {
        "color_marca": "#c4a161",
        "bg_app": "#050505",
        "card_bg": "#1a1a1a",
        "texto_principal": "#f7f1e1",
        "texto_secundario": "#a69c8a",
        "logo_url": "/static/cilindro_barberia.png"
    },

    # --- CONFIGURACIÓN DE LA PORTADA (PRIMERA IMPRESIÓN) ---
    "PORTADA": {
        # Elige 'minimalista' (opción 2.1) o 'imagen' (opción 2.2)
        "tipo": "imagen", 
        
        # Interruptores: True para mostrar, False para ocultar
        "mostrar_logo": False,
        "mostrar_nombre": True,
        
        # Configuración para el tipo 'minimalista'
        "color_fondo": "#121212", 
        
        # Configuración para el tipo 'imagen'
        "imagen_fondo": "/static/prueba_fondo.jpg" 
    },
    
    # 3. BLOQUE SERVICIOS
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

    "direccion": "Calle Falsa 123, Tu Ciudad",
    "sobre_nosotros": [
        "Somos expertos en barbería clásica y moderna.",
        "Calidad, estilo y un ambiente relajado para que disfrutes de tu momento."
    ],
}