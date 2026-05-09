import streamlit as st
import math
import random
import time
import json
from datetime import datetime, timedelta

# --- 1. CONFIGURACIÓN INICIAL (DEBE IR DE PRIMERO) ---
st.set_page_config(layout="wide", page_title="Sistema Suizo Pro - Franz Lameda")

# --- 2. INICIALIZACIÓN DEL ESTADO (EVITA EL ERROR DE LA LÍNEA 3) ---
VALORES_INICIALES = {
    'asistentes': [],
    'juegos_ganados': {},
    'puntos_favor': {},
    'puntos_contra': {},
    'efectividad': {},
    'jugadores_reposo_previos': [],
    'mesas_actuales': [],
    'jugadores_pausa': [],
    'parejas_previas': [],
    'historial_mesas': [],
    'ronda_actual': 1,
    'registro_abierto': True,
    'torneo_finalizado': False,
    'meta_puntos': 100,
    'lanzar_globos': False,
    'fin_tiempo': None,
    'cronometro_activo': False
}

for clave, valor in VALORES_INICIALES.items():
    if clave not in st.session_state:
        st.session_state[clave] = valor

# --- 3. FUNCIONES DE RESGUARDO ---
def exportar_datos():
    datos = {k: st.session_state[k] for k in VALORES_INICIALES.keys()}
    datos['parejas_previas'] = [list(p) for p in datos['parejas_previas']]
    return json.dumps(datos, indent=4)

def importar_datos(archivo_subido):
    try:
        datos = json.load(archivo_subido)
        for k in VALORES_INICIALES.keys():
            if k == 'parejas_previas':
                st.session_state[k] = [set(p) for p in datos[k]]
            else:
                st.session_state[k] = datos[k]
        st.success("✅ Sistema restaurado. ¡Adelante!")
        time.sleep(1)
        st.rerun()
    except Exception as e:
        st.error(f"Error al cargar: {e}")

# --- 4. LÓGICA DEL TORNEO ---
def agregar_jugador():
    nombre = st.session_state.nuevo_nombre.strip().upper()
    if nombre and nombre not in st.session_state.asistentes:
        st.session_state.asistentes.append(nombre)
        st.session_state.asistentes.sort()
    st.session_state.nuevo_nombre = ""

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
        intentos = 0
        while intentos < len(jugadores):
            candidatos = jugadores[-n_reposo:]
            if any(j in st.session_state.jugadores_reposo_previos for j in candidatos) and len(jugadores) > n_reposo:
                jugadores.insert(0, jugadores.pop())
                intentos += 1
            else: break
        reposados_hoy = jugadores[-n_reposo:]
        for r in reposados_hoy:
            jugadores.remove(r)
            st.session_state.jugadores_reposo_previos.append(r)
            
    st.session_state.jugadores_pausa = reposados_hoy
    n_mesas = len(jugadores) // 4
    mesas_nuevas = []
    disponibles = jugadores.copy()
    
    for _ in range(n_mesas):
        a = disponibles.pop(0)
        c_idx = next((i for i, c in enumerate(disponibles) if {a, c} not in st.session_state.parejas_previas), 0)
        c = disponibles.pop(c_idx)
        st.session_state.parejas_previas.append({a, c})
        b = disponibles.pop(0)
        d_idx = next((i for i, c in enumerate(disponibles) if {b, c} not in st.session_state.parejas_previas), 0)
        d = disponibles.pop(d_idx)
        st.session_state.parejas_previas.append({b, d})
        mesas_nuevas.append([a, b, c, d])
        
    st.session_state.mesas_actuales = mesas_nuevas
    st.session_state.historial_mesas.append({'ronda': st.session_state.ronda_actual, 'mesas': mesas_nuevas, 'reposo': reposados_hoy.copy()})

