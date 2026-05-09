import streamlit as st
import math
import random
import time
import json
from datetime import datetime, timedelta

# --- CONFIGURACIÓN Y ESTADO ---
st.set_page_config(layout="wide", page_title="Sistema Suizo Pro - Franz Lameda")

# Lista de todas las variables que necesitamos salvar
KEYS_PARA_GUARDAR = [
    'asistentes', 'juegos_ganados', 'puntos_favor', 'puntos_contra', 
    'efectividad', 'jugadores_reposo_previos', 'mesas_actuales', 
    'jugadores_pausa', 'parejas_previas', 'historial_mesas', 
    'ronda_actual', 'registro_abierto', 'torneo_finalizado', 'meta_puntos'
]

for key in KEYS_PARA_GUARDAR:
    if key not in st.session_state:
        if any(x in key for x in ['previos', 'mesas', 'pausa', 'parejas', 'asistentes', 'historial']):
            st.session_state[key] = []
        elif key in ['ronda_actual']:
            st.session_state[key] = 1
        elif key in ['registro_abierto']:
            st.session_state[key] = True
        elif key in ['torneo_finalizado']:
            st.session_state[key] = False
        elif key in ['meta_puntos']:
            st.session_state[key] = 100
        else:
            st.session_state[key] = {}

if 'lanzar_globos' not in st.session_state: st.session_state.lanzar_globos = False
if 'fin_tiempo' not in st.session_state: st.session_state.fin_tiempo = None
if 'cronometro_activo' not in st.session_state: st.session_state.cronometro_activo = False

# --- NUEVAS FUNCIONES DE RESPALDO Y RECUPERACIÓN ---

def exportar_datos():
    """Crea un archivo JSON con el estado actual del torneo"""
    datos = {key: st.session_state[key] for key in KEYS_PARA_GUARDAR}
    # Convertimos sets a listas para que JSON los acepte (parejas_previas usa sets)
    datos['parejas_previas'] = [list(p) for p in datos['parejas_previas']]
    return json.dumps(datos, indent=4)

def importar_datos(archivo_subido):
    """Lee el JSON y reconstruye el torneo"""
    try:
        datos = json.load(archivo_subido)
        for key in KEYS_PARA_GUARDAR:
            if key == 'parejas_previas':
                st.session_state[key] = [set(p) for p in datos[key]]
            else:
                st.session_state[key] = datos[key]
        st.success("✅ Torneo restaurado con éxito.")
        time.sleep(1)
        st.rerun()
    except Exception as e:
        st.error(f"Error al cargar el archivo: {e}")

# --- FUNCIONES CORE ---

def agregar_jugador_enter():
    nombre = st.session_state.nuevo_nombre.strip().upper()
    if nombre and nombre not in st.session_state.asistentes:
        st.session_state.asistentes.append(nombre)
        st.session_state.asistentes.sort()
    st.session_state.nuevo_nombre = "" 

@st.dialog("Editar Atleta")
def editar_atleta_dialog(nombre_viejo):
    nuevo_nombre = st.text_input("Corregir nombre de Atleta:", value=nombre_viejo).strip().upper()
    if st.button("✅ GUARDAR CAMBIO"):
        if nuevo_nombre and nuevo_nombre != nombre_viejo:
            idx = st.session_state.asistentes.index(nombre_viejo)
            st.session_state.asistentes[idx] = nuevo_nombre
            st.session_state.asistentes.sort()
            for dict_stat in [st.session_state.juegos_ganados, st.session_state.puntos_favor, 
                             st.session_state.puntos_contra, st.session_state.efectividad]:
                if nombre_viejo in dict_stat:
                    dict_stat[nuevo_nombre] = dict_stat.pop(nombre_viejo)
            st.rerun()

