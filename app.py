import streamlit as st
import math
import random

# Configuración de la página
st.set_page_config(layout="wide", page_title="Sistema Suizo Pro - Franz Lameda")

# --- MEMORIA DEL PROGRAMA ---
if 'asistentes' not in st.session_state:
    st.session_state.asistentes = []
if 'registro_abierto' not in st.session_state:
    st.session_state.registro_abierto = True
if 'ronda_actual' not in st.session_state:
    st.session_state.ronda_actual = 1
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
if 'torneo_finalizado' not in st.session_state:
    st.session_state.torneo_finalizado = False

# --- FUNCIONES ---
def registrar_y_limpiar():
    nombre = st.session_state.ingreso_nombre.strip().upper()
    if nombre and nombre not in st.session_state.asistentes:
        st.session_state.asistentes.append(nombre)
        st.session_state.asistentes.sort()
        st.session_state.ingreso_nombre = ""
        st.session_state.juegos_ganados[nombre] = 0
        st.session_state.puntos_favor[nombre] = 0
        st.session_state.puntos_contra[nombre] = 0

def generar_ronda_suiza():
    # ORDEN DE MÉRITO FRANZ LAMEDA
    jugadores = sorted(st.session_state.asistentes, 
                      key=lambda x: (st.session_state.juegos_ganados[x], 
                                     st.session_state.puntos_favor[x], 
                                     -st.session_state.puntos_contra[x]), 
                      reverse=True)
    
    if st.session_state.ronda_actual == 1:
        random.shuffle(jugadores)
    
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
    st.session_state.jugadores_pausa = disponibles
    
    # ASIGNACIÓN DE PUNTOS POR REPOSO (META COMPLETA Y MEDIA CONTRA)
    meta = st.session_state.meta_puntos
    for p in st.session_state.jugadores_pausa:
        st.session_state.juegos_ganados[p] += 1
        st.session_state.puntos_favor[p] += meta
        st.session_state.puntos_contra[p] += (meta // 2)

def procesar_ronda():
    for i, m in enumerate(st.session_state.mesas_actuales):
        p_izq = st.session_state.get(f"p_izq_{i}_{st.session_state.ronda_actual}", 0)
        p_der = st.session_state.get(f"p_der_{i}_{st.session_state.ronda_actual}", 0)
        
        for p, pf, pc in [(m[0], p_izq, p_der), (m[2], p_izq, p_der), (m[1], p_der, p_izq), (m[3], p_der, p_izq)]:
            st.session_state.puntos_favor[p] += pf
            st.session_state.puntos_contra[p] += pc
            if pf > pc: st.session_state.juegos_ganados[p] += 1

    rondas_max = math.ceil(math.log2(len(st.session_state.asistentes)))
    
    if st.session_state.ronda_actual >= rondas_max:
        st.session_state.torneo_finalizado = True
        st.balloons()
    else:
        st.session_state.ronda_actual += 1
        st.balloons()
        generar_ronda_suiza()

# --- INTERFAZ ---
st.title("🏆 Sistema Suizo - El Poeta Franz Lameda")

if st.session_state.registro_abierto:
    st.session_state.meta_puntos = st.radio("Meta del Encuentro:", [100, 200], horizontal=True)
    st.text_input("Nombre del Jugador:", key="ingreso_nombre", on_change=registrar_y_limpiar)
    if st.button("🚀 INICIAR TORNEO"):
        if len(st.session_state.asistentes) >= 4:
            st.session_state.registro_abierto = False
            generar_ronda_suiza()
            st.rerun()
else:
    rondas_max = math.ceil(math.log2(len(st.session_state.asistentes)))
    
    # PANEL DE CONTROL (AJUSTADO SEGÚN IMAGE_1092A1.PNG)
    cols = st.columns(5)
    cols[0].metric("Ronda", f"{st.session_state.ronda_actual} de {rondas_max}")
    cols[1].metric("Inscritos", len(st.session_state.asistentes))
    cols[2].metric("En Reposo", len(st.session_state.jugadores_pausa)) 
    cols[3].metric("Estado", "FINALIZADO" if st.session_state.torneo_finalizado else "EN CURSO")
    cols[4].metric("Meta", st.session_state.meta_puntos)

    if not st.session_state.torneo_finalizado:
        st.markdown("---")
        for i, m in enumerate(st.session_state.mesas_actuales):
            c1, c2, c3, c4, c5 = st.columns([3,1,1,1,3])
            c1.info(f"{m[0]} / {m[2]}")
            c2.number_input("Pts", key=f"p_izq_{i}_{st.session_state.ronda_actual}", label_visibility="collapsed", min_value=0)
            c3.markdown(f"<center><h3>{i+1}</h3></center>", unsafe_allow_html=True)
            c4.number_input("Pts", key=f"p_der_{i}_{st.session_state.ronda_actual}", label_visibility="collapsed", min_value=0)
            c5.success(f"{m[1]} / {m[3]}")
        
        if st.session_state.jugadores_pausa:
            st.markdown("### 💤 Jugadores en Reposo")
            for p in st.session_state.jugadores_pausa:
                st.warning(f"**{p}** está en reposo. Suma automáticamente **{st.session_state.meta_puntos}** a favor.")
        
        st.markdown("---")
        if st.button("✅ REGISTRAR RESULTADOS"):
            procesar_ronda()
            st.rerun()
    else:
        st.header("🥇 RANKING DEFINITIVO")
        ranking = sorted(st.session_state.asistentes, 
                        key=lambda x: (st.session_state.juegos_ganados[x], 
                                       st.session_state.puntos_favor[x], 
                                       -st.session_state.puntos_contra[x]), reverse=True)
        for i, j in enumerate(ranking, 1):
            color = "gold" if i==1 else "silver" if i==2 else "#cd7f32" if i==3 else "transparent"
            st.markdown(f"<div style='padding:15px; border-radius:10px; border: 2px solid #eee; background-color:{color}; color:black; margin-bottom:10px; font-size:1.2em'><b>{i}° {j}</b> — Ganados: {st.session_state.juegos_ganados[j]} | Efectividad: {st.session_state.puntos_favor[j]} | Recibidos: {st.session_state.puntos_contra[j]}</div>", unsafe_allow_html=True)
