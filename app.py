import streamlit as st
import math
import random
from datetime import datetime, timedelta

# --- CONFIGURACIÓN Y ESTADO ---
st.set_page_config(layout="wide", page_title="Sistema Suizo Pro - Franz Lameda")

# Inicialización de variables protegidas
for key in ['asistentes', 'juegos_ganados', 'puntos_favor', 'puntos_contra', 
            'jugadores_reposo_previos', 'mesas_actuales', 'jugadores_pausa', 
            'parejas_previas', 'historial_mesas']:
    if key not in st.session_state:
        st.session_state[key] = [] if any(x in key for x in ['previos', 'mesas', 'pausa', 'parejas', 'asistentes', 'historial']) else {}

if 'ronda_actual' not in st.session_state: st.session_state.ronda_actual = 1
if 'registro_abierto' not in st.session_state: st.session_state.registro_abierto = True
if 'torneo_finalizado' not in st.session_state: st.session_state.torneo_finalizado = False
if 'lanzar_globos' not in st.session_state: st.session_state.lanzar_globos = False
if 'fin_tiempo' not in st.session_state: st.session_state.fin_tiempo = None

# --- FUNCIONES CORE ---
def agregar_jugador_enter():
    nombre = st.session_state.nuevo_nombre.strip().upper()
    if nombre and nombre not in st.session_state.asistentes:
        st.session_state.asistentes.append(nombre)
        st.session_state.asistentes.sort()
    st.session_state.nuevo_nombre = "" 

def generar_ronda_suiza():
    jugadores = sorted(st.session_state.asistentes, 
                      key=lambda x: (st.session_state.juegos_ganados.get(x, 0), 
                                     st.session_state.puntos_favor.get(x, 0), 
                                     -st.session_state.puntos_contra.get(x, 0)), 
                      reverse=True)
    
    if st.session_state.ronda_actual == 1:
        random.shuffle(jugadores)
    
    n_reposo = len(jugadores) % 4
    reposados_hoy = []
    if n_reposo > 0:
        candidatos = [j for j in reversed(jugadores) if j not in st.session_state.jugadores_reposo_previos]
        if not candidatos:
            st.session_state.jugadores_reposo_previos = []
            candidatos = list(reversed(jugadores))
        
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
        'reposo': reposados_hoy.copy()
    })