def generar_ronda_suiza():
    # Ordenar por mérito (Suizo)
    jugadores = sorted(st.session_state.asistentes, 
                      key=lambda x: (st.session_state.juegos_ganados.get(x, 0), 
                                     st.session_state.efectividad.get(x, 0), 
                                     -st.session_state.puntos_contra.get(x, 0)), 
                      reverse=True)
    
    if st.session_state.ronda_actual == 1: 
        random.shuffle(jugadores)
    
    n_reposo = len(jugadores) % 4
    reposados_hoy = []
    
    if n_reposo > 0:
        # LÓGICA DE ACOMODO AUTOMÁTICO (SUBE Y BAJA SILENCIOSO)
        intentos = 0
        while intentos < len(jugadores):
            candidatos_reposo = jugadores[-n_reposo:]
            repite_reposo = any(j in st.session_state.jugadores_reposo_previos for j in candidatos_reposo)
            
            if repite_reposo and len(jugadores) > n_reposo:
                jugadores.insert(0, jugadores.pop()) # Sube al último, baja al de arriba
                intentos += 1
            else:
                break
        
        reposados_hoy = jugadores[-n_reposo:]
        for r in reposados_hoy:
            jugadores.remove(r)
            st.session_state.jugadores_reposo_previos.append(r)
            
    st.session_state.jugadores_pausa = reposados_hoy
    
    # Emparejamiento de Mesas
    n_mesas = len(jugadores) // 4
    mesas_generadas = []
    disponibles = jugadores.copy()
    
    for _ in range(n_mesas):
        a = disponibles.pop(0)
        c_idx = next((i for i, cand in enumerate(disponibles) if {a, cand} not in st.session_state.parejas_previas), 0)
        c = disponibles.pop(c_idx)
        st.session_state.parejas_previas.append({a, c})
        
        b = disponibles.pop(0)
        d_idx = next((i for i, cand in enumerate(disponibles) if {b, cand} not in st.session_state.parejas_previas), 0)
        d = disponibles.pop(d_idx)
        st.session_state.parejas_previas.append({b, d})
        
        mesas_generadas.append([a, b, c, d])
        
    st.session_state.mesas_actuales = mesas_generadas
    st.session_state.historial_mesas.append({
        'ronda': st.session_state.ronda_actual, 
        'mesas': mesas_generadas, 
        'reposo': reposados_hoy.copy()
    })

def finalizar_ronda():
    meta = st.session_state.meta_puntos
    for i, m in enumerate(st.session_state.mesas_actuales):
        p_izq = st.session_state.get(f"p_izq_{i}_{st.session_state.ronda_actual}", 0)
        p_der = st.session_state.get(f"p_der_{i}_{st.session_state.ronda_actual}", 0)
        
        ef_izq = (p_izq - meta) if p_izq < p_der else (meta - p_der)
        ef_der = (p_der - meta) if p_der < p_izq else (meta - p_izq)
        
        for p, pf, pc, ef in [(m[0], p_izq, p_der, ef_izq), (m[2], p_izq, p_der, ef_izq), 
                              (m[1], p_der, p_izq, ef_der), (m[3], p_der, p_izq, ef_der)]:
            st.session_state.puntos_favor[p] = st.session_state.puntos_favor.get(p, 0) + pf
            st.session_state.puntos_contra[p] = st.session_state.puntos_contra.get(p, 0) + pc
            st.session_state.efectividad[p] = st.session_state.efectividad.get(p, 0) + ef
            if pf > pc: st.session_state.juegos_ganados[p] = st.session_state.juegos_ganados.get(p, 0) + 1
            
    beneficio_reposo = meta // 2
    for r in st.session_state.jugadores_pausa:
        st.session_state.juegos_ganados[r] = st.session_state.juegos_ganados.get(r, 0) + 1
        st.session_state.efectividad[r] = st.session_state.efectividad.get(r, 0) + beneficio_reposo
        
    st.session_state.lanzar_globos = True
    st.session_state.fin_tiempo = None 
    st.session_state.cronometro_activo = False
    
    if st.session_state.ronda_actual >= math.ceil(math.log2(len(st.session_state.asistentes))): 
        st.session_state.torneo_finalizado = True
    else:
        st.session_state.ronda_actual += 1
        generar_ronda_suiza()
    st.rerun()

# --- INTERFAZ ---
st.title("🏆 Sistema Suizo Pro - El
