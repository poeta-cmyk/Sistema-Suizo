# --- 4. SECCIÓN: INSCRIPCIÓN (Con Contador de Atletas) ---
if st.session_state.seccion_activa == "INSCRIPCIÓN":
    st.header("ASOCIACIÓN DE DOMINÓ DEL ESTADO LARA ADEL")
    
    st.session_state.meta_encuentro = st.radio("Meta del encuentro:", [100, 200], 
                                              index=1 if st.session_state.meta_encuentro == 200 else 0, 
                                              horizontal=True)

    def agregar_atleta():
        nom = st.session_state.campo_nom.upper().strip()
        if nom and nom not in st.session_state.asistentes:
            st.session_state.asistentes.append(nom)
            st.session_state.estados[nom] = True
            for k in ['jg', 'jj', 'iep', 'efec', 'dif']:
                st.session_state[k][nom] = 0
            st.session_state.asistentes.sort() 
        st.session_state.campo_nom = "" 

    st.text_input("Nombre del Atleta + ENTER:", key="campo_nom", on_change=agregar_atleta)

    # --- EL AJUSTE SOLICITADO: CONTADOR DE JUGADORES ---
    total_inscritos = len(st.session_state.asistentes)
    total_activos = len([n for n in st.session_state.asistentes if st.session_state.estados[n]])
    
    col_info1, col_info2 = st.columns(2)
    col_info1.metric("TOTAL INSCRITOS", f"{total_inscritos} Atletas")
    col_info2.metric("LISTOS PARA MESA", f"{total_activos} Atletas")
    
    st.divider()
    
    # Gestión de lista con botones de acción
    for nombre in st.session_state.asistentes:
        col_nom, col_check, col_edit, col_del = st.columns([3, 1, 1, 1])
        
        # Nombre y Estado
        status_icon = "👤" if st.session_state.estados[nombre] else "💤"
        col_nom.write(f"{status_icon} **{nombre}**")
        
        # Botón para Retirar/Activar (Cambia el estado sin borrar datos)
        if col_check.button("✅" if st.session_state.estados[nombre] else "❌", key=f"st_{nombre}"):
            st.session_state.estados[nombre] = not st.session_state.estados[nombre]
            st.rerun()
        
        # Editar Nombre
        if col_edit.button("📝", key=f"ed_{nombre}"):
            st.session_state.editando = nombre
            st.rerun()
            
        # Eliminar por completo (Error de inscripción)
        if col_del.button("🗑️", key=f"del_{nombre}"):
            st.session_state.asistentes.remove(nombre)
            st.rerun()

    # Formulario de Edición (Modal)
    if st.session_state.editando:
        with st.container(border=True):
            st.subheader(f"Editando: {st.session_state.editando}")
            nuevo_n = st.text_input("Nuevo nombre:", value=st.session_state.editando).upper()
            c_ed1, c_ed2 = st.columns(2)
            if c_ed1.button("ACEPTAR CAMBIO"):
                v = st.session_state.editando
                idx = st.session_state.asistentes.index(v)
                st.session_state.asistentes[idx] = nuevo_n
                for k in ['estados', 'jg', 'jj', 'iep', 'efec', 'dif']:
                    st.session_state[k][nuevo_n] = st.session_state[k].pop(v)
                st.session_state.editando = None
                st.session_state.asistentes.sort()
                st.rerun()
            if c_ed2.button("CANCELAR"):
                st.session_state.editando = None
                st.rerun()

    st.divider()
    if st.button("🚀 SORTEAR E IR A MESAS"):
        activos = [n for n in st.session_state.asistentes if st.session_state.estados[n]]
        if len(activos) >= 4:
            random.shuffle(activos)
            n_m = (len(activos) // 4) * 4
            st.session_state.historial_completo.append({
                'mesas': [activos[i:i+4] for i in range(0, n_m, 4)],
                'reposo': activos[n_m:], 'listas': [], 'reposo_ok': False
            })
            st.session_state.seccion_activa = "MESAS"; st.rerun()
        else:
            st.warning("Se requieren al menos 4 jugadores activos para iniciar.")
