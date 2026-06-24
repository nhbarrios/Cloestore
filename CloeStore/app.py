import streamlit as st
import urllib.parse
import json
import os
import requests
import base64

# ==========================================
# CONFIGURACIÓN GENERAL Y APIS
# ==========================================
# 🔒 Estos valores ya NO están escritos aquí. Se leen desde Secrets (ver secrets.toml)
IMGBB_API_KEY = st.secrets.get("IMGBB_API_KEY", "")
CLAVE_ADMIN = st.secrets.get("CLAVE_ADMIN", "")

# 🗄️ Base de datos en la nube (JSONBin.io) — así tus datos NO se borran al reiniciarse el servidor
JSONBIN_API_KEY = st.secrets.get("JSONBIN_API_KEY", "")
JSONBIN_BIN_ID = st.secrets.get("JSONBIN_BIN_ID", "")
JSONBIN_URL = f"https://api.jsonbin.io/v3/b/{JSONBIN_BIN_ID}"

# 🛠️ Valores por defecto (se usan solo la primera vez, luego todo se edita desde el panel admin)
LOGO_URL_DEFAULT = "https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=150"

DEFAULT_DATA = {
    "logo_url": LOGO_URL_DEFAULT,
    "config": {
        "nombre_tienda": "El Mundo de Cloe",
        "eslogan": "Tu Tienda Virtual de Confianza",
        "numero_whatsapp": "50588325774",
        "ubicacion": "Isla de Ometepe, Nicaragua",
        "horario": "Lunes a Sábado: 8 AM - 6 PM",
        "envios": "Entregas locales garantizadas",
        "facebook": "",
        "tiktok": "",
        "instagram": "",
        "x": "",
        "correo": ""
    },
    "secciones": {},
    "lista_productos": []
}

def cargar_datos():
    if not JSONBIN_API_KEY or not JSONBIN_BIN_ID:
        st.error("⚠️ Falta configurar JSONBIN_API_KEY y JSONBIN_BIN_ID en Secrets. Revisa la guía de configuración que te dieron.")
        st.stop()

    try:
        res = requests.get(f"{JSONBIN_URL}/latest", headers={"X-Master-Key": JSONBIN_API_KEY}, timeout=10)
        datos = res.json().get("record", {}) if res.status_code == 200 else {}
    except Exception as e:
        st.error(f"⚠️ No se pudo conectar con la base de datos en la nube: {e}")
        st.stop()

    # Si faltan llaves (primera vez, o un bin vacío) se completan con los valores por defecto
    cambios_pendientes = False
    if "logo_url" not in datos:
        datos["logo_url"] = LOGO_URL_DEFAULT
        cambios_pendientes = True
    if "config" not in datos:
        datos["config"] = DEFAULT_DATA["config"].copy()
        cambios_pendientes = True
    else:
        for llave, valor in DEFAULT_DATA["config"].items():
            if llave not in datos["config"]:
                datos["config"][llave] = valor
                cambios_pendientes = True
    if "secciones" not in datos:
        datos["secciones"] = {}
        cambios_pendientes = True
    if "lista_productos" not in datos:
        datos["lista_productos"] = []
        cambios_pendientes = True

    if cambios_pendientes:
        guardar_datos(datos)

    return datos

def guardar_datos(datos):
    try:
        requests.put(
            JSONBIN_URL,
            json=datos,
            headers={"X-Master-Key": JSONBIN_API_KEY, "Content-Type": "application/json"},
            timeout=10
        )
    except Exception as e:
        st.error(f"⚠️ No se pudieron guardar los cambios en la nube: {e}")

def subir_imagen_a_nube(file_buffer):
    """Sube la imagen a ImgBB y devuelve la URL pública permanente."""
    if not IMGBB_API_KEY:
        st.error("❌ Error: No se ha detectado la clave de la API.")
        return None
    try:
        url = "https://api.imgbb.com/1/upload"
        file_buffer.seek(0)
        b64_image = base64.b64encode(file_buffer.read()).decode('utf-8')
        payload = {
            "key": IMGBB_API_KEY,
            "image": b64_image
        }
        res = requests.post(url, data=payload)
        res_json = res.json()
        if res.status_code == 200 and res_json.get("success"):
            return res_json["data"]["url"]
        else:
            mensaje_error = res_json.get("error", {}).get("message", "Error desconocido al subir la imagen.")
            st.error(f"Error de ImgBB: {mensaje_error}")
            return None
    except Exception as e:
        st.error(f"Error de conexión al subir imagen: {e}")
        return None

def nombre_sugerido_desde_archivo(filename):
    """Convierte 'blusa_rosada_01.jpg' en 'Blusa Rosada 01' como sugerencia de nombre."""
    nombre = os.path.splitext(filename)[0]
    nombre = nombre.replace("_", " ").replace("-", " ")
    return nombre.strip().title()

