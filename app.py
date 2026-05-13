import streamlit as st

# --- 1. CONFIGURACIÓN E INICIALIZACIÓN ---
st.set_page_config(layout="wide", page_title="SISTEMA ADEL - PRO")

if 'asistentes' not in st.session_state:
    st.session_state.update({
        'asistentes': [], 'juegos_ganados': {}, 'efectividad': {}, 
        'puntos_contra': {}, 'ronda_actual': 1, 'registro_abierto': True, 
        'historial_completo': [], 'tarjetas': {}
    })

# --- 2. FUNCIONES DE LÓGICA ---
def registrar_atleta():
    nombre = st.session_state.nuevo_atleta.strip().upper()
    if nombre and nombre not in st.session_state.asistentes:
        st.session_state.asistentes.append(nombre)
        st.session_state.asistentes.sort()
        # Inicialización garantizada para todos
        for n in st.session_state.asistentes:
            if n not in st.session_state.tarjetas:
                st.session_state.tarjetas[n] = "NINGUNA"
                st.session_state.juegos_ganados[n] = 0
                st.session_state.efectividad[n] = 0
                st.session_state.puntos_contra[n] = 0
    st.session_state.nuevo_atleta = ""

def generar_ronda():
    # Orden por mérito para emparejar
    rk = sorted(st.session_state.asistentes, 
                key=lambda x: (st.session_state.juegos_ganados[x], 
                               st.session_state.efectividad[x], 
                               -st.session_state.puntos_contra[x]), reverse=True)
    
    cant_mesas = len(rk) // 4
    activos = rk[:cant_mesas * 4]
    reposo = rk[cant_mesas * 4:] # Los que no alcanzaron mesa
    
    mesas = []
    for i in range(0, len(activos), 4):
        mesas.append(activos[i:i+4])
    
    st.session_state.historial_completo.append({
        'ronda': st.session_state.ronda_actual,
        'mesas': mesas,
        'reposo': reposo,
        'finalizada': False
    })
    st.session_state.registro_abierto = False

# --- 3. NAVEGACIÓN ---
with st.sidebar:
    st.title("🏆 MENÚ ADEL")
    pagina = st.radio("Sección:", ["🎮 MESA TÉCNICA", "📺 PANTALLA ADEL"])

# --- PÁGINA: MESA TÉCNICA ---
if pagina == "🎮 MESA TÉCNICA":
    st.header("ADEL")
    
    if st.session_state.registro_abierto:
        st.subheader("Registro de Atletas")
        st.text_input("Nombre del Atleta + ENTER:", key="nuevo_atleta", on_change=registrar_atleta)
        if st.session_state.asistentes:
            st.markdown(f"### Inscritos: {len(st.session_state.asistentes)}")
            for i, n in enumerate(st.session_state.asistentes): st.text(f"{i+1}. {n}")
            if st.button("🚀 INICIAR TORNEO") and len(st.session_state.asistentes) >= 4:
                generar_ronda()
                st.rerun()
    else:
        tab1, tab2 = st.tabs(["📝 RESULTADOS", "📊 BAREMO Y TARJETAS"])
        r_data = st.session_state.historial_completo[-1]
        
        with tab1:
            st.subheader(f"Carga de Resultados - Ronda {r_data['ronda']}")
            # Mostrar quiénes están en reposo en la mesa técnica
            if r_data['reposo']:
                st.warning(f"Atletas en Reposo: {', '.join(r_data['reposo'])}")
            
            for i, m in enumerate(r_data['mesas']):
                with st.container(border=True):
                    st.write(f"**MESA {i+1}**")
                    c1, c2 = st.columns(2)
                    with c1: st.number_input(f"A) {m[0]} --- C) {m[2]}", key=f"pAC_m{i}", min_value=0)
                    with c2: st.number_input(f"B) {m[1]} --- D) {m[3]}", key=f"pBD_m{i}", min_value=0)

        with tab2:
            st.subheader("Baremo Oficial y Sanciones")
            cols = st.columns([0.5, 2, 0.7, 0.7, 0.7, 1.5])
            for col, h in zip(cols, ["Pos", "Atleta", "JG", "Efect", "PC", "TARJETAS"]):
                col.write(f"**{h}**")
            
            # El baremo siempre muestra a TODOS los inscritos
            rk_all = sorted(st.session_state.asistentes, 
                            key=lambda x: (st.session_state.juegos_ganados[x], 
                                           st.session_state.efectividad[x], 
                                           -st.session_state.puntos_contra[x]), reverse=True)
            for i, n in enumerate(rk_all):
                c = st.columns([0.5, 2, 0.7, 0.7, 0.7, 1.5])
                c[0].write(i+1)
                c[1].write(n)
                c[2].write(st.session_state.juegos_ganados[n])
                c[3].write(st.session_state.efectividad[n])
                c[4].write(st.session_state.puntos_contra[n])
                st.session_state.tarjetas[n] = c[5].selectbox(
                    "Sanción", ["NINGUNA", "AMARILLA 🟨", "ROJA 🟥", "NEGRA ⬛"], 
                    key=f"tj_{n}", label_visibility="collapsed",
                    index=["NINGUNA", "AMARILLA 🟨", "ROJA 🟥", "NEGRA ⬛"].index(st.session_state.tarjetas.get(n, "NINGUNA"))
                )

# --- PÁGINA: PANTALLA ADEL ---
elif pagina == "📺 PANTALLA ADEL":
    st.header("Monitor Oficial ADEL")
    if not st.session_state.historial_completo:
        st.info("Esperando registro de atletas...")
    else:
        r_data = st.session_state.historial_completo[-1]
        
        # Bloque de Reposo resaltado
        if r_data['reposo']:
            st.error(f"⌛ ATLETAS EN REPOSO: {', '.join(r_data['reposo'])}")
            st.markdown("---")

        filas = [r_data['mesas'][i:i + 4] for i in range(0, len(r_data['mesas']), 4)]
        for f_idx, fila in enumerate(filas):
            cols = st.columns(4)
            for i, m in enumerate(fila):
                num_m = (f_idx * 4) + i + 1
                with cols[i]:
                    with st.container(border=True):
                        st.markdown(f"<div style='text-align:center; font-weight:bold;'>A) {m[0]}</div>", unsafe_allow_html=True)
                        cl, cm, cr = st.columns([1.2, 1, 1.2])
                        cl.markdown(f"<div style='text-align:right; font-size:0.8em; margin-top:10px;'>B) {m[1]}</div>", unsafe_allow_html=True)
                        cm.markdown(f"<div style='text-align:center; font-size:1.1em; color:#FF4B4B; font-weight:bold; margin-top:5px;'>MESA {num_m}</div>", unsafe_allow_html=True)
                        cr.markdown(f"<div style='text-align:left; font-size:0.8em; margin-top:10px;'>D) {m[3]}</div>", unsafe_allow_html=True)
                        st.markdown(f"<div style='text-align:center; font-weight:bold;'>C) {m[2]}</div>", unsafe_allow_html=True)
