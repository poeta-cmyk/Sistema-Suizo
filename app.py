import streamlit as st
import math

# --- 1. CONFIGURACIÓN E INICIALIZACIÓN ---
st.set_page_config(layout="wide", page_title="SISTEMA ADEL - PRO")

# Inicialización de memoria (Session State)
if 'asistentes' not in st.session_state:
    st.session_state.update({
        'asistentes': [], 'juegos_ganados': {}, 'efectividad': {}, 
        'puntos_contra': {}, 'ronda_actual': 1, 'registro_abierto': True, 
        'historial_completo': [], 'tarjetas': {}, 'parejas_jugadas': []
    })

# --- 2. FUNCIONES DE LÓGICA ---
def registrar_atleta():
    nombre = st.session_state.nuevo_atleta.strip().upper()
    if nombre and nombre not in st.session_state.asistentes:
        st.session_state.asistentes.append(nombre)
        st.session_state.tarjetas[nombre] = "NINGUNA"
        st.session_state.juegos_ganados[nombre] = 0
        st.session_state.efectividad[nombre] = 0
        st.session_state.puntos_contra[nombre] = 0
    st.session_state.nuevo_atleta = ""

def generar_ronda():
    # Ordenar por Baremo ADEL: JG -> Efect -> -PC
    rk = sorted(st.session_state.asistentes, 
                key=lambda x: (st.session_state.juegos_ganados[x], 
                               st.session_state.efectividad[x], 
                               -st.session_state.puntos_contra[x]), reverse=True)
    
    activos = rk[:]
    mesas = []
    while len(activos) >= 4:
        # Lógica 1-3 vs 2-4 (Parejas balanceadas)
        m = [activos.pop(0), activos.pop(0), activos.pop(0), activos.pop(0)]
        mesas.append([m[0], m[1], m[2], m[3]]) # Orden: Norte, Sur, Este, Oeste
    
    st.session_state.historial_completo.append({
        'ronda': st.session_state.ronda_actual,
        'mesas': mesas,
        'finalizada': False
    })
    st.session_state.registro_abierto = False

# --- 3. NAVEGACIÓN LATERAL ---
with st.sidebar:
    st.title("🏆 MENÚ ADEL")
    pagina = st.radio("Sección:", ["🎮 MESA TÉCNICA", "📺 PANTALLA ADEL"])

# --- PÁGINA 1: MESA TÉCNICA ---
if pagina == "🎮 MESA TÉCNICA":
    st.header("Control de Torneo y Justicia")
    
    if st.session_state.registro_abierto:
        st.subheader("Registro de Atletas")
        st.text_input("Nombre del Atleta:", key="nuevo_atleta", on_change=registrar_atleta)
        st.write(f"Inscritos: {len(st.session_state.asistentes)}")
        if st.button("🚀 INICIAR TORNEO") and len(st.session_state.asistentes) >= 4:
            generar_ronda()
            st.rerun()
    else:
        tab1, tab2 = st.tabs(["📝 RESULTADOS", "📊 BAREMO Y TARJETAS"])
        
        with tab1:
            r_data = st.session_state.historial_completo[-1]
            st.subheader(f"Ronda {r_data['ronda']}")
            for i, m in enumerate(r_data['mesas']):
                with st.container(border=True):
                    st.write(f"**MESA {i+1}**")
                    c1, c2 = st.columns(2)
                    st.number_input(f"Pts Pareja A ({m[0]}-{m[2]})", key=f"pA_m{i}", min_value=0)
                    st.number_input(f"Pts Pareja B ({m[1]}-{m[3]})", key=f"pB_m{i}", min_value=0)

        with tab2:
            st.subheader("Baremo Oficial")
            # Encabezados según tu imagen
            cols = st.columns([0.5, 2, 0.7, 0.7, 0.7, 1.5])
            headers = ["Pos", "Atleta", "JG", "Efect", "PC", "TARJETAS"]
            for col, h in zip(cols, headers): col.write(f"**{h}**")

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
                # Selector manual de tarjetas
                st.session_state.tarjetas[n] = c[5].selectbox(
                    "Sanción", ["NINGUNA", "AMARILLA 🟨", "ROJA 🟥", "NEGRA ⬛"],
                    key=f"tj_{n}", label_visibility="collapsed"
                )

# --- PÁGINA 2: PANTALLA ADEL ---
elif pagina == "📺 PANTALLA ADEL":
    st.header("Monitor de Proyección ADEL")
    if not st.session_state.historial_completo:
        st.warning("Esperando inicio...")
    else:
        r_data = st.session_state.historial_completo[-1]
        cols = st.columns(2)
        for i, m in enumerate(r_data['mesas']):
            with cols[i % 2]:
                # Diseño en cruz con "ADEL" central
                with st.container(border=True):
                    st.markdown(f"<h3 style='text-align:center;'>MESA {i+1}</h3>", unsafe_allow_html=True)
                    st.markdown(f"<div style='text-align:center;'><b>{m[0]}</b></div>", unsafe_allow_html=True)
                    c_izq, c_mid, c_der = st.columns([1,1,1])
                    c_izq.markdown(f"<div style='text-align:right; margin-top:20px;'>{m[1]}</div>", unsafe_allow_html=True)
                    c_mid.markdown("<div style='text-align:center; font-size:2em; color:red;'>ADEL</div>", unsafe_allow_html=True)
                    c_der.markdown(f"<div style='text-align:left; margin-top:20px;'>{m[3]}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div style='text-align:center;'><b>{m[2]}</b></div>", unsafe_allow_html=True)
