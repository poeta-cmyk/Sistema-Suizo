import streamlit as st
import math
import random
import json

# --- 1. CONFIGURACIÓN E INICIALIZACIÓN ---
st.set_page_config(layout="wide", page_title="ADEL - Sistema de Torneo")

# Inicialización de memoria total (Caja fuerte de datos)
for key, default in {
    'asistentes': [], 'juegos_ganados': {}, 'efectividad': {}, 
    'puntos_contra': {}, 'ronda_actual': 1, 'registro_abierto': True, 
    'meta_puntos': 100, 'historial_completo': [], 'parejas_jugadas': [], 'historial_reposo': []
}.items():
    if key not in st.session_state: st.session_state[key] = default

# --- 2. LÓGICA DE CONTROL (Funciones) ---
def calcular_rondas(n):
    return math.ceil(math.log2(n)) + 1 if n >= 4 else 0

def procesar_registro():
    n = st.session_state.nuevo_atleta.strip().upper()
    if n and n not in st.session_state.asistentes:
        st.session_state.asistentes.append(n)
        st.session_state.asistentes.sort()
    st.session_state.nuevo_atleta = ""

def generar_ronda_adel():
    rk = sorted(st.session_state.asistentes, 
                key=lambda x: (st.session_state.juegos_ganados.get(x, 0), 
                               st.session_state.efectividad.get(x, 0),
                               -st.session_state.puntos_contra.get(x, 0)), reverse=True)
    
    n_reposo = len(rk) % 4
    reposados = []
    if n_reposo > 0:
        candidatos = [j for j in reversed(rk) if j not in st.session_state.historial_reposo]
        if not candidatos: 
            st.session_state.historial_reposo = []
            candidatos = list(reversed(rk))
        reposados = candidatos[:n_reposo]
        st.session_state.historial_reposo.extend(reposados)
    
    activos = [j for j in rk if j not in reposados]
    mesas = []
    
    while len(activos) >= 4:
        j1 = activos[0]
        comp = None
        for i in range(2, len(activos)):
            posible = activos[i]
            if tuple(sorted((j1, posible))) not in st.session_state.parejas_jugadas:
                comp = posible
                break
        if not comp: comp = activos[2]
        
        activos.remove(j1); activos.remove(comp)
        j2 = activos[0]; rival_comp = activos[1]
        activos.remove(j2); activos.remove(rival_comp)
        
        mesas.append([j1, j2, comp, rival_comp]) # 1-3 vs 2-4
        st.session_state.parejas_jugadas.append(tuple(sorted((j1, comp))))
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
            ef, gan, per, cg, cp = meta-p2, [mesa[0], mesa[2]], [mesa[1], mesa[3]], p2, p1
        else:
            ef, gan, per, cg, cp = meta-p1, [mesa[1], mesa[3]], [mesa[0], mesa[2]], p1, p2
        for g in gan:
            st.session_state.juegos_ganados[g] = st.session_state.juegos_ganados.get(g,0)+1
            st.session_state.efectividad[g] = st.session_state.efectividad.get(g,0)+ef
            st.session_state.puntos_contra[g] = st.session_state.puntos_contra.get(g,0)+cg
        for p in per:
            st.session_state.efectividad[p] = st.session_state.efectividad.get(p,0)-ef
            st.session_state.puntos_contra[p] = st.session_state.puntos_contra.get(p,0)+cp
    for r in r_data['reposo']:
        st.session_state.juegos_ganados[r] = st.session_state.juegos_ganados.get(r,0)+1
        st.session_state.efectividad[r] = st.session_state.efectividad.get(r,0)+(meta//2)
    st.session_state.ronda_actual += 1
    generar_ronda_adel()
    st.rerun()

# --- 3. NAVEGACIÓN ---
with st.sidebar:
    st.title("📌 MENÚ ADEL")
    pagina = st.radio("Ir a:", ["🎮 Control de Torneo", "📺 Monitor de Pantalla"])
    st.markdown("---")
    st.header("💾 Seguridad")
    backup = {k:st.session_state[k] for k in ['asistentes','juegos_ganados','efectividad','puntos_contra','ronda_actual','historial_completo','registro_abierto','meta_puntos', 'parejas_jugadas', 'historial_reposo']}
    st.download_button("📥 RESGUARDAR", data=json.dumps(backup, indent=4), file_name="adel_backup.json")
    archivo = st.file_uploader("Restaurar:", type=["json"])
    if archivo and st.button("🔄 CARGAR"):
        datos = json.load(archivo)
        for k, v in datos.items(): st.session_state[k] = v
        st.rerun()

# --- HOJA 1: CONTROL DE TORNEO ---
if pagina == "🎮 Control de Torneo":
    st.title("Panel de Control ADEL")
    
    if st.session_state.registro_abierto:
        st.subheader("📝 Registro de Atletas")
        st.session_state.meta_puntos = st.radio("Meta:", [100, 200], horizontal=True)
        st.text_input("Atleta + ENTER:", key="nuevo_atleta", on_change=procesar_registro)
        if st.session_state.asistentes:
            st.info(f"**Inscritos ({len(st.session_state.asistentes)}):** {', '.join(st.session_state.asistentes)}")
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
        
        st.header(f"🃏 Ronda {r_ver}")
        t1, t2 = st.tabs(["🗂️ Anotar Puntos", "📊 Ranking"])
        with t1:
            for i, m in enumerate(r_data['mesas']):
                st.markdown(f"**Mesa {i+1}**")
                c1, c2, c3 = st.columns([2, 1, 2])
                with c1: st.info(f"{m[0]} / {m[2]}")
                with c2:
                    st.number_input("P1", key=f"p1_r{r_ver}_m{i}", min_value=0)
                    st.number_input("P2", key=f"p2_r{r_ver}_m{i}", min_value=0)
                with c3: st.success(f"{m[1]} / {m[3]}")
            if not r_data['finalizada'] and r_ver == st.session_state.ronda_actual:
                if st.button("💾 FINALIZAR RONDA"): finalizar_ronda()
        with t2:
            rk = sorted(st.session_state.asistentes, key=lambda x: (st.session_state.juegos_ganados.get(x,0), st.session_state.efectividad.get(x,0), -st.session_state.puntos_contra.get(x,0)), reverse=True)
            st.table([{"Pos": i+1, "Atleta": j, "G": st.session_state.juegos_ganados.get(j,0), "Ef": st.session_state.efectividad.get(j,0), "Contra": st.session_state.puntos_contra.get(j,0)} for i, j in enumerate(rk)])

# --- HOJA 2: MONITOR DE PANTALLA (PROYECCIÓN) ---
elif pagina == "📺 Monitor de Pantalla":
    st.title("Visualización del Torneo")
    
    if not st.session_state.historial_completo:
        st.warning("Esperando el inicio del torneo...")
    else:
        # Mostramos siempre la ronda actual para el público
        r_data = st.session_state.historial_completo[-1]
        st.header(f"Ronda Actual: {r_data['ronda']}")
        
        if r_data['reposo']:
            st.warning(f"💤 REPOSO: {', '.join(r_data['reposo'])}")
        
        # DIBUJO DE MESAS EN CUADRÍCULA (Estilo el dibujo que pasaste)
        cols = st.columns(2) # 2 mesas por fila para que se vea grande
        for i, m in enumerate(r_data['mesas']):
            with cols[i % 2]:
                with st.container(border=True):
                    st.markdown(f"<h3 style='text-align: center; color: yellow;'>MESA {i+1}</h3>", unsafe_allow_html=True)
                    st.markdown(f"<p style='text-align: center; margin:0;'>{m[0]}</p>", unsafe_allow_html=True)
                    col_izq, col_img, col_der = st.columns([1,1,1])
                    with col_izq: st.markdown(f"<p style='text-align: right; padding-top: 20px;'>{m[1]}</p>", unsafe_allow_html=True)
                    with col_img: st.image("https://cdn-icons-png.flaticon.com/512/3505/3505417.png", width=80) # Icono de domino
                    with col_der: st.markdown(f"<p style='text-align: left; padding-top: 20px;'>{m[3]}</p>", unsafe_allow_html=True)
                    st.markdown(f"<p style='text-align: center; margin:0;'>{m[2]}</p>", unsafe_allow_html=True)
                    st.markdown("---")
        
        st.markdown("### 🏆 Ranking Top 10")
        rk = sorted(st.session_state.asistentes, key=lambda x: (st.session_state.juegos_ganados.get(x,0), st.session_state.efectividad.get(x,0), -st.session_state.puntos_contra.get(x,0)), reverse=True)
        st.table([{"Pos": i+1, "Atleta": j, "G": st.session_state.juegos_ganados.get(j,0), "Ef": st.session_state.efectividad.get(j,0)} for i, j in enumerate(rk[:10])])
