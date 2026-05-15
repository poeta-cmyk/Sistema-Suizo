import streamlit as st

# --- 1. CONFIGURACIÓN E INICIALIZACIÓN (Blindaje contra NameError) ---
st.set_page_config(layout="wide", page_title="ADEL SISTEMA SUIZO")

if 'inicializado' not in st.session_state:
    st.session_state.update({
        'inicializado': True,
        'asistentes': [],
        'estados': {},
        'meta_puntos': 200,
        'n_rondas': 5,
        'seccion': "INSCRIPCIÓN",
        'editando': None
    })

# --- 2. NAVEGACIÓN LATERAL ---
with st.sidebar:
    st.title("🏆 MENÚ ADEL")
    st.session_state.seccion = st.radio("VENTANAS:", ["INSCRIPCIÓN", "MESAS", "RESULTADOS", "RANKING"])

# --- 3. SECCIÓN DE INSCRIPCIÓN ---
if st.session_state.seccion == "INSCRIPCIÓN":
    st.markdown("<h1 style='text-align: center;'>ASOCIACIÓN DE DOMINÓ DEL ESTADO LARA “ADEL”</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center;'>SISTEMA SUIZO</h2>", unsafe_allow_html=True)
    st.divider()

    col_izq, col_der = st.columns([2, 1])

    with col_izq:
        # Selector de Meta (Persistente)
        st.session_state.meta_puntos = st.radio("Meta del encuentro:", [100, 200], 
                                                index=1 if st.session_state.meta_puntos == 200 else 0, 
                                                horizontal=True)
        
        # Registro con ENTER (Corregido SyntaxError)
        def registrar():
            txt = st.session_state.nuevo_atleta.upper().strip()
            if txt and txt not in st.session_state.asistentes:
                st.session_state.asistentes.append(txt)
                st.session_state.estados[txt] = True
                st.session_state.asistentes.sort()
            st.session_state.nuevo_atleta = ""

        st.text_input("Nombre del Atleta + ENTER:", key="nuevo_atleta", on_change=registrar)

    with col_der:
        # Control total de N (Usted decide las rondas)
        st.markdown("<h3 style='text-align: center;'>NÚMERO DE RONDAS</h3>", unsafe_allow_html=True)
        st.session_state.n_rondas = st.number_input("N:", min_value=1, max_value=20, value=st.session_state.n_rondas)

    st.divider()
    
    # Monitor de Atletas
    n_total = len(st.session_state.asistentes)
    n_activos = sum(1 for a in st.session_state.asistentes if st.session_state.estados[a])
    st.subheader(f"📊 ATLETAS: {n_total} | ACTIVOS: {n_activos}")

    # Lista de Gestión (Botones de sus capturas)
    for atleta in st.session_state.asistentes:
        c1, c2, c3, c4 = st.columns([4, 1, 1, 1])
        c1.write(f"**{atleta}**")
        
        if c2.button("✅" if st.session_state.estados[atleta] else "💤", key=f"st_{atleta}"):
            st.session_state.estados[atleta] = not st.session_state.estados[atleta]
            st.rerun()
            
        if c3.button("📝", key=f"ed_{atleta}"):
            st.session_state.editando = atleta
            st.rerun()
            
        if c4.button("🗑️", key=f"del_{atleta}"):
            st.session_state.asistentes.remove(atleta)
            st.rerun()

    # Modal para editar nombre
    if st.session_state.editando:
        with st.form("form_edit"):
            nuevo = st.text_input("Nuevo nombre:", value=st.session_state.editando).upper()
            if st.form_submit_button("ACTUALIZAR"):
                idx = st.session_state.asistentes.index(st.session_state.editando)
                st.session_state.asistentes[idx] = nuevo
                st.session_state.editando = None
                st.session_state.asistentes.sort()
                st.rerun()

    if st.button("🚀 SORTEAR E IR A MESAS"):
        if n_activos >= 4:
            st.success(f"Torneo de {st.session_state.n_rondas} rondas a {st.session_state.meta_puntos} pts.")
        else:
            st.error("Se necesitan más atletas activos.")
