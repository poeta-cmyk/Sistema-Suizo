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
        st.session_state.tarjetas[nombre] = "NINGUNA"
        st.session_state.juegos_ganados[nombre] = 0
        st.session_state.efectividad[nombre] = 0
        st.session_state.puntos_contra[nombre] = 0
    st.session_state.nuevo_atleta = ""

def generar_ronda():
    rk_merito = sorted(st.session_state.asistentes, 
                       key=lambda x: (st.session_state.juegos_ganados[x], 
                                      st.session_state.efectividad[x], 
                                      -st.session_state.puntos_contra[x]), reverse=True)
    activos = rk_merito[:]
    mesas = []
    while len(activos) >= 4:
        # Estructura: [Norte(A), Sur(B), Este(C), Oeste(D)]
        mesas.append([activos.pop(0), activos.pop(0), activos.pop(0), activos.pop(0)])
    
    st.session_state.historial_completo.append({
        'ronda': st.session_state.ronda_actual,
        'mesas': mesas,
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
            st.markdown(f"### Atletas Inscritos ({len(st.session_state.asistentes)})")
            for i, nombre in enumerate(st.session_state.asistentes):
                st.text(f"{i+1}. {nombre}")
            
            st.markdown("---")
            if st.button("🚀 INICIAR TORNEO") and len(st.session_state.asistentes) >= 4:
                generar_ronda()
                st.rerun()
    else:
        tab1, tab2 = st.tabs(["📝 RESULTADOS", "📊 BAREMO Y TARJETAS"])
        
        with tab1:
            r_data = st.session_state.historial_completo[-1]
            st.subheader(f"Carga de Puntos - Ronda {r_data['ronda']}")
            for i, m in enumerate(r_data['mesas']):
                with st.container(border=True):
                    st.write(f"**MESA {i+1}**")
                    c1, c2 = st.columns(2)
                    # Nomenclatura solicitada: A) Nombre C) Nombre
                    with c1: 
                        st.number_input(f"A) {m[0]} --- C) {m[2]}", 
                                        key=f"pAC_m{i}", min_value=0, step=1)
                    # Nomenclatura solicitada: B) Nombre D) Nombre
                    with c2: 
                        st.number_input(f"B) {m[1]} --- D) {m[3]}", 
                                        key=f"pBD_m{i}", min_value=0, step=1)

        with tab2:
            st.subheader("Baremo Oficial")
            cols = st.columns([0.5, 2, 0.7, 0.7, 0.7, 1.5])
            for col, h in zip(cols, ["Pos", "Atleta", "JG", "Efect", "PC", "TARJETAS"]):
                col.write(f"**{h}**")
            
            rk_sorted = sorted(st.session_state.asistentes, 
                               key=lambda x: (st.session_state.juegos_ganados[x], 
                                              st.session_state.efectividad[x], 
                                              -st.session_state.puntos_contra[x]), reverse=True)
            for i, n in enumerate(rk_sorted):
                c = st.columns([0.5, 2, 0.7, 0.7, 0.7, 1.5])
                c[0].write(i+1)
                c[1].write(n)
                c[2].write(st.session_state.juegos_ganados[n])
                c[3].write(st.session_state.efectividad[n])
                c[4].write(st.session_state.puntos_contra[n])
                st.session_state.tarjetas[n] = c[5].selectbox(
                    "Sanción", ["NINGUNA", "AMARILLA 🟨", "ROJA 🟥", "NEGRA ⬛"], 
                    key=f"tj_{n}", label_visibility="collapsed"
                )

# --- PÁGINA: PANTALLA ADEL ---
elif pagina == "📺 PANTALLA ADEL":
    st.header("Monitor Oficial ADEL")
    if not st.session_state.historial_completo:
        st.warning("Inicie el torneo en la Mesa Técnica.")
    else:
        r_data = st.session_state.historial_completo[-1]
        cols = st.columns(2)
        for i, m in enumerate(r_data['mesas']):
            with cols[i % 2]:
                with st.container(border=True):
                    # El nombre superior es el Atleta A
                    st.markdown(f"<div style='text-align:center; font-weight:bold;'>A) {m[0]}</div>", unsafe_allow_html=True)
                    cl, cm, cr = st.columns([1,1,1])
                    # Lateral izquierdo: B
                    cl.markdown(f"<div style='text-align:right; margin-top:15px;'>B) {m[1]}</div>", unsafe_allow_html=True)
                    cm.markdown(f"<div style='text-align:center; font-size:1.5em; color:#FF4B4B; font-weight:bold; margin-top:5px;'>MESA {i+1}</div>", unsafe_allow_html=True)
                    # Lateral derecho: D
                    cr.markdown(f"<div style='text-align:left; margin-top:15px;'>D) {m[3]}</div>", unsafe_allow_html=True)
                    # Inferior: C (Pareja de A)
                    st.markdown(f"<div style='text-align:center; font-weight:bold;'>C) {m[2]}</div>", unsafe_allow_html=True)
