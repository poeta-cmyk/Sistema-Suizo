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

# --- 3. LÓGICA DE REGISTRO ---
def agregar_jugador_enter():
    nombre = st.session_state.nuevo_nombre.strip().upper()
    if nombre and nombre not in st.session_state.asistentes:
        st.session_state.asistentes.append(nombre)
        st.session_state.asistentes.sort()
    st.session_state.nuevo_nombre = "" 

# --- 4. LÓGICA DE TORNEO (BAREMOS ADEL) ---
def finalizar_ronda():
    meta = st.session_state.meta_puntos
    # Buscamos la ronda actual en el historial
    idx_h = next(i for i, h in enumerate(st.session_state.historial_mesas) if h['ronda'] == st.session_state.ronda_actual)
    
    for i, mesa in enumerate(st.session_state.mesas_actuales):
        p_izq = st.session_state.get(f"p_izq_{i}_{st.session_state.ronda_actual}", 0)
        p_der = st.session_state.get(f"p_der_{i}_{st.session_state.ronda_actual}", 0)
        
        # Guardamos resultado real
        st.session_state.historial_mesas[idx_h]['resultados'][i] = {'izq': p_izq, 'der': p_der}
        
        # Determinamos ganador y calculamos valor de efectividad basado en tu lógica
        # Ef = Meta - Puntos del Perdedor
        if p_izq >= p_der:
            valor_ef = meta - p_der
            ganadores, perdedores = [mesa[0], mesa[2]], [mesa[1], mesa[3]]
            p_gan, p_per = p_izq, p_der
        else:
            valor_ef = meta - p_izq
            ganadores, perdedores = [mesa[1], mesa[3]], [mesa[0], mesa[2]]
            p_gan, p_per = p_der, p_izq

        # Aplicar baremos a Ganadores
        for g in ganadores:
            st.session_state.juegos_ganados[g] = st.session_state.juegos_ganados.get(g, 0) + 1
            st.session_state.efectividad[g] = st.session_state.efectividad.get(g, 0) + valor_ef
            st.session_state.puntos_favor[g] = st.session_state.puntos_favor.get(g, 0) + p_gan
            st.session_state.puntos_contra[g] = st.session_state.puntos_contra.get(g, 0) + p_per

        # Aplicar baremos a Perdedores
        for p in perdedores:
            st.session_state.efectividad[p] = st.session_state.efectividad.get(p, 0) - valor_ef
            st.session_state.puntos_favor[p] = st.session_state.puntos_favor.get(p, 0) + p_per
            st.session_state.puntos_contra[p] = st.session_state.puntos_contra.get(p, 0) + p_gan

    # Jugadores en pausa (Reposo) - Se les da el juego ganado y Ef neutral/meta según estilo
    for r in st.session_state.jugadores_pausa:
        st.session_state.juegos_ganados[r] = st.session_state.juegos_ganados.get(r, 0) + 1
        st.session_state.efectividad[r] = st.session_state.efectividad.get(r, 0) + (meta // 2)

    st.session_state.ronda_actual += 1
    # Aquí vendría la función de generar_ronda_suiza()
    st.rerun()

# --- 5. INTERFAZ ---
st.title("Asociación de Dominó del Estado Lara (ADEL) - Sistema Suizo")

with st.sidebar:
    st.header("💾 Seguridad del Torneo")
    st.download_button("📥 RESGUARDAR", data=exportar_datos(), file_name="respaldo_torneo.json", mime="application/json")
    archivo = st.file_uploader("📂 RESTAURAR", type=['json'])
    if archivo and st.button("✅ Confirmar"):
        importar_datos(archivo)
    st.markdown("---")
    st.caption("Creado por Poeta")

if st.session_state.registro_abierto:
    st.subheader("📝 Registro de Atletas")
    st.session_state.meta_puntos = st.radio("Meta:", [100, 200], horizontal=True)
    st.text_input("Atleta + ENTER:", key="nuevo_nombre", on_change=agregar_jugador_enter)
    if st.session_state.asistentes:
        st.write(f"**Inscritos:** {', '.join(st.session_state.asistentes)}")
        if st.button("🚀 INICIAR"):
            st.session_state.registro_abierto = False
            # generar_ronda_suiza() - Necesita estar definida
            st.rerun()
else:
    # Mostrar Ranking con los 3 Baremos: 1. G, 2. Ef, 3. Puntos Recibidos (Menor es mejor)
    st.subheader("📊 Ranking Oficial ADEL")
    rk = sorted(st.session_state.asistentes, 
                key=lambda x: (st.session_state.juegos_ganados.get(x, 0), 
                               st.session_state.efectividad.get(x, 0), 
                               -st.session_state.puntos_contra.get(x, 0)), 
                reverse=True)
    
    tabla = []
    for i, j in enumerate(rk):
        tabla.append({
            "Pos": i+1, "Atleta": j, 
            "G": st.session_state.juegos_ganados.get(j, 0), 
            "Ef": st.session_state.efectividad.get(j, 0),
            "P. Contra": st.session_state.puntos_contra.get(j, 0)
        })
    st.table(tabla)
