import streamlit as st
import math
import random

st.set_page_config(layout="wide")
st.title("Sistema Suizo Pro - " + "El Poeta Franz Lameda")

# --- MEMORIA EXTENDIDA ---
if 'asistentes' not in st.session_state:
    st.session_state.asistentes = []
if 'registro_abierto' not in st.session_state:
    st.session_state.registro_abierto = True
if 'ronda_actual' not in st.session_state:
    st.session_state.ronda_actual = 1
if 'historial_puntos' not in st.session_state:
    st.session_state.historial_puntos = {} 
if 'mesas_actuales' not in st.session_state:
    st.session_state.mesas_actuales = []
if 'jugadores_pausa' not in st.session_state:
    st.session_state.jugadores_pausa = []
if 'meta_puntos' not in st.session_state:
    st.session_state.meta_puntos = 100
# Memoria de enfrentamientos para evitar repeticiones
if 'parejas_previas' not in st.session_state:
    st.session_state.parejas_previas = [] # Lista de sets {jugador1, jugador2}

# --- LÓGICA DE EMPAREJAMIENTO SUIZO ---
def generar_ronda_suiza():
    jugadores = sorted(st.session_state.asistentes, 
                      key=lambda x: st.session_state.historial_puntos[x], 
                      reverse=True)
    
    if st.session_state.ronda_actual == 1:
        random.shuffle(jugadores)
    
    n_mesas = len(jugadores) // 4
    mesas = []
    disponibles = jugadores.copy()
    
    # Lógica de emparejamiento evitando repetición de pareja (A con C)
    for _ in range(n_mesas):
        mesa = []
        # Tomamos al de mayor puntaje actual
        a = disponibles.pop(0)
        mesa.append(a)
        
        # Buscamos un compañero (C) que no haya estado con A
        socio_encontrado = False
        for i, candidato in enumerate(disponibles):
            # Verificamos si ya fueron pareja
            if {a, candidato} not in st.session_state.parejas_previas:
                c = disponibles.pop(i)
                mesa.append(c) # Lo ponemos en posición C (índice 2 de la mesa)
                socio_encontrado = True
                st.session_state.parejas_previas.append({a, c})
                break
        
        if not socio_encontrado: # Si ya jugó con todos, toca repetir (caso extremo)
            c = disponibles.pop(0)
            mesa.append(c)
            
        # Los otros dos son los rivales (B y D)
        b = disponibles.pop(0)
        d = disponibles.pop(0)
        
        # Orden de la mesa: [A, B, C, D]
        # Tu diseño: Izquierda A/C, Derecha B/D
        mesas.append([mesa[0], b, mesa[1], d])
        
    st.session_state.mesas_actuales = mesas
    st.session_state.jugadores_pausa = disponibles # El remanente

# --- (Resto de la interfaz igual, pero llamando a generar_ronda_suiza) ---
