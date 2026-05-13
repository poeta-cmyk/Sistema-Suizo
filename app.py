import streamlit as st
import math

# --- 1. CONFIGURACIÓN Y MEMORIA ---
st.set_page_config(layout="wide", page_title="SISTEMA ADEL - PRO")

if 'asistentes' not in st.session_state:
    st.session_state.update({
        'asistentes': [], 'juegos_ganados': {}, 'efectividad': {}, 
        'puntos_contra': {}, 'puntos_favor': {}, 'ronda_actual': 1,
        'registro_abierto': True, 'historial_completo': [], 'tarjetas': {}
    })

# --- 2. BAREMO LOGARÍTMICO ADEL ---
def recalcular_baremo(atleta):
    pf = st.session_state.puntos_favor[atleta]
    pc = st.session_state.puntos_contra[atleta]
    # Base 1 para evitar errores de log(0)
    v_f = pf if pf > 0 else 1
    v_c = pc if pc > 0 else 1
    st.session_state.efectividad[atleta] = math.log10(v_f / v_c) + 1

# --- 3. NAVEGACIÓN RECTIFICADA ---
with st.sidebar:
    st.title("🏆 MENÚ ADEL")
    # Estas etiquetas ahora están amarradas a la lógica de abajo
    seccion = st.radio("SELECCIONAR PANEL:", ["CONFIGURACIÓN Y CARGA", "MONITOR PÚBLICO"])

# --- 4. PANEL TÉCNICO (CONFIGURACIÓN Y CARGA) ---
if seccion == "CONFIGURACIÓN Y CARGA":
    st.header("Mesa Técnica: Control de Torneo")
    
    if st.session_state.registro_abierto:
        st.subheader("Inscripción de Atletas")
        atleta_nuevo = st.text_input("Nombre del Atleta + ENTER:").upper()
        if atleta_nuevo and atleta_nuevo not in st.session_state.asistentes:
            st.session_state.asistentes.append(atleta_nuevo)
            for k in ['juegos_ganados', 'puntos_contra', 'puntos_favor']: 
                st.session_state[k][atleta_nuevo] = 0
            st.session_state.efectividad[atleta_nuevo] = 1.0
            st.rerun()
        
        if st.session_state.asistentes:
            st.write(f"Atletas en nómina: {len(st.session_state.asistentes)}") #
            if st.button("🚀 INICIAR TORNEO"):
                # Generar Ronda 1
                jug = st.session_state.asistentes.copy()
                num_jug = (len(jug) // 4) * 4
                mesas = [jug[i:i+4] for i in range(0, num_jug, 4)]
                st.session_state.historial_completo.append({
                    'ronda': 1, 'mesas': mesas, 'reposo': jug[num_jug:]
                })
                st.session_state.registro_abierto = False
                st.rerun()
    else:
        # Carga de resultados
        r_info = st.session_state.historial_completo[-1]
        st.subheader(f"Carga de Resultados - Ronda {r_info['ronda']}")
        
        for i, m in enumerate(r_info['mesas']):
            with st.expander(f"MESA {i+1} - {m[0]}, {m[1]}, {m[2]}, {m[3]}", expanded=True):
                c1, c2 = st.columns(2)
                p_ac = c1.number_input(f"Puntos A+C ({m[0]}/{m[2]})", key=f"ac_{i}", min_value=0)
                p_bd = c2.number_input(f"Puntos B+D ({m[1]}/{m[3]})", key=f"bd_{i}", min_value=0)
                
                if st.button(f"GUARDAR MESA {i+1}", key=f"btn_{i}"):
                    # Actualización de Puntos
                    st.session_state.puntos_favor[m[0]] += p_ac; st.session_state.puntos_contra[m[0]] += p_bd
                    st.session_state.puntos_favor[m[2]] += p_ac; st.session_state.puntos_contra[m[2]] += p_bd
                    st.session_state.puntos_favor[m[1]] += p_bd; st.session_state.puntos_contra[m[1]] += p_ac
                    st.session_state.puntos_favor[m[3]] += p_bd; st.session_state.puntos_contra[m[3]] += p_ac
                    # JG
                    if p_ac > p_bd:
                        st.session_state.juegos_ganados[m[0]] += 1; st.session_state.juegos_ganados[m[2]] += 1
                    elif p_bd > p_ac:
                        st.session_state.juegos_ganados[m[1]] += 1; st.session_state.juegos_ganados[m[3]] += 1
                    # Baremo
                    for a in m: recalcular_baremo(a)
                    st.toast(f"Mesa {i+1} lista")

# --- 5. PANEL PÚBLICO (MONITOR) ---
elif seccion == "MONITOR PÚBLICO":
    st.header("Monitor Oficial ADEL")
    if not st.session_state.historial_completo:
        st.info("Esperando que la Mesa Técnica inicie el torneo...")
    else:
        r_data = st.session_state.historial_completo[-1]
        st.subheader(f"Distribución - Ronda {r_data['ronda']}")
        if r_data['reposo']: st.error(f"⌛ EN REPOSO: {', '.join(r_data['reposo'])}") #
        
        for idx, mj in enumerate(r_data['mesas']):
            with st.container(border=True):
                st.markdown(f"<h3 style='text-align:center;'>MESA {idx+1}</h3>", unsafe_allow_html=True)
                ca, cm, cd = st.columns([1, 1, 1])
                cm.markdown(f"<div style='text-align:center;'><b>A</b><br>{mj[0]}<br><br><b>C</b><br>{mj[2]}</div>", unsafe_allow_html=True)
                ca.markdown(f"<div style='text-align:right;'><br><b>B</b><br>{mj[1]}</div>", unsafe_allow_html=True)
                cd.markdown(f"<div style='text-align:left;'><br><b>D</b><br>{mj[3]}</div>", unsafe_allow_html=True)
