def generar_ronda_suiza():
    # 1. ORDENAR DE MAYOR A MENOR (MÉRITO PURO)
    jugadores = sorted(st.session_state.asistentes, 
                      key=lambda x: st.session_state.historial_puntos[x], 
                      reverse=True)
    
    # En ronda 1, el azar manda para romper el orden alfabético
    if st.session_state.ronda_actual == 1:
        random.shuffle(jugadores)
    
    n_mesas = len(jugadores) // 4
    mesas_generadas = []
    disponibles = jugadores.copy()
    
    for i in range(n_mesas):
        mesa = []
        
        # JUGADOR A: El primero disponible (el de más puntos)
        a = disponibles.pop(0)
        mesa.append(a)
        
        # JUGADOR C (Pareja de A): Buscamos al siguiente con más puntos que NO haya sido su pareja
        c_idx = -1
        for j, candidato in enumerate(disponibles):
            if {a, candidato} not in st.session_state.parejas_previas:
                c_idx = j
                break
        
        if c_idx != -1:
            c = disponibles.pop(c_idx)
            st.session_state.parejas_previas.append({a, c})
        else:
            # Si ya jugó con todos los disponibles, toma al siguiente por obligación
            c = disponibles.pop(0) 
            
        # JUGADOR B: El siguiente con más puntos disponible (Rival 1)
        b = disponibles.pop(0)
        
        # JUGADOR D (Pareja de B): Buscamos al siguiente que NO haya sido pareja de B
        d_idx = -1
        for k, candidato in enumerate(disponibles):
            if {b, candidato} not in st.session_state.parejas_previas:
                d_idx = k
                break
        
        if d_idx != -1:
            d = disponibles.pop(d_idx)
            st.session_state.parejas_previas.append({b, d})
        else:
            d = disponibles.pop(0)

        # Mesa queda: [A (Líder 1), B (Líder 2), C (Socio de A), D (Socio de B)]
        # En tu espejo: IZQ (A/C) vs DER (B/D)
        mesas_generadas.append([a, b, c, d])
        
    st.session_state.mesas_actuales = mesas_generadas
    st.session_state.jugadores_pausa = disponibles # Los de menor puntaje quedan en pausa
    
    # Asignar puntos por pausa
    meta = st.session_state.meta_puntos
    for p in st.session_state.jugadores_pausa:
        st.session_state.historial_puntos[p] += meta
