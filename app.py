import streamlit as st
import random

# --- 1. CONFIGURACIÓN INICIAL (Blindaje contra errores) ---
st.set_page_config(page_title="SISTEMA SUIZO ADEL", layout="wide")

# Inicializamos el diccionario de datos si no existe
if 'inicializado' not in st.session_state:
    st.session_state.update({
        'inicializado': True,
        'asistentes': [],
        'estados': {},
        'meta_puntos': 200,
        'n_rondas': 6,
        'seccion': "INSCRIPCIÓN",
        'editando': None
    })

# --- 2. MENÚ LATERAL ---
with st.sidebar:
    st.title("🏆 MENÚ ADEL")
    st.session_state.seccion = st.radio(
        "SECCIÓN:", 
        ["INSCRIPCIÓN", "MESAS", "RESULTADOS", "RANKING"],
        index=0
    )

# --- 3. SECCIÓN DE INSCRIPCIÓN ---
if st.session_state.seccion == "INSCRIPCIÓN":
    st.markdown("<h1 style='text-align: center;'>ASOCIACIÓN DE DOMINÓ DEL ESTADO LARA ADEL</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center;'>SISTEMA SUIZO</h2>", unsafe_allow_html=True)
    
    col_izq, col_der = st.columns([2, 1])

    with col_izq:
        # Selector de Meta (Funciona sin NameError ahora)
        st.session_state.meta_puntos = st.radio(
            "Meta del encuentro:", [100, 200], 
            index=1 if st.session_state.meta_puntos == 200 else 0, 
            horizontal=True
        )
        
        # Función para registrar atletas con ENTER
        def registrar_atleta():
            nombre = st.session_state.campo_registro.upper().strip()
            if nombre and nombre not in st.session_state.asistentes:
                st.session_state.asistentes.append(nombre)
                st.session_state.estados[nombre] = True
                st.session_state.asistentes.sort()
            st.session_state.campo_registro = ""

        st.text_input("Nombre del Atleta + ENTER:", key="campo_registro", on_change=registrar_atleta)

    with col_der:
        st.markdown("<h3 style='text-align: center;'>NÚMERO DE RONDAS</h3>", unsafe_allow_html=True)
        # Sincronización del número de rondas N
        st.session_state.n_rondas = st.number_input("N", min_value=1, max_value=20, value=st.session_state.n_rondas)

    st.divider()
    
    # Monitor de Atletas Activos
    num_total = len(st.session_state.asistentes)
    num_activos = sum(1 for a in st.session_state.asistentes if st.session_state.estados[a])
    st.subheader(f"📊 ATLETAS: {num_total} | ACTIVOS: {num_activos}")

    # Gestión de la Nómina (Iconos de sus capturas)
    for atleta in st.session_state.asistentes:
        c1, c2, c3, c4 = st.columns([4, 1, 1, 1])
        c1.write(f"**{atleta}**")
        
        # Estado (Activo/Retirado)
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

    # Formulario de edición si se activa
    if st.session_state.editando:
        with st.form("edicion"):
            nuevo_nombre = st.text_input("Corregir nombre:", value=st.session_state.editando).upper()
            if st.form_submit_button("GUARDAR"):
                idx = st.session_state.asistentes.index(st.session_state.editando)
                st.session_state.asistentes[idx] = nuevo_nombre
                st.session_state.editando = None
                st.session_state.asistentes.sort()
                st.rerun()

    if st.button("🚀 SORTEAR E IR A MESAS"):
        if num_activos >= 4:
            st.success(f"Torneo configurado: {st.session_state.n_rondas} rondas a {st.session_state.meta_puntos} pts.")
        else:
            st.warning("Se necesitan al menos 4 atletas activos.")

else:
    st.info(f"Sección de {st.session_state.seccion} en construcción. Configuración: {st.session_state.n_rondas} rondas.")
