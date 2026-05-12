import streamlit as st
import math
import random
import time
from datetime import datetime, timedelta

# --- 1. CONFIGURACIÓN Y ESTADO ---
st.set_page_config(layout="wide", page_title="ADEL - Sistema de Torneo")

# Inimport streamlit as st
import math
import random
import time
import json
from datetime import datetime, timedelta

# --- 1. CONFIGURACIÓN Y ESTADO ---
st.set_page_config(layout="wide", page_title="ADEL - Sistema Suizo")

# Inicialización robusta de variables
keys = ['asistentes', 'juegos_ganados', 'puntos_favor', 'puntos_contra', 
        'efectividad', 'jugadores_reposo_previos', 'mesas_actuales', 
        'jugadores_pausa', 'parejas_previas', 'historial_mesas']

for key in keys:
    if key not in st.session_state:
        st.session_state[key] = [] if any(x in key for x in ['previos', 'mesas', 'pausa', 'parejas', 'asistentes', 'historial']) else {}

if 'ronda_actual' not in st.session_state: st.session_state.ronda_actual = 1
if 'registro_abierto' not in st.session_state: st.session_state.registro_abierto = True
if 'torneo_finalizado' not in st.session_state: st.session_state.torneo_finalizado = False
if 'fin_tiempo' not in st.session_state: st.session_state.fin_tiempo = None
if 'cronometro_activo' not in st.session_state: st.session_state.cronometro_activo = False

# --- 2. FUNCIONES DE SEGURIDAD (RESGUARDAR/RESTAURAR) ---
def exportar_datos():
    datos = {k: st.session_state[k] for k in keys + ['ronda_actual', 'registro_abierto', 'torneo_finalizado']}
    return json.dumps(datos, indent=4)

def importar_datos(archivo_subido):
    if archivo_subido is not None:
        datos = json.load(archivo_subido)
        for k, v in datos.items():
            st.session_state[k] = v
        st.rerun()

# --- 3. LÓGICA DEL TORNEO ---
def agregar_jugador_enter():
    nombre = st.session_state.nuevo_nombre.strip().upper()
    if nombre and nombre not in st.session_state.asistentes:
        st.session_state.asistentes.append(nombre)
        st.session_state.asistentes.sort()
    st.session_state.nuevo_nombre = "" 

@st.dialog("Editar Atleta")
def editar_atleta_dialog(nombre_viejo):
    nuevo_nombre = st.text_input("Corregir nombre:", value=nombre_viejo).strip().upper()
    if st.button("✅ GUARDAR"):
        if nuevo_nombre and nuevo_nombre != nombre_viejo:
            idx = st.session_state.asistentes.index(nombre_viejo)
            st.session_state.asistentes[idx] = nuevo_nombre
            st.session_state.asistentes.sort()
            st.rerun()

def generar_ronda_suiza():
    jugadores = sorted(st.session_state.asistentes, 
                      key=lambda x: (st.session_state.juegos_ganados.get(x, 0), 
                                     st.session_state.efectividad.get(x, 0)), reverse=True)
    if st.session_state.ronda_actual == 1: random.shuffle(jugadores)
    
    n_reposo = len(jugadores) % 4
    reposados_hoy = jugadores[-n_reposo:] if n_reposo > 0 else []
    jugadores_activos = jugadores[:-n_reposo] if n_reposo > 0 else jugadores
    
    st.session_state.jugadores_pausa = reposados_hoy
    mesas = []
    for i in range(0, len(jugadores_activos), 4):
        mesas.append(jugadores_activos[i:i+4])
    
    st.session_state.mesas_actuales = mesas
    st.session_state.historial_mesas.append({
        'ronda': st.session_state.ronda_actual, 'mesas': mesas, 
        'reposo': reposados_hoy, 'resultados': {}
    })

def finalizar_ronda():
    meta = st.session_state.meta_puntos
    # Lógica de guardado de resultados y avance de ronda...
    st.session_state.ronda_actual += 1
    generar_ronda_suiza()
    st.rerun()

# --- 4. INTERFAZ ---
st.title("Asociación de Dominó del Estado Lara (ADEL) - Sistema Suizo")

with st.sidebar:
    st.header("💾 Seguridad del Torneo")
    st.download_button("📥 RESGUARDAR (Descargar Memoria)", data=exportar_datos(), file_name="respaldo_torneo.json", mime="application/json")
    
    archivo = st.file_uploader("📂 RESTAURAR DESDE ARCHIVO", type=['json'])
    if archivo:
        if st.button("✅ Confirmar Restauración"):
            importar_datos(archivo)
            
    if not st.session_state.registro_abierto:
        st.markdown("---")
        st.header("⏱️ Reloj de Ronda")
        # Lógica del cronómetro...
        
    st.markdown("---")
    st.caption("Creado por Poeta")

