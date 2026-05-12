import streamlit as st
import math
import random
import time
import json
from datetime import datetime, timedelta

# --- CONFIGURACIÓN Y ESTADO ---
st.set_page_config(layout="wide", page_title="ADEL - Franz Lameda")

# Inicialización de variables de estado
if 'asistentes' not in st.session_state: st.session_state.asistentes = []
if 'juegos_ganados' not in st.session_state: st.session_state.juegos_ganados = {}
if 'puntos_favor' not in st.session_state: st.session_state.puntos_favor = {}
if 'puntos_contra' not in st.session_state: st.session_state.puntos_contra = {}
if 'efectividad' not in st.session_state: st.session_state.efectividad = {}
if 'jugadores_reposo_previos' not in st.session_state: st.session_state.jugadores_reposo_previos = []
if 'mesas_actuales' not in st.session_state: st.session_state.mesas_actuales = []
if 'jugadores_pausa' not in st.session_state: st.session_state.jugadores_pausa = []
if 'parejas_previas' not in st.session_state: st.session_state.parejas_previas = []
if 'historial_mesas' not in st.session_state: st.session_state.historial_mesas = []
if 'ronda_actual' not in st.session_state: st.session_state.ronda_actual = 1
if 'registro_abierto' not in st.session_state: st.session_state.registro_abierto = True
if 'torneo_finalizado' not in st.session_state: st.session_state.torneo_finalizado = False
if 'fin_tiempo' not in st.session_state: st.session_state.fin_tiempo = None
if 'cronometro_activo' not in st.session_state: st.session_state.cronometro_activo = False

# --- FUNCIONES DE GESTIÓN ---
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
            for d in [st.session_state.juegos_ganados, st.session_state.puntos_favor, 
                      st.session_state.puntos_contra, st.session_state.efectividad]:
                if nombre_viejo in d: d[nuevo_nombre] = d.pop(nombre_viejo)
            st.rerun()

def generar_ronda_suiza():
    jugadores = sorted(st.session_state.asistentes, 
                      key=lambda x: (st.session_state.juegos_ganados.get(x, 0), 
                                     st.session_state.efectividad.get(x, 0), 
                                     -st.session_state.puntos_contra.get(x, 0)), 
                      reverse=True)
    if st.session_state.ronda_actual == 1: random.shuffle(jugadores)
    n_reposo = len(jugadores) % 4
    reposados_hoy = []
    if n_reposo > 0:
        candidatos = [j for j in reversed(jugadores) if j not in st.session_state.jugadores_reposo_previos]
        if not candidatos: st.session_state.jugadores_reposo_previos = []; candidatos = list(reversed(jugadores))
        reposados_hoy = candidatos[:n_reposo]
        for r in reposados_hoy:
            jugadores.remove(r)
            st.session_state.jugadores_reposo_previos.append(r)
    st.session_state.jugadores_pausa = reposados_hoy
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
        'reposo': reposados_hoy.copy(),
        'resultados': {}
    })

