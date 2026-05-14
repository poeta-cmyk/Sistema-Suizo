# --- 3. SECCIÓN: INSCRIPCIÓN ---
if st.session_state.seccion_activa == "INSCRIPCIÓN":
    st.header("ASOCIACIÓN DE DOMINÓ DEL ESTADO LARA ADEL")
    
    st.session_state.meta_encuentro = st.radio("Meta del encuentro:", [100, 200], 
                                              index=1 if st.session_state.meta_encuentro == 200 else 0, 
                                              horizontal=True)

    # Función que se activa con el ENTER
    def procesar_atleta():
        nuevo_nombre = st.session_state.nuevo_atleta.upper().strip()
        if nuevo_nombre and nuevo_nombre not in st.session_state.asistentes:
            st.session_state.asistentes.append(nuevo_nombre)
            # Inicializar sus baremos ADEL
            st.session_state.estados[nuevo_nombre] = True
            for k in ['jg', 'jj', 'iep', 'efec', 'dif']:
                st.session_state[k][nuevo_nombre] = 0
            # Reordenar alfabéticamente tras cada ingreso
            st.session_state.asistentes.sort()
        # Blanquear el campo para el siguiente
        st.session_state.nuevo_atleta = ""

    st.text_input("Nombre del Atleta + ENTER:", key="nuevo_atleta", on_change=procesar_atleta)

    st.divider()
    
    # Listado con Gestión de Botones
    for nombre in st.session_state.asistentes:
        c1, c2, c3, c4 = st.columns([3, 1, 1, 1])
        
        # Estado visual: Si está retirado se ve distinto
        label = f"👤 {nombre}" if st.session_state.estados[nombre] else f"🚫 {nombre} (RETIRADO)"
        c1.markdown(f"**{label}**")
        
        # Botón de Activo/Retirado (Para que no juegue más pero mantenga números)
        if c2.button("✅" if st.session_state.estados[nombre] else "💤", key=f"state_{nombre}"):
            st.session_state.estados[nombre] = not st.session_state.estados[nombre]
            st.rerun()

        # Botón Editar
        if c3.button("📝", key=f"edit_{nombre}"):
            st.session_state.editando = nombre
            st.rerun()

        # Botón Eliminar (Solo usar antes de sorteo o para errores críticos)
        if c4.button("🗑️", key=f"del_{nombre}"):
            st.session_state.asistentes.remove(nombre)
            st.rerun()

    # Ventana Emergente de Edición (Modal)
    if st.session_state.editando:
        with st.form("form_edicion"):
            nuevo_valor = st.text_input("Corregir nombre:", value=st.session_state.editando).upper()
            if st.form_submit_state("GUARDAR CAMBIOS"):
                # Lógica para renombrar llaves en el diccionario y mantener puntos
                viejo = st.session_state.editando
                idx = st.session_state.asistentes.index(viejo)
                st.session_state.asistentes[idx] = nuevo_valor
                for k in ['estados', 'jg', 'jj', 'iep', 'efec', 'dif']:
                    st.session_state[k][nuevo_valor] = st.session_state[k].pop(viejo)
                st.session_state.editando = None
                st.session_state.asistentes.sort()
                st.rerun()

    st.divider()
    activos = [n for n in st.session_state.asistentes if st.session_state.estados[n]]
    st.info(f"Atletas en nómina: {len(st.session_state.asistentes)} | Listos para jugar: {len(activos)}")
