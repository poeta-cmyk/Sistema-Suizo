import streamlit as st
import math
import random
import json

# --- 1. CONFIGURACIÓN ---
st.set_page_config(layout="wide", page_title="ADEL - Sistema Suizo")

# Memoria del sistema
if 'asistentes' not in st.session_state: st.session_state.asistentes = []
if 'juegos_ganados' not in st.session_state: st.session_state.juegos_ganados = {}
if 'efectividad' not in st.session_state: st.session_state.efectividad = {}
if 'puntos_contra' not in st.session_state: st.session_state.puntos_contra = {}
if 'ronda_actual' not in st.session_state: st.session_state.ronda_actual = 1
if 'registro_abierto' not in st.session_state: st.session_state.registro_abierto = True
if 'meta_puntos' not in st.session_state: st.session_state.meta_puntos = 100
if 'mesas_actuales' not in st.session_state: st.session_state.mesas_actuales = []
if 'jugadores_pausa' not in st.session_state: st.session_state.jugadores_pausa = []

# --- 2. FUNCIONES LÓGICAS ---

def exportar_datos():
    datos = {k: st.session_state[k] for k in ['asistentes', 'juegos_ganados', 'efectividad', 'puntos_contra', 'ronda_actual', 'registro_abierto', 'meta_puntos']}
    return json.dumps(datos, indent=4)

def procesar_registro():
    nombre = st.session_state.nuevo_atleta.strip().upper()
    if nombre and nombre not in st.session_state.asistentes:
        st.session_state.asistentes.append(nombre)
        st.session_state.asistentes.sort()
    st.session_state.nuevo_atleta = ""

@st.dialog("Editar Atleta")
def editar_atleta_dialog(nombre_viejo):
    nuevo_nombre = st.text_input("Corregir nombre:", value=nombre_viejo).strip().upper()
    if st.button("✅ GUARDAR CAMBIO"):
        if nuevo_nombre and nuevo_nombre != nombre_viejo:
            idx = st.session_state.asistentes.index(nombre_viejo)
            st.session_state.asistentes[idx] = nuevo_nombre
            st.session_state.asistentes.sort()
            st.rerun()

def generar_ronda_suiza():
    # Ordenar por Baremos ADEL: G, Ef, -Contra
    jugadores = sorted(st.session_state.asistentes, 
                      key=lambda x: (st.session_state.juegos_ganados.get(x, 0), 
                                     st.session_state.efectividad.get(x, 0),
                                     -st.session_state.puntos_contra.get(x, 0)), reverse=True)
    
    if st.session_state.ronda_actual == 1 and sum(st.session_state.juegos_ganados.values()) == 0:
        random.shuffle(jugadores)
    
    n_reposo = len(jugadores) % 4
    st.session_state.jugadores_pausa = jugadores[-n_reposo:] if n_reposo > 0 else []
    activos = jugadores[:-n_reposo] if n_reposo > 0 else jugadores
    
    st.session_state.mesas_actuales = [activos[i:i+4] for i in range(0, len(activos), 4)]

