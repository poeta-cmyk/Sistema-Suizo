import streamlit as st
import math
import random

# Configuración de la página
st.set_page_config(layout="wide", page_title="Sistema Suizo Pro")

# --- MEMORIA DEL PROGRAMA (SESSION STATE) ---
if 'asistentes' not in st.session_state:
    st.session_state.asistentes = []
if 'registro_abierto' not in st.session_state:
    st.session_state.registro_abierto = True
if 'ronda_actual' not in st.session_state:
    st.session_state.ronda_actual = 1

# Estadísticas para el orden de mérito de Franz Lameda
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

# --- FUNCIONES DE LÓGICA ---
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
    # ORDEN ESTRICTO DE MÉRITO (Franz Lameda):
    # 1. Ganados (Desc) | 2. Favor (Desc) | 3. Contra (Asc)
    jugadores = sorted(st.session_state.asistentes, 
                      key=lambda x: (
                          st.session_state.juegos_ganados[x], 
                          st.session_state.puntos_favor[x], 
                          -st.session_state.puntos_contra[x]
                      ), 
                      reverse=True)
    
    if st.session_state.ronda_actual == 1:
        random.shuffle(jugadores)
    
    n_mesas = len(jugadores) // 4
    mesas_generadas = []
    disponibles = jugadores.copy()
    
    for _ in range(n_mesas):
        # El primero de la tabla (A) busca socio (C)
        a = disponibles.pop(0)
        c_idx = -1
        for i, cand in enumerate(disponibles):
            if {a, cand} not in st.session_state.parejas_previas:
                c_idx = i
                break
        
        if c_idx != -1:
            c = disponibles.pop(c_idx)
            st.session_state.parejas_previas.append({a, c})
        else:
            c = disponibles.pop(0)
            
        # El siguiente líder disponible (B) busca socio (D)
        b = disponibles.pop(0)
        d_idx = -1
        for i, cand in enumerate(disponibles):
            if {b, cand} not in st.session_state.parejas_previas:
                d_idx = i
                break
        
        if d_idx != -1:
            d = disponibles.pop(d_idx)
            st.session_state.parejas_previas.append({b, d})
        else:
            d = disponibles.pop(0)
        
        # Estructura: Pareja Izq (A/C) vs Pareja Der (B/D)
        mesas_generadas.append([a, b, c, d])
        
    st.session_state.mesas_actuales = mesas_generadas
    st.session_state.jugadores_pausa = disponibles
    
    # El receso gana automáticamente
    meta = st.session_state.meta_puntos
    for p in st.session_state.jugadores_pausa:
        st.session_state.juegos_ganados[p] += 1
        st.session_state.puntos_favor[p] += meta
        st.session_state.puntos_contra[p] += (meta // 2)

def procesar_ronda():
    # Sumar puntos usando los nombres correctos de las variables
    for i in range(len(st.session_state.mesas_actuales)):
        m = st.session_state.mesas_actuales[i]
        key_izq = f"p_izq_{i}_{st.session_state.ronda_actual}"
        key_der = f"p_der_{i}_{st.session_state.ronda_actual}"
        
        p_izq = st.session_state.get(key_izq, 0)
        p_der = st.session_state.get(key_der, 0)
        
        # Pareja A/C (Izquierda)
        for p in [m[0], m[2]]:
            st.session_state.puntos_favor[p] += p_izq
            st.session_state.puntos_contra[p] += p_der
            if p_izq > p_der:
                st.session_state.juegos_ganados[p] += 1
                
        # Pareja B/D (Derecha)
        for p in [m[1], m[3]]:
            st.session_state.puntos_favor[p] += p_der
            st.session_state.puntos_contra[p] += p_izq
            if p_der > p_izq:
                st.session_state.juegos_ganados[p] += 1
        
    st.session_state.ronda_actual += 1
    generar_ronda_suiza()

# --- INTERFAZ VISUAL ---
st.title("Sistema Suizo Pro - El Poeta Franz Lameda")

if st.session_state.registro_abierto:
    st.subheader("Configuración e Inscripción")
    st.session_state.meta_puntos = st.radio("Meta de puntos:", [100, 200], horizontal=True)
    st.text_input("Nombre del jugador:", key="ingreso_nombre", on_change=registrar_y_limpiar)
    
    if st.button("Finalizar Registro e Iniciar"):
        if len(st.session_state.asistentes) >= 4:
            st.session_state.registro_abierto = False
            generar_ronda_suiza()
            st.rerun()
        else:
            st.error("Mínimo 4 jugadores.")

    for i, jug in enumerate(st.session_state.asistentes, 1):
        c_n, c_d = st.columns([0.9, 0.1])
        c_n.write(f"{i}. {jug}")
        if c_d.button("X", key=f"del_{jug}"):
            st.session_state.asistentes.remove(jug)
            st.rerun()

else:
    # PANEL DE CONTROL
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Jugadores", len(st.session_state.asistentes))
    c2.metric("Ronda Actual", st.session_state.ronda_actual)
    c3.metric("Meta", f"{st.session_state.meta_puntos} pts")
    c4.metric("En Pausa", len(st.session_state.jugadores_pausa))

    st.markdown("---")
    st.header(f"🎲 DISTRIBUCIÓN DE MESAS - RONDA {st.session_state.ronda_actual}")

    # Encabezados de Espejo
    h1, h2, h3, h4, h5 = st.columns([4, 1, 1, 1, 4])
    h1.write("**PAREJA A/C (Izquierda)**")
    h2.write("**Pts**")
    h3.markdown("<center><b>MESA</b></center>", unsafe_allow_html=True)
    h4.write("**Pts**")
    h5.write("**PAREJA B/D (Derecha)**")

    for i, m in enumerate(st.session_state.mesas_actuales):
        col_izq, pts_izq, num_mesa, pts_der, col_der = st.columns([4, 1, 1, 1, 4])
        with col_izq: st.info(f"{m[0]} / {m[2]}")
        with pts_izq: 
            st.number_input("", key=f"p_izq_{i}_{st.session_state.ronda_actual}", min_value=0, max_value=st.session_state.meta_puntos, step=1, label_visibility="collapsed")
        with num_mesa: 
            st.markdown(f"<h3 style='text-align: center; margin: 0;'>{i+1}</h3>", unsafe_allow_html=True)
        with pts_der: 
            st.number_input("", key=f"p_der_{i}_{st.session_state.ronda_actual}", min_value=0, max_value=st.session_state.meta_puntos, step=1, label_visibility="collapsed")
        with col_der: st.success(f"{m[1]} / {m[3]}")

    if st.session_state.jugadores_pausa:
        st.warning(f"**EN PAUSA (Ganan {st.session_state.meta_puntos} a {st.session_state.meta_puntos//2}):** {', '.join(st.session_state.jugadores_pausa)}")

    st.markdown("---")
    if st.button(f"REGISTRAR RESULTADOS DE RONDA {st.session_state.ronda_actual}"):
        procesar_ronda()
        st.rerun()

    with st.expander("Tabla de Posiciones Pro (Mérito Franz Lameda)"):
        ranking = sorted(st.session_state.asistentes, 
                        key=lambda x: (st.session_state.juegos_ganados[x], st.session_state.puntos_favor[x], -st.session_state.puntos_contra[x]), 
                        reverse=True)
        for i, j in enumerate(ranking, 1):
            st.write(f"{i}. **{j}** | Ganados: {st.session_state.juegos_ganados[j]} | Favor: {st.session_state.puntos_favor[j]} | Contra: {st.session_state.puntos_contra[j]}")
