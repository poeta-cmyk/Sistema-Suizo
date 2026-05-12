import streamlit as st
import math
import random
import json

# --- 1. CONFIGURACIÓN E INICIALIZACIÓN ---
st.set_page_config(layout="wide", page_title="ADEL - Sistema Suizo")

# Inicialización de memoria total (NO SE BORRA NADA)
if 'asistentes' not in st.session_state: st.session_state.asistentes = []
if 'juegos_ganados' not in st.session_state: st.session_state.juegos_ganados = {}
if 'efectividad' not in st.session_state: st.session_state.efectividad = {}
if 'puntos_contra' not in st.session_state: st.session_state.puntos_contra = {}
if 'ronda_actual' not in st.session_state: st.session_state.ronda_actual = 1
if 'registro_abierto' not in st.session_state: st.session_state.registro_abierto = True
if 'meta_puntos' not in st.session_state: st.session_state.meta_puntos = 100
if 'historial_completo' not in st.session_state: st.session_state.historial_completo = []

# --- 2. FUNCIONES DE CÁLCULO ---

def calcular_rondas_necesarias(n):
    if n < 4: return 0
    return math.ceil(math.log2(n)) + 1

def procesar_registro():
    nombre = st.session_state.nuevo_atleta.strip().upper()
    if nombre and nombre not in st.session_state.asistentes:
        st.session_state.asistentes.append(nombre)
        st.session_state.asistentes.sort()
    st.session_state.nuevo_atleta = ""

def generar_nueva_ronda():
    # Baremo ADEL: G -> Ef -> -Contra
    jugadores = sorted(st.session_state.asistentes, 
                      key=lambda x: (st.session_state.juegos_ganados.get(x, 0), 
                                     st.session_state.efectividad.get(x, 0),
                                     -st.session_state.puntos_contra.get(x, 0)), reverse=True)
    
    if st.session_state.ronda_actual == 1 and not st.session_state.historial_completo:
        random.shuffle(jugadores)
    
    n_reposo = len(jugadores) % 4
    reposados = jugadores[-n_reposo:] if n_reposo > 0 else []
    activos = jugadores[:-n_reposo] if n_reposo > 0 else jugadores
    
    mesas = [activos[i:i+4] for i in range(0, len(activos), 4)]
    
    # Guardamos en el historial antes de mostrar
    st.session_state.historial_completo.append({
        'ronda': st.session_state.ronda_actual,
        'mesas': mesas,
        'reposo': reposados,
        'finalizada': False
    })

