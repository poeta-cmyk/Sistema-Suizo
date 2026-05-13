import streamlit as st
import math

# --- 1. CONFIGURACIÓN ---
st.set_page_config(layout="wide", page_title="SISTEMA ADEL")

if 'asistentes' not in st.session_state:
    st.session_state.update({
        'asistentes': [], 
        'juegos_ganados': {}, 
        'efectividad': {}, 
        'puntos_contra': {}, 
        'puntos_favor': {}, 
        'registro_abierto': True, 
        'historial_completo': []
    })

# --- 2. BAREMO LOGARÍTMICO ---
def recalcular_baremo(atleta):
    pf = st.session_state.puntos_favor[atleta]
    pc = st.session_state.puntos_contra[atleta]
    v_f = pf if pf > 0 else 1
    v_c = pc if pc > 0 else 1
    st.session_state.efectividad[atleta] = math.log10(v_f / v_c) + 1

# --- 3. MENÚ ---
with st.sidebar:
    st.title("🏆 MENÚ ADEL")
    opcion = st.radio("SECCIÓN:", ["MESAS", "PANTALLA ADEL"])

# --- 4. SECCIÓN: MESAS (CONTROL Y CARGA) ---
if opcion == "MESAS":
    st.header("Mesa Técnica: Control de Torneo")
    
    if st.session_state.registro_abierto:
        nombre = st.text_input("Nombre del Atleta + ENTER:").upper()
        if nombre and nombre not in st.session_state.asistentes:
            st.session_state.asistentes.append(nombre)
            for k in ['juegos_ganados', 'puntos_contra', 'puntos_favor']: 
                st.session_state[k][nombre] = 0
            st.session_state.efectividad[nombre] = 1.0
            st.rerun()
        
        if st.session_state.asistentes:
            st.write(f"Inscritos ({len(st.session_state.asistentes)}):")
            # SE MUESTRA LA LISTA DE INSCRITOS PARA VALIDAR NOMBRES
            for i, n in enumerate(st.session_state.asistentes):
                st.text(f"{i+1}. {n}")
                
            if st.button("🚀 INICIAR TORNEO"):
                jug = st.session_state.asistentes.copy()
                n_jug = (len(jug) // 4) * 4
                mesas = [jug[i:i+4] for i in range(0, n_jug, 4)]
                st.session_state.historial_completo.append({
                    'ronda': 1, 'mesas': mesas, 'reposo': jug[n_jug:]
                })
                st.session_state.registro_abierto = False
                st.rerun()
    else:
        tab_c, tab_b = st.tabs(["📝 CARGA", "📊 BAREMO"])
        r = st.session_state.historial_completo[-1]
        
        with tab_c:
            for i, m in enumerate(r['mesas']):
                # NOMBRES VISIBLES EN EL TÍTULO DEL EXPANDER
                with st.expander(f"MESA {i+1}: {m[0]}, {m[1]}, {m[2]}, {m[3]}", expanded=True):
                    c1, c2 = st.columns(2)
                    p_ac = c1.number_input(f"A+C ({m[0]}/{m[2]})", key=f"ac_{i}", min_value=0)
                    p_bd = c2.number_input(f"B+D ({m[1]}/{m[3]})", key=f"bd_{i}", min_value=0)
                    
                    if st.button(f"GUARDAR MESA {i+1}", key=f"btn_{i}"):
                        st.session_state.puntos_favor[m[0]] += p_ac; st.session_state.puntos_contra[m[0]] += p_bd
                        st.session_state.puntos_favor[m[2]] += p_ac; st.session_state.puntos_contra[m[2]] += p_bd
                        st.session_state.puntos_favor[m[1]] += p_bd; st.session_state.puntos_contra[m[1]] += p_ac
                        st.session_state.puntos_favor[m[3]] += p_bd; st.session_state.puntos_contra[m[3]] += p_ac
                        if p_ac > p_bd:
                            st.session_state.juegos_ganados[m[0]] += 1; st.session_state.juegos_ganados[m[2]] += 1
                        elif p_bd > p_ac:
                            st.session_state.juegos_ganados[m[1]] += 1; st.session_state.juegos_ganados[m[3]] += 1
                        for a in m: recalcular_baremo(a)
                        st.success("Guardado")

        with tab_b:
            for n in sorted(st.session_state.asistentes, key=lambda x: (st.session_state.juegos_ganados[x], st.session_state.efectividad[x]), reverse=True):
                st.write(f"**{n}** | JG: {st.session_state.juegos_ganados[n]} | Ef: {st.session_state.efectividad[n]:.4f}")

# --- 5. SECCIÓN: PANTALLA ADEL ---
elif opcion == "PANTALLA ADEL":
    st.header("Monitor Oficial ADEL")
    if st.session_state.historial_completo:
        rd = st.session_state.historial_completo[-1]
        if rd['reposo']: st.error(f"⌛ REPOSO: {', '.join(rd['reposo'])}")
        
        for idx, mj in enumerate(rd['mesas']):
            with st.container(border=True):
                st.markdown(f"<h3 style='text-align:center;'>MESA {idx+1}</h3>", unsafe_allow_html=True)
                ca, cm, cd = st.columns([1, 1, 1])
                # NOMBRES EN MONITOR PÚBLICO
                cm.markdown(f"<div style='text-align:center;'><b>A</b><br>{mj[0]}<br><br><b>C</b><br>{mj[2]}</div>", unsafe_allow_html=True)
                ca.markdown(f"<div style='text-align:right;'><br><b>B</b><br>{mj[1]}</div>", unsafe_allow_html=True)
                cd.markdown(f"<div style='text-align:left;'><br><b>D</b><br>{mj[3]}</div>", unsafe_allow_html=True)
