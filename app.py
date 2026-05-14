import streamlit as st
import math
import random

# --- 1. CONFIGURACIÓN Y ESTADO INICIAL ---
st.set_page_config(layout="wide", page_title="SISTEMA ADEL")

# CSS Ajustado: Mesas más grandes y fuentes más legibles
st.markdown("""
    <style>
    .mesa-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        margin-bottom: 40px; /* Más espacio entre filas */
        padding: 15px;
    }
    .mesa-centro {
        width: 140px;  /* Aumentado de 100px */
        height: 140px; /* Aumentado de 100px */
        border: 5px solid black;
        background-color: #FFFF00;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        position: relative;
        box-shadow: 3px 3px 10px rgba(0,0,0,0.2);
    }
    .adel-text { font-weight: bold; font-size: 28px; color: #003399; margin: 0; line-height: 1; }
    .n-mesa { font-weight: bold; font-size: 36px; color: #CC0000; margin: 0; line-height: 1; }
    
    .jugador { font-weight: bold; font-size: 18px; text-align: center; color: #333; }
    .norte { margin-bottom: 10px; }
    .sur { margin-top: 10px; }
    
    .fila-central {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 100%;
    }
    .este-oeste {
        writing-mode: vertical-rl;
        text-orientation: mixed;
        padding: 0 20px; /* Más separación lateral */
    }
    </style>
    """, unsafe_allow_html=True)

if 'asistentes' not in st.session_state:
    st.session_state.update({
        'asistentes': [], 'estados': {}, 'juegos_ganados': {}, 'efectividad': {},
        'puntos_contra': {}, 'puntos_favor': {}, 'historial_completo': [],
        'editando': None, 'meta_torneo': 100, 'seccion_activa': "INSCRIPCIÓN"
    })

def recalcular_baremo(atleta):
    pf, pc = st.session_state.puntos_favor.get(atleta, 0), st.session_state.puntos_contra.get(atleta, 0)
    st.session_state.efectividad[atleta] = math.log10(max(pf,1) / max(pc,1)) + 1

# --- 2. NAVEGACIÓN ---
with st.sidebar:
    st.title("🏆 MENÚ ADEL")
    opcion = st.radio("SECCIÓN:", ["INSCRIPCIÓN", "MESAS", "RESULTADOS", "RANKING"], 
                      index=["INSCRIPCIÓN", "MESAS", "RESULTADOS", "RANKING"].index(st.session_state.seccion_activa))
    st.session_state.seccion_activa = opcion

# --- 3. SECCIÓN: INSCRIPCIÓN ---
if st.session_state.seccion_activa == "INSCRIPCIÓN":
    st.caption("Creado por Poeta")
    st.header("ASOCIACIÓN DE DOMINÓ DEL ESTADO LARA ADEL")
    st.session_state.meta_torneo = st.radio("Meta del encuentro:", [100, 200], horizontal=True)
    
    def procesar_atleta():
        nom = st.session_state.campo_input.upper().strip()
        if nom and nom not in st.session_state.asistentes:
            st.session_state.asistentes.append(nom)
            st.session_state.estados[nom] = True
            st.session_state.juegos_ganados[nom], st.session_state.puntos_favor[nom], st.session_state.puntos_contra[nom], st.session_state.efectividad[nom] = 0, 0, 0, 1.0
        st.session_state.campo_input = ""

    st.text_input("Nombre del Atleta + ENTER:", key="campo_input", on_change=procesar_atleta)
    activos = [n for n in st.session_state.asistentes if st.session_state.estados[n]]
    
    if st.button("🚀 SORTEAR E IR A RONDA 1"):
        if len(activos) >= 4:
            random.shuffle(activos)
            n_jug = (len(activos) // 4) * 4
            st.session_state.historial_completo.append({
                'ronda': 1, 'mesas': [activos[i:i+4] for i in range(0, n_jug,
