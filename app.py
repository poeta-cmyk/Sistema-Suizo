import streamlit as st
import math

# --- 1. CONFIGURACIÓN E INICIALIZACIÓN ---
st.set_page_config(layout="wide", page_title="SISTEMA ADEL")

if 'asistentes' not in st.session_state:
    st.session_state.update({
        'asistentes': [], 
        'estados': {}, 
        'juegos_ganados': {}, 
        'efectividad': {}, 
        'puntos_contra': {}, 
        'puntos_favor': {}, 
        'historial_completo': [],
        'editando': None 
    })

# --- 2. BAREMO LOGARÍTMICO ---
def recalcular_baremo(atleta):
    pf = st.session_state.puntos_favor.get(atleta, 0)
    pc = st.session_state.puntos_contra.get(atleta, 0)
    v_f = pf if pf > 0 else 1
    v_c = pc if pc > 0 else 1
    st.session_state.efectividad[atleta] = math.log10(v_f / v_c) + 1

# --- 3. MENÚ ---
with st.sidebar:
    st.title("🏆 MENÚ ADEL")
    opcion = st.radio("SECCIÓN:", ["INSCRIPCIÓN", "MESAS", "RESULTADOS", "RANKING"])

# --- 4. SECCIÓN: INSCRIPCIÓN (SU BASE DATOS BLINDADA) ---
if opcion == "INSCRIPCIÓN":
    st.caption("Creado por Poeta")
    st.header("ASOCIACIÓN DE DOMINÓ DEL ESTADO LARA ADEL SISTEMA SUIZO")
    st.subheader("Control de Nómina y Asistencia")
    
    def procesar_entrada():
        texto = st.session_state.campo_input.upper().strip()
        if texto:
            if st.session_state.editando:
                viejo = st.session_state.editando
                if texto != viejo:
                    idx = st.session_state.asistentes.index(viejo)
                    st.session_state.asistentes[idx] = texto
                    for k in ['estados', 'juegos_ganados', 'puntos_contra', 'puntos_favor', 'efectividad']:
                        st.session_state[k][texto] = st.session_state[k].pop(viejo)
                st.session_state.editando = None
            elif texto not in st.session_state.asistentes:
                st.session_state.asistentes.append(texto)
                st.session_state.estados[texto] = True
                for k in ['juegos_ganados', 'puntos_contra', 'puntos_favor']: 
                    st.session_state[k][texto] = 0
                st.session_state.efectividad[texto] = 1.0
            st.session_state.asistentes.sort()
        st.session_state.campo_input = "" 

    label_dinamico = f"Corrigiendo a: {st.session_state.editando}" if st.session_state.editando else "ATLETA"
    st.text_input(label_dinamico, key="campo_input", on_change=procesar_entrada)
    
    if st.session_state.asistentes:
        activos = [n for n in st.session_state.asistentes if st.session_state.estados[n]]
        st.write(f"### Atletas inscritos: {len(st.session_state.asistentes)} - Activos: {len(activos)}")
        for n in st.session_state.asistentes:
            c_nom, c_act, c_edit, c_del = st.columns([3, 1, 1, 1])
            c_nom.text(f"• {n}")
            if c_act.button("✅ ACTIVO" if st.session_state.estados[n] else "❌ RETIRADO", key=f"st_{n}"):
                st.session_state.estados[n] = not st.session_state.estados[n]; st.rerun()
            if c_edit.button("📝", key=f"ed_{n}"):
                st.session_state.editando = n; st.rerun()
            if c_del.button("🗑️", key=f"br_{n}"):
                st.session_state.asistentes.remove(n); st.rerun()

