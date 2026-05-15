import streamlit as st

# --- 1. CONFIGURACIÓN E INICIALIZACIÓN (Blindaje total) ---
st.set_page_config(layout="wide", page_title="ADEL SISTEMA SUIZO")

if 'inicializado' not in st.session_state:
    st.session_state.update({
        'inicializado': True,
        'asistentes': [],
        'estados': {},
        'meta_puntos': 200,
        'seccion': "INSCRIPCIÓN",
        'editando': None
    })

# --- 2. NAVEGACIÓN LATERAL (MENÚ ADEL) ---
with st.sidebar:
    st.title("🏆 MENÚ ADEL")
    st.session_state.seccion = st.radio(
        "VENTANAS:", 
        ["INSCRIPCIÓN", "MESAS", "RESULTADOS", "RANKING"]
    )

# --- 3. SECCIÓN DE INSCRIPCIÓN (LA PORTADA) ---
if st.session_state.seccion == "INSCRIPCIÓN":
    # Cuerpo Principal: Identidad Institucional
    st.markdown("<h1 style='text-align: center; color: #deff9a;'>ASOCIACIÓN DE DOMINÓ DEL ESTADO LARA “ADEL”</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center;'>SISTEMA SUIZO</h2>", unsafe_allow_html=True)
    st.divider()

    # Layout de Registro y Meta
    col_izq, col_der = st.columns([2, 1])

    with col_izq:
        # Registro de atletas con ENTER
        def registrar():
            txt = st.session_state.nuevo_atleta.upper().strip()
            if txt and txt not in st.session_state.asistentes:
                st.session_state.asistentes.append(txt)
                st.session_state.estados[txt] = True
                st.session_state.asistentes.sort()
            st.session_state.nuevo_atleta = ""

        st.text_input("Nombre del Atleta + ENTER:", key="nuevo_atleta", on_change=registrar)

    with col_der:
        # Selector de Meta (Sigue siendo esencial para el sistema)
        st.session_state.meta_puntos = st.radio(
            "Meta del encuentro:", [100, 200], 
            index=1 if st.session_state.meta_puntos == 200 else 0, 
            horizontal=True
        )

    st.divider()
    
    # 5. Monitor de Atletas Inscritos y Activos
    n_total = len(st.session_state.asistentes)
    n_activos = sum(1 for a in st.session_state.asistentes if st.session_state.estados[a])
    
    st.markdown(f"""
        <div style='background-color: #1e293b; padding: 10px; border-radius: 10px; text-align: center; border: 1px solid #deff9a;'>
            <h3 style='margin: 0; color: white;'>ATLETAS INSCRITOS: {n_total} | ACTIVOS: {n_activos}</h3>
        </div>
    """, unsafe_allow_html=True)

    st.write("") # Espaciador

    # 6. Lista de Atletas (Eliminar, Editar, Borrar)
    for atleta in st.session_state.asistentes:
        c1, c2, c3, c4 = st.columns([4, 1, 1, 1])
        
        # Nombre del atleta (se atenúa si está en retiro/pausa)
        color = "white" if st.session_state.estados[atleta] else "#64748b"
        c1.markdown(f"<p style='font-size: 1.2rem; font-weight: bold; color: {color};'>{atleta}</p>", unsafe_allow_html=True)
        
        # Botón de Estado
        if c2.button("✅" if st.session_state.estados[atleta] else "💤", key=f"st_{atleta}", help="Activo/Retiro"):
            st.session_state.estados[atleta] = not st.session_state.estados[atleta]
            st.rerun()
            
        # Botón Editar
        if c3.button("📝", key=f"ed_{atleta}", help="Corregir nombre"):
            st.session_state.editando = atleta
            st.rerun()
            
        # Botón Eliminar
        if c4.button("🗑️", key=f"del_{atleta}", help="Eliminar de la lista"):
            st.session_state.asistentes.remove(atleta)
            st.session_state.estados.pop(atleta)
            st.rerun()

    # Modal para edición de nombre
    if st.session_state.editando:
        with st.form("form_edicion"):
            nuevo = st.text_input("Corregir nombre:", value=st.session_state.editando).upper()
            if st.form_submit_button("ACTUALIZAR"):
                idx = st.session_state.asistentes.index(st.session_state.editando)
                st.session_state.asistentes[idx] = nuevo
                st.session_state.estados[nuevo] = st.session_state.estados.pop(st.session_state.editando)
                st.session_state.editando = None
                st.session_state.asistentes.sort()
                st.rerun()

    st.divider()

    # 7. Botón de acción final
    if st.button("🚀 GENERAR SORTEO Y PASAR A MESAS"):
        if n_activos >= 4:
            st.success("Sorteo realizado con éxito. Redirigiendo...")
            # Aquí saltará a la lógica de MESAS en el futuro
        else:
            st.error("Se necesitan al menos 4 atletas activos para iniciar.")

else:
    # Aviso para las otras pestañas
    st.info(f"Sección de {st.session_state.seccion} lista para recibir la lógica de sorteo.")
