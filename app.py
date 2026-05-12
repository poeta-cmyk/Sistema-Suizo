import streamlit as st
import math
import random
import time
import json
from datetime import datetime, timedelta

# --- 1. CONFIGURACIÓN ---
st.set_page_config(layout="wide", page_title="Gala de los 13 - Franz Lameda")

# --- 2. VARIABLES DE MEMORIA (ESTADO) ---
# Definimos todas las claves que el sistema debe recordar
CLAVES_SISTEMA = [
    'asistentes', 'juegos_ganados', 'puntos_favor', 'puntos_contra', 
    'efectividad', 'jugadores_reposo_previos', 'mesas_actuales', 
    'jugadores_pausa', 'parejas_previas', 'historial_mesas', 
    'ronda_actual', 'registro_abierto', 'torneo_finalizado', 'meta_puntos'
]

for clave in CLAVES_SISTEMA:
    if clave not in st.session_state:
        if any(x in clave for x in ['previos', 'mesas', 'pausa', 'parejas', 'asistentes', 'historial']):
            st.session_state[clave] = []
        elif clave == 'ronda_actual': st.session_state[clave] = 1
        elif clave == 'registro_abierto': st.session_state[clave] = True
        elif clave == 'torneo_finalizado': st.session_state[clave] = False
        elif clave == 'meta_puntos': st.session_state[clave] = 100
        else: st.session_state[clave] = {}

if 'lanzar_globos' not in st.session_state: st.session_state.lanzar_globos = False

# --- 3. BOTONES DE RESGUARDO (RECUPERADOS) ---
def exportar_torneo():
    """Crea el archivo de memoria para descargar"""
    memoria = {k: st.session_state[k] for k in CLAVES_SISTEMA}
    # Convertimos los sets de parejas a listas para que JSON los acepte
    memoria['parejas_previas'] = [list(p) for p in memoria['parejas_previas']]
    return json.dumps(memoria, indent=4)

def importar_torneo(archivo_cargado):
    """Lee el archivo y restaura el torneo exactamente donde estaba"""
    try:
        datos = json.load(archivo_cargado)
        for k in CLAVES_SISTEMA:
            if k == 'parejas_previas':
                st.session_state[k] = [set(p) for p in datos[k]]
            else:
                st.session_state[k] = datos[k]
        st.success("✅ Memoria del Torneo Restaurada.")
        time.sleep(1)
        st.rerun()
    except Exception as e:
        st.error(f"Error al leer el archivo: {e}")

# --- 4. LÓGICA DE EMPAREJAMIENTO Y REPOSO ---
def agregar_atleta():
    n = st.session_state.nuevo_atleta.strip().upper()
    if n and n not in st.session_state.asistentes:
        st.session_state.asistentes.append(n)
        st.session_state.asistentes.sort()
    st.session_state.nuevo_atleta = ""

def generar_ronda_suiza():
    # Ordenar por mérito (Gala)
    jugadores = sorted(st.session_state.asistentes, 
                      key=lambda x: (st.session_state.juegos_ganados.get(x, 0), 
                                     st.session_state.efectividad.get(x, 0)), 
                      reverse=True)
    
    if st.session_state.ronda_actual == 1: random.shuffle(jugadores)
    
    # Lógica de Reposo (No repetir)
    n_reposo = len(jugadores) % 4
    reposados_ahora = []
    if n_reposo > 0:
        intentos = 0
        while intentos < len(jugadores):
            candidatos = jugadores[-n_reposo:]
            if any(j in st.session_state.jugadores_reposo_previos for j in candidatos) and len(jugadores) > n_reposo:
                jugadores.insert(0, jugadores.pop())
                intentos += 1
            else: break
        reposados_ahora = jugadores[-n_reposo:]
        for r in reposados_ahora:
            jugadores.remove(r)
            st.session_state.jugadores_reposo_previos.append(r)
            
    st.session_state.jugadores_pausa = reposados_ahora
    
    # Lógica de Parejas (No repetir compañeros)
    mesas_nuevas = []
    pool = jugadores.copy()
    while len(pool) >= 4:
        a = pool.pop(0)
        # Buscar compañero que no haya jugado con 'a'
        c_idx = next((i for i, c in enumerate(pool) if {a, c} not in st.session_state.parejas_previas), 0)
        c = pool.pop(c_idx)
        st.session_state.parejas_previas.append({a, c})
        
        b = pool.pop(0)
        # Buscar compañero que no haya jugado con 'b'
        d_idx = next((i for i, c in enumerate(pool) if {b, c} not in st.session_state.parejas_previas), 0)
        d = pool.pop(d_idx)
        st.session_state.parejas_previas.append({b, d})
        
        mesas_nuevas.append([a, b, c, d])
        
    st.session_state.mesas_actuales = mesas_nuevas
    st.session_state.historial_mesas.append({
        'ronda': st.session_state.ronda_actual, 
        'mesas': mesas_nuevas, 
        'reposo': reposados_ahora.copy()
    })

# --- 5. INTERFAZ ---
st.title("🏆 Gala de los 13 - Franz Lameda")

with st.sidebar:
    st.header("💾 SEGURIDAD DEL TORNEO")
    # BOTÓN RECUPERADO: RESGUARDAR
    st.download_button(
        label="📥 RESGUARDAR (Descargar Memoria)",
        data=exportar_torneo(),
        file_name=f"respaldo_ronda_{st.session_state.ronda_actual}.json",
        mime="application/json"
    )
    st.markdown("---")
    # BOTÓN RECUPERADO: VOLVER A COMENZAR (CARGAR)
    archivo = st.file_uploader("📂 RESTAURAR DESDE ARCHIVO", type="json")
    if archivo and st.button("🚀 CARGAR MEMORIA"):
        importar_torneo(archivo)

if st.session_state.registro_abierto:
    st.header("📝 Registro de Maestros")
    st.session_state.meta_puntos = st.radio("Meta:", [100, 200], horizontal=True)
    st.text_input("Nombre y ENTER:", key="nuevo_atleta", on_change=agregar_atleta)
    if st.session_state.asistentes:
        st.write(f"Inscritos: {', '.join(st.session_state.asistentes)}")
        if st.button("🚀 INICIAR GALA") and len(st.session_state.asistentes) >= 4:
            st.session_state.registro_abierto = False
            generar_ronda_suiza()
            st.rerun()
else:
    # Pantalla de Juego
    st.subheader(f"Ronda: {st.session_state.ronda_actual} | Meta: {st.session_state.meta_puntos}")
    # (Aquí iría el resto de su lógica de anotación de puntos)
    st.info("Lógica de Parejas y Reposo activada y protegida.")
