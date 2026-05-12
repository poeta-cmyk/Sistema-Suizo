import streamlit as st
import math
import random
import time
import json
from datetime import datetime, timedelta

# --- 1. CONFIGURACIÓN Y ESTADO ---
st.set_page_config(layout="wide", page_title="ADEL - Sistema Suizo")

# Inicialización robusta de variables
keys = ['asistentes', 'juegos_ganados', 'puntos_favor', 'puntos_contra', 
        'efectividad', 'jugadores_reposo_previos', 'mesas_actuales', 
        'jugadores_pausa', 'parejas_previas', 'historial_mesas']

for key in keys:
    if key not in st.session_state:
        st.session_state[key] = [] if any(x in key for x in ['previos', 'mesas', 'pausa', 'parejas', 'asistentes', 'historial']) else {}

if 'ronda_actual' not in st.session_state: st.session_state.ronda_actual = 1
if 'registro_abierto' not in st.session_state: st.session_state.registro_abierto = True
if 'torneo_finalizado' not in st.session_state: st.session_state.torneo_finalizado = False
if 'fin_tiempo' not in st.session_state: st.session_state.fin_tiempo = None
if 'cronometro_activo' not in st.session_state: st.session_state.cronometro_activo = False

# --- 2. FUNCIONES DE SEGURIDAD (RESGUARDAR/RESTAURAR) ---
def exportar_datos():
    datos = {k: st.session_state[k] for k in keys + ['ronda_actual', 'registro_abierto', 'torneo_finalizado']}
    return json.dumps(datos, indent=4)

def importar_datos(archivo_subido):
    if archivo_subido is not None:
        datos = json.load(archivo_subido)
        for k, v in datos.items():
            st.session_state[k] = v
        st.rerun()

# --- 3. LÓGICA DEL TORNEO ---
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
            st.session_state.asistentes.sort()
            st.rerun()

def generar_ronda_suiza():
    jugadores = sorted(st.session_state.asistentes, 
                      key=lambda x: (st.session_state.juegos_ganados.get(x, 0), 
                                     st.session_state.efectividad.get(x, 0)), reverse=True)
    if st.session_state.ronda_actual == 1: random.shuffle(jugadores)
    
    n_reposo = len(jugadores) % 4
    reposados_hoy = jugadores[-n_reposo:] if n_reposo > 0 else []
    jugadores_activos = jugadores[:-n_reposo] if n_reposo > 0 else jugadores
    
    st.session_state.jugadores_pausa = reposados_hoy
    mesas = []
    for i in range(0, len(jugadores_activos), 4):
        mesas.append(jugadores_activos[i:i+4])
    
    st.session_state.mesas_actuales = mesas
    st.session_state.historial_mesas.append({
        'ronda': st.session_state.ronda_actual, 'mesas': mesas, 
        'reposo': reposados_hoy, 'resultados': {}
    })

def finalizar_ronda():
    meta = st.session_state.meta_puntos
    # Lógica de guardado de resultados y avance de ronda...
    st.session_state.ronda_actual += 1
    generar_ronda_suiza()
    st.rerun()

# --- 4. INTERFAZ ---
st.title("Asociación de Dominó del Estado Lara (ADEL) - Sistema Suizo")

with st.sidebar:
    st.header("💾 Seguridad del Torneo")
    st.download_button("📥 RESGUARDAR (Descargar Memoria)", data=exportar_datos(), file_name="respaldo_torneo.json", mime="application/json")
    
    archivo = st.file_uploader("📂 RESTAURAR DESDE ARCHIVO", type=['json'])
    if archivo:
        if st.button("✅ Confirmar Restauración"):
            importar_datos(archivo)
            
    if not st.session_state.registro_abierto:
        st.markdown("---")
        st.header("⏱️ Reloj de Ronda")
        # Lógica del cronómetro...
        
    st.markdown("---")
    st.caption("Creado por Poeta")

if st.session_state.registro_abierto:
    st.subheader("📝 Registro de Atletas")
    st.session_state.meta_puntos = st.radio("Meta:", [100, 200], horizontal=True)
    st.text_input("Nombre y ENTER:", key="nuevo_nombre", on_change=agregar_jugador_enter)
    
    if st.session_state.asistentes:
        st.write(f"**Inscritos:** {', '.join(st.session_state.asistentes)}")
        if st.button("🚀 INICIAR TORNEO"):
            st.session_state.registro_abierto = False
            generar_ronda_suiza()
            st.rerun()
else:
    # Interfaz de mesas y resultados...
    st.write(f"### Ronda Actual: {st.session_state.ronda_actual}")
    for i, mesa in enumerate(st.session_state.mesas_actuales):
        st.info(f"Mesa {i+1}: {mesa[0]}, {mesa[2]} VS {mesa[1]}, {mesa[3]}")
