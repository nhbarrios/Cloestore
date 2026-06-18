import streamlit as st
import urllib.parse
import json
import os
import requests
import base64

# ==========================================
# CONFIGURACIÓN GENERAL Y APIS
# ==========================================
NUMERO_WHATSAPP = "50588325774" 
st.set_page_config(page_title="CloeStore - Catálogo Oficial", page_icon="🛍️", layout="wide")

# 🔑 Tu llave real de ImgBB integrada directamente
IMGBB_API_KEY = "1e5fcc62125e29d232617174f88d2e6c" 

DB_FILE = "database.json"

# 🛠️ Logo por defecto (se usa solo si nunca has subido uno desde el panel de admin)
LOGO_URL_DEFAULT = "https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=150"

DEFAULT_DATA = {
    "logo_url": LOGO_URL_DEFAULT,
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
    # Compatibilidad: si la base de datos es de antes de tener logo editable
    if "logo_url" not in datos:
        datos["logo_url"] = LOGO_URL_DEFAULT
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

if "carrito" not in st.session_state:
    st.session_state.carrito = {}

if "mensaje_exito" not in st.session_state:
    st.session_state.mensaje_exito = False

# 🔒 CONTROL DE ACCESO CON STREAMLIT SECRETS
query_params = st.query_params
clave_secreta = st.secrets.get("CLAVE_ADMIN", "210825")
es_admin = query_params.get("admin") == clave_secreta

# ------------------------------------------
# VISTA 1: ÁREA DE ADMINISTRACIÓN
# ------------------------------------------
if es_admin:
    st.title("⚙️ Centro de Control CloeStore")
    st.caption("Panel de administración con carga directa de imágenes a la nube.")
    st.markdown("---")
    
    if st.session_state.mensaje_exito:
        st.success("💾 ¡CAMBIOS Y FOTOS GUARDADAS CON ÉXITO EN LA NUBE!")
        st.session_state.mensaje_exito = False 
    
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
    # 🌟 ESPACIO DE ENCABEZADO PUBLICITARIO E INFORMATIVO
    col_logo, col_info = st.columns([1, 4])
    
    with col_logo:
        st.image(datos_actuales.get("logo_url", LOGO_URL_DEFAULT), width=130)
        
    with col_info:
        st.markdown("<h1 style='margin-bottom: 0px;'>🛍️ CloeStore</h1>", unsafe_allow_html=True)
        st.markdown("<p style='font-size: 18px; color: gray; margin-top: 0px;'>Tu Tienda Virtual de Confianza</p>", unsafe_allow_html=True)
        
        # Detalles informativos organizados
        col_inf_1, col_inf_2, col_inf_3 = st.columns(3)
        with col_inf_1:
            st.markdown("📍 **Ubicación:**<br>Isla de Ometepe, Nicaragua", unsafe_allow_html=True)
        with col_inf_2:
            st.markdown("⏰ **Atención:**<br>Lunes a Sábado: 8 AM - 6 PM", unsafe_allow_html=True)
        with col_inf_3:
            st.markdown("🚚 **Envíos:**<br>Entregas locales garantizadas", unsafe_allow_html=True)

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
                    mensaje_final = f"¡Hola CloeStore!\n\nMi nombre es *{nombre_cliente}* y estoy interesada en consultar el precio de los siguientes productos para un apartado:\n\n{texto_productos}"
                    mensaje_codificado = urllib.parse.quote(mensaje_final)
                    url_final = f"https://wa.me/{NUMERO_WHATSAPP}?text={mensaje_codificado}"
                    st.link_button("🚀 Consultar Precio en WhatsApp", url_final, type="primary", use_container_width=True)
                else:
                    st.warning("✍️ Escribe tu nombre para activar el botón de WhatsApp.")
