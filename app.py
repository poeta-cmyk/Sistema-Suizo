import streamlit as st
import math
import random
import time
from datetime import datetime, timedelta

# --- CONFIGURACIÓN Y ESTADO (INVARIABLE) ---
st.set_page_config(layout="wide", page_title="Sistema Suizo Pro - Franz Lameda")

for key in ['asistentes', 'juegos_ganados', 'puntos_favor', 'puntos_contra', 
            'efectividad', 'jugadores_reposo_previos', 'mesas_actuales', 
            'jugadores_pausa', 'parejas_previas', 'historial_mesas']:
    if key not in st.session_state:
        st.session_state[key] = [] if any(x in key for x in ['previos', 'mesas', 'pausa', 'parejas', 'asistentes', 'historial']) else {}

if 'ronda_actual' not in st.session_state: st.session_state.ronda_actual = 1
if 'registro_abierto' not in st.session_state: st.session_state.registro_abierto = True
if 'torneo_finalizado' not in st.session_state: st.session_state.torneo_finalizado = False
if 'lanzar_globos' not in st.session_state: st.session_state.lanzar_globos = False
if 'fin_tiempo' not in st.session_state: st.session_state.fin_tiempo = None
if 'cronometro_activo' not in st.session_state: st.session_state.cronometro_activo = False

# --- FUNCIONES CORE (INVARIABLES) ---
def agregar_jugador_enter():
    nombre = st.session_state.nuevo_nombre.strip().upper()
    if nombre and nombre not in st.session_state.asistentes:
        st.session_state.asistentes.append(nombre)
        st.session_state.asistentes.sort()
    st.session_state.nuevo_nombre = "" 

def eliminar_jugadores():
    for j in st.session_state.a_eliminar:
        st.session_state.asistentes.remove(j)
    st.session_state.asistentes.sort()

# --- NUEVA FUNCIÓN DE EDICIÓN ---
@st.dialog("Editar Atleta")
def editar_atleta_dialog(nombre_viejo):
    nuevo_nombre = st.text_input("Corregir nombre de Atleta:", value=nombre_viejo).strip().upper()
    if st.button("✅ GUARDAR CAMBIO"):
        if nuevo_nombre and nuevo_nombre != nombre_viejo:
            # Actualizar en la lista principal
            idx = st.session_state.asistentes.index(nombre_viejo)
            st.session_state.asistentes[idx] = nuevo_nombre
            st.session_state.asistentes.sort()
            
            # Traspasar estadísticas si existen
            for dict_stat in [st.session_state.juegos_ganados, st.session_state.puntos_favor, 
                             st.session_state.puntos_contra, st.session_state.efectividad]:
                if nombre_viejo in dict_stat:
                    dict_stat[nuevo_nombre] = dict_stat.pop(nombre_viejo)
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
        a = disponibles.pop(0); c_idx = next((i for i, cand in enumerate(disponibles) if {a, cand} not in st.session_state.parejas_previas), 0)
        c = disponibles.pop(c_idx); st.session_state.parejas_previas.append({a, c})
        b = disponibles.pop(0); d_idx = next((i for i, cand in enumerate(disponibles) if {b, cand} not in st.session_state.parejas_previas), 0)
        d = disponibles.pop(d_idx); st.session_state.parejas_previas.append({b, d})
        mesas_generadas.append([a, b, c, d])
    st.session_state.mesas_actuales = mesas_generadas
    st.session_state.historial_mesas.append({'ronda': st.session_state.ronda_actual, 'mesas': mesas_generadas, 'reposo': reposados_hoy.copy()})

