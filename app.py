import streamlit as st
import math
import random
import json

# --- 1. CONFIGURACIÓN ---
st.set_page_config(layout="wide", page_title="ADEL - Sistema Suizo")

# Inicialización de memoria del sistema
keys = ['asistentes', 'juegos_ganados', 'puntos_favor', 'puntos_contra', 
        'efectividad', 'jugadores_reposo_previos', 'mesas_actuales', 
        'jugadores_pausa', 'parejas_previas', 'historial_mesas']

for key in keys:
    if key not in st.session_state:
        st.session_state[key] = [] if any(x in key for x in ['previos', 'mesas', 'pausa', 'parejas', 'asistentes', 'historial']) else {}

if 'ronda_actual' not in st.session_state: st.session_state.ronda_actual = 1
if 'registro_abierto' not in st.session_state: st.session_state.registro_abierto = True
if 'meta_puntos' not in st.session_state: st.session_state.meta_puntos = 100

# --- 2. FUNCIONES LÓGICAS ---

def exportar_datos():
    datos = {k: st.session_state[k] for k in keys + ['ronda_actual', 'registro_abierto', 'meta_puntos']}
    return json.dumps(datos, indent=4)

def generar_ronda_suiza():
    jugadores = sorted(st.session_state.asistentes, 
                      key=lambda x: (st.session_state.juegos_ganados.get(x, 0), 
                                     st.session_state.efectividad.get(x, 0),
                                     -st.session_state.puntos_contra.get(x, 0)), reverse=True)
    
    if st.session_state.ronda_actual == 1 and sum(st.session_state.juegos_ganados.values()) == 0:
        random.shuffle(jugadores)
    
    n_reposo = len(jugadores) % 4
    reposados = jugadores[-n_reposo:] if n_reposo > 0 else []
    activos = jugadores[:-n_reposo] if n_reposo > 0 else jugadores
    
    st.session_state.jugadores_pausa = reposados
    st.session_state.mesas_actuales = [activos[i:i+4] for i in range(0, len(activos), 4)]
    
    st.session_state.historial_mesas.append({
        'ronda': st.session_state.ronda_actual, 
        'mesas': st.session_state.mesas_actuales, 
        'reposo': reposados
    })

def finalizar_ronda():
    meta = st.session_state.meta_puntos
    for i, mesa in enumerate(st.session_state.mesas_actuales):
        p_izq = st.session_state.get(f"p_izq_{i}", 0)
        p_der = st.session_state.get(f"p_der_{i}", 0)
        
        if p_izq >= p_der:
            val_ef = meta - p_der
            gan, per = [mesa[0], mesa[2]], [mesa[1], mesa[3]]
            pg, pp = p_izq, p_der
        else:
            val_ef = meta - p_izq
            gan, per = [mesa[1], mesa[3]], [mesa[0], mesa[2]]
            pg, pp = p_der, p_izq

        for g in gan:
            st.session_state.juegos_ganados[g] = st.session_state.juegos_ganados.get(g, 0) + 1
            st.session_state.efectividad[g] = st.session_state.efectividad.get(g, 0) + val_ef
            st.session_state.puntos_contra[g] = st.session_state.puntos_contra.get(g, 0) + pp
        for p in per:
            st.session_state.efectividad[p] = st.session_state.efectividad.get(p, 0) - val_ef
            st.session_state.puntos_contra[p] = st.session_state.puntos_contra.get(p, 0) + pg

    for r in st.session_state.jugadores_pausa:
        st.session_state.juegos_ganados[r] = st.session_state.juegos_ganados.get(r, 0) + 1
        st.session_state.efectividad[r] = st.session_state.efectividad.get(r, 0) + (meta // 2)

    st.session_state.ronda_actual += 1
    generar_ronda_suiza()
    st.rerun()

# --- 3. INTERFAZ ---

st.title("Asociación de Dominó del Estado Lara (ADEL) - Sistema Suizo")

with st.sidebar:
    st.header("💾 Seguridad")
    st.download_button("📥 RESGUARDAR", data=exportar_datos(), file_name="respaldo_adel.json", mime="application/json")
    st.markdown("---")
    st.caption("Creado por Poeta")

if st.session_state.registro_abierto:
    st.subheader("📝 Registro de Atletas")
    st.session_state.meta_puntos = st.radio("Meta:", [100, 200], horizontal=True)
    
    nombre_input = st.text_input("Atleta + ENTER:").upper().strip()
    if nombre_input and nombre_input not in st.session_state.asistentes:
        st.session_state.asistentes.append(nombre_input)
        st.session_state.asistentes.sort()
        st.rerun()

    if st.session_state.asistentes:
        # RECUPERADO: Contador de inscritos que te encantaba
        st.write(f"**Inscritos ({len(st.session_state.asistentes)}):** {', '.join(st.session_state.asistentes)}")
        
        atleta_sel = st.selectbox("Seleccione para eliminar:", st.session_state.asistentes)
        if st.button("🗑️ Eliminar Seleccionado"):
            st.session_state.asistentes.remove(atleta_sel)
            st.rerun()
            
        if st.button("🚀 INICIAR TORNEO") and len(st.session_state.asistentes) >= 4:
            generar_ronda_suiza()
            st.session_state.registro_abierto = False
            st.rerun()
else:
    st.header(f"🃏 Ronda Actual: {st.session_state.ronda_actual}")
    
    tab1, tab2 = st.tabs(["🗂️ Mesas de Juego", "📊 Tabla de Posiciones"])
    
    with tab1:
        for i, m in enumerate(st.session_state.mesas_