def finalizar_ronda():
    # 1. Procesar mesas jugadas
    for i, m in enumerate(st.session_state.mesas_actuales):
        p_izq = st.session_state.get(f"p_izq_{i}_{st.session_state.ronda_actual}", 0)
        p_der = st.session_state.get(f"p_der_{i}_{st.session_state.ronda_actual}")
        
        # Puntos para cada jugador de la pareja
        for p, pf, pc in [(m[0], p_izq, p_der), (m[2], p_izq, p_der), (m[1], p_der, p_izq), (m[3], p_der, p_izq)]:
            st.session_state.puntos_favor[p] = st.session_state.puntos_favor.get(p, 0) + pf
            st.session_state.puntos_contra[p] = st.session_state.puntos_contra.get(p, 0) + pc
            if pf > pc: 
                st.session_state.juegos_ganados[p] = st.session_state.juegos_ganados.get(p, 0) + 1

    # 2. Procesar jugador en reposo (Asignación única)
    for r in st.session_state.jugadores_pausa:
        st.session_state.juegos_ganados[r] = st.session_state.juegos_ganados.get(r, 0) + 1
        st.session_state.puntos_favor[r] = st.session_state.puntos_favor.get(r, 0) + (st.session_state.meta_puntos // 2)
        st.session_state.puntos_contra[r] = st.session_state.puntos_contra.get(r, 0) + 0

    rondas_max = math.ceil(math.log2(len(st.session_state.asistentes)))
    st.session_state.lanzar_globos = True
    st.session_state.fin_tiempo = None 
    
    if st.session_state.ronda_actual >= rondas_max:
        st.session_state.torneo_finalizado = True
    else:
        st.session_state.ronda_actual += 1
        generar_ronda_suiza()
    st.rerun()

# --- INTERFAZ ---
st.title("🏆 Sistema Suizo - El Poeta Franz Lameda")

if st.session_state.lanzar_globos:
    st.balloons()
    st.session_state.lanzar_globos = False

if st.session_state.registro_abierto:
    st.session_state.meta_puntos = st.radio("Meta del Encuentro:", [100, 200], horizontal=True)
    st.text_input("Escribe el nombre y presiona ENTER para añadir:", key="nuevo_nombre", on_change=agregar_jugador_enter)
    st.write(f"**Inscritos ({len(st.session_state.asistentes)}):** {', '.join(st.session_state.asistentes)}")
    if st.button("🚀 EMPEZAR TORNEO") and len(st.session_state.asistentes) >= 4:
        st.session_state.registro_abierto = False
        generar_ronda_suiza()
        st.rerun()
else:
    r_max = math.ceil(math.log2(len(st.session_state.asistentes)))
    
    with st.sidebar:
        st.header("⏱️ Cronómetro")
        dur = st.number_input("Minutos de la ronda:", 1, 60, 20)
        if st.button("🔔 Iniciar Tiempo"):
            st.session_state.fin_tiempo = datetime.now() + timedelta(minutes=dur)
        if st.session_state.fin_tiempo:
            rest = st.session_state.fin_tiempo - datetime.now()
            if rest.total_seconds() > 0:
                m, s = divmod(int(rest.total_seconds()), 60)
                st.header(f"⏳ {m:02d}:{s:02d}")
                if st.button("🔄 Actualizar Reloj"): st.rerun()
            else:
                st.error("🚨 ¡TIEMPO AGOTADO!")

    if not st.session_state.torneo_finalizado:
        opciones_ronda = list(range(1, st.session_state.ronda_actual + 1))
        ronda_a_ver = st.selectbox("🔍 Ver Ronda:", opciones_ronda, index=len(opciones_ronda)-1)

        c1, c2, c3 = st.columns(3)
        c1.metric("Ronda actual", f"{st.session_state.ronda_actual} / {r_max}")
        c2.metric("Meta", st.session_state.meta_puntos)
        c3.metric("Jugadores", len(st.session_state.asistentes))

        if st.session_state.ronda_actual > 1:
            with st.expander("📊 RANKING ACTUAL", expanded=False):
                ranking_temp = sorted(st.session_state.asistentes, 
                                     key=lambda x: (st.session_state.juegos_ganados.get(x,0), 
                                                    st.session_state.puntos_favor.get(x,0), 
                                                    -st.session_state.puntos_contra.get(x,0)), reverse=True)
                st.table([{"Pos": i+1, "Jugador": j, "G": st.session_state.juegos_ganados.get(j, 0), "Pts+": st.session_state.puntos_favor.get(j, 0)} for i, j in enumerate(ranking_temp)])

        st.markdown("---")
        datos_ronda = next((item for item in st.session_state.historial_mesas if item['ronda'] == ronda_a_ver), None)
        
        if datos_ronda:
            for i, m in enumerate(datos_ronda['mesas']):
                col1, col2, col3 = st.columns([2, 1, 2])
                with col1: st.info(f"{m[0]} y {m[2]}")
                with col2: 
                    disponible = ronda_a_ver == st.session_state.ronda_actual
                    st.number_input("Pts", key=f"p_izq_{i}_{ronda_a_ver}", min_value=0, step=1, disabled=not disponible)
                    st.markdown(f"<center><b>Mesa {i+1}</b></center>", unsafe_allow_html=True)
                    st.number_input("Pts", key=f"p_der_{i}_{ronda_a_ver}", min_value=0, step=1, disabled=not disponible)
                with col3: st.success(f"{m[1]} y {m[3]}")
            
            if datos_ronda['reposo']:
                st.warning(f"💤 **EN REPOSO:** {', '.join(datos_ronda['reposo'])}")
        
        if st.session_state.ronda_actual == ronda_a_ver:
            if st.button(f"💾 Registrar Ronda {st.session_state.ronda_actual}"):
                finalizar_ronda()
    else:
        st.header("🥇 POSICIONES FINALES")
        ranking_final = sorted(st.session_state.asistentes, 
                        key=lambda x: (st.session_state.juegos_ganados.get(x,0), 
                                       st.session_state.puntos_favor.get(x,0), 
                                       -st.session_state.puntos_contra.get(x,0)), reverse=True)
        st.table([{"Pos": i+1, "Jugador": j, "G": st.session_state.juegos_ganados.get(j, 0), "Pts+": st.session_state.puntos_favor.get(j, 0), "Pts-": st.session_state.puntos_contra.get(j, 0)} for i, j in enumerate(ranking_final)])