def finalizar_ronda():
    meta = st.session_state.meta_puntos
    for i, m in enumerate(st.session_state.mesas_actuales):
        p_izq = st.session_state.get(f"p_izq_{i}_{st.session_state.ronda_actual}", 0)
        p_der = st.session_state.get(f"p_der_{i}_{st.session_state.ronda_actual}", 0)
        ef_izq = (p_izq - meta) if p_izq < p_der else (meta - p_der)
        ef_der = (p_der - meta) if p_der < p_izq else (meta - p_izq)
        for p, pf, pc, ef in [(m[0], p_izq, p_der, ef_izq), (m[2], p_izq, p_der, ef_izq), 
                              (m[1], p_der, p_izq, ef_der), (m[3], p_der, p_izq, ef_der)]:
            st.session_state.puntos_favor[p] = st.session_state.puntos_favor.get(p, 0) + pf
            st.session_state.puntos_contra[p] = st.session_state.puntos_contra.get(p, 0) + pc
            st.session_state.efectividad[p] = st.session_state.efectividad.get(p, 0) + ef
            if pf > pc: st.session_state.juegos_ganados[p] = st.session_state.juegos_ganados.get(p, 0) + 1
    beneficio_reposo = meta // 2
    for r in st.session_state.jugadores_pausa:
        st.session_state.juegos_ganados[r] = st.session_state.juegos_ganados.get(r, 0) + 1
        st.session_state.efectividad[r] = st.session_state.efectividad.get(r, 0) + beneficio_reposo
        st.session_state.puntos_contra[r] = st.session_state.puntos_contra.get(r, 0) + 0
    st.session_state.lanzar_globos = True
    st.session_state.fin_tiempo = None 
    st.session_state.cronometro_activo = False
    if st.session_state.ronda_actual >= math.ceil(math.log2(len(st.session_state.asistentes))): st.session_state.torneo_finalizado = True
    else:
        st.session_state.ronda_actual += 1
        generar_ronda_suiza()
    st.rerun()

# --- INTERFAZ ---
st.title("🏆 Sistema Suizo - El Poeta Franz Lameda")

if st.session_state.lanzar_globos:
    st.balloons(); st.session_state.lanzar_globos = False

if st.session_state.registro_abierto:
    st.session_state.meta_puntos = st.radio("Meta del Encuentro:", [100, 200], horizontal=True)
    st.text_input("Escribe el nombre y presiona ENTER:", key="nuevo_nombre", on_change=agregar_jugador_enter)
    if st.session_state.asistentes:
        st.write(f"**Inscritos ({len(st.session_state.asistentes)}):** {', '.join(st.session_state.asistentes)}")
        col_el1, col_el2, col_el3 = st.columns([3, 0.5, 0.5])
        with col_el1: 
            seleccionado = st.selectbox("Seleccione Atleta para gestionar:", st.session_state.asistentes, key="atleta_gestion")
        with col_el2: 
            if st.button("✏️", help="Editar nombre"):
                editar_atleta_dialog(seleccionado)
        with col_el3:
            if st.button("🗑️", help="Eliminar Atleta"):
                st.session_state.asistentes.remove(seleccionado)
                st.session_state.asistentes.sort()
                st.rerun()
                
    if st.button("🚀 EMPEZAR TORNEO") and len(st.session_state.asistentes) >= 4:
        st.session_state.registro_abierto = False; generar_ronda_suiza(); st.rerun()
