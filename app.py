import streamlit as st

# --- 1. CONFIGURACIÓN E INICIALIZACIÓN (Blindaje total) ---
st.set_page_config(layout="wide", page_title="ADEL SISTEMA SUIZO")

# Inicializamos todo de un solo golpe para evitar el AttributeError
if 'asistentes' not in st.session_state:
    st.session_state['asistentes'] = []
    st.session_state['estados'] = {}
    st.session_state['meta_puntos'] = 200
    st.session_state['seccion'] = "INSCRIPCIÓN"
    st.session_state['editando'] = None

# --- 2. MENÚ LATERAL ---
with st.sidebar:
    st.title("🏆 MENÚ ADEL")
    # Usamos una clave (key) para que Streamlit gestione el cambio de sección solo
    st.session_state.seccion = st.radio(
        "VENTANAS:", 
        ["INSCRIPCIÓN", "MESAS", "RESULTADOS", "RANKING"],
        key="radio_navegacion"
    )

# --- 3. SECCIÓN DE INSCRIPCIÓN (PORTADA) ---
if st.session_state.seccion == "INSCRIPCIÓN":
    # Títulos principales
    st.markdown("<h1 style='text-align: center; color: #deff9a;'>ASOCIACIÓN DE DOMINÓ DEL ESTADO LARA “ADEL”</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center;'>SISTEMA SUIZO</h2>", unsafe_allow_html=True)
    st.divider()

    # Columnas para Meta y Registro
    col_izq, col_der = st.columns([2, 1])

    with col_izq:
        # Función para registrar con ENTER
        def registrar():
            txt = st.session_state.input_nombre.upper().strip()
            if txt and txt not in st.session_state.asistentes:
                st.session_state.asistentes.append(txt)
                st.session_state.estados[txt] = True
                st.session_state.asistentes.sort()
            st.session_state.input_nombre = "" # Limpia el campo

        st.text_input("Nombre del Atleta + ENTER:", key="input_nombre", on_change=registrar)

    with col_der:
        # Selector de Meta (100 o 200)
        st.session_state.meta_puntos = st.radio(
            "Meta del encuentro:", [100, 200], 
            index=1 if st.session_state.meta_puntos == 200 else 0, 
            horizontal=True
        )

    st.divider()
    
    # Conteo de atletas
    total = len(st.session_state.asistentes)
    activos = sum(1 for a in st.session_state.asistentes if st.session_state.estados[a])
    st.subheader(f"📊 ATLETAS: {total} | ACTIVOS: {activos}")

    # --- LISTA DE ATLET
