import streamlit as st
import math
import random
import json

# --- 1. CONFIGURACIÓN ---
st.set_page_config(layout="wide", page_title="ADEL - Sistema Suizo Pro")

# Inicialización de memoria blindada
for key, default in {
    'asistentes': [], 'juegos_ganados': {}, 'efectividad': {}, 
    'puntos_contra': {}, 'ronda_actual': 1, 'registro_abierto': True, 
    'meta_puntos': 100, 'historial_completo': [], 'parejas_jugadas': [], 'historial_reposo': []
}.items():
    if key not in st.session_state: st.session_state[key] = default

# --- 2. FUNCIONES LÓGICAS ---
def calcular_rondas(n):
    return math.ceil(math.log2(n)) + 1 if n >= 4 else 0

def procesar_registro():
    n = st.session_state.nuevo_atleta.strip().upper()
    if n and n not in st.session_state.asistentes:
        st.session_state.asistentes.append(n)
        st.session_state.asistentes.sort()
    st.session_state.nuevo_atleta = ""

def generar_ronda_adel():
    # Ordenar por ranking: G -> Ef -> -Contra
    rk = sorted(st.session_state.asistentes, 
                key=lambda x: (st.session_state.juegos_ganados.get(x, 0), 
                               st.session_state.efectividad.get(x, 0),
                               -st.session_state.puntos_contra.get(x, 0)), reverse=True)
    
    # Manejo de Reposo (No repite)
    n_reposo = len(rk) % 4
    reposados = []
    if n_reposo > 0:
        # Busca a los últimos del ranking que NO hayan reposado
        candidatos_reposo = [j for j in reversed(rk) if j not in st.session_state.historial_reposo]
        if not candidatos_reposo: # Si ya todos reposaron, reiniciamos ciclo
            st.session_state.historial_reposo = []
            candidatos_reposo = list(reversed(rk))
        
        reposados = candidatos_reposo[:n_reposo]
        st.session_state.historial_reposo.extend(reposados)
    
    activos = [j for j in rk if j not in reposados]
    mesas = []
    
    # Lógica de Emparejamiento 1-3 vs 2-4
    while len(activos) >= 4:
        j1 = activos[0]
        # Buscar compañero (idealmente el 3ero, si no, el siguiente que no haya jugado con j1)
        companero = None
        for i in range(2, len(activos)): 
            posible = activos[i]
            dupla = tuple(sorted((j1, posible)))
            if dupla not in st.session_state.parejas_jugadas:
                companero = posible
                break
        
        if not companero: companero = activos[2] # Si no hay opción, el 3ero por defecto
        
        # El rival es el 2do y el 4to (o siguientes disponibles)
        activos.remove(j1)
        activos.remove(companero)
        
        j2 = activos[0]
        rival_comp = activos[1]
        activos.remove(j2)
        activos.remove(rival_comp)
        
        mesas.append([j1, j2, companero, rival_comp]) # Pareja A: 1-3, Pareja B: 2-4
        st.session_state.parejas_jugadas.append(tuple(sorted((j1, companero))))
        st.session_state.parejas_jugadas.append(tuple(sorted((j2, rival_comp))))

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
            ef, gan, per, c_gan, c_per = meta - p2, [mesa[0], mesa[2]], [mesa[1], mesa[3]], p2, p1
        else:
            ef, gan, per, c_gan, c_per = meta - p1, [mesa[1], mesa[3]], [mesa[0], mesa[2]], p1, p2

        for g in gan:
            st.session_state.juegos_ganados[g] = st.session_state.juegos_ganados.get(g, 0) + 1
            st.session_state.efectividad[g] = st.session_state.efectividad.get(g, 0) + ef
            st.session_state.puntos_contra[g] = st.session_state.puntos_contra.get(g, 0) + c_gan
        for p in per:
            st.session_state.efectividad[p] = st.session_state.efectividad.get(p, 0) - ef
            st.session_state.puntos_contra[p] = st.session_state.puntos_contra.get(p, 0) + c_per

    for r in r_data['reposo']:
        st.session_state.juegos_ganados[r] = st.session_state.juegos_ganados.get(r, 0) + 1
        st.session_state.efectividad[r] = st.session_state.efectividad.get(r, 0) + (meta // 2)

    st.session_state.historial_completo[r_idx]['finalizada'] = True
    st.session_state.ronda_actual += 1
    generar_ronda_adel()
    st.rerun()

# --- 3. INTERFAZ ---
st.title("Asociación de Dominó del Estado Lara (ADEL) - Sistema Suizo")

with st.sidebar:
    st.header("Seguridad del Torneo")
    backup = {k:st.session_state[k] for k in ['asistentes','juegos_ganados','efectividad','puntos_contra','ronda_actual','historial_completo','registro_abierto','meta_puntos', 'parejas_jugadas', 'historial_reposo']}
    st.download_button("📥 RESGUARDAR", data=json.dumps(backup, indent=4), file_name="respaldo_adel.json")
    st.markdown("---")
    st.header("RESTAURAR")
    archivo = st.file_uploader("Subir respaldo JSON", type=["json"])
    if archivo and st.button("🔄 CARGAR DATOS"):
        datos = json.load(archivo)
        for k, v in datos.items(): st.session_state[k] = v
        st.rerun()
    st.caption("Creado por Poeta")

if st.session_state.registro_abierto:
    st.subheader("📝 Registro de Atletas")
    st.session_state.meta_puntos = st.radio("Meta:", [100, 200], horizontal=True)
    st.text_input("Atleta + ENTER:", key="nuevo_atleta", on_change=procesar_registro)

    if st.session_state.asistentes:
        st.info(f"**Inscritos ({len(st.session_state.asistentes)}):** {', '.join(st.session_state.asistentes)}")
        st.write(f"Rondas según fórmula ($\log_2(n)+1$): **{calcular_rondas(len(st.session_state.asistentes))}**")
        
        sel = st.selectbox("Gestionar:", st.session_state.asistentes)
        c1, c2 = st.columns(2)
        with c1:
            @st.dialog("Editar")
            def ed(n):
                nuevo = st.text_input("Nombre:", value=n).upper().strip()
                if st.button("OK"):
                    st.session_state.asistentes[st.session_state.asistentes.index(n)] = nuevo
                    st.rerun()
            if st.button("✏️ Editar"): ed(sel)
        with c2:
            if st.button("🗑️ Borrar"):
                st.session_state.asistentes.remove(sel)
                st.rerun()
        if st.button("🚀 INICIAR TORNEO") and len(st.session_state.asistentes) >= 4:
            st.session_state.registro_abierto = False
            generar_ronda_adel()
            st.rerun()
else:
    r_list = [h['ronda'] for h in st.session_state.historial_completo]
    r_ver = st.selectbox("📅 Ver Ronda:", r_list, index=len(r_list)-1)
    r_data = st.session_state.historial_completo[r_ver-1]
    
    st.header(f"🃏 Ronda Actual: {r_ver} de {calcular_rondas(len(st.session_state.asistentes))}")
    t1, t2 = st.tabs(["🗂️ Mesas", "📊 Ranking Oficial"])
    
    with t1:
        if r_data['reposo']:
            st.warning(f"💤 **EN REPOSO:** {', '.join(r_data['reposo'])}")
        for i, m in enumerate(r_data['mesas']):
            st.markdown(f"**Mesa {i+1}** (Cruces: {m[0]}-{m[2]} vs {m[1]}-{m[3]})")
            c1, c2, c3 = st.columns([2, 1, 2])
            with c1: st.info(f"🔵 **Pareja A:**\n\n{m[0]} / {m[2]}")
            with c2:
                st.number_input("Pts A", key=f"p1_r{r_ver}_m{i}", min_value=0)
                st.number_input("Pts B", key=f"p2_r{r_ver}_m{i}", min_value=0)
            with c3: st.success(f"🔴 **Pareja B:**\n\n{m[1]} / {m[3]}")
            st.markdown("---")
        if not r_data['finalizada'] and r_ver == st.session_state.ronda_actual:
            if st.button("💾 FINALIZAR RONDA"): finalizar_ronda()

    with t2:
        rk = sorted(st.session_state.asistentes, key=lambda x: (st.session_state.juegos_ganados.get(x,0), st.session_state.efectividad.get(x,0), -st.session_state.puntos_contra.get(x,0)), reverse=True)
        st.table([{"Pos": i+1, "Atleta": j, "G": st.session_state.juegos_ganados.get(j,0), "Ef": st.session_state.efectividad.get(j,0), "Contra": st.session_state.puntos_contra.get(j,0)} for i, j in enumerate(rk)])