def finalizar_ronda():
    meta = st.session_state.meta_puntos
    idx_h = next(i for i, h in enumerate(st.session_state.historial_mesas) if h['ronda'] == st.session_state.ronda_actual)
    for i, m in enumerate(st.session_state.mesas_actuales):
        p_izq = st.session_state.get(f"p_izq_{i}_{st.session_state.ronda_actual}", 0)
        p_der = st.session_state.get(f"p_der_{i}_{st.session_state.ronda_actual}", 0)
        st.session_state.historial_mesas[idx_h]['resultados'][i] = {'izq': p_izq, 'der': p_der}
        ef_izq = (p_izq - meta) if p_izq < p_der else (meta - p_der)
        ef_der = (p_der - meta) if p_der < p_izq else (meta - p_izq)
        for p, pf, pc, ef in [(m[0], p_izq, p_der, ef_izq), (m[2], p_izq, p_der, ef_izq), 
                              (m[1], p_der, p_izq, ef_der), (m[3], p_der, p_izq, ef_der)]:
            st.session_state.puntos_favor[p] = st.session_state.puntos_favor.get(p, 0) + pf
            st.session_state.puntos_contra[p] = st.session_state.puntos_contra.get(p, 0) + pc
            st.session_state.efectividad[p] = st.session_state.efectividad.get(p, 0) + ef
            if pf > pc: st.session_state.juegos_ganados[p] = st.session_state.juegos_ganados.get(p, 0) + 1
    for r in st.session_state.jugadores_pausa:
        st.session_state.juegos_ganados[r] = st.session_state.juegos_ganados.get(r, 0) + 1
        st.session_state.efectividad[r] = st.session_state.efectividad.get(r, 0) + (meta // 2)
    st.session_state.fin_tiempo = None; st.session_state.cronometro_activo = False
    if st.session_state.ronda_actual >= math.ceil(math.log2(len(st.session_state.asistentes))):
        st.session_state.torneo_finalizado = True
    else: st.session_state.ronda_actual += 1; generar_ronda_suiza()
    st.rerun()

# --- INTERFAZ ---
st.title("🏆 Gala de los 13 - Franz Lameda (Asociación de Dominó del Estado Lara ADEL)")

# BARRA LATERAL (Sidebar)
with st.sidebar:
    if not st.session_state.registro_abierto:
        st.header("⏱️ Reloj de Ronda")
        dur_ajuste = st.number_input("Minutos:", 1, 60, 20)
        c_btns = st.columns(2)
        with c_btns[0]:
            if st.button("🔔 INICIAR"):
                st.session_state.fin_tiempo = datetime.now() + timedelta(minutes=dur_ajuste)
                st.session_state.cronometro_activo = True; st.rerun()
        with c_btns[1]:
            if st.button("🔄 REINICIAR"):
                st.session_state.fin_tiempo = None; st.session_state.cronometro_activo = False; st.rerun()
        if st.session_state.cronometro_activo:
            restante = st.session_state.fin_tiempo - datetime.now()
            segundos = restante.total_seconds()
            if segundos > 0:
                m, s = divmod(int(segundos), 60)
                if segundos <= 300:
                    st.markdown(f'<div style="background-color:#FFEB3B;padding:20px;border-radius:10px;border:5px solid #F44336;text-align:center;"><p style="color:#F44336;font-size:20px;font-weight:bold;">⚠️ ÚLTIMOS MINUTOS</p><h1 style="color:#F44336;font-size:60px;margin:0;">{m:02d}:{s:02d}</h1></div>', unsafe_allow_html=True)
                else: st.markdown(f"<h1 style='text-align:center;'>⏳ {m:02d}:{s:02d}</h1>", unsafe_allow_html=True)
                time.sleep(1); st.rerun()
            else:
                st.markdown('<div style="background-color:#F44336;padding:20px;border-radius:10px;text-align:center;"><h2 style="color:white;margin:0;">🛑 TIEMPO VENCIDO</h2></div>', unsafe_allow_html=True)
                st.session_state.cronometro_activo = False
    
    # FIRMA DEL POETA (Letras pequeñas al final de la barra lateral)
    st.markdown("---")
    st.caption("Creado por Poeta")

# CUERPO PRINCIPAL
if st.session_state.registro_abierto:
    st.subheader("📝 Registro de Atletas")
    st.session_state.meta_puntos = st.radio("Meta:", [100, 200], horizontal=True)
    st.text_input("Nombre y ENTER:", key="nuevo_nombre", on_change=agregar_jugador_enter)
    if st.session_state.asistentes:
        st.write(f"**Inscritos ({len(st.session_state.asistentes)}):** {', '.join(st.session_state.asistentes)}")
        col1, col2, col3 = st.columns([3, 0.5, 0.5])
        with col1: sel = st.selectbox("Seleccione Atleta:", st.session_state.asistentes)
        with col2: 
            if st.button("✏️"): editar_atleta_dialog(sel)
        with col3:
            if st.button("🗑️"): st.session_state.asistentes.remove(sel); st.session_state.asistentes.sort(); st.rerun()
    if st.button("🚀 INICIAR TORNEO") and len(st.session_state.asistentes) >= 4:
        st.session_state.registro_abierto = False; generar_ronda_suiza(); st.rerun()
else:
    if not st.session_state.torneo_finalizado:
        opciones_ronda = list(range(1, st.session_state.ronda_actual + 1))
        ronda_v = st.selectbox("🔍 Ver Ronda:", opciones_ronda, index=len(opciones_ronda)-1)
        if st.session_state.ronda_actual > 1:
            with st.expander("📊 RANKING ACTUAL"):
                rk = sorted(st.session_state.asistentes, key=lambda x: (st.session_state.juegos_ganados.get(x,0), st.session_state.efectividad.get(x,0), -st.session_state.puntos_contra.get(x,0)), reverse=True)
                st.table([{"Pos": i+1, "Jugador": j, "G": st.session_state.juegos_ganados.get(j, 0), "Ef": st.session_state.efectividad.get(j, 0)} for i, j in enumerate(rk)])

        datos_r = next((it for it in st.session_state.historial_mesas if it['ronda'] == ronda_v), None)
        if datos_r:
            for i, m in enumerate(datos_r['mesas']):
                c1, c2, c3 = st.columns([2, 1, 2])
                with c1: st.info(f"{m[0]} y {m[2]}")
                with
