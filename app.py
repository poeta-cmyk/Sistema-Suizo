import streamlit as st

# --- 1. CONFIGURACIÓN E INICIALIZACIÓN ---
st.set_page_config(layout="wide", page_title="ADEL SISTEMA SUIZO")

# Inicializamos el estado para evitar errores de variables perdidas
if 'asistentes' not in st.session_state:
    st.session_state.update({
        'asistentes': [],
        'estados': {},
        'meta_puntos': 200,
        'seccion': "INSCRIPCIÓN",
        'editando': None
    })

# --- 2. MENÚ LATERAL ---
with st.sidebar:
    st.title("🏆 MENÚ ADEL")
    st.session_state.seccion = st.radio("VENTANAS:", ["INSCRIPCIÓN", "MESAS", "RESULTADOS", "RANKING"])

# --- 3. SECCIÓN DE INSCRIPCIÓN ---
if st.session_state.seccion == "INSCRIPCIÓN":
    st.markdown("<h1 style='text-align: center;'>ASOCIACIÓN DE DOMINÓ DEL ESTADO LARA “ADEL”</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center;'>SISTEMA SUIZO</h2>", unsafe_allow_html=True)
    st.divider()

    col_reg, col_meta = st.columns([2, 1])

    with col_reg:
        def registrar():
            nom = st.session_state.input_nombre.upper().strip()
            if nom and nom not in st.session_state.asistentes:
                st.session_state.asistentes.append(nom)
                st.session_state.estados[nom] = True
                st.session_state.asistentes.sort()
            st.session_state.input_nombre = ""

        st.text_input("Nombre del Atleta + ENTER:", key="input_nombre", on_change=registrar)

    with col_meta:
        st.session_state.meta_puntos = st.radio("Meta del encuentro:", [100, 200], 
                                                index=1 if st.session_state.meta_puntos == 200 else 0, 
                                                horizontal=True)

    st.divider()
    
    # Monitor de Conteo
    total = len(st.session_state.asistentes)
    activos = sum(1 for a in st.session_state.asistentes if st.session_state.estados[a])
    st.markdown(f"### 📋 INSCRITOS: {total} | ✅ ACTIVOS: {activos}")

    # --- 4. LA LISTA DE ATLETAS (Garantizada) ---
    if not st.session_state.asistentes:
        st.info("Nómina vacía. Ingrese nombres arriba para comenzar.")
    else:
        # Encabezados de tabla
        h1, h2, h3, h4 = st.columns([4, 1, 1, 1])
        h1.write("**NOMBRE DEL ATLETA**")
        h2.write("**ESTADO**")
        h3.write("**EDITAR**")
        h4.write("**BORRAR**")

        for atleta in st.session_state.asistentes:
            c1, c2, c3, c4 = st.columns([4, 1, 1, 1])
            
            # Nombre
            color = "white" if st.session_state.estados[atleta] else "#64748b"
            c1.markdown(f"<p style='font-size: 1.1rem; color: {color}; margin: 5px 0;'>{atleta}</p>", unsafe_allow_html=True)
            
            # Botón Estado (Check)
            if c2.button("✅" if st.session_state.estados[atleta] else "💤", key=f"st_{atleta}"):
                st.session_state.estados[atleta] = not st.session_state.estados[atleta]
                st.rerun()
                
            # Botón Editar (Lápiz)
            if c3.button("📝", key=f"ed_{atleta}"):
                st.session_state.editando = atleta
                st.rerun()
                
            # Botón Borrar (Papelera)
            if c4.button("🗑️", key=f"del_{atleta}"):
                st.session_state.asistentes.remove(atleta)
                st.session_state.estados.pop(atleta)
                st.rerun()

    # Formulario para editar si se activa
    if st.session_state.editando:
        st.divider()
        with st.container(border=True):
            st.warning(f"Corrigiendo a: {st.session_state.editando}")
            nuevo_nom = st.text_input("Nuevo nombre:", value=st.session_state.editando).upper()
            if st.button("GUARDAR CAMBIO"):
                idx = st.session_state.asistentes.index(st.session_state.editando)
                st.session_state.asistentes[idx] = nuevo_nom
                st.session_state.estados[nuevo_nom] = st.session_state.estados.pop(st.session_state.editando)
                st.session_state.editando = None
                st.session_state.asistentes.sort()
                st.rerun()

    st.divider()
    if st.button("🚀 GENERAR SORTEO"):
        if activos >= 4:
            st.success("Sorteo listo.")
        else:
            st.error("Se necesitan al menos 4 activos.")
