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

DB_FILE = "database.json"

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
        "envios": "Entregas locales garantizadas"
    },
    "secciones": {
        "Ropa de Niño": {"anuncio": "¡Colección de temporada con 15% de descuento directo! ❄️", "activa": True},
        "Calzado": {"anuncio": "Calzado unisex cómodo para los consentidos del hogar. 👟", "activa": True},
        "Bisutería y Accesorios": {"anuncio": "Prendas delicadas para resaltar tu estilo diario. ✨", "activa": True}
    },
    "lista_productos": [
        {"id": 1, "nombre": "Conjunto Infantil Unisex - Algodón Premium", "categoria": "Ropa de Niño", "imagen": "https://images.unsplash.com/photo-1519704943960-ab388d5904ca?w=500", "activo": True, "agotado": False},
        {"id": 2, "nombre": "Zapatos Deportivos Blandos para Bebé", "categoria": "Calzado", "imagen": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=500", "activo": True, "agotado": False},
        {"id": 3, "nombre": "Pulsera Ajustable de Bisutería Artesanal", "categoria": "Bisutería y Accesorios", "imagen": "https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?w=500", "activo": True, "agotado": True}
    ]
}

def cargar_datos():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_DATA, f, ensure_ascii=False, indent=4)
        return DEFAULT_DATA
    with open(DB_FILE, "r", encoding="utf-8") as f:
        datos = json.load(f)
    # Compatibilidad: si la base de datos es de antes de tener logo/config editables
    if "logo_url" not in datos:
        datos["logo_url"] = LOGO_URL_DEFAULT
    if "config" not in datos:
        datos["config"] = DEFAULT_DATA["config"].copy()
    else:
        for llave, valor in DEFAULT_DATA["config"].items():
            datos["config"].setdefault(llave, valor)
    return datos

def guardar_datos(datos):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=4)

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

datos_actuales = cargar_datos()

st.set_page_config(page_title=f"{datos_actuales['config']['nombre_tienda']} - Catálogo Oficial", page_icon="🛍️", layout="wide")

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
        
        guardar_config = st.form_submit_button("💾 Guardar Configuración", type="primary", use_container_width=True)
        
        if guardar_config:
            datos_actuales["config"]["nombre_tienda"] = nuevo_nombre.strip() or datos_actuales["config"]["nombre_tienda"]
            datos_actuales["config"]["eslogan"] = nuevo_eslogan
            datos_actuales["config"]["numero_whatsapp"] = nuevo_whatsapp.strip()
            datos_actuales["config"]["ubicacion"] = nueva_ubicacion
            datos_actuales["config"]["horario"] = nuevo_horario
            datos_actuales["config"]["envios"] = nuevos_envios
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
        st.markdown(f"<h1 style='margin-bottom: 0px;'>🛍️ {cfg['nombre_tienda']}</h1>", unsafe_allow_html=True)
        st.markdown(f"<p style='font-size: 18px; color: gray; margin-top: 0px;'>{cfg['eslogan']}</p>", unsafe_allow_html=True)
        
        # Detalles informativos organizados
        col_inf_1, col_inf_2, col_inf_3 = st.columns(3)
        with col_inf_1:
            st.markdown(f"📍 **Ubicación:**<br>{cfg['ubicacion']}", unsafe_allow_html=True)
        with col_inf_2:
            st.markdown(f"⏰ **Atención:**<br>{cfg['horario']}", unsafe_allow_html=True)
        with col_inf_3:
            st.markdown(f"🚚 **Envíos:**<br>{cfg['envios']}", unsafe_allow_html=True)

    st.markdown("---")
    
    secciones_activas = [name for name, info in datos_actuales["secciones"].items() if info["activa"]]
    
    if not secciones_activas:
        st.info("Catálogo en mantenimiento por actualización de mercadería. ¡Vuelve pronto!")
    else:
        categoria_seleccionada = st.selectbox("🔍 ¿Qué línea deseas explorar hoy?:", ["Todos"] + secciones_activas)
        col_tienda, col_carrito = st.columns([3, 1])
        
        with col_tienda:
            if categoria_seleccionada != "Todos":
                anuncio_actual = datos_actuales["secciones"][categoria_seleccionada]["anuncio"]
                if anuncio_actual:
                    st.info(f"📢 {anuncio_actual}")
                    
            cols_grid = st.columns(3)
            col_idx = 0
            
            for prod in datos_actuales["lista_productos"]:
                if not prod["activo"] or prod["categoria"] not in secciones_activas:
                    continue
                if categoria_seleccionada != "Todos" and prod["categoria"] != categoria_seleccionada:
                    continue
                    
                with cols_grid[col_idx % 3]:
                    st.image(prod["imagen"], use_container_width=True)
                    st.subheader(prod["nombre"])
                    st.caption(f"Línea: {prod['categoria']}")
                    
                    if prod["agotado"]:
                        st.button("❌ Agotado temporalmente", key=f"btn_ago_{prod['id']}", disabled=True, use_container_width=True)
                    else:
                        if st.button("➕ Agregar para consultar", key=f"add_{prod['id']}", use_container_width=True):
                            st.session_state.carrito[prod["id"]] = prod["nombre"]
                            st.toast(f"Agregado: {prod['nombre']}")
                    st.write("")
                    col_idx += 1
                    
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
