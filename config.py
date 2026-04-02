# config.py


CONFIGURACION = {


    "visibilidad": {
        "mostrar_servicios": True,      # Casi siempre será True
        "mostrar_equipo": True,         # False para barberos que trabajan solos
        "mostrar_galeria_pelo": True,        # False si aún no tienen fotos pro
        "mostrar_sobre_nosotros": True, # False para un estilo más directo
        "mostrar_ubicacion": True,       # Por si es barbero a domicilio
        "mostrar_galeria_local": True     
    },

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
        "tipo": "minimalista", 
        
        # Interruptores: True para mostrar, False para ocultar
        "mostrar_logo": True,
        "mostrar_nombre": True,
        
        # Configuración para el tipo 'minimalista'
        "color_fondo": "#121212", 
        
        # Configuración para el tipo 'imagen'
        "imagen_fondo": "/static/prueba_fondo.jpg" 
    },

    "galeria_pelo": [
        {"url": "/static/corte1.jpg", "titulo": "Degradado Clásico"},
        {"url": "/static/corte2.jpg", "titulo": "Arreglo de Barba Premium"},
        {"url": "/static/corte3.jpg", "titulo": "Corte Moderno"},
        {"url": "/static/corte4.jpg", "titulo": "Estilo Vikingo"}
    ],
    
"galeria_local": [
        {"url": "/static/salon.jpg", "titulo": "Degradado Clásico"},
        {"url": "/static/maquinilla.jpg", "titulo": "Arreglo de Barba Premium"}
    ],

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

"equipo": [
        {
            "nombre": "RUBÉN",
            "foto": "/static/barbero1.jpg",
            "descripcion": "Especialista en degradados y diseño de barba. 5 años de experiencia dando el mejor servicio.",
            "redes": {
                "instagram": "https://www.instagram.com/juangalleg0o_",
                "tiktok": "https://tiktok.com/@tu_usuario"
            }
        },
        {
            "nombre": "CARLOS",
            "foto": "/static/barbero2.jpg",
            "descripcion": "Maestro en cortes clásicos a tijera. La vieja escuela llevada al siguiente nivel.",
            "redes": {
                "instagram": "https://instagram.com/usuario_carlos"
                # Si Carlos no tiene TikTok, simplemente no se pone esa línea y la web no mostrará el icono
            }
        }
    ],
"MAPA_URL": "https://www.google.com/maps/embed?pb=!1m14!1m12!1m3!1d189.64377181469467!2d-3.3645095897029598!3d40.490740967552114!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!5e0!3m2!1ses!2ses!4v1775146748934!5m2!1ses!2ses", 
"DIRECCION_ESCRITA": "Calle de Ejemplo 123, Código Postal, Ciudad, País",

    "sobre_nosotros": [
        "Somos expertos en barbería clásica y moderna.",
        "Calidad, estilo y un ambiente relajado para que disfrutes de tu momento."
    ],
}