# --- 5. SECCIÓN: RESULTADOS (AQUÍ ES DONDE ANOTA) ---
elif opcion == "RESULTADOS":
    st.caption("Creado por Poeta")
    st.header("ASOCIACIÓN DE DOMINÓ DEL ESTADO LARA ADEL SISTEMA SUIZO")
    st.subheader("Carga de Resultados Técnicos")
    
    jugadores_activos = [n for n in st.session_state.asistentes if st.session_state.estados[n]]
    
    if st.button("🚀 SORTEAR SIGUIENTE RONDA"):
        if len(jugadores_activos) < 4:
            st.error("Se necesitan al menos 4 atletas activos para sortear.")
        else:
            import random
            random.shuffle(jugadores_activos)
            n_jug = (len(jugadores_activos) // 4) * 4
            mesas = [jugadores_activos[i:i+4] for i in range(0, n_jug, 4)]
            # Guardamos la ronda con espacios vacíos para puntos
            st.session_state.historial_completo.append({
                'ronda': len(st.session_state.historial_completo) + 1, 
                'mesas': mesas, 
                'reposo': jugadores_activos[n_jug:],
                'puntos': {} # Aquí se guardarán los resultados
            })
            st.rerun()

    if st.session_state.historial_completo:
        r_actual = st.session_state.historial_completo[-1]
        st.write(f"## RONDA {r_actual['ronda']}")
        
        for idx, mj in enumerate(r_actual['mesas']):
            with st.expander(f"MESA {idx+1}", expanded=True):
                c1, c2, c3 = st.columns([2, 1, 2])
                
                # Pareja A+C
                p1 = f"{mj[0]} y {mj[2]}"
                val1 = st.number_input(f"Puntos {p1}", min_value=0, max_value=100, key=f"r{r_actual['ronda']}m{idx}p1")
                
                # Pareja B+D
                p2 = f"{mj[1]} y {mj[3]}"
                val2 = st.number_input(f"Puntos {p2}", min_value=0, max_value=100, key=f"r{r_actual['ronda']}m{idx}p2")
                
                if st.button(f"GUARDAR MESA {idx+1}", key=f"btn_m{idx}"):
                    # Lógica para procesar y enviar al Ranking
                    for j en [mj[0], mj[2]]: 
                        st.session_state.puntos_favor[j] += val1
                        st.session_state.puntos_contra[j] += val2
                    for j en [mj[1], mj[3]]: 
                        st.session_state.puntos_favor[j] += val2
                        st.session_state.puntos_contra[j] += val1
                    
                    if val1 > val2:
                        for j en [mj[0], mj[2]]: st.session_state.juegos_ganados[j] += 1
                    elif val2 > val1:
                        for j en [mj[1], mj[3]]: st.session_state.juegos_ganados[j] += 1
                    
                    for j en mj: recalcular_baremo(j)
                    st.success(f"Mesa {idx+1} procesada.")

# --- 6. SECCIÓN: MESAS (VISTA PÚBLICA) ---
elif opcion == "MESAS":
    st.caption("Creado por Poeta")
    st.header("ASOCIACIÓN DE DOMINÓ DEL ESTADO LARA ADEL SISTEMA SUIZO")
    if not st.session_state.historial_completo:
        st.info("No hay mesas activas. Vaya a RESULTADOS para sortear.")
    else:
        r = st.session_state.historial_completo[-1]
        for idx, mj in enumerate(r['mesas']):
            st.subheader(f"MESA {idx+1}")
            st.write(f"Silla A: {mj[0]} | Silla C: {mj[2]}")
            st.write(f"VS")
            st.write(f"Silla B: {mj[1]} | Silla D: {mj[3]}")
            st.divider()

# --- 7. SECCIÓN: RANKING ---
elif opcion == "RANKING":
    st.caption("Creado por Poeta")
    st.header("ASOCIACIÓN DE DOMINÓ DEL ESTADO LARA ADEL SISTEMA SUIZO")
    st.subheader("Clasificación")
    if st.session_state.asistentes:
        # Aquí se mostrará la tabla con los puntos acumulados
        st.write(st.session_state.juegos_ganados)
