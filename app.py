import streamlit as st
import random

# --- 1. INICIALIZACIÓN DEL ESTADO (Previene el NameError) ---
if 'asistentes' not in st.session_state:
    st.session_state.update({
        'asistentes': [],
        'estados': {},
        'jg': {}, 'jj': {}, 'iep': {}, 'efec': {}, 'dif': {},
        'seccion_activa': "INSCRIPCIÓN",
        'n_rondas': 6,  # Valor por defecto
        'meta_puntos': 200,
        'editando': None
    })

# --- 2. BARRA LATERAL (MENÚ ADEL) ---
with st.sidebar:
    st.title("🏆 MENÚ ADEL")
    opciones = ["INSCRIPCIÓN", "MESAS", "RESULTADOS", "RANKING"]
    st.session_state.seccion_activa = st.radio("SECCIÓN:", opciones)

# --- 3. LÓGICA DE INSCRIPCIÓN ---
if st.session_state.seccion_activa == "INSCRIPCIÓN":
    # Encabezados según su diseño
    st.markdown("<h1 style='text-align: center;'>ASOCIACIÓN DE DOMINÓ DEL ESTADO LARA ADEL</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center;'>SISTEMA SUIZO</h2>", unsafe_allow_html=True)
    
    col_izq, col_der = st.columns([2, 1])

    with col_izq:
        st.session_state.meta_puntos = st.radio("Meta del encuentro:", [100, 200], 
                                                index=1 if st.session_state.meta_puntos == 200 else 0, 
                                                horizontal=True)
        
        # Función para agregar con ENTER
        def registrar():
            txt = st.session_state.nuevo_atleta.upper().strip()
            if txt and txt not in st.session_state.asistentes:
                st.session_state.asistentes.append(txt)
                st.session_state.estados[txt] = True
                for k in ['jg', 'jj', 'iep', 'efec', 'dif']: st.session_state[k][txt] = 0
                st.session_state.asistentes.sort()
            st.session_state.nuevo_atleta = ""

        st.text_input("Nombre del Atleta + ENTER:", key="nuevo_atleta", on_change=registrar)

    with col_der:
        st.markdown("<h3 style='text-align: center;'>NÚMERO DE RONDAS</h3>", unsafe_allow_html=True)
        st.session_state.n_rondas = st.number_input("N", min_value=1, max_value=20, value=st.session_state.n_rondas)

    st.divider()
    
    # Monitor de Atletas
    activos = sum(1 for a in st.session_state.asistentes if st.session_state.estados[a])
    st.subheader(f"📊 ATLETAS: {len(st.session_state.asistentes)} | ACTIVOS: {activos}")

    # Lista de Gestión (CRUD)
    for atleta in st.session_state.asistentes:
        c1, c2, c3, c4 = st.columns([4, 1, 1, 1])
        c1.write(f"**{atleta}**")
        
        # Activo / Retiro
        if c2.button("✅" if st.session_state.estados[atleta] else "💤", key=f"st_{atleta}"):
            st.session_state.estados[atleta] = not st.session_state.estados[atleta]
            st.rerun()
            
        # Editar
        if c3.button("📝", key=f"ed_{atleta}"):
            st.session_state.editando = atleta
            st.rerun()
            
        # Eliminar
        if c4.button("🗑️", key=f"del_{atleta}"):
            st.session_state.asistentes.remove(atleta)
            st.rerun()

    # Modal simple para editar
    if st.session_state.editando:
        with st.form("form_editar"):
            nuevo = st.text_input("Nuevo nombre:", value=st.session_state.editando).upper()
            if st.form_submit_button("ACTUALIZAR"):
                # Lógica de renombrado (se mantiene simple para cerrar hoy)
                idx = st.session_state.asistentes.index(st.session_state.editando)
                st.session_state.asistentes[idx] = nuevo
                st.session_state.editando = None
                st.rerun()

    if st.button("🚀 SORTEAR E IR A MESAS"):
        if activos >= 4:
            st.success(f"Sorteo generado para {st.session_state.n_rondas} rondas.")
            # Aquí iría la lógica del algoritmo Kirkman/Suizo en la próxima sesión
        else:
            st.warning("Faltan atletas para iniciar.")

else:
    st.info(f"Sección {st.session_state.seccion_activa} en construcción. Meta: {st.session_state.meta_puntos} pts.")
