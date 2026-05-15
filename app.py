# --- 3. CUERPO PRINCIPAL: INSCRIPCIÓN (Ajustado) ---
if st.session_state.seccion_activa == "INSCRIPCIÓN":
    # 1. Nombre Institucional Exacto
    st.markdown("<h1 style='text-align: center; color: #deff9a;'>ASOCIACIÓN DE DOMINÓ DEL ESTADO LARA “ADEL”</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center;'>SISTEMA SUIZO</h2>", unsafe_allow_html=True)
    st.divider()

    # Contenedor para parámetros iniciales
    with st.container(border=True):
        col_config1, col_config2 = st.columns(2)
        
        # 2. Número de rondas: N (Ajuste de persistencia)
        st.session_state.n_rondas = col_config1.number_input(
            "Número de rondas (N):", 
            min_value=1, 
            max_value=15, 
            value=st.session_state.n_rondas,
            key="input_n_rondas"
        )
        
        # 3. Selector de la meta del encuentro
        st.session_state.meta_encuentro = col_config2.radio(
            "Meta del encuentro (Puntos):", 
            [100, 200], 
            index=1 if st.session_state.meta_encuentro == 200 else 0, 
            horizontal=True,
            key="input_meta"
        )

    # 4. Recuadro para anotar jugador con ENTER
    def agregar_atleta():
        nom = st.session_state.campo_nom.upper().strip()
        if nom and nom not in st.session_state.asistentes:
            st.session_state.asistentes.append(nom)
            st.session_state.estados[nom] = True
            for k in ['jg', 'jj', 'iep', 'efec', 'dif']: 
                st.session_state[k][nom] = 0
            st.session_state.asistentes.sort() 
        st.session_state.campo_nom = "" 

    st.subheader("Registro de Atletas")
    st.text_input("Nombre del Atleta + [ENTER]:", key="campo_nom", on_change=agregar_atleta)

    # 5. Monitor de Atletas
    n_total = len(st.session_state.asistentes)
    n_activos = sum(1 for n in st.session_state.asistentes if st.session_state.estados[n])
    
    # Estética de aviso profesional
    st.markdown(f"""
    <div style='background-color: #1e293b; padding: 15px; border-radius: 10px; border-left: 5px solid #deff9a;'>
        <h3 style='margin: 0; color: white;'>ATLETAS INSCRITOS: {n_total} | ACTIVOS: {n_activos}</h3>
        <p style='margin: 0; color: #94a3b8;'>Torneo configurado a {st.session_state.n_rondas} rondas.</p>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # 6. Lista de atletas con funciones Editar, Eliminar, Borrar
    if st.session_state.asistentes:
        for nombre in st.session_state.asistentes:
            c_nom, c_est, c_ed, c_el = st.columns([3, 1, 1, 1])
            
            # Formato visual según estado
            status_color = "white" if st.session_state.estados[nombre] else "#64748b"
            c_nom.markdown(f"<span style='color: {status_color};'>{nombre}</span>", unsafe_allow_html=True)
            
            # Cambiar estado (Activo/Retiro)
            if c_est.button("✅" if st.session_state.estados[nombre] else "💤", key=f"st_{nombre}"):
                st.session_state.estados[nombre] = not st.session_state.estados[nombre]
                st.rerun()
                
            # Editar
            if c_ed.button("📝", key=f"ed_{nombre}"):
                st.session_state.editando = nombre
                st.rerun()
                
            # Eliminar/Borrar (Remover del sistema)
            if c_el.button("🗑️", key=f"del_{nombre}"):
                st.session_state.asistentes.remove(nombre)
                for k in ['estados', 'jg', 'jj', 'iep', 'efec', 'dif']: 
                    st.session_state[k].pop(nombre)
                st.rerun()

    # 7. Sorteo y Transición
    st.divider()
    if st.button("🚀 GENERAR SORTEO RONDA 1 E IR A MESAS"):
        activos = [n for n in st.session_state.asistentes if st.session_state.estados[n]]
        if len(activos) >= 4:
            random.shuffle(activos)
            n_m = (len(activos) // 4) * 4
            st.session_state.historial_completo.append({
                'ronda_actual': 1,
                'mesas': [activos[i:i+4] for i in range(0, n_m, 4)],
                'reposo': activos[n_m:],
                'listas': [],
                'reposo_ok': False
            })
            st.session_state.seccion_activa = "MESAS"
            st.rerun()
        else:
            st.error("Se necesitan al menos 4 atletas activos.")
