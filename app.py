# --- 5. SECCIÓN: RESULTADOS (Corregida para ignorar el Reposo) ---
elif st.session_state.seccion_activa == "RESULTS":
    st.header("Carga de Resultados")
    if st.session_state.historial_completo:
        r = st.session_state.historial_completo[-1]
        
        # Verificamos que existan mesas creadas
        if not r['mesas']:
            st.warning("No hay mesas activas para esta ronda.")
        else:
            for i, m in enumerate(r['mesas']):
                # Solo mostramos la mesa si no ha sido procesada aún
                if i not in r['listas']:
                    with st.expander(f"MESA {i+1}", expanded=True):
                        c1, c2 = st.columns(2)
                        # Emparejamientos fijos según la visual de las mesas
                        v1 = c1.number_input(f"PUNTOS A-C ({m[0]} / {m[2]}):", 0, 250, key=f"v1_{i}")
                        v2 = c2.number_input(f"PUNTOS B-D ({m[1]} / {m[3]}):", 0, 250, key=f"v2_{i}")
                        
                        if st.button(f"REGISTRAR MESA {i+1}", key=f"b_{i}"):
                            # Sumar puntos a la pareja A-C
                            for j in [m[0], m[2]]:
                                st.session_state.puntos_favor[j] += v1
                                st.session_state.puntos_contra[j] += v2
                                if v1 > v2: st.session_state.juegos_ganados[j] += 1
                            
                            # Sumar puntos a la pareja B-D
                            for j in [m[1], m[3]]:
                                st.session_state.puntos_favor[j] += v2
                                st.session_state.puntos_contra[j] += v1
                                if v2 > v1: st.session_state.juegos_ganados[j] += 1
                            
                            # Recalcular efectividad de los 4 jugadores
                            for j in m: 
                                recalcular_baremo(j)
                            
                            # Marcar mesa como lista para que desaparezca de esta vista
                            r['listas'].append(i)
                            st.rerun()
            
            # Mensaje de control si ya se cargaron todas las mesas
            if len(r['listas']) == len(r['mesas']):
                st.success("✅ Todos los resultados de la ronda han sido procesados.")
