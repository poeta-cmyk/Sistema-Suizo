import streamlit as st
import math
import random

# Configuración de la página
st.set_page_config(layout="wide", page_title="Sistema Suizo Pro")

# --- MEMORIA DEL PROGRAMA (SESSION STATE) ---
if 'asistentes' not in st.session_state:
    st.session_state.asistentes = []
if 'registro_abierto' not in st.session_state:
    st.session_state.registro_abierto = True
if 'ronda_actual' not in st.session_state:
    st.session_state.ronda_actual = 1
# Diccionarios de estadísticas
if 'juegos_ganados' not in st.session_state:
    st.session_state.juegos_ganados = {} 
if 'puntos_favor' not in st.session_state:
    st.session_state.puntos_favor = {} 
if 'puntos_contra' not in st.session_state:
    st.session_state.puntos_contra = {} 

if 'mesas_actuales' not in st.session_state:
    st.session_state.mesas_actuales = []
if 'jugadores_pausa' not in st.session_state:
    st.session_state.jugadores_pausa = []
if 'meta_puntos' not in st.session_state:
    st.session_state.meta_puntos = 100
if 'parejas_previas' not in st.session_state:
    st.session_state.parejas_previas = [] 

# --- FUNCIONES DE LÓGICA ---
def registrar_y_limpiar():
    nombre = st.session_state.ingreso_nombre.strip().upper()
    if nombre and nombre not in st.session_state.asistentes:
        st.session_state.asistentes.append(nombre)
        st.session_state.asistentes.sort()
        st.session_state.ingreso_nombre = ""
        # Inicializar stats
        st.session_state.juegos_ganados[nombre] = 0
        st.session_state.puntos_favor[nombre] = 0
        st.session_state.puntos_contra[nombre] = 0

def generar_ronda_suiza():
    # ORDEN DE MÉRITO SEGÚN FRANZ LAMEDA:
    # 1. Juegos Ganados (Desc)
    # 2. Puntos a Favor (Desc)
    # 3. Puntos en Contra (Asc)
    jugadores = sorted(st.session_state.asistentes, 
                      key=lambda x: (
                          st.session_state.juegos_ganados[x], 
                          st.session_state.puntos_favor[x], 
                          -st.session_state.puntos_contra[x] # Negativo para que el menor sea "mayor"
                      ), 
                      reverse=True)
    
    if st.session_state.ronda_actual == 1:
        random.shuffle(jugadores)
    
    n_mesas = len(jugadores) // 4
    mesas_generadas = []
    disponibles = jugadores.copy()
    
    for _ in range(n_mesas):
        # Pareja A/C (Izquierda)
        a = disponibles.pop(0)
        c_idx = -1
        for i, cand in enumerate(disponibles):
            if {a, cand} not in st.session_state.parejas_previas:
                c_idx = i
                break
        c = disponibles.pop(c_idx) if c_idx != -1 else disponibles.pop(0)
        st.session_state.parejas_previas.append({a, c})
        
        # Pareja B/D (Derecha)
        b = disponibles.pop(0)
        d_idx = -1
        for i, cand in enumerate(disponibles):
            if {b, cand} not in st.session_state.parejas_previas:
                d_idx = i
                break
        d = disponibles.pop(d_idx) if d_idx != -1 else disponibles.pop(0)
        st.session_state.parejas_previas.append({b, d})
        
        mesas_generadas.append([a, b, c, d])
        
    st.session_state.mesas_actuales = mesas_generadas
    st.session_state.jugadores_pausa = disponibles
    
    # El que queda en pausa gana el juego por la meta
    for p in st.session_state.jugadores_pausa:
        st.session_state.juegos_ganados[p] += 1
        st.session_state.puntos_favor[p] += st.session_state.meta_puntos
        st.session_state.puntos_contra[p] += (st.session_state.meta_puntos // 2)

def procesar_ronda():
    for i in range(len(st.session_state.mesas_actuales)):
        m = st.session_state.mesas_actuales[i]
        p_izq = st.session_state.get(f"p_izq_{i}_{st.session_state.ronda_actual}", 0)
        p_der = st.session_state.get(f"p_der_{i}_{st.session_state.ronda_actual}", 0)
        
        # Actualizar A y C
        st.session_state.p_favor[m[0]] += p_izq; st.session_state.p_contra[m[0]] += p_der
        st.session_state.p_favor[m[2]] += p_izq; st.session_state.p_contra[m[2]] += p_der
        if p_izq > p_der: 
            st.session_state.juegos_ganados[m[0]] += 1; st.session_state.juegos_ganados[m[2]] += 1
            
        # Actualizar B y D
        st.session_state.p_favor[m[1]] += p_der; st.session_state.p_contra[m[1]] += p_izq
        st.session_state.p_favor[m[3]] += p_der; st.session_state.p_contra[m[3]] += p_izq
        if p_der > p_izq: 
            st.session_state.juegos_ganados[m[1]] += 1; st.session_state.juegos_ganados[m[3]] += 1
        
    st.session_state.ronda_actual += 1
    generar_ronda_suiza()

# --- INTERFAZ ---
st.title("Sistema Suizo Pro - El Poeta Franz Lameda")

if st.session_state.registro_abierto:
    st.session_state.meta_puntos = st.radio("Meta:", [100, 200], horizontal=True)
    st.text_input("Jugador:", key="ingreso_nombre", on_change=registrar_y_limpiar)
    if st.button("Iniciar Torneo"):
        if len(st.session_state.asistentes) >= 4:
            st.session_state.registro_abierto = False
            generar_ronda_suiza()
            st.rerun()

if not st.session_state.registro_abierto:
    # Panel superior de indicadores y distribución de mesas (Igual al diseño anterior)
    # [AQUÍ SE MANTIENE EL DISEÑO DE ESPEJO QUE YA TENEMOS FUNCIONANDO]
    # ... (Omito el resto para brevedad, pero en tu app.py pégalo completo)