def finalizar_ronda():
    meta = st.session_state.meta_puntos
    for i, m in enumerate(st.session_state.mesas_actuales):
        p_izq = st.session_state.get(f"p_izq_{i}_{st.session_state.ronda_actual}", 0)
        p_der = st.session_state.get(f"p_der_{i}_{st.session_state.ronda_actual}", 0)
        ef_izq = (p_izq - meta) if p_izq < p_der else (meta - p_der)
        ef_der = (p_der - meta) if p_der < p_izq else (meta - p_izq)
        for p, pf, pc, ef in [(m[0], p_izq, p_der, ef_izq), (m[2], p_izq, p_der, ef_izq), (m[1], p_der, p_izq, ef_der), (m[3], p_der, p_izq, ef_der)]:
            st.session_state.puntos_favor[p] = st.session_state.puntos_favor.get(p, 0) + pf
            st.session_state.puntos_contra[p] = st.session_state.puntos_contra.get(p, 0) + pc
            st.session_state.efectividad[p] = st.session_state.efectividad.get(p, 0) + ef
            if pf > pc: st.session_state.juegos_ganados[p] = st.session_state.juegos_ganados.get(p, 0) + 1
            
    for r in st.session_state.jugadores_pausa:
        st.session_state.juegos_ganados[r] = st.session_state.juegos_ganados.get(r, 0) + 1
        st.session_state.efectividad[r] = st.session_state.efectividad.get(r, 0) + (meta // 2)
    
    st.session_state.lanzar_globos = True
    if st.session_state.ronda_actual >= math.ceil(math.log2(len(st.session_state.asistentes))):
        st.session_state.torneo_finalizado = True
    else:
        st.session_state.ronda_actual += 1
        generar_ronda_suiza()
    st.rerun()

# --- 5. INTERFAZ ---
st.title("🏆 Sistema Suizo Pro - El Poeta Franz Lameda")

with st.sidebar:
    st.header("💾 PANEL DE CONTROL")
    st.download_button("📥 RESGUARDAR TORNEO", data=exportar_datos(), file_name="respaldo_torneo.json", mime="application/json")
    archivo = st.file_uploader("📂 VOLVER A COMENZAR", type="json")
    if archivo and st.button("🚀 CARGAR DATOS"): importar_datos(archivo)
    st.markdown("---")
    st.header("⏱️ RELOJ")
    minutos = st.number_input("Minutos:", 1, 60, 20)
    if st.button("🔔 INICIAR"):
        st.session_state.fin_tiempo = datetime.now() + timedelta(minutes=minutos)
        st.session_state.cronometro_activo = True
        st.rerun()
    if st.session_state.cronometro_activo:
        restante = (st.session_state.fin_tiempo - datetime.now()).total_seconds()
        if restante > 0:
            m, s = divmod(int(restante), 60)
            st.markdown(f"<h1 style='text-align: center; color: red;'>⏳ {m:02d}:{s:02d}</h1>", unsafe_allow_html=True)
            time.sleep(1); st.rerun()
        else: st.error("🛑 TIEMPO CUMPLIDO")

if st.session_state.lanzar_globos:
    st.balloons()
    st.session_state.lanzar_globos = False

if st.session_state.registro_abierto:
    st.header("📝 Inscripción de Atletas")
    st.session_state.meta_puntos = st.radio("Meta:", [100, 200], horizontal=True)
    st.text_input("Nombre y ENTER:", key="nuevo_nombre", on_change=agregar_jugador)
    if st.session_state.asistentes:
        st.write(f"Inscritos: {', '.join(st.session_state.asistentes)}")
        if st.button("🚀 EMPEZAR TORNEO") and len(st.session_state.asistentes) >= 4:
            st.session_state.registro_abierto = False; generar_ronda_suiza(); st.rerun()
else:
    if not st.session_state.torneo_finalizado:
        opciones = list(range(1, st.session_state.ronda_actual + 1))
        r_ver = st.selectbox("Ronda:", opciones, index=len(opciones)-1)
        with st.expander("📊 RANKING"):
            rk = sorted(st.session_state.asistentes, key=lambda x: (st.session_state.juegos_ganados.get(x,0), st.session_state.efectividad.get(x,0)), reverse=True)
            st.table([{"Pos": i+1, "Jugador": j, "G": st.session_state.juegos_ganados.get(j,0), "Ef": st.session_state.efectividad.get(j,0)} for i, j in enumerate(rk)])
        
        datos_r = next((x for x in st.session_state.historial_mesas if x['ronda'] == r_ver), None)
        if datos_r:
            for i, m in enumerate(datos_r['mesas']):
                c1, c2, c3 = st.columns([2, 1, 2])
                with c1: st.info(f"{m[0]} y {m[2]}")
                with c2:
                    st.number_input("Pts", key=f"p_izq_{i}_{r_ver}", min_value=0)
                    st.markdown(f"<center><b>Mesa {i+1}</b></center>", unsafe_allow_html=True)
                    st.number_input("Pts", key=f"p_der_{i}_{r_ver}", min_value=0)
                with c3: st.success(f"{m[1]} y {m[3]}")
            if r_ver == st.session_state.ronda_actual:
                if st.button(f"💾 REGISTRAR RONDA {r_ver}"): finalizar_ronda()
    else:
        st.header("🥇 POSICIONES FINALES")
        final = sorted(st.session_state.asistentes, key=lambda x: (st.session_state.juegos_ganados.get(x,0), st.session_state.efectividad.get(x,0)), reverse=True)
        st.table([{"Pos": i+1, "Atleta": j, "G": st.session_state.juegos_ganados.get(j,0), "Ef": st.session_state.efectividad.get(j,0)} for i, j in enumerate(final)])
