# --- PANTALLA PRINCIPAL ---

if st.session_state.lanzar_globos:
    st.balloons(); st.session_state.lanzar_globos = False

if st.session_state.registro_abierto:
    st.header("📝 Registro de Atletas")
    st.session_state.meta_puntos = st.radio("Meta del Encuentro:", [100, 200], horizontal=True)
    st.text_input("Escribe el nombre y presiona ENTER:", key="nuevo_nombre", on_change=agregar_jugador_enter)
    
    if st.session_state.asistentes:
        st.write(f"**Inscritos ({len(st.session_state.asistentes)}):** {', '.join(st.session_state.asistentes)}")
        col_el1, col_el2, col_el3 = st.columns([3, 0.5, 0.5])
        with col_el1: 
            seleccionado = st.selectbox("Seleccione Atleta para gestionar:", st.session_state.asistentes, key="atleta_gestion")
        with col_el2: 
            if st.button("✏️", help="Editar nombre"): editar_atleta_dialog(seleccionado)
        with col_el3:
            if st.button("🗑️", help="Eliminar Atleta"):
                st.session_state.asistentes.remove(seleccionado)
                st.session_state.asistentes.sort()
                st.rerun()
                
    if st.button("🚀 EMPEZAR TORNEO") and len(st.session_state.asistentes) >= 4:
        st.session_state.registro_abierto = False; generar_ronda_suiza(); st.rerun()
else:
    # Pantalla de Juego y Ranking
    r_max = math.ceil(math.log2(len(st.session_state.asistentes)))
    
    if not st.session_state.torneo_finalizado:
        opciones_ronda = list(range(1, st.session_state.ronda_actual + 1))
        ronda_a_ver = st.selectbox("🔍 Ver Ronda:", opciones_ronda, index=len(opciones_ronda)-1)
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Ronda", f"{st.session_state.ronda_actual}/{r_max}")
        c2.metric("Meta", st.session_state.meta_puntos)
        c3.metric("Jugadores", len(st.session_state.asistentes))
        c4.metric("En Reposo", len(st.session_state.asistentes) % 4)

        with st.expander("📊 RANKING ACTUAL", expanded=False):
            ranking_temp = sorted(st.session_state.asistentes, key=lambda x: (st.session_state.juegos_ganados.get(x,0), st.session_state.efectividad.get(x,0), -st.session_state.puntos_contra.get(x,0)), reverse=True)
            st.table([{"Pos": i+1, "Jugador": j, "G": st.session_state.juegos_ganados.get(j, 0), "Ef": st.session_state.efectividad.get(j, 0), "Pts-": st.session_state.puntos_contra.get(j, 0)} for i, j in enumerate(ranking_temp)])

        st.markdown("---")
        datos_ronda = next((item for item in st.session_state.historial_mesas if item['ronda'] == ronda_a_ver), None)
        if datos_ronda:
            for i, m in enumerate(datos_ronda['mesas']):
                col1, col2, col3 = st.columns([2, 1, 2])
                with col1: st.info(f"{m[0]} y {m[2]}")
                with col2: 
                    disponible = ronda_a_ver == st.session_state.ronda_actual
                    st.number_input("Pts", key=f"p_izq_{i}_{ronda_a_ver}", min_value=0, disabled=not disponible)
                    st.markdown(f"<center><b>Mesa {i+1}</b></center>", unsafe_allow_html=True)
                    st.number_input("Pts", key=f"p_der_{i}_{ronda_a_ver}", min_value=0, disabled=not disponible)
                with col3: st.success(f"{m[1]} y {m[3]}")
            if datos_ronda['reposo']: st.warning(f"💤 **EN REPOSO:** {', '.join(datos_ronda['reposo'])}")
        
        if st.session_state.ronda_actual == ronda_a_ver:
            if st.button(f"💾 Registrar Ronda {st.session_state.ronda_actual}"): finalizar_ronda()
    else:
        st.header("🥇 POSICIONES FINALES")
        ranking_final = sorted(st.session_state.asistentes, key=lambda x: (st.session_state.juegos_ganados.get(x,0), st.session_state.efectividad.get(x,0), -st.session_state.puntos_contra.get(x,0)), reverse=True)
        st.table([{"Pos": i+1, "Jugador": j, "G": st.session_state.juegos_ganados.get(j, 0), "Ef": st.session_state.efectividad.get(j, 0), "Pts-": st.session_state.puntos_contra.get(j, 0)} for i, j in enumerate(ranking_final)])
