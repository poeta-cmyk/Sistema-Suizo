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
if 'meta_puntos' not in st.session_state: st.session_state.meta_puntos = 100

# --- 2. SEGURIDAD (RESGUARDAR/RESTAURAR) ---
def exportar_datos():
    datos = {k: st.session_state[k] for k in keys + ['ronda_actual', 'registro_abierto', 'torneo_finalizado', 'meta_puntos']}
    return json.dumps(datos, indent=4)

def importar_datos(archivo_subido):
    if archivo_subido is not None:
        datos = json.load(archivo_subido)
        for k, v in datos.items():
            st.session_state[k] = v
        st.rerun()

# --- 3. LÓGICA DE REGISTRO ---
def agregar_jugador_enter():
    nombre = st.session_state.nuevo_nombre.strip().upper()
    if nombre and nombre not in st.session_state.asistentes:
        st.session_state.asistentes.append(nombre)
        st.session_state.asistentes.sort()
    st.session_state.nuevo_nombre = "" 

@st.dialog("Editar Atleta")
def editar_atleta_dialog(nombre_viejo):
    nuevo_nombre = st.text_input("Corregir nombre:", value=nombre_viejo).strip().upper()
    if st.button("✅ GUARDAR CAMBIO"):
        if nuevo_nombre and nuevo_nombre != nombre_viejo:
            idx = st.session_state.asistentes.index(nombre_viejo)
            st.session_state.asistentes[idx] = nuevo_nombre
            st.session_state.asistentes.sort()
            st.rerun()

# --- 4. INTERFAZ ---
st.title("Asociación de Dominó del Estado Lara (ADEL) - Sistema Suizo")

with st.sidebar:
    st.header("💾 Seguridad del Torneo")
    st.download_button("📥 RESGUARDAR", data=exportar_datos(), file_name="respaldo_torneo.json", mime="application/json")
    
    archivo = st.file_uploader("📂 RESTAURAR", type=['json'])
    if archivo:
        if st.button("✅ Confirmar Restauración"):
            importar_datos(archivo)
            
    st.markdown("---")
    st.caption("Creado por Poeta")

if st.session_state.registro_abierto:
    st.subheader("📝 Registro de Atletas")
    st.session_state.meta_puntos = st.radio("Meta:", [100, 200], horizontal=True)
    st.text_input("Atleta + ENTER:", key="nuevo_nombre", on_change=agregar_jugador_enter)
    
    if st.session_state.asistentes:
        st.markdown("---")
        st.write(f"**Inscritos ({len(st.session_state.asistentes)}):**")
        
        # Lista con opciones de edición y borrado
        col_sel, col_ed, col_del = st.columns([3, 0.5, 0.5])
        with col_sel:
            atleta_sel = st.selectbox("Seleccione para modificar:", st.session_state.asistentes, label_visibility="collapsed")
        with col_ed:
            if st.button("✏️", help="Editar nombre"):
                editar_atleta_dialog(atleta_sel)
        with col_del:
            if st.button("🗑️", help="Borrar atleta"):
                st.session_state.asistentes.remove(atleta_sel)
                st.rerun()
        
        st.write(f"Lista actual: {', '.join(st.session_state.asistentes)}")
        
        if st.button("🚀 INICIAR"):
            if len(st.session_state.asistentes) >= 4:
                st.session_state.registro_abierto = False
                # Aquí iría la llamada a generar_ronda_suiza() cuando la tengamos lista
                st.rerun()
            else:
                st.warning("Se requieren al menos 4 atletas para iniciar.")
