import streamlit as st
import math
import random
import time
from datetime import datetime, timedelta

# 1. Configuración Inicial (Siempre al principio)
st.set_page_config(layout="wide", page_title="Sistema Suizo Pro - Franz Lameda")

# 2. Inicialización del Estado (Asegura que nada nazca vacío)
keys_list = ['asistentes', 'juegos_ganados', 'puntos_favor', 'puntos_contra', 
             'efectividad', 'jugadores_reposo_previos', 'mesas_actuales', 
             'jugadores_pausa', 'parejas_previas', 'historial_mesas']

for key in keys_list:
    if key not in st.session_state:
        if any(x in key for x in ['previos', 'mesas', 'pausa', 'parejas', 'asistentes', 'historial']):
            st.session_state[key] = []
        else:
            st.session_state[key] = {}

if 'ronda_actual' not in st.session_state: st.session_state.ronda_actual = 1
if 'registro_abierto' not in st.session_state: st.session_state.registro_abierto = True
if 'torneo_finalizado' not in st.session_state: st.session_state.torneo_finalizado = False
if 'lanzar_globos' not in st.session_state: st.session_state.lanzar_globos = False
if 'fin_tiempo' not in st.session_state: st.session_state.fin_tiempo = None
if 'cronometro_activo' not in st.session_state: st.session_state.cronometro_activo = False

# 3. Funciones de Gestión
def agregar_jugador():
    nombre = st.session_state.nuevo_nombre.strip().upper()
    if nombre and nombre not in st.session_state.asistentes:
        st.session_state.asistentes.append(nombre)
        st.session_state.asistentes.sort()
    st.session_state.nuevo_nombre = ""

@st.dialog("Editar Atleta")
def editar_atleta(nombre_viejo):
    nuevo = st.text_input("Nuevo nombre:", value=nombre_viejo).strip().upper()
    if st.button("GUARDAR"):
        if nuevo and nuevo != nombre_viejo:
            idx = st.session_state.asistentes.index(nombre_viejo)
            st.session_state.asistentes[idx] = nuevo
            st.rerun()

def generar_ronda():
    jugadores = sorted(st.session_state.asistentes, 
                      key=lambda x: (st.session_state.juegos_ganados.get(x, 0), 
                                     st.session_state.efectividad.get(x, 0)), reverse=True)
    if st.session_state.ronda_actual == 1: random.shuffle(jugadores)
    
    n_reposo = len(jugadores) % 4
    reposo = []
    if n_reposo > 0:
        candidatos = [j for j in reversed(jugadores) if j not in st.session_state.jugadores_reposo_previos]
        if not candidatos: candidatos = list(reversed(jugadores))
        reposo = candidatos[:n_reposo]
        for r in reposo:
            jugadores.remove(r)
            st.session_state.jugadores_reposo_previos.append(r)
    
    st.session_state.jugadores_pausa = reposo
    mesas = []
    temp = jugadores.copy()
    while len(temp) >= 4:
        m = [temp.pop(0), temp.pop(0), temp.pop(0), temp.pop(0)]
        mesas.append(m)
    
    st.session_state.mesas_actuales = mesas
    st.session_state.historial_mesas.append({
        'ronda': st.session_state.ronda_actual, 
        'mesas': mesas, 
        'reposo': reposo
    })

# 4. Interfaz Principal
st.title("🏆 Sistema Suizo Pro - El Poeta Franz Lameda")

if st.session_state.registro_abierto:
    st.session_state.meta_puntos = st.radio("Meta:", [100, 200], horizontal=True)
    st.text_input("Nombre del Atleta:", key="nuevo_nombre", on_change=agregar_jugador)
    
    if st.session_state.asistentes:
        st.write(f"Inscritos: {len(st.session_state.asistentes)}")
        sel = st.selectbox("Gestionar:", st.session_state.asistentes)
        c1, c2 = st.columns(2)
        with c1:
            if st.button("✏️ Editar"): editar_atleta(sel)
        with c2:
            if st.button("🗑️ Eliminar"): 
                st.session_state.asistentes.remove(sel)
                st.rerun()
        
        if st.button("🚀 INICIAR TORNEO") and len(st.session_state.asistentes) >= 4:
            st.session_state.registro_abierto = False
            generar_ronda()
            st.rerun()
else:
    # Lógica de Torneo (Mesas y Ranking)
    st.write(f"### Ronda Actual: {st.session_state.ronda_actual}")
    
    # Mostrar Mesas
    for i, mesa in enumerate(st.session_state.mesas_actuales):
        st.write(f"**Mesa {i+1}**")
        st.write(f"{mesa[0]} y {mesa[2]} VS {mesa[1]} y {mesa[3]}")
    
    if st.button("Finalizar Ronda"):
        st.session_state.ronda_actual += 1
        generar_ronda()
        st.rerun()

    if st.button("Reiniciar Todo"):
        st.session_state.clear()
        st.rerun()
