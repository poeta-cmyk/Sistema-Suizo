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

# --- 3. MENÚ (ORDEN CRÍTICO) ---
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
            st.write(f"Inscritos: {len(st.session_state.asistentes)}")
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
            st.subheader(f"Carga de Resultados - Ronda {