# ==========================================
# 🎨 IDENTIDAD VISUAL "EL MUNDO DE CLOE"
# Paleta tomada directamente del logo: turquesa, coral, amarillo sol y lavanda sobre crema.
# ==========================================
COLOR_CREMA = "#FBF6EC"
COLOR_TURQUESA = "#2EC4C0"
COLOR_CORAL = "#F2607D"
COLOR_AMARILLO = "#FFC93C"
COLOR_LAVANDA = "#B79FD1"
COLOR_CACAO = "#4A3B31"
PALETA_SECCIONES = [COLOR_TURQUESA, COLOR_CORAL, COLOR_AMARILLO, COLOR_LAVANDA]

def inyectar_estilos():
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Baloo+2:wght@500;600;700;800&family=Nunito:wght@400;600;700;800&display=swap');

    html, body, [class*="css"], .stMarkdown, p, span, label {{
        font-family: 'Nunito', sans-serif;
    }}

    h1, h2, h3, h4 {{
        font-family: 'Baloo 2', cursive !important;
        color: {COLOR_CACAO} !important;
    }}

    [data-testid="stAppViewContainer"] {{
        background-color: {COLOR_CREMA};
    }}

    [data-testid="stImage"] img {{
        border-radius: 16px;
    }}

    div[data-testid="stVerticalBlockBorderWrapper"] {{
        border-radius: 22px !important;
        border: 2px solid {COLOR_TURQUESA} !important;
        background-color: #FFFFFF !important;
        box-shadow: 0px 4px 10px rgba(46,196,192,0.15);
    }}

    .stButton > button, .stFormSubmitButton > button {{
        border-radius: 999px !important;
        font-family: 'Baloo 2', cursive !important;
        font-weight: 600 !important;
        border: 2px solid {COLOR_TURQUESA} !important;
        color: {COLOR_TURQUESA} !important;
        background-color: #FFFFFF !important;
        transition: all 0.25s ease !important;
        position: relative !important;
        overflow: hidden !important;
    }}

    .stButton > button:hover, .stFormSubmitButton > button:hover {{
        background-color: #E5FBFA !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 18px rgba(46,196,192,0.3) !important;
    }}

    .stButton > button[kind="primary"], .stFormSubmitButton > button[kind="primary"] {{
        background-color: {COLOR_CORAL} !important;
        border: 2px solid {COLOR_CORAL} !important;
        color: #FFFFFF !important;
    }}

    .stButton > button[kind="primary"]:hover {{
        background-color: #d94e69 !important;
        border-color: #d94e69 !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 18px rgba(242,96,125,0.35) !important;
    }}

    .stLinkButton a {{
        border-radius: 999px !important;
        font-family: 'Baloo 2', cursive !important;
        font-weight: 700 !important;
        background-color: {COLOR_CORAL} !important;
        border: 2px solid {COLOR_CORAL} !important;
        color: #FFFFFF !important;
        justify-content: center !important;
        transition: all 0.25s ease !important;
    }}

    .stLinkButton a:hover {{
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 18px rgba(242,96,125,0.35) !important;
    }}

    div[data-baseweb="select"] {{
        border-radius: 14px !important;
        overflow: hidden;
    }}

    input, textarea {{
        border-radius: 12px !important;
    }}

    /* ── TARJETAS DE PRODUCTO ── */
    .producto-card {{
        background: #FFFFFF;
        border-radius: 20px;
        overflow: hidden;
        border: 2px solid rgba(46,196,192,0.25);
        box-shadow: 0 4px 14px rgba(0,0,0,0.07);
        transition: transform 0.35s cubic-bezier(0.34,1.56,0.64,1),
                    box-shadow 0.35s ease;
        margin-bottom: 18px;
        /* Scroll-reveal: empieza invisible y bajada */
        opacity: 0;
        transform: translateY(36px);
    }}

    .producto-card.visible {{
        opacity: 1;
        transform: translateY(0);
    }}

    .producto-card:hover {{
        transform: translateY(-6px) scale(1.02) !important;
        box-shadow: 0 16px 36px rgba(46,196,192,0.22) !important;
        border-color: {COLOR_TURQUESA} !important;
    }}

    .producto-card img {{
        width: 100%;
        aspect-ratio: 1 / 1;
        object-fit: cover;
        display: block;
        transition: transform 0.45s ease;
    }}

    .producto-card:hover img {{
        transform: scale(1.06);
    }}

    .producto-card-body {{
        padding: 12px 14px 14px;
    }}

    .producto-card-nombre {{
        font-family: 'Baloo 2', cursive;
        font-weight: 700;
        font-size: 15px;
        color: {COLOR_CACAO};
        margin: 0 0 2px 0;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }}

    .producto-card-linea {{
        font-size: 12px;
        color: #AAA;
        margin: 0 0 10px 0;
    }}

    .producto-card-btn {{
        display: block;
        width: 100%;
        padding: 9px 0;
        text-align: center;
        border-radius: 999px;
        font-family: 'Baloo 2', cursive;
        font-weight: 700;
        font-size: 14px;
        border: 2px solid {COLOR_TURQUESA};
        color: {COLOR_TURQUESA};
        background: #FFFFFF;
        cursor: pointer;
        transition: all 0.2s ease;
        position: relative;
        overflow: hidden;
    }}

    .producto-card-btn:hover {{
        background: {COLOR_TURQUESA};
        color: #FFFFFF;
        box-shadow: 0 4px 14px rgba(46,196,192,0.4);
    }}

    .producto-card-btn.agotado {{
        border-color: #DDD;
        color: #BBB;
        cursor: not-allowed;
    }}

    /* ── RIPPLE en botones ── */
    .ripple {{
        position: absolute;
        border-radius: 50%;
        transform: scale(0);
        animation: ripple-anim 0.55s linear;
        background: rgba(255,255,255,0.45);
        pointer-events: none;
    }}

    @keyframes ripple-anim {{
        to {{ transform: scale(4); opacity: 0; }}
    }}

    /* ── BANNER HERO animado ── */
    @keyframes hero-shimmer {{
        0%   {{ background-position: 0% 50%; }}
        50%  {{ background-position: 100% 50%; }}
        100% {{ background-position: 0% 50%; }}
    }}

    .hero-banner {{
        background: linear-gradient(135deg, {COLOR_TURQUESA}, #1FA8A4, {COLOR_CORAL}, {COLOR_TURQUESA});
        background-size: 300% 300%;
        animation: hero-shimmer 8s ease infinite;
        border-radius: 22px;
        padding: 18px 26px;
        box-shadow: 0 4px 18px rgba(46,196,192,0.3);
    }}

    .hero-banner h1 {{
        margin: 0;
        color: #FFFFFF !important;
        font-size: clamp(22px, 4vw, 32px);
    }}

    .hero-banner p {{
        margin: 4px 0 0 0;
        font-size: 17px;
        color: #FFF3DC;
    }}

    /* ── SKELETON loader para imágenes ── */
    @keyframes skeleton-pulse {{
        0%   {{ background-position: -400px 0; }}
        100% {{ background-position: 400px 0; }}
    }}

    .skeleton-img {{
        width: 100%;
        aspect-ratio: 1 / 1;
        background: linear-gradient(90deg, #EEE 25%, #F8F8F8 50%, #EEE 75%);
        background-size: 800px 100%;
        animation: skeleton-pulse 1.4s infinite linear;
        border-radius: 12px;
    }}

    /* ── SECCIÓN TÍTULO con borde decorativo animado ── */
    .seccion-titulo {{
        display: inline-flex;
        align-items: center;
        gap: 10px;
        background: linear-gradient(90deg, rgba(46,196,192,0.12), transparent);
        border-left: 5px solid {COLOR_TURQUESA};
        border-radius: 0 999px 999px 0;
        padding: 8px 22px 8px 16px;
        margin: 12px 0;
    }}

    .seccion-titulo span {{
        font-family: 'Baloo 2', cursive;
        font-weight: 800;
        font-size: 20px;
        color: {COLOR_CACAO};
    }}

    /* ── Info cards con hover suave ── */
    .info-card {{
        background: #FFFFFF;
        border-radius: 14px;
        padding: 10px 14px;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }}

    .info-card:hover {{
        transform: translateY(-3px);
        box-shadow: 0 6px 16px rgba(0,0,0,0.08);
    }}

    </style>

    <script>
    // ── SCROLL REVEAL con IntersectionObserver ──
    (function() {{
        function initReveal() {{
            var cards = document.querySelectorAll('.producto-card');
            if (!cards.length) {{ setTimeout(initReveal, 500); return; }}

            var observer = new IntersectionObserver(function(entries) {{
                entries.forEach(function(entry, i) {{
                    if (entry.isIntersecting) {{
                        // Stagger: cada tarjeta se anima con un pequeño delay
                        setTimeout(function() {{
                            entry.target.classList.add('visible');
                        }}, i * 80);
                        observer.unobserve(entry.target);
                    }}
                }});
            }}, {{ threshold: 0.12 }});

            cards.forEach(function(card) {{ observer.observe(card); }});
        }}
        document.addEventListener('DOMContentLoaded', function() {{ setTimeout(initReveal, 800); }});

        // Re-observar cuando Streamlit re-renderiza
        var mo = new MutationObserver(function() {{ setTimeout(initReveal, 400); }});
        mo.observe(document.body, {{ childList: true, subtree: true }});
    }})();

    // ── RIPPLE en botones .producto-card-btn ──
    document.addEventListener('click', function(e) {{
        var btn = e.target.closest('.producto-card-btn');
        if (!btn || btn.classList.contains('agotado')) return;
        var circle = document.createElement('span');
        var d = Math.max(btn.clientWidth, btn.clientHeight);
        var rect = btn.getBoundingClientRect();
        circle.className = 'ripple';
        circle.style.width = circle.style.height = d + 'px';
        circle.style.left = (e.clientX - rect.left - d/2) + 'px';
        circle.style.top  = (e.clientY - rect.top  - d/2) + 'px';
        btn.appendChild(circle);
        setTimeout(function() {{ circle.remove(); }}, 600);
    }});
    </script>
    """, unsafe_allow_html=True)

def pildora_seccion(nombre, color):
    st.markdown(f"""
    <div class="seccion-titulo">
        <div style="width:12px; height:12px; border-radius:50%; background:{color}; 
                    box-shadow: 0 0 0 4px {color}33; flex-shrink:0;"></div>
        <span>{nombre}</span>
    </div>
    """, unsafe_allow_html=True)

def boton_red_social(etiqueta, url, color_fondo, icono_slug=None):
    """Genera un botón tipo píldora. Si se da icono_slug, usa el logo oficial de la marca (vía Simple Icons)."""
    icono_html = ""
    if icono_slug:
        icono_html = f'<img src="https://cdn.simpleicons.org/{icono_slug}/FFFFFF" width="18" style="vertical-align:middle; margin-right:8px;">'
    return f"""
    <a href="{url}" target="_blank" style="display:block; text-align:center; background:{color_fondo};
       color:#FFFFFF !important; padding:9px 10px; border-radius:999px; font-family:'Baloo 2', cursive;
       font-weight:700; text-decoration:none; font-size:15px;">
       {icono_html}{etiqueta}
    </a>
    """

def renderizar_grid_productos(productos):
    """Dibuja una cuadrícula de 3 columnas con tarjetas animadas de producto."""
    # Generamos el HTML de todas las tarjetas en una sola inyección para
    # poder usar las clases CSS/JS de animación que definimos en inyectar_estilos()
    tarjetas_html = '<div style="display:grid; grid-template-columns: repeat(3, 1fr); gap:18px; padding: 4px 0 12px;">'

    for prod in productos:
        if prod["agotado"]:
            btn_html = f'<div class="producto-card-btn agotado">❌ Agotado</div>'
        else:
            # El onclick manda un mensaje especial que Streamlit NO escucha —
            # por eso debajo del grid seguimos poniendo st.button ocultos para
            # que la lógica del carrito siga funcionando igual que antes.
            btn_html = f'<div class="producto-card-btn" onclick="document.getElementById(\'cloe_add_{prod["id"]}\').click()">➕ Agregar</div>'

        tarjetas_html += f"""
        <div class="producto-card" id="card_{prod['id']}">
            <div style="overflow:hidden; border-radius:18px 18px 0 0;">
                <img src="{prod['imagen']}" alt="{prod['nombre']}"
                     loading="lazy"
                     onerror="this.style.display='none'; this.nextElementSibling.style.display='block';"
                     style="opacity:1;" />
                <div class="skeleton-img" style="display:none;"></div>
            </div>
            <div class="producto-card-body">
                <p class="producto-card-nombre">{prod['nombre']}</p>
                <p class="producto-card-linea">Línea: {prod['categoria']}</p>
                {btn_html}
            </div>
        </div>
        """

    tarjetas_html += "</div>"
    st.markdown(tarjetas_html, unsafe_allow_html=True)

    # Botones reales de Streamlit (ocultos visualmente) para que el carrito funcione
    # El JS de cada tarjeta los activa haciendo click programático
    for prod in productos:
        if not prod["agotado"]:
            btn_key = f"add_{prod['id']}"
            with st.container():
                st.markdown(f'<div style="display:none" id="wrapper_cloe_add_{prod["id"]}">', unsafe_allow_html=True)
                if st.button("add", key=btn_key, help=prod["nombre"]):
                    st.session_state.carrito[prod["id"]] = prod["nombre"]
                    st.toast(f"✅ Agregado: {prod['nombre']}")
                st.markdown('</div>', unsafe_allow_html=True)

    # Script que conecta el botón visual con el botón real de Streamlit
    st.markdown("""
    <script>
    (function patchBotones() {
        document.querySelectorAll('.producto-card-btn:not(.agotado)').forEach(function(btn) {
            var match = btn.getAttribute('onclick') && btn.getAttribute('onclick').match(/cloe_add_(\\d+)/);
            if (!match) return;
            var id = match[1];
            btn.addEventListener('click', function() {
                // Busca el botón real de Streamlit que tiene el texto "add" y el key correcto
                var allBtns = document.querySelectorAll('button');
                for (var b of allBtns) {
                    if (b.closest('#wrapper_cloe_add_' + id)) { b.click(); break; }
                }
            });
        });
    })();
    </script>
    """, unsafe_allow_html=True)

datos_actuales = cargar_datos()

st.set_page_config(page_title=f"{datos_actuales['config']['nombre_tienda']} - Catálogo Oficial", page_icon="🛍️", layout="wide")
inyectar_estilos()

if "carrito" not in st.session_state:
    st.session_state.carrito = {}

if "mensaje_exito" not in st.session_state:
    st.session_state.mensaje_exito = False

if "es_admin" not in st.session_state:
    st.session_state.es_admin = False

# 🔒 CONTROL DE ACCESO: login con contraseña (no se ve en la URL)
# Para entrar, visita tu página agregando "?admin" al final del enlace, ej:
# https://tuapp.streamlit.app/?admin
query_params = st.query_params
solicito_panel_admin = "admin" in query_params

if solicito_panel_admin and not st.session_state.es_admin:
    st.title("🔒 Acceso al Panel de Administración")
    if not CLAVE_ADMIN:
        st.error("⚠️ No se ha configurado CLAVE_ADMIN en Secrets. Revisa la guía de configuración.")
        st.stop()
    with st.form("form_login_admin"):
        clave_ingresada = st.text_input("Clave de administrador:", type="password")
        entrar = st.form_submit_button("Entrar", type="primary", use_container_width=True)
    if entrar:
        if clave_ingresada == CLAVE_ADMIN:
            st.session_state.es_admin = True
            st.rerun()
        else:
            st.error("❌ Clave incorrecta. Intenta de nuevo.")
    st.stop()

es_admin = st.session_state.es_admin

# ------------------------------------------
# VISTA 1: ÁREA DE ADMINISTRACIÓN
# ------------------------------------------
if es_admin:
    col_titulo, col_logout = st.columns([4, 1])
    with col_titulo:
        st.title(f"⚙️ Centro de Control {datos_actuales['config']['nombre_tienda']}")
        st.caption("Panel de administración con carga directa de imágenes a la nube.")
    with col_logout:
        st.write("")
        if st.button("🚪 Cerrar sesión", use_container_width=True):
            st.session_state.es_admin = False
            st.rerun()
    st.markdown("---")
    
    if st.session_state.mensaje_exito:
        st.success("💾 ¡CAMBIOS Y FOTOS GUARDADAS CON ÉXITO EN LA NUBE!")
        st.session_state.mensaje_exito = False 
    
    # --- CONFIGURACIÓN GENERAL DE LA TIENDA ---
    st.header("⚙️ Configuración General")
    st.write("Cambia el nombre, contacto y datos de tu tienda sin tocar el código.")
    with st.form("form_config_general"):
        nuevo_nombre = st.text_input("Nombre de la tienda:", value=datos_actuales["config"]["nombre_tienda"])
        nuevo_eslogan = st.text_input("Eslogan:", value=datos_actuales["config"]["eslogan"])
        nuevo_whatsapp = st.text_input("Número de WhatsApp (con código de país, sin '+' ni espacios):", value=datos_actuales["config"]["numero_whatsapp"])
        nueva_ubicacion = st.text_input("📍 Ubicación:", value=datos_actuales["config"]["ubicacion"])
        nuevo_horario = st.text_input("⏰ Horario de atención:", value=datos_actuales["config"]["horario"])
        nuevos_envios = st.text_input("🚚 Información de envíos:", value=datos_actuales["config"]["envios"])
        
        st.markdown("**🔗 Redes sociales y contacto** (déjalos vacíos si todavía no los tienes — el botón solo aparece en la tienda cuando hay un enlace)")
        nuevo_facebook = st.text_input("📘 Enlace de Facebook:", value=datos_actuales["config"].get("facebook", ""), placeholder="https://facebook.com/tu_pagina")
        nuevo_instagram = st.text_input("📸 Enlace de Instagram:", value=datos_actuales["config"].get("instagram", ""), placeholder="https://instagram.com/tu_cuenta")
        nuevo_tiktok = st.text_input("🎵 Enlace de TikTok:", value=datos_actuales["config"].get("tiktok", ""), placeholder="https://tiktok.com/@tu_cuenta")
        nuevo_x = st.text_input("✖️ Enlace de X (Twitter):", value=datos_actuales["config"].get("x", ""), placeholder="https://x.com/tu_cuenta")
        nuevo_correo = st.text_input("✉️ Correo electrónico:", value=datos_actuales["config"].get("correo", ""), placeholder="tutienda@correo.com")
        
        guardar_config = st.form_submit_button("💾 Guardar Configuración", type="primary", use_container_width=True)
        
        if guardar_config:
            datos_actuales["config"]["nombre_tienda"] = nuevo_nombre.strip() or datos_actuales["config"]["nombre_tienda"]
            datos_actuales["config"]["eslogan"] = nuevo_eslogan
            datos_actuales["config"]["numero_whatsapp"] = nuevo_whatsapp.strip()
            datos_actuales["config"]["ubicacion"] = nueva_ubicacion
            datos_actuales["config"]["horario"] = nuevo_horario
            datos_actuales["config"]["envios"] = nuevos_envios
            datos_actuales["config"]["facebook"] = nuevo_facebook.strip()
            datos_actuales["config"]["instagram"] = nuevo_instagram.strip()
            datos_actuales["config"]["tiktok"] = nuevo_tiktok.strip()
            datos_actuales["config"]["x"] = nuevo_x.strip()
            datos_actuales["config"]["correo"] = nuevo_correo.strip()
            guardar_datos(datos_actuales)
            st.session_state.mensaje_exito = True
            st.rerun()

    st.markdown("---")
    
    # --- LOGO DE LA TIENDA ---
    st.header("🖼️ Logo de la Tienda")
    col_logo_actual, col_logo_subir = st.columns([1, 3])
    
    with col_logo_actual:
        st.write("**Logo actual:**")
        st.image(datos_actuales.get("logo_url", LOGO_URL_DEFAULT), width=100)
    
    with col_logo_subir:
        if "contador_logo" not in st.session_state:
            st.session_state.contador_logo = 0
        
        archivo_logo = st.file_uploader(
            "Sube una imagen para reemplazar el logo:",
            type=["png", "jpg", "jpeg"],
            accept_multiple_files=False,
            key=f"logo_up_{st.session_state.contador_logo}"
        )
        
        if archivo_logo is not None:
            if st.button("💾 Guardar nuevo logo", type="primary", key="btn_guardar_logo"):
                with st.spinner("Subiendo logo a la nube..."):
                    url_logo = subir_imagen_a_nube(archivo_logo)
                    if url_logo:
                        datos_actuales["logo_url"] = url_logo
                        guardar_datos(datos_actuales)
                        st.session_state.mensaje_exito = True
                        # Cambia el key del uploader para "vaciarlo" tras guardar
                        st.session_state.contador_logo += 1
                        st.rerun()

    st.markdown("---")
    
    # --- GESTIÓN DE SECCIONES ---
    st.header("🗂️ Gestión de Secciones del Catálogo")
    with st.expander("➕ Crear o Eliminar una Sección Completa", expanded=False):
        col_nueva, col_accion = st.columns([3, 1])
        with col_nueva:
            nueva_sec_nombre = st.text_input("Nombre de la nueva sección:", placeholder="Ej: Vestidos Juveniles...", key="input_nueva_seccion")
        with col_accion:
            st.write("##")
            if st.button("Crear Sección", use_container_width=True, type="primary"):
                if nueva_sec_nombre and nueva_sec_nombre not in datos_actuales["secciones"]:
                    datos_actuales["secciones"][nueva_sec_nombre] = {"anuncio": "", "activa": True}
                    guardar_datos(datos_actuales)
                    st.session_state.mensaje_exito = True
                    st.rerun()
                    
        st.write("---")
        for sec_name, sec_info in list(datos_actuales["secciones"].items()):
            col_check, col_del = st.columns([3, 1])
            with col_check:
                estado_check = st.checkbox(f"Sección Activa: {sec_name}", value=sec_info["activa"], key=f"status_{sec_name}")
                if estado_check != sec_info["activa"]:
                    datos_actuales["secciones"][sec_name]["activa"] = estado_check
                    guardar_datos(datos_actuales)
                    st.session_state.mensaje_exito = True
                    st.rerun()
            with col_del:
                if st.button("🗑️ Eliminar Sección", key=f"del_sec_{sec_name}"):
                    del datos_actuales["secciones"][sec_name]
                    datos_actuales["lista_productos"] = [p for p in datos_actuales["lista_productos"] if p["categoria"] != sec_name]
                    guardar_datos(datos_actuales)
                    st.session_state.mensaje_exito = True
                    st.rerun()

    st.markdown("---")
    
    # --- FORMULARIO DE EDICIÓN DE PRODUCTOS EXISTENTES ---
    st.header("📦 Productos Existentes")
    st.write("Edita anuncios, nombres, visibilidad y disponibilidad de tus productos actuales.")
    
    with st.form(key="formulario_maestro_cloe"):
        st.form_submit_button("💾 GUARDAR CAMBIOS DE PRODUCTOS", use_container_width=True, type="primary", key="btn_guardar_arriba")
        st.write("")
        
        for sec_name, sec_info in datos_actuales["secciones"].items():
            if not sec_info["activa"]:
                continue
                
            with st.container(border=True):
                st.subheader(f"📁 Categoría: {sec_name}")
                
                st.text_input(f"📢 Anuncio / Promoción para {sec_name}:", value=sec_info["anuncio"], key=f"ann_{sec_name}")
                
                st.write("**📦 Artículos registrados:**")
                prod_de_seccion = [p for p in datos_actuales["lista_productos"] if p["categoria"] == sec_name]
                
                if not prod_de_seccion:
                    st.info("Sin artículos todavía. Usa el subidor masivo más abajo para agregar fotos.")
                else:
                    for prod in prod_de_seccion:
                        col_p_img, col_p_nombre, col_p_vis, col_p_ago, col_p_del = st.columns([1, 3, 2, 2, 1])
                        with col_p_img:
                            st.image(prod["imagen"], width=50)
                        with col_p_nombre:
                            st.text_input("Nombre", value=prod["nombre"], key=f"name_{prod['id']}", label_visibility="collapsed")
                        with col_p_vis:
                            st.checkbox("🟢 Visible", value=prod["activo"], key=f"act_{prod['id']}")
                        with col_p_ago:
                            st.checkbox("🔴 Agotado", value=prod.get("agotado", False), key=f"ago_{prod['id']}")
                        with col_p_del:
                            st.checkbox("🗑️ Borrar", value=False, key=f"del_{prod['id']}")
                            
        st.markdown("---")
        boton_guardar_final = st.form_submit_button("💾 GUARDAR CAMBIOS DE PRODUCTOS", use_container_width=True, type="primary", key="btn_guardar_abajo")
        
        if boton_guardar_final:
            productos_actualizados = []
            
            for sec_name in datos_actuales["secciones"]:
                if f"ann_{sec_name}" in st.session_state:
                    datos_actuales["secciones"][sec_name]["anuncio"] = st.session_state[f"ann_{sec_name}"]
            
            for prod in datos_actuales["lista_productos"]:
                key_del = f"del_{prod['id']}"
                if key_del in st.session_state and st.session_state[key_del]:
                    continue
                
                if f"name_{prod['id']}" in st.session_state:
                    prod["nombre"] = st.session_state[f"name_{prod['id']}"]
                    prod["activo"] = st.session_state[f"act_{prod['id']}"]
                    prod["agotado"] = st.session_state[f"ago_{prod['id']}"]
                
                productos_actualizados.append(prod)
            
            datos_actuales["lista_productos"] = productos_actualizados
            guardar_datos(datos_actuales)
            st.session_state.mensaje_exito = True
            st.rerun()

    st.markdown("---")

    # --- SUBIDOR MASIVO DE IMÁGENES CON NOMBRE POR FOTO ---
    st.header("📸 Subida Masiva de Fotos Nuevas")
    st.write("Selecciona varias fotos a la vez para una sección y ponle nombre a cada una antes de publicarla en el catálogo.")

    for sec_name, sec_info in datos_actuales["secciones"].items():
        if not sec_info["activa"]:
            continue

        contador_key = f"contador_subidor_{sec_name}"
        if contador_key not in st.session_state:
            st.session_state[contador_key] = 0

        with st.container(border=True):
            st.subheader(f"📁 {sec_name}")
            fotos_subidas = st.file_uploader(
                f"Arrastra o selecciona las fotos para {sec_name}:",
                type=["png", "jpg", "jpeg"],
                accept_multiple_files=True,
                key=f"masivo_up_{sec_name}_{st.session_state[contador_key]}"
            )

            if fotos_subidas:
                st.write(f"**Ponle nombre a cada foto ({len(fotos_subidas)} seleccionadas):**")
                for idx, foto in enumerate(fotos_subidas):
                    col_img, col_nombre = st.columns([1, 4])
                    with col_img:
                        st.image(foto, width=70)
                    with col_nombre:
                        nombre_key = f"nombre_masivo_{sec_name}_{st.session_state[contador_key]}_{idx}_{foto.name}"
                        st.text_input(
                            "Nombre del producto",
                            value=nombre_sugerido_desde_archivo(foto.name),
                            key=nombre_key,
                            label_visibility="collapsed",
                            placeholder="Nombre del producto..."
                        )

                if st.button(f"💾 Publicar fotos de {sec_name}", key=f"btn_publicar_{sec_name}", type="primary", use_container_width=True):
                    with st.spinner(f"Subiendo {len(fotos_subidas)} fotos de {sec_name} a la nube..."):
                        errores = 0
                        for idx, foto in enumerate(fotos_subidas):
                            url_nube = subir_imagen_a_nube(foto)
                            if url_nube:
                                nombre_key = f"nombre_masivo_{sec_name}_{st.session_state[contador_key]}_{idx}_{foto.name}"
                                nombre_final = st.session_state.get(nombre_key, "").strip()
                                if not nombre_final:
                                    nombre_final = nombre_sugerido_desde_archivo(foto.name)
                                nuevo_id = max([p["id"] for p in datos_actuales["lista_productos"]], default=0) + 1
                                datos_actuales["lista_productos"].append({
                                    "id": nuevo_id,
                                    "nombre": nombre_final,
                                    "categoria": sec_name,
                                    "imagen": url_nube,
                                    "activo": True,
                                    "agotado": False
                                })
                            else:
                                errores += 1
                        guardar_datos(datos_actuales)
                        st.session_state.mensaje_exito = True
                        # Cambia el key del uploader para "vaciarlo" y evitar publicar las mismas fotos dos veces
                        st.session_state[contador_key] += 1
                        if errores:
                            st.warning(f"⚠️ {errores} foto(s) no se pudieron subir. Las demás se publicaron correctamente.")
                        st.rerun()

# ------------------------------------------
# VISTA 2: ÁREA DEL CLIENTE (URL Normal)
# ------------------------------------------
else:
    cfg = datos_actuales["config"]
    
    # 🌟 ESPACIO DE ENCABEZADO PUBLICITARIO E INFORMATIVO
    col_logo, col_info = st.columns([1, 4])
    
    with col_logo:
        st.image(datos_actuales.get("logo_url", LOGO_URL_DEFAULT), width=130)
        
    with col_info:
        st.markdown(f"""
        <div class="hero-banner">
            <h1>🛍️ {cfg['nombre_tienda']}</h1>
            <p>{cfg['eslogan']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Detalles informativos organizados
        st.write("")
        col_inf_1, col_inf_2, col_inf_3 = st.columns(3)
        with col_inf_1:
            st.markdown(f"""<div class="info-card" style="border:2px solid {COLOR_CORAL};">
                <span style="font-size:13px; color:#999;">📍 UBICACIÓN</span><br>
                <span style="font-weight:700; color:{COLOR_CACAO};">{cfg['ubicacion']}</span>
            </div>""", unsafe_allow_html=True)
        with col_inf_2:
            st.markdown(f"""<div class="info-card" style="border:2px solid {COLOR_AMARILLO};">
                <span style="font-size:13px; color:#999;">⏰ ATENCIÓN</span><br>
                <span style="font-weight:700; color:{COLOR_CACAO};">{cfg['horario']}</span>
            </div>""", unsafe_allow_html=True)
        with col_inf_3:
            st.markdown(f"""<div class="info-card" style="border:2px solid {COLOR_LAVANDA};">
                <span style="font-size:13px; color:#999;">🚚 ENVÍOS</span><br>
                <span style="font-weight:700; color:{COLOR_CACAO};">{cfg['envios']}</span>
            </div>""", unsafe_allow_html=True)

        # 🔗 Redes sociales y contacto directo (solo se muestran si ya las configuraste)
        enlaces_contacto = []
        if cfg.get("facebook"):
            enlaces_contacto.append(("Facebook", cfg["facebook"], "#1877F2", "facebook"))
        if cfg.get("instagram"):
            enlaces_contacto.append(("Instagram", cfg["instagram"], "#E1306C", "instagram"))
        if cfg.get("tiktok"):
            enlaces_contacto.append(("TikTok", cfg["tiktok"], "#000000", "tiktok"))
        if cfg.get("x"):
            enlaces_contacto.append(("X", cfg["x"], "#000000", "x"))
        if cfg.get("numero_whatsapp"):
            enlaces_contacto.append(("WhatsApp", f"https://wa.me/{cfg['numero_whatsapp']}", "#25D366", "whatsapp"))
        if cfg.get("correo"):
            enlaces_contacto.append(("Correo", f"mailto:{cfg['correo']}", COLOR_LAVANDA, None))

        if enlaces_contacto:
            st.write("")
            cols_enlaces = st.columns(len(enlaces_contacto))
            for col_enlace, (etiqueta, url, color, slug) in zip(cols_enlaces, enlaces_contacto):
                with col_enlace:
                    st.markdown(boton_red_social(etiqueta, url, color, slug), unsafe_allow_html=True)

    st.markdown("---")
    
    secciones_activas = [name for name, info in datos_actuales["secciones"].items() if info["activa"]]
    
    if not secciones_activas:
        st.info("Catálogo en mantenimiento por actualización de mercadería. ¡Vuelve pronto!")
    else:
        color_por_seccion = {nombre: PALETA_SECCIONES[i % len(PALETA_SECCIONES)] for i, nombre in enumerate(secciones_activas)}
        categoria_seleccionada = st.selectbox("🔍 ¿Qué línea deseas explorar hoy?:", ["Todos"] + secciones_activas)
        col_tienda, col_carrito = st.columns([3, 1])
        
        with col_tienda:
            if categoria_seleccionada != "Todos":
                pildora_seccion(categoria_seleccionada, color_por_seccion[categoria_seleccionada])
                anuncio_actual = datos_actuales["secciones"][categoria_seleccionada]["anuncio"]
                if anuncio_actual:
                    st.info(f"📢 {anuncio_actual}")

                productos_a_mostrar = [
                    p for p in datos_actuales["lista_productos"]
                    if p["activo"] and p["categoria"] == categoria_seleccionada
                ]
                if not productos_a_mostrar:
                    st.info("Todavía no hay artículos visibles en esta sección.")
                else:
                    renderizar_grid_productos(productos_a_mostrar)
            else:
                hubo_contenido = False
                for sec_name in secciones_activas:
                    productos_sec = [
                        p for p in datos_actuales["lista_productos"]
                        if p["activo"] and p["categoria"] == sec_name
                    ]
                    if not productos_sec:
                        continue

                    hubo_contenido = True
                    pildora_seccion(sec_name, color_por_seccion[sec_name])
                    anuncio_sec = datos_actuales["secciones"][sec_name]["anuncio"]
                    if anuncio_sec:
                        st.caption(f"📢 {anuncio_sec}")

                    renderizar_grid_productos(productos_sec)
                    st.markdown("---")

                if not hubo_contenido:
                    st.info("Todavía no hay artículos visibles en el catálogo.")
                    
        with col_carrito:
            st.subheader("🛒 Tu Consulta")
            if not st.session_state.carrito:
                st.info("Tu lista está vacía.")
            else:
                nombre_cliente = st.text_input("Tu Nombre Completo:", placeholder="Ej: María Pérez")
                st.write("**Productos:**")
                items_mensaje = []
                
                for id_prod, nombre_prod in list(st.session_state.carrito.items()):
                    st.caption(f"• {nombre_prod}")
                    items_mensaje.append(f"- {nombre_prod} (ID: #{id_prod})")
                    if st.button("Quitar ❌", key=f"del_{id_prod}"):
                        del st.session_state.carrito[id_prod]
                        st.rerun()
                
                st.markdown("---")
                if nombre_cliente:
                    texto_productos = "\n".join(items_mensaje)
                    mensaje_final = f"¡Hola {cfg['nombre_tienda']}!\n\nMi nombre es *{nombre_cliente}* y estoy interesada en consultar el precio de los siguientes productos para un apartado:\n\n{texto_productos}"
                    mensaje_codificado = urllib.parse.quote(mensaje_final)
                    url_final = f"https://wa.me/{cfg['numero_whatsapp']}?text={mensaje_codificado}"
                    st.link_button("🚀 Consultar Precio en WhatsApp", url_final, type="primary", use_container_width=True)
                else:
                    st.warning("✍️ Escribe tu nombre para activar el botón de WhatsApp.")
