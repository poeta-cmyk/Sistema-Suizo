import streamlit as st
import math
import random

st.set_page_config(layout="wide")
st.title("Sistema Suizo - Gestión de Rondas")

# --- MEMORIA DEL PROGRAMA ---
if 'asistentes' not in st.session_state:
    st.session_state.asistentes = []
if 'registro_abierto' not in st.session_state:
    st.session_state.registro_abierto = True
if 'ronda_actual' not in st.session_state:
    st.session_state.ronda_actual = 1
if 'historial_puntos' not in st.session_state:
    st.session_state.historial_puntos = {} 
if 'mesas_actuales' not in st.session_state:
    st.session_state.mesas_actuales = []
if 'jugadores_pausa' not in st.session_state:
    st.session_state.jugadores_pausa = []
if 'meta_puntos' not in st.session_state:
    st.session_state.meta_puntos = 100

# --- FUNCIONES DE LÓGICA ---
def registrar_y_limpiar():
    nombre = st.session_state.ingreso_nombre.strip().upper()
    if nombre and nombre not in st.session_state.asistentes:
        st.session_state.asistentes.append(nombre)
        st.session_state.asistentes.sort()
        st.session_state.ingreso_nombre = ""
        st.session_state.historial_puntos[nombre] = 0

def generar_ronda():
    n = len(st.session_state.asistentes)
    if n < 4: return

    # Ordenar por puntos (Sistema Suizo)
    jugadores_ordenados = sorted(st.session_state.asistentes, 
                                 key=lambda x: st.session_state.historial_puntos[x], 
                                 reverse=True)
    
    if st.session_state.ronda_actual == 1:
        random.shuffle(jugadores_ordenados)

    n_mesas = n // 4
    total_mesas = n_mesas * 4
    
    st.session_state.mesas_actuales = [jugadores_ordenados[i:i+4] for i in range(0, total_mesas, 4)]
    st.session_state.jugadores_pausa = jugadores_ordenados[total_mesas:]
    
    # Victoria automática en Pausa
    meta = st.session_state.meta_puntos
    for p in st.session_state.jugadores_pausa:
        st.session_state.historial_puntos[p] += meta

def procesar_ronda():
    # 1. Sumar puntos
    for i in range(len(st.session_state.mesas_actuales)):
        m = st.session_state.mesas_actuales[i]
        p_izq = st.session_state[f"p_izq_{i}_{st.session_state.ronda_actual}"]
        p_der = st.session_state[f"p_der_{i}_{st.session_state.ronda_actual}"]
        
        st.session_state.historial_puntos[m[0]] += p_izq
        st.session_state.historial_puntos[m[2]] += p_izq
        st.session_state.historial_puntos[m[1]] += p_der
        st.session_state.historial_puntos[m[3]] += p_der
        
    # 2. Avanzar ronda y generar nuevos cruces
    st.session_state.ronda_actual += 1
    generar_ronda()

# --- INTERFAZ ---
if st.session_state.registro_abierto:
    st.subheader("Configuración del Torneo")
    st.session_state.meta_puntos = st.radio("Meta de puntos del encuentro:", [100, 200], horizontal=True)
    
    st.text_input("Escriba el nombre o nick del jugador:", key="ingreso_nombre", on_change=registrar_y_limpiar)
    if st.button("Finalizar registro e iniciar Ronda 1"):
        st.session_state.registro_abierto = False
        generar_ronda()
        st.rerun()

# --- PANEL DE INDICADORES ---
n_jugadores = len(st.session_state.asistentes)
if n_jugadores > 0:
    st.markdown("---")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Jugadores", n_jugadores)
    c2.metric("Ronda", st.session_state.ronda_actual)
    c3.metric("Meta", f"{st.session_state.meta_puntos} pts")
    c4.metric("En Pausa", len(st.session_state.jugadores_pausa))

# --- MESAS ---
if not st.session_state.registro_abierto:
    st.header(f"🎲 DISTRIBUCIÓN DE MESAS - RONDA {st.session_state.ronda_actual}")
    
    h1, h2, h3, h4, h5 = st.columns([4, 1, 1, 1, 4])
    h1.write("**PAREJA A/C**")
    h2.write("**Pts**")
    h3.markdown("<center><b>MESA</b></center>", unsafe_allow_html=True)
    h4.write("**Pts**")
    h5.write("**PAREJA B/D**")

    for i, m in enumerate(st.session_state.mesas_actuales):
        c_izq, p_izq_col, n_mesa, p_der_col, c_der = st.columns([4, 1, 1, 1, 4])
        with c_izq: st.info(f"{m[0]} / {m[2]}")
        with p_izq_col: 
            # Agregamos la ronda a la llave (key) para que se resetee el valor
            st.number_input("", key=f"p_izq_{i}_{st.session_state.ronda_actual}", min_value=0, max_value=st.session_state.meta_puntos, step=1, label_visibility="collapsed")
        with n_mesa: st.markdown(f"<h3 style='text-align: center; margin: 0;'>{i+1}</h3>", unsafe_allow_html=True)
        with p_der_col: 
            st.number_input("", key=f"p_der_{i}_{st.session_state.ronda_actual}", min_value=0, max_value=st.session_state.meta_puntos, step=1, label_visibility="collapsed")
        with c_der: st.success(f"{m[1]} / {m[3]}")

    if st.session_state.jugadores_pausa:
        st.warning(f"**EN PAUSA (Ganan {st.session_state.meta_puntos} a {st.session_state.meta_puntos//2}):** {', '.join(st.session_state.jugadores_pausa)}")

    st.markdown("---")
    if st.button(f"REGISTRAR RESULTADOS DE RONDA {st.session_state.ronda_actual}"):
        procesar_ronda()
        st.rerun()

    with st.expander("Ver Tabla de Posiciones Acumulada"):
        ranking = sorted(st.session_state.historial_puntos.items(), key=lambda x: x[1], reverse=True)
        for i, (jug, pts) in enumerate(ranking, 1):
            st.write(f"{i}. **{jug}**: {pts} puntos")
