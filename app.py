import streamlit as st
import math

# --- 1. CONFIGURACIÓN E INICIALIZACIÓN ---
st.set_page_config(layout="wide", page_title="SISTEMA ADEL - PRO")

if 'total_rondas' not in st.session_state:
    st.session_state.total_rondas = 5

if 'asistentes' not in st.session_state:
    st.session_state.update({
        'asistentes': [], 'juegos_ganados': {}, 'efectividad': {}, 
        'puntos_contra': {}, 'puntos_favor': {}, 'ronda_actual': 1,
        'registro_abierto': True, 'historial_completo': [], 'tarjetas': {}
    })

# --- 2. LÓGICA DE CÁLCULO ---
def calcular_efectividad_log(pf, pc):
    if pc == 0: pc = 1
    if pf == 0: pf = 1
    return math.log10(pf / pc) + 1

def registrar_atleta():
    nombre = st.session_state.nuevo_atleta.strip().upper()
    if nombre and nombre not in st.session_state.asistentes:
        st.session_state.asistentes.append(nombre)
        st.session_state.asistentes.sort()
        st.session_state.tarjetas[nombre] = "NINGUNA"
        st.session_state.juegos_ganados[nombre] = 0
        st.session_state.efectividad[nombre] = 0.0
        st.session_state.puntos_contra[nombre] = 0
        st.session_state.puntos_favor[nombre] = 0
    st.session_state.nuevo_atleta = ""

def generar_ronda():
    rk = sorted(st.session_state.asistentes, 
                key=lambda x: (st.session_state.juegos_ganados[x], 
                               st.session_state.efectividad[x], 
                               -st.session_state.puntos_contra[x]), reverse=True)
    cant_mesas = len(rk) // 4
    activos = rk[:cant_mesas * 4]
    reposo = rk[cant_mesas * 4:]
    mesas = [activos[i:i+4] for i in range(0, len(activos), 4)]
    st.session_state.historial_completo.append({
        'ronda': st.session_state.ronda_actual, 'mesas': mesas, 'reposo': reposo
    })
    st.session_state.registro_abierto = False

# --- 3. NAVEGACIÓN CORREGIDA ---
with st.sidebar:
    st.title("🏆 MENÚ ADEL")
    # El orden aquí debe coincidir con las condicionales de abajo
    pagina = st.radio("Sección:", ["🎮 MESAS", "📺 PANTALLA ADEL"])

# --- SECCIÓN: MESAS (CARGA Y CONTROL) ---
if pagina == "🎮 MESAS": # Ahora sí dirige a la gestión técnica
    st.header("ADEL - Panel de Control")
    if st.session_state.registro_abierto:
        st.subheader("Registro de Atletas")
        st.text_input("Nombre del Atleta + ENTER:", key="nuevo_atleta", on_change=registrar_atleta)
        if st.session_state.asistentes:
            st.markdown(f"**Inscritos: {len(st.session_state.asistentes)}**")
            if st.button("🚀 INICIAR TORNEO"):
                generar_ronda(); st.rerun()
    else:
        tab1, tab2 = st.tabs(["📝 RESULTADOS", "📊 BAREMO Y TARJETAS"])
        r_data = st.session_state.historial_completo[-1]
        with tab1:
            st.subheader(f"Carga de Puntos - Ronda {r_data['ronda']} (de {st.session_state.total_rondas})")
            if r_data['reposo']: st.warning(f"En Reposo: {', '.join(r_data['reposo'])}")
            for i, m in enumerate(r_data['mesas']):
                with st.container(border=True):
                    st.write(f"**MESA {i+1}**")
                    c1, c2 = st.columns(2)
                    with c1: st.number_input(f"A) {m[0]} --- C) {m[2]}", key=f"pAC_m{i}", min_value=0)
                    with c2: st.number_input(f"B) {m[1]} --- D) {m[3]}", key=f"pBD_m{i}", min_value=0)
        with tab2:
            st.subheader("Baremo Oficial y Sanciones")
            cols = st.columns([0.5, 2, 0.7, 0.7, 0.7, 1.5])
            for col, h in zip(cols, ["Pos", "Atleta", "JG", "Efect", "PC", "TARJETAS"]): col.write(f"**{h}**")
            rk_all = sorted(st.session_state.asistentes, key=lambda x: (st.session_state.juegos_ganados[x], st.session_state.efectividad[x], -st.session_state.puntos_contra[x]), reverse=True)
            for i, n in enumerate(rk_all):
                c = st.columns([0.5, 2, 0.7, 0.7, 0.7, 1.5])
                c[0].write(i+1); c[1].write(n); c[2].write(st.session_state.juegos_ganados[n])
                c[3].write(f"{st.session_state.efectividad[n]:.3f}"); c[4].write(st.session_state.puntos_contra[n])
                st.session_state.tarjetas[n] = c[5].selectbox("Sanción", ["NINGUNA", "AMARILLA 🟨", "ROJA 🟥", "NEGRA ⬛"], key=f"tj_{n}", label_visibility="collapsed")

# --- SECCIÓN: PANTALLA ADEL (MONITOR) ---
elif pagina == "📺 PANTALLA ADEL": # Ahora sí dirige al monitor público
    st.header("Monitor Oficial ADEL")
    if st.session_state.historial_completo:
        r_data = st.session_state.historial_completo[-1]
        st.subheader(f"Ronda {r_data['ronda']} (de {st.session_state.total_rondas})")
        if r_data['reposo']: st.error(f"⌛ ATLETAS EN REPOSO: {', '.join(r_data['reposo'])}")
        filas = [r_data['mesas'][i:
