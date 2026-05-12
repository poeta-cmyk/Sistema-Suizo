import streamlit as st
import math
import random
import json

# --- 1. CONFIGURACIÓN ---
st.set_page_config(layout="wide", page_title="ADEL - Sistema Suizo")

# Inicialización robusta de memoria
for key, default in {
    'asistentes': [], 'juegos_ganados': {}, 'efectividad': {}, 
    'puntos_contra': {}, 'ronda_actual': 1, 'registro_abierto': True, 
    'meta_puntos': 100, 'historial_completo': []
}.items():
    if key not in st.session_state: st.session_state[key] = default

# --- 2. FUNCIONES LÓGICAS ---
def calcular_rondas_necesarias(n):
    return math.ceil(math.log2(n)) + 1 if n >= 4 else 0

def procesar_registro():
    n = st.session_state.nuevo_atleta.strip().upper()
    if n and n not in st.session_state.asistentes:
        st.session_state.asistentes.append(n)
        st.session_state.asistentes.sort()
    st.session_state.nuevo_atleta = ""

def generar_ronda():
    # Orden ADEL: G -> Ef -> -Contra
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
    
    st.session_state.historial_completo.append({
        'ronda': st.session_state.ronda_actual, 'mesas': mesas, 
        'reposo': reposados, 'finalizada': False
    })

def finalizar_ronda():
    meta = st.session_state.meta_puntos
    r_idx = st.session_state.ronda_actual - 1
    r_data = st.session_state.historial_completo[r_idx]
    
    for i, mesa in enumerate(r_data['mesas']):
        p1 = st.session_state.get(f"p1_r{st.session_state.ronda_actual}_m{i}", 0)
        p2 = st.session_state.get(f"p2_r{st.session_state.ronda_actual}_m{i}", 0)
        
        if p1 >= p2:
            ef, gan, per, contra_gan, contra_per = meta - p2, [mesa[0], mesa[2]], [mesa[1], mesa[3]], p2, p1
        else:
            ef, gan, per, contra_gan, contra_per = meta - p1, [mesa[1], mesa[3]], [mesa[0], mesa[2]], p1, p2

        for g in gan:
            st.session_state.juegos_ganados[g] = st.session_state.juegos_ganados.get(g, 0) + 1
            st.session_state.efectividad[g] = st.session_state.efectividad.get(g, 0) + ef
            st.session_state.puntos_contra[g] = st.session_state.puntos_contra.get(g, 0) + contra_gan
        for p in per:
            st.session_state.efectividad[p] = st.session_state.efectividad.get(p, 0) - ef
            st.session_state.puntos_contra[p] = st.session_state.puntos_contra.get(p, 0) + contra_per

    for r in r_data['reposo']:
        st.session_state.juegos_ganados[r] = st.session_state.juegos_ganados.get(r, 0) + 1
        st.session_state.efectividad[r] = st.session_state.efectividad.get(r, 0) + (meta // 2)

    st.session_state.historial_completo[r_idx]['finalizada'] = True
    st.session_state.ronda_actual += 1
    generar_ronda()
    st.rerun()

# --- 3. INTERFAZ ---
st.title("Asociación de Dominó del Estado Lara (ADEL) - Sistema Suizo")

with st.sidebar:
    st.header("💾 Seguridad")
    if st.button("📥 RESGUARDAR"):
        st.download_button("Bajar Backup", data=json.dumps({k:st.session_state[k] for k in ['asistentes','juegos_ganados','efectividad','puntos_contra','ronda_actual','historial_completo']}, indent=4), file_name="adel_backup.json")
    st.markdown("---")
    st.caption("Creado por Poeta")

if st.session_state.registro_abierto:
    st.subheader("📝 Registro de Atletas")
    st.session_state.meta_puntos = st.radio("Meta:", [100, 200], horizontal=True)
    st.text_input("Atleta + ENTER:", key="nuevo_atleta", on_change=procesar_registro)

    if st.session_state.asistentes:
        st.info(f"**Inscritos ({len(st.session_state.asistentes)}):** {', '.join(st.session_state.asistentes)}")
        c_sel, c_ed, c_del = st.columns([2, 0.5, 0.5])
        with c_sel: sel = st.selectbox("Atleta:", st.session_state.asistentes, label_visibility="collapsed")
        with c_ed:
            @st.dialog("Editar")
            def edit(n):
                nuevo = st.text_input("Nombre:", value=n).upper().strip()
                if st.button("Ok"):
                    st.session_state.asistentes[st.session_state.asistentes.index(n)] = nuevo
                    st.rerun()
            if st.button("✏️"): edit(sel)
        with c_del:
            if st.button("🗑️"):
                st.session_state.asistentes.remove(sel)
                st.rerun()
        if st.button("🚀 INICIAR") and len(st.session_state.asistentes) >= 4:
            st.session_state.registro_abierto = False
            generar_ronda()
            st.rerun()
else:
    # NAVEGACIÓN SEGURA (Sin errores de índice)
    r_disponibles = [h['ronda'] for h in st.session_state.historial_completo]
    r_ver = st.selectbox("📅 Ver Ronda:", r_disponibles, index=len(r_disponibles)-1)
    r_data = st.session_state.historial_completo[r_ver-1]
    
    st.header(f"🃏 Ronda {r_ver}")
    t1, t2 = st.tabs(["🗂️ Mesas", "📊 Ranking"])
    
    with t1:
        if r_data['reposo']:
            st.warning(f"💤 **EN REPOSO:** {', '.join(r_data['reposo'])}")
        for i, m in enumerate(r_data['mesas']):
            with st.container():
                st.markdown(f"**Mesa {i+1}**")
                c1, c2, c3 = st.columns([2, 1, 2])
                with c1: st.info(f"{m[0]} / {m[2]}")
                with c2:
                    st.number_input("P1", key=f"p1_r{r_ver}_m{i}", min_value=0)
                    st.number_input("P2", key=f"p2_r{r_ver}_m{i}", min_value=0)
                with c3: st.success(f"{m[1]} / {m[3]}")
        if not r_data['finalizada'] and r_ver == st.session_state.ronda_actual:
            if st.button("💾 CERRAR RONDA"): finalizar_ronda()

    with t2:
        rk = sorted(st.session_state.asistentes, key=lambda x: (st.session_state.juegos_ganados.get(x,0), st.session_state.efectividad.get(x,0), -st.session_state.puntos_contra.get(x,0)), reverse=True)
        st.table([{"Pos": i+1, "Atleta": j, "G": st.session_state.juegos_ganados.get(j,0), "Ef": st.session_state.efectividad.get(j,0), "Contra": st.session_state.puntos_contra.get(j,0)} for i, j in enumerate(rk)])