else:
    r_max = math.ceil(math.log2(len(st.session_state.asistentes)))
    
    # --- SECCIÓN DEL TIEMPO (INVARIABLE) ---
    with st.sidebar:
        st.header("⏱️ Reloj de Ronda")
        dur_ajuste = st.number_input("Establecer Minutos:", 1, 60, 20)
        col_btns = st.columns(2)
        with col_btns[0]:
            if st.button("🔔 INICIAR"):
                st.session_state.fin_tiempo = datetime.now() + timedelta(minutes=dur_ajuste)
                st.session_state.cronometro_activo = True
                st.rerun()
        with col_btns[1]:
            if st.button("🔄 REINICIAR"):
                st.session_state.fin_tiempo = None
                st.session_state.cronometro_activo = False
                st.rerun()
        if st.session_state.cronometro_activo:
            restante = st.session_state.fin_tiempo - datetime.now()
            segundos = restante.total_seconds()
            if segundos > 0:
                mins, secs = divmod(int(segundos), 60)
                if segundos <= 300:
                    st.markdown(f"""<div style="background-color: #FFEB3B; padding: 20px; border-radius: 10px; border: 5px solid #F44336; text-align: center;">
                            <p style="color: #F44336; font-size: 20px; font-weight: bold; margin-bottom: 5px;">⚠️ ÚLTIMOS MINUTOS</p>
                            <h1 style="color: #F44336; font-size: 60px; margin: 0;">{mins:02d}:{secs:02d}</h1></div>""", unsafe_allow_html=True)
                else: st.markdown(f"<h1 style='text-align: center;'>⏳ {mins:02d}:{secs:02d}</h1>", unsafe_allow_html=True)
                time.sleep(1); st.rerun()
            else:
                st.markdown("""<div style="background-color: #F44336; padding: 20px; border-radius: 10px; text-align: center;">
                        <h2 style="color: white; margin: 0;">🛑 TIEMPO VENCIDO</h2></div>""", unsafe_allow_html=True)
                st.session_state.cronometro_activo = False

    # --- PANTALLA PRINCIPAL (INVARIABLE) ---
    if not st.session_state.torneo_finalizado:
        opciones_ronda = list(range(1, st.session_state.ronda_actual + 1))
        ronda_a_ver = st.selectbox("🔍 Ver Ronda:", opciones_ronda, index=len(opciones_ronda)-1)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Ronda", f"{st.session_state.ronda_actual}/{r_max}")
        c2.metric("Meta", st.session_state.meta_puntos)
        c3.metric("Jugadores", len(st.session_state.asistentes))
        c4.metric("En Reposo", len(st.session_state.asistentes) % 4)

        if st.session_state.ronda_actual > 1:
            with st.expander("📊 RANKING ACTUAL", expanded=False):
                ranking_temp = sorted(st.session_state.asistentes, key=lambda x: (st.session_state.juegos_ganados.get(x,0), st.session_state.efectividad.get(x,0), -st.session_state.puntos_contra.get(x,0)), reverse=True)
                st.table([{"Pos": i+1, "Jugador": j, "G": st.session_state.juegos_ganados.get(j, 0), "Ef": st.session_state.efectividad.get(j, 0), "Pts-": st.session_state.puntos_contra.get(j, 0)} for i, j in enumerate(ranking_temp)])

        st.markdown("---")
        datos_ronda = next((item for item in st.session_state.historial_mesas if item['ronda'] == ronda_a_ver), None)
        if datos_ronda:
            for i, m in enumerate(datos_ronda['mesas']):
                col1, col2, col3 = st.columns([2, 1, 2])
                with col1: st.info(f"{m[0]} y {m[2]}")
                with col2: 
                    disponible = ronda_a_ver == st.session_state.ronda_actual
                    st.number_input("Pts", key=f"p_izq_{i}_{ronda_a_ver}", min_value=0, disabled=not disponible)
                    st.markdown(f"<center><b>Mesa {i+1}</b></center>", unsafe_allow_html=True)
                    st.number_input("Pts", key=f"p_der_{i}_{ronda_a_ver}", min_value=0, disabled=not disponible)
                with col3: st.success(f"{m[1]} y {m[3]}")
            if datos_ronda['reposo']: st.warning(f"💤 **EN REPOSO:** {', '.join(datos_ronda['reposo'])}")
        if st.session_state.ronda_actual == ronda_a_ver:
            if st.button(f"💾 Registrar Ronda {st.session_state.ronda_actual}"): finalizar_ronda()
    else:
        st.header("🥇 POSICIONES FINALES")
        ranking_final = sorted(st.session_state.asistentes, key=lambda x: (st.session_state.juegos_ganados.get(x,0), st.session_state.efectividad.get(x,0), -st.session_state.puntos_contra.get(x,0)), reverse=True)
        st.table([{"Pos": i+1, "Jugador": j, "G": st.session_state.juegos_ganados.get(j, 0), "Ef": st.session_state.efectividad.get(j, 0), "Pts-": st.session_state.puntos_contra.get(j, 0)} for i, j in enumerate(ranking_final)])