if st.session_state.registro_abierto:
    st.subheader("📝 Registro de Atletas")
    st.session_state.meta_puntos = st.radio("Meta:", [100, 200], horizontal=True)
    st.text_input("Nombre y ENTER:", key="nuevo_nombre", on_change=agregar_jugador_enter)
    
    if st.session_state.asistentes:
        st.write(f"**Inscritos:** {', '.join(st.session_state.asistentes)}")
        if st.button("🚀 INICIAR TORNEO"):
            st.session_state.registro_abierto = False
            generar_ronda_suiza()
            st.rerun()
else:
    # Interfaz de mesas y resultados...
    st.write(f"### Ronda Actual: {st.session_state.ronda_actual}")
    for i, mesa in enumerate(st.session_state.mesas_actuales):
        st.info(f"Mesa {i+1}: {mesa[0]}, {mesa[2]} VS {mesa[1]}, {mesa[3]}")icialización de variables de estado (Blindaje contra errores de carga)
keys = ['asistentes', 'juegos_ganados', 'puntos_favor', 'puntos_contra', 
        'efectividad', 'jugadores_reposo_previos', 'mesas_actuales', 
        'jugadores_pausa', 'parejas_previas', 'historial_mesas']

for key in keys:
    if key not in st.session_state:
        st.session_state[key] = [] if any(x in key for x in ['previos', 'mesas', 'pausa', 'parejas', 'asistentes', 'historial']) else {}

if 'ronda_actual' not in st.session_state: st.session_state.ronda_actual = 1
if 'registro_abierto' not in st.session_state: st.session_state.registro_abierto = True
if 'torneo_finalizado' not in st.session_state: st.session_state.torneo_finalizado = False
if 'fin_tiempo' not in st.session_state: st.session_state.fin_tiempo = None
if 'cronometro_activo' not in st.session_state: st.session_state.cronometro_activo = False

# --- 2. FUNCIONES DE LÓGICA ---
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
        'ronda': st.session_state.ronda_actual, 'mesas': mesas_generadas, 
        'reposo': reposados_hoy.copy(), 'resultados': {}
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
    if st.session_state.ronda_actual >= math.ceil(math.log2(len(st.session_state.asistentes))): st.session_state.torneo_finalizado = True
    else: st.session_state.ronda_actual += 1; generar_ronda_suiza()
    st.rerun()

# --- 3. INTERFAZ ---
# Título Institucional Único
st.title("Asociación de Dominó del Estado Lara (ADEL)")

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
    st.markdown("---")
    # Sello de Autoría
    st.caption("Creado por Poeta")

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
                with c2:
                    if ronda_v < st.session_state.ronda_actual:
                        pts_h = datos_r.get('resultados', {}).get(i, {'izq': 0, 'der': 0})
                        st.markdown(f"<h3 style='text-align:center;'>{pts_h['izq']}</h3><center><b>Mesa {i+1}</b></center><h3 style='text-align:center;'>{pts_h['der']}</h3>", unsafe_allow_html=True)
                    else:
                        st.number_input("Pts", key=f"p_izq_{i}_{ronda_v}", min_value=0)
                        st.markdown(f"<center><b>Mesa {i+1}</b></center>", unsafe_allow_html=True)
                        st.number_input("Pts", key=f"p_der_{i}_{ronda_v}", min_value=0)
                with c3: st.success(f"{m[1]} y {m[3]}")
            if datos_r['reposo']: st.warning(f"💤 **REPOSO:** {', '.join(datos_r['reposo'])}")
        if st.session_state.ronda_actual == ronda_v:
            if st.button(f"💾 Registrar Ronda {st.session_state.ronda_actual}"): finalizar_ronda()
    else:
        st.header("🥇 POSICIONES FINALES")
        rk_f = sorted(st.session_state.asistentes, key=lambda x: (st.session_state.juegos_ganados.get(x,0), st.session_state.efectividad.get(x,0), -st.session_state.puntos_contra.get(x,0)), reverse=True)
        st.table([{"Pos": i+1, "Jugador": j, "G": st.session_state.juegos_ganados.get(j, 0), "Ef": st.session_state.efectividad.get(j, 0)} for i, j in enumerate(rk_f)])
