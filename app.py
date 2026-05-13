import streamlit as st
import math
import random
import json

# --- 1. CONFIGURACIÓN E INICIALIZACIÓN ---
st.set_page_config(layout="wide", page_title="ADEL - Sistema Pro")

for key, default in {
    'asistentes': [], 'juegos_ganados': {}, 'efectividad': {}, 
    'puntos_contra': {}, 'ronda_actual': 1, 'registro_abierto': True, 
    'meta_puntos': 100, 'historial_completo': [], 'parejas_jugadas': [], 'historial_reposo': []
}.items():
    if key not in st.session_state: st.session_state[key] = default

# --- 2. LÓGICA DE CONTROL ---
def calcular_rondas(n):
    return math.ceil(math.log2(n)) + 1 if n >= 4 else 0

def procesar_registro():
    n = st.session_state.nuevo_atleta.strip().upper()
    if n and n not in st.session_state.asistentes:
        st.session_state.asistentes.append(n)
        st.session_state.asistentes.sort()
    st.session_state.nuevo_atleta = ""

def generar_ronda_adel():
    rk = sorted(st.session_state.asistentes, 
                key=lambda x: (st.session_state.juegos_ganados.get(x, 0), 
                               st.session_state.efectividad.get(x, 0),
                               -st.session_state.puntos_contra.get(x, 0)), reverse=True)
    
    n_reposo = len(rk) % 4
    reposados = []
    if n_reposo > 0:
        candidatos = [j for j in reversed(rk) if j not in st.session_state.historial_reposo]
        if not candidatos: 
            st.session_state.historial_reposo = []
            candidatos = list(reversed(rk))
        reposados = candidatos[:n_reposo]
        st.session_state.historial_reposo.extend(reposados)
    
    activos = [j for j in rk if j not in reposados]
    mesas = []
    
    while len(activos) >= 4:
        j1 = activos[0]
        comp = None
        # Intenta emparejar 1 con 3 (índice 2), si no, busca al siguiente
        for i in range(2, len(activos)):
            posible = activos[i]
            if tuple(sorted((j1, posible))) not in st.session_state.parejas_jugadas:
                comp = posible
                break
        if not comp: comp = activos[2]
        
        activos.remove(j1
