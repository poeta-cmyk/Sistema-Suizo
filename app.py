# --- 5. SECCIÓN: RESULTADOS (Lógica de Puntuación por Reposo) ---
elif st.session_state.seccion_activa == "RESULTADOS":
    st.header("Carga de Resultados")
    if st.session_state.historial_completo:
        r = st.session_state.historial_completo[-1]
        
        # Obtener la meta del encuentro (por defecto 200 si no se encuentra)
        meta = st.session_state.get('meta_encuentro', 200)
        puntos_reposo = meta // 2

        # Procesar victorias automáticas con puntos (Mitad de la Meta a 0)
        if r.get('reposo') and not r.get('reposo_procesado'):
            for p in r['reposo']:
                st.session_state.juegos_ganados[p] += 1
                st.session_state.puntos_favor[p] += puntos_reposo
                st.session_state.puntos_contra[p] += 0
                recalcular_baremo(p)
            r['reposo_procesado'] = True

        # Mostrar indicador de victoria por reposo con el marcador calculado
        if r.get('reposo'):
            for p in r['reposo']:
                st.markdown(f'''
                    <div class="victoria-reposo">
                        🏆 {p}: Gana por Reposo ({puntos_reposo} a 0)
                    </div>
                ''', unsafe_allow_html=True)
            st.divider()

        # Carga de mesas... (el resto del código se mantiene igual)
