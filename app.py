import streamlit as st
import math
import random
import time
import json
from datetime import datetime, timedelta

# --- 1. CONFIGURACIÓN Y ESTADO ---
st.set_page_config(layout="wide", page_title="ADEL - Sistema Suizo")

keys = ['asistentes', 'juegos_ganados', 'puntos_favor', 'puntos_contra', 
        'efectividad', 'jugadores_reposo_previos', 'mesas_actuales', 
        'jugadores_pausa', 'parejas_previas', 'historial_mesas']

for key in keys:
    if key not in st.session_state:
        st.session_state[key] = [] if any(x in key for x in ['previos', 'mesas', 'pausa', 'parejas', 'asistentes', 'historial']) else {}

if 'ronda_actual' not in st.session_state: st.session_state.ronda_actual = 1
if 'registro_abierto' not in st.session_state: st.session_state.registro_abierto = True
if 'torneo_finalizado' not in st.session_state: st.session_state.torneo_finalizado = False
if 'meta_puntos' not in st.session_state: st.session_state.meta_puntos = 100

# --- 2. SEGURIDAD ---
def exportar_datos():
    datos = {k: st.session_state[k] for k in keys + ['ronda_actual', 'registro_abierto', 'torneo_finalizado', 'meta_puntos']}
    return json.dumps(datos, indent=4)

def importar_datos(archivo_subido):
    if archivo_subido is not None:
        datos = json.load(archivo_subido)
        for k, v in datos.items():
            st.session_state[k] = v
        st.rerun()

# --- 3. LÓGICA DE REGISTRO Y RONDAS ---
def agregar_jugador_enter():
    nombre = st.session_state.nuevo_nombre.strip().upper()
    if nombre and nombre not in st.session_state.asistentes:
        st.session_state.asistentes.append(nombre)
        st.session_state.asistentes.sort()
    st.session_state.nuevo_nombre = "" 

@st.dialog("Editar Atleta")
def editar_atleta_dialog(nombre_viejo):
    nuevo_nombre = st.text_input("Corregir nombre:", value=nombre_viejo).strip().upper()
    if st.button("✅ GUARDAR"):
        if nuevo_nombre and nuevo_nombre != nombre_viejo:
            idx = st.session_state.asistentes.index(nombre_viejo)
            st.session_state.asistentes[idx] = nuevo_nombre
            st.rerun()

def generar_ronda_suiza():
    # Ordenar para emparejamiento (G, Ef, -Contra)
    jugadores = sorted(st.session_state.asistentes, 
                      key=lambda x: (st.session_state.juegos_ganados.get(x, 0), 
                                     st.session_state.efectividad.get(x, 0),
                                     -st.session_state.puntos_contra.get(x, 0)), reverse=True)
    
    if st.session_state.ronda_actual == 1: random.shuffle(jugadores)
    
    n_reposo = len(jugadores) % 4
    reposados = jugadores[-n_reposo:] if n_reposo > 0 else []
    activos = jugadores[:-n_reposo] if n_reposo > 0 else jugadores
    
    st.session_state.jugadores_pausa = reposados
    mesas = [activos[i:i+4] for i in range(0, len(activos), 4)]
    
    st.session_state.mesas_actuales = mesas
    st.session_state.historial_mesas.append({
        'ronda': st.session_state.ronda_actual, 'mesas': mesas, 
        'reposo': reposados, 'resultados': {}
    })

def finalizar_ronda():
    meta = st.session_state.meta_puntos
    idx_h = len(st.session_state.historial_mesas) - 1
    
    for i, mesa in enumerate(st.session_state.mesas_actuales):
        p_izq = st.session_state.get(f"p_izq_{i}", 0)
        p_der = st.session_state.get(f"p_der_{i}", 0)
        
        st.session_state.historial_mesas[idx_h]['resultados'][i] = {'izq': p_izq, 'der': p_der}
        
        # Lógica ADEL: Ef = Meta - Puntos Perdedor
        if p_izq >= p_der:
            val_ef = meta - p_der
            gan,
