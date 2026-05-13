import streamlit as st
import math

# 1. ESTADO DEL SISTEMA
if 'asistentes' not in st.session_state:
    st.session_state.update({
        'asistentes': [], 'juegos_ganados': {}, 'efectividad': {}, 
        'puntos_contra': {}, 'puntos_favor': {}, 'ronda_actual': 1,
        'registro_abierto': True, 'historial_completo': [], 'tarjetas': {}
    })

# 2. FÓRMULA LOGARÍTMICA (BAREMO ADEL)
def calcular_baremo(atleta):
    pf = st.session_state.puntos_favor[atleta]
    pc = st.session_state.puntos_contra[atleta]
    # Evitar log(0)
    v_f = pf if pf > 0 else 1
    v_c = pc if pc > 0 else 1
    st.session_state.efectividad[atleta] = math.log10(v_f / v_c) + 1

# 3. NAVEGACIÓN (SELECTOR FORZADO)
with st.sidebar:
    st.title("🏆 MENÚ ADEL")
    # Se eliminan ambigüedades en las etiquetas
    ir_a = st.radio("SELECCIONAR PANEL:", ["CONFIGURAR / CARGAR", "MONITOR PÚBLICO"])

# 4. PANEL DE CONTROL (MES