def finalizar_ronda():
    meta = st.session_state.meta_puntos
    for i, mesa in enumerate(st.session_state.mesas_actuales):
        p_izq = st.session_state.get(f"p_izq_{i}", 0)
        p_der = st.session_state.get(f"p_der_{i}", 0)
        
        # Lógica ADEL: Ef = Meta - Puntos Perdedor
        if p_izq >= p_der:
            val_ef = meta - p_der
            gan, per, pg, pp = [mesa[0], mesa[2]], [mesa[1], mesa[3]], p_izq, p_der
        else:
            val_ef = meta - p_izq
            gan, per, pg, pp = [mesa[1], mesa[3]], [mesa[0], mesa[2]], p_der, p_izq
            
        for g in gan:
            st.session_state.juegos_ganados[g] = st.session_state.juegos_ganados.get(g, 0) + 1
            st.session_state.efectividad[g] = st.session_state.efectividad.get(g, 0) + val_ef
            st.session_state.puntos_contra[g] = st.session_state.puntos_contra.get(g, 0) + pp
        for p in per:
            st.session_state.efectividad[p] = st.session_state.efectividad.get(p, 0) - val_ef
            st.session_state.puntos_contra[p] = st.session_state.puntos_contra.get(p, 0) + pg

    # Lógica de Reposo: Gana mitad de meta a 0
    for r in st.session_state.jugadores_pausa:
        st.session_state.juegos_ganados[r] = st.session_state.juegos_ganados.get(r, 0) + 1
        st.session_state.efectividad[r] = st.session_state.efectividad.get(r, 0) + (meta // 2)
        st.session_state.puntos_contra[r] = st.session_state.puntos_contra.get(r, 0) + 0

    st.session_state.ronda_actual += 1
    generar_ronda_suiza()
    st.rerun()

# --- 3. INTERFAZ ---
st.title("Asociación de Dominó del Estado Lara (ADEL) - Sistema Suizo")

with st.sidebar:
    st.header("💾 Seguridad")
    st.download_button("📥 RESGUARDAR", data=exportar_datos(), file_name="respaldo.json", mime="application/json")
    st.markdown("---")
    st.caption("Creado por Poeta")

if st.session_state.registro_abierto:
    st.subheader("📝 Registro de Atletas")
    st.session_state.meta_puntos = st.radio("Meta:", [100, 200], horizontal=True)
    st.text_input("Atleta + ENTER:", key="nuevo_atleta", on_change=procesar_registro)

    if st.session_state.asistentes:
        st.info(f"**Inscritos ({len(st.session_state.asistentes)}):** {', '.join(st.session_state.asistentes)}")
        col_s, col_e, col_b = st.columns([2, 0.5, 0.5])
        with col_s: sel = st.selectbox("Gestionar atleta:", st.session_state.asistentes, label_visibility="collapsed")
        with col_e: 
            if st.button("✏️"): editar_atleta_dialog(sel)
        with col_b:
            if st.button("🗑️"):
                st.session_state.asistentes.remove(sel)
                st.rerun()
            
        if st.button("🚀 INICIAR TORNEO") and len(st.session_state.asistentes) >= 4:
            generar_ronda_suiza()
            st.session_state.registro_abierto = False
            st.rerun()
else:
    st.header(f"🃏 Ronda Actual: {st.session_state.ronda_actual}")
    t1, t2 = st.tabs(["🗂️ Mesas de Juego", "📊 Ranking Oficial"])
    
    with t1:
        # AQUÍ APARECE EL REPOSO DE UNA VEZ
        if st.session_state.jugadores_pausa:
            st.warning(f"💤 **EN REPOSO:** {', '.join(st.session_state.jugadores_pausa)} (Gana {st.session_state.meta_puntos // 2} a 0)")
        
        for i, m in enumerate(st.session_state.mesas_actuales):
            st.markdown(f"#### Mesa {i+1}")
            c1, c2, c3 = st.columns([2, 1, 2])
            with c1: st.info(f"**Pareja 1:**\n\n{m[0]} / {m[2]}")
            with c2:
                st.number_input(f"Pts P1", key=f"p_izq_{i}", min_value=0, step=1)
                st.number_input(f"Pts P2", key=f"p_der_{i}", min_value=0, step=1)
            with c3: st.success(f"**Pareja 2:**\n\n{m[1]} / {m[3]}")
            st.markdown("---")
            
        if st.button("💾 FINALIZAR RONDA"):
            finalizar_ronda()

    with t2:
        rk = sorted(st.session_state.asistentes, 
                    key=lambda x: (st.session_state.juegos_ganados.get(x,0), 
                                   st.session_state.efectividad.get(x,0), 
                                   -st.session_state.puntos_contra.get(x,0)), reverse=True)
        st.table([{"Pos": i+1, "Atleta": j, "G": st.session_state.juegos_ganados.get(j,0), 
                   "Ef": st.session_state.efectividad.get(j,0), "Contra": st.session_state.puntos_contra.get(j,0)} 
                  for i, j in enumerate(rk)])
