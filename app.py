import streamlit as st

# --- 1. CONFIGURACIÓN E INICIALIZACIÓN ---
st.set_page_config(layout="wide", page_title="ADEL SISTEMA SUIZO")

if 'asistentes' not in st.session_state:
    st.session_state.update({
        'asistentes': [],
        'estados': {},
        'meta_puntos': 200,
        'seccion': "INSCRIPCIÓN",
        'editando': None
    })

# --- 2. NAVEGACIÓN ---
with st.sidebar:
    st.title("🏆 MENÚ ADEL")
    st.session_state.seccion = st.radio("VENTANAS:", ["INSCRIPCIÓN", "MESAS", "RESULTADOS", "RANKING"])

# --- 3. SECCIÓN DE INSCRIPCIÓN ---
if st.session_state.seccion == "INSCRIPCIÓN":
    st.markdown("<h1 style='text-align: center; color: #deff9a;'>ASOCIACIÓN DE DOMINÓ DEL ESTADO LARA “ADEL”</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center;'>SISTEMA SUIZO</h2>", unsafe_allow_html=True)
    st.divider()

    col_izq, col_der = st.columns([2, 1])

    with col_izq:
        # Función de registro (Ahora fuerza el refresco)
        def registrar():
            txt = st.session_state.nuevo_atleta.upper().strip()
            if txt and txt not in st.session_state.asistentes:
                st.session_state.asistentes.append(txt)
                st.session_state.estados[txt] = True
                st.session_state.asistentes.sort()
            st.session_state.nuevo_atleta = "" # Limpia el campo

        st.text_input("Nombre del Atleta + ENTER:", key="nuevo_atleta", on_change=registrar)

    with col_der:
        st.session_state.meta_puntos = st.radio("Meta del encuentro:", [100, 200], 
                                                index=1 if st.session_state.meta_puntos == 200 else 0, 
                                                horizontal=True)

    st.divider()
    
    # Monitor de conteo
    n_total = len(st.session_state.asistentes)
    n_activos = sum(1 for a in st.session_state.asistentes if st.session_state.estados[a])
    st.markdown(f"### 📋 INSCRITOS: {n_total} | ✅ ACTIVOS: {n_activos}")

    # --- LA LISTA (Garantizada) ---
    # Usamos un contenedor dedicado para que la lista siempre se vea
    container_lista = st.container()
    
    with container_lista:
        if not st.session_state.asistentes:
            st.write("_No hay atletas inscritos aún._")
        else:
            for atleta in st.session_state.asistentes:
                c1, c2, c3, c4 = st.columns([4, 1, 1, 1])
                
                # Nombre
                color = "white" if st.session_state.estados[atleta] else "#64748b"
                c1.markdown(f"<p style='font-size: 1.1rem; color: {color}; margin
