import streamlit as st
import math
import random
import json

# --- 1. CONFIGURACIÓN ---
st.set_page_config(layout="wide", page_title="ADEL - Sistema Suizo")

# Inicialización de memoria (Blindaje para que no se pierdan datos)
if 'asistentes' not in st.session_state: st.session_state.asistentes = []
if 'juegos_ganados' not in st.session_state: st.session_state.juegos_ganados = {}
if 'efectividad' not in st.session_state: st.session_state.efectividad = {}
if 'puntos_contra' not in st.session_state: st.session_state.puntos_contra = {}
if 'ronda_actual' not in st.session_state: st.session_state.ronda_actual = 1
if 'registro_abierto' not in st.session_state: st.session_state.registro_abierto = True
if 'meta_puntos' not in st.session_state: st.session_state.meta_puntos = 100
if 'mesas_actuales' not in st.session_state: st.session_state.mesas_actuales = []
if 'jugadores_pausa' not in st.session_state: st.session_state.jugadores_pausa = []

# --- 2. FUNCIONES ---
def exportar_datos():
    datos = {
        'asistentes': st.session_state.asistentes,
        'juegos_ganados': st.session_state.juegos_ganados,
        'efectividad': st.session_state.efectividad,
        'puntos_contra': st.session_state.puntos_contra,
        'ronda_actual': st.session_state.ronda_actual,
        'registro_abierto': st.session_state.registro_abierto,
        'meta_puntos': st.session_state.meta_puntos
    }
    return json.dumps(datos, indent=4)

def generar_ronda_suiza():
    # Ordenar por Baremos ADEL: 1. Ganados, 2. Ef, 3. Menos Puntos en Contra
    jugadores = sorted(st.session_state.asistentes, 
                      key=lambda x: (st.session_state.juegos_ganados.get(x, 0), 
                                     st.session_state.efectividad.get(x, 0),
                                     -st.session_state.puntos_contra.get(x, 0)), reverse=True)
    
    if st.session_state.ronda_actual == 1:
        random.shuffle(jugadores)
    
    n_reposo = len(jugadores) % 4
    st.session_state.jugadores_pausa = jugadores[-n_reposo:] if n_reposo > 0 else []
    activos = jugadores[:-n_reposo] if n_reposo > 0 else jugadores
    
    st.session_state.mesas_actuales = [activos[i:i+4] for i in range(0, len(activos), 4)]

def finalizar_ronda():
    meta = st.session_state.meta_puntos
    for i, mesa in enumerate(st.session_state.mesas_actuales):
        # Marcadores libres
        p_izq = st.session_state.get(f"p_izq_{i}", 0)
        p_der = st.session_state.get(f"p_der_{i}", 0)
        
        # Lógica ADEL: Ef = Meta - Puntos Perdedor
        if p_izq >= p_der:
            val_ef = meta - p_der
            gan, per = [mesa[0], mesa[2]], [mesa[1], mesa[3]]
            pp = p_der
        else:
            val_ef = meta - p_izq
            gan, per = [mesa[1], mesa[3]], [mesa[0], mesa[2]]
            pp = p_izq

        for g in gan:
            st.session_state.juegos_ganados[g] = st.session_state.juegos_ganados.get(g, 0) + 1
            st.session_state.efectividad[g] = st.session_state.efectividad.get(g, 0) + val_ef
            st.session_state.puntos_contra[g] = st.session_state.puntos_contra.get(g, 0) + pp
        for p in per:
            st.session_state.efectividad[p] = st.session_state.efectividad.get(p, 0) - val_ef
            # En el perdedor, los puntos que recibió son los del ganador (pp es el suyo, hay que sumar el del otro)
            st.session_state.puntos_contra[p] = st.session_state.puntos_contra.get(p, 0) + (p_izq if p_izq > p_der else p_der)

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
    st.download_button("📥 RESGUARDAR", data=exportar_datos(), file_name="respaldo.json", mime="application/json")
    st.markdown("---")
    st.caption("Creado por Poeta")

if st.session_state.registro_abierto:
    st.subheader("📝 Registro de Atletas")
    st.session_state.meta_puntos = st.radio("Meta:", [100, 200], horizontal=True)
    
    # Campo de texto para inscripción
    nombre_in = st.text_input("Atleta + ENTER:").upper().strip()
    if nombre_in and nombre_in not in st.session_state.asistentes:
        st.session_state.asistentes.append(nombre_in)
        st.session_state.asistentes.sort()
        st.rerun()

    if st.session_state.asistentes:
        # AQUÍ ESTÁ LO QUE TE ENCANTA: Contador y Lista
        st.info(f"**Atletas Inscritos ({len(st.session_state.asistentes)}):**\n\n{', '.join(st.session_state.asistentes)}")
        
        atleta_sel = st.selectbox("Seleccione para eliminar:", st.session_state.asistentes)
        if st.button("🗑️ Eliminar Seleccionado"):
            st.session_state.asistentes.remove(atleta_sel)
            st.rerun()
            
        if st.button("🚀 INICIAR TORNEO") and len(st.session_state.asistentes) >= 4:
            generar_ronda_suiza()
            st.session_state.registro_abierto = False
            st.rerun()
else:
    # --- PANTALLA INTERNA ---
    st.header(f"🃏 Ronda Actual: {st.session_state.ronda_actual}")
    
    tab1, tab2 = st.tabs(["🗂️ Mesas de Juego", "📊 Tabla de Posiciones"])
    
    with tab1:
        for i, m in enumerate(st.session_state.mesas_actuales):
            st.subheader(f"Mesa {i+1}")
            c1, c2, c3 = st.columns([2, 1, 2])
            with c1: st.write(f"🔵 **Pareja 1:**\n{m[0]} / {m[2]}")
            with c2:
                st.number_input(f"Pts P1", key=f"p_izq_{i}", min_value=0, step=1)
                st.number_input(f"Pts P2", key=f"p_der_{i}", min_value=0, step=1)
            with c3: st.write(f"🔴 **Pareja 2:**\n{m[1]} / {m[3]}")
            st.markdown("---")
        
        if st.button("💾 FINALIZAR RONDA"):
            finalizar_ronda()

    with tab2:
        rk = sorted(st.session_state.asistentes, 
                    key=lambda x: (st.session_state.juegos_ganados.get(x, 0), 
                                   st.session_state.efectividad.get(x, 0),
                                   -st.session_state.puntos_contra.get(x, 0)), reverse=True)
        
        tabla = [{"Pos": i+1, "Atleta": j, "G": st.session_state.juegos_ganados.get(j,0), 
                  "Ef": st.session_state.efectividad.get(j,0), "Contra": st.session_state.puntos_contra.get(j,0)} 
                 for i, j in enumerate(rk)]
        st.table(tabla)
