import streamlit as st
import math
import random
import time
import json
from datetime import datetime, timedelta

# --- 1. CONFIGURACIÓN E IDENTIDAD ---
st.set_page_config(layout="wide", page_title="Sistema Suizo Pro - Franz Lameda")

# --- 2. INICIALIZACIÓN DEL ESTADO ---
KEYS_SUIZO = [
    'asistentes', 'juegos_ganados', 'puntos_favor', 'puntos_contra', 
    'efectividad', 'jugadores_reposo_previos', 'mesas_actuales', 
    'jugadores_pausa', 'parejas_previas', 'historial_mesas', 
    'ronda_actual', 'registro_abierto', 'torneo_finalizado', 'meta_puntos'
]

for key in KEYS_SUIZO:
    if key not in st.session_state:
        if any(x in key for x in ['previos', 'mesas', 'pausa', 'parejas', 'asistentes', 'historial']):
            st.session_state[key] = []
        elif key == 'ronda_actual':
            st.session_state[key] = 1
        elif key == 'registro_abierto':
            st.session_state[key] = True
        elif key == 'torneo_finalizado':
            st.session_state[key] = False
        elif key == 'meta_puntos':
            st.session_state[key] = 100
        else:
            st.session_state[key] = {}

if 'lanzar_globos' not in st.session_state: st.session_state.lanzar_globos = False
if 'fin_tiempo' not in st.session_state: st.session_state.fin_tiempo = None
if 'cronometro_activo' not in st.session_state: st.session_state.cronometro_activo = False

# --- 3. FUNCIONES DE RESGUARDO Y RECUPERACIÓN ---
def exportar_torneo():
    datos = {k: st.session_state[k] for k in KEYS_SUIZO}
    datos['parejas_previas'] = [list(p) for p in datos['parejas_previas']]
    return json.dumps(datos, indent=4)

def importar_torneo(file):
    try:
        datos = json.load(file)
        for k in KEYS_SUIZO:
            if k == 'parejas_previas':
                st.session_state[k] = [set(p) for p in datos[k]]
            else:
                st.session_state[k] = datos[k]
        st.success("✅ Sistema restaurado correctamente.")
        time.sleep(1)
        st.rerun()
    except Exception as e:
        st.error(f"Error al cargar: {e}")

# --- 4. LÓGICA DE COMPETENCIA ---
def agregar_atleta():
    nom = st.session_state.nuevo_atleta.strip().upper()
    if nom and nom not in st.session_state.asistentes:
        st.session_state.asistentes.append(nom)
        st.session_state.asistentes.sort()
    st.session_state.nuevo_atleta = ""

def generar_ronda():
    jugadores = sorted(st.session_state.asistentes, 
                      key=lambda x: (st.session_state.juegos_ganados.get(x, 0), 
                                     st.session_state.efectividad.get(x, 0), 
                                     -st.session_state.puntos_contra.get(x, 0)), 
                      reverse=True)
    if st.session_state.ronda_actual == 1: random.shuffle(jugadores)
    
    n_rep = len(jugadores) % 4
    hoy_rep = []
    if n_rep > 0:
        intentos = 0
        while intentos < len(jugadores):
            cands = jugadores[-n_rep:]
            if any(j in st.session_state.jugadores_reposo_previos for j in cands) and len(jugadores) > n_rep:
                jugadores.insert(0, jugadores.pop())
                intentos += 1
            else: break
        hoy_rep = jugadores[-n_rep:]
        for r in hoy_rep:
            jugadores.remove(r)
            st.session_state.jugadores_reposo_previos.append(r)
            
    st.session_state.jugadores_pausa = hoy_rep
    n_mesas = len(jugadores) // 4
    nuevas_mesas = []
    dispo = jugadores.copy()
    
    for _ in range(n_mesas):
        a = dispo.pop(0)
        c_i = next((i for i, c in enumerate(dispo) if {a, c} not in st.session_state.parejas_previas), 0)
        c = dispo.pop(c_i)
        st.session_state.parejas_previas.append({a, c})
        b = dispo.pop(0)
        d_i = next((i for i, c in enumerate(dispo) if {b, c} not in st.session_state.parejas_previas), 0)
        d = dispo.pop(d_i)
        st.session_state.parejas_previas.append({b, d})
        nuevas_mesas.append([a, b, c, d])
        
    st.session_state.mesas_actuales = nuevas_mesas
    st.session_state.historial_mesas.append({'ronda': st.session_state.ronda_actual, 'mesas': nuevas_mesas, 'reposo': hoy_rep.copy()})

def cerrar_ronda():
    meta = st.session_state.meta_puntos
    for i, m in enumerate(st.session_state.mesas_actuales):
        pi = st.session_state.get(f"pi_{i}_{st.session_state.ronda_