def finalizar_ronda():
    meta = st.session_state.meta_puntos
    idx = st.session_state.ronda_actual - 1
    ronda_data = st.session_state.historial_completo[idx]
    
    for i, mesa in enumerate(ronda_data['mesas']):
        p_izq = st.session_state.get(f"p_izq_r{st.session_state.ronda_actual}_{i}", 0)
        p_der = st.session_state.get(f"p_der_r{st.session_state.ronda_actual}_{i}", 0)
        
        if p_izq >= p_der:
            val_ef = meta - p_der
            gan, per, pp = [mesa[0], mesa[2]], [mesa[1], mesa[3]], p_der
            pg = p_izq
        else:
            val_ef = meta - p_izq
            gan, per, pp = [mesa[1], mesa[3]], [mesa[0], mesa[2]], p_izq
            pg = p_der

        for g in gan:
            st.session_state.juegos_ganados[g] = st.session_state.juegos_ganados.get(g, 0) + 1
            st.session_state.efectividad[g] = st.session_state.efectividad.get(g, 0) + val_ef
            st.session_state.puntos_contra[g] = st.session_state.puntos_contra.get(g, 0) + pp
        for p in per:
            st.session_state.efectividad[p] = st.session_state.efectividad.get(p, 0) - val_ef
            st.session_state.puntos_contra[p] = st.session_state.puntos_contra.get(p, 0) + pg

    for r in ronda_data['reposo']:
        st.session_state.juegos_ganados[r] = st.session_state.juegos_ganados.get(r, 0) + 1
        st.session_state.efectividad[r] = st.session_state.efectividad.get(r, 0) + (meta // 2)

    st.session_state.historial_completo[idx]['finalizada'] = True
    st.session_state.ronda_actual += 1
    generar_nueva_ronda()
    st.rerun()

# --- 3. INTERFAZ ---
st.title("Asociación de Dominó del Estado Lara (ADEL) - Sistema Suizo")

with st.sidebar:
    st.header("💾 Seguridad")
    if st.button("📥 RESGUARDAR"):
        st.download_button("Descargar JSON", data=json.dumps({k: st.session_state[k] for k in ['asistentes', 'juegos_ganados', 'efectividad', 'puntos_contra', 'ronda_actual', 'historial_completo']}, indent=4), file_name="respaldo.json")
    st.markdown("---")
    st.caption("Creado por Poeta")

if st.session_state.registro_abierto:
    st.subheader("📝 Registro de Atletas")
    st.session_state.meta_puntos = st.radio("Meta:", [100, 200], horizontal=True)
    st.text_input("Atleta + ENTER:", key="nuevo_atleta", on_change=procesar_registro)

    if st.session_state.asistentes:
        n_atletas = len(st.session_state.asistentes)
        r_nec = calcular_rondas_necesarias(n_atletas)
        st.info(f"**Inscritos ({n_atletas}):** {', '.join(st.session_state.asistentes)}")
        st.write(f"Rondas estimadas: **{r_nec}**")
        
        col_s, col_e, col_b = st.columns([2, 0.5, 0.5])
        with col_s: sel = st.selectbox("Gestionar:", st.session_state.asistentes)
        with col_e:
            @st.dialog("Editar")
            def ed(n):
                nuevo = st.text_input("Nuevo nombre:", value=n).upper().strip()
                if st.button("Guardar"):
                    st.session_state.asistentes[st.session_state.asistentes.index(n)] = nuevo
                    st.rerun()
            if st.button("✏️"): ed(sel)
        with col_b:
            if st.button("🗑️"):
                st.session_state.asistentes.remove(sel)
                st.rerun()
            
        if st.button("🚀 INICIAR") and n_atletas >= 4:
            st.session_state.registro_abierto = False
            generar_nueva_ronda()
            st.rerun()
else:
    # NAVEGACIÓN DE RONDAS (RECUPERADO)
    rondas_list = [h['ronda'] for h in st.session_state.historial_completo]
    r_ver = st.selectbox("📅 Ver Ronda:", rondas_list, index=st.session_state.ronda_actual-1)
    
    r_data = st.session_state.historial_completo[r_ver-1]
    
    st.header(f"🃏 Ronda {r_ver} de {calcular_rondas_necesarias(len(st.session_state.asistentes))}")
    
    t1, t2 = st.tabs(["🗂️ Mesas", "📊 Ranking"])
    
    with t1:
        if r_data['reposo']:
            st.warning(f"💤 **REPOSO:** {', '.join(r_data['reposo'])}")
        
        for i, m in enumerate(r_data['mesas']):
            with st.container():
                st.markdown(f"**Mesa {i+1}**")
                c1, c2, c3 = st.columns([2, 1, 2])
                with c1: st.info(f"{m[0]} / {m[2]}")
                with c2:
                    # Key única por ronda y mesa para que no se borren
                    st.number_input("P1", key=f"p_izq_r{r_ver}_{i}", min_value=0)
                    st.number_input("P2", key=f"p_der_r{r_ver}_{i}", min_value=0)
                with c3: st.success(f"{m[1]} / {m[3]}")
                st.markdown("---")
        
        if not r_data['finalizada'] and r_ver == st.session_state.ronda_actual:
            if st.button("💾 CERRAR ESTA RONDA"):
                finalizar_ronda()

    with t2:
        rk = sorted(st.session_state.asistentes, key=lambda x: (st.session_state.juegos_ganados.get(x,0), st.session_state.efectividad.get(x,0), -st.session_state.puntos_contra.get(x,0)), reverse=True)
        st.table([{"Pos": i+1, "Atleta": j, "G": st.session_state.juegos_ganados.get(j,0), "Ef": st.session_state.efectividad.get(j,0), "Contra": st.session_state.puntos_contra.get(j,0)} for i, j in enumerate(rk)])
