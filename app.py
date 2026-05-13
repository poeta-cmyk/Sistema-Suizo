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
    # Baremo oficial logarítmico
    val_pf = pf if pf > 0 else 1
    val_pc = pc if pc > 0 else 1
    return math.log10(val_pf / val_pc) + 1

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
    # Cierre de corchete verificado para evitar SyntaxError
    mesas = [activos[i:i+4] for i in range(0, len(activos), 4)]
    st.session_state.historial_completo.append({
        'ronda': st.session_state.ronda_actual, 'mesas': mesas, 'reposo': reposo
    })
    st.session_state.registro_abierto = False

# --- 3. NAVEGACIÓN RECTIFICADA ---
with st.sidebar:
    st.title("🏆 MENÚ ADEL")
    # El orden aquí debe ser idéntico al de las condiciones de abajo
    opcion = st.radio("Sección:", ["MESAS", "PANTALLA ADEL"])

# --- SECCIÓN: MESAS (CONTROL TÉCNICO) ---
if opcion == "MESAS": # Ahora muestra correctamente el Control
    st.header("ADEL - Control de Torneo y Justicia")
    if st.session_state.registro_abierto:
        st.subheader("Registro de Atletas")
        st.text_input("Nombre del Atleta + ENTER:", key="nuevo_atleta", on_change=registrar_atleta)
        if st.session_state.asistentes:
            st.markdown(f"**Atletas Inscritos: {len(st.session_state.asistentes)}**") #
            for i, n in enumerate(st.session_state.asistentes): st.text(f"{i+1}. {n}")
            if st.button("🚀 INICIAR TORNEO"):
                generar_ronda(); st.rerun()
    else:
        tab1, tab2 = st.tabs(["📝 RESULTADOS", "📊 BAREMO Y TARJETAS"])
        r_data = st.session_state.historial_completo[-1]
        with tab1:
            st.subheader(f"Carga de Puntos - Ronda {r_data['ronda']} (de {st.session_state.total_rondas})") #
            if r_data['reposo']: st.warning(f"Atletas en Reposo: {', '.join(r_data['reposo'])}")
            for i, m in enumerate(r_data['mesas']):
                with st.container(border=True):
                    st.write(f"**MESA {i+1}**")
                    c1, c2 = st.columns(2)
                    with c1: st.number_input(f"A) {m[0]} --- C) {m[2]}", key=f"pAC_m{i}", min_value=0) #
                    with c2: st.number_input(f"B) {m[1]} --- D) {m[3]}", key=f"pBD_m{i}", min_value=0)
        with tab2:
            st.subheader("Baremo Oficial y Sanciones") #
            cols = st.columns([0.5, 2, 0.7, 0.7, 0.7, 1.5])
            for col, h in zip(cols, ["Pos", "Atleta", "JG", "Efect", "PC", "TARJETAS"]): col.write(f"**{h}**")
            rk_all = sorted(st.session_state.asistentes, key=lambda x: (st.session_state.juegos_ganados[x], st.session_state.efectividad[x], -st.session_state.puntos_contra[x]), reverse=True)
            for i, n in enumerate(rk_all):
                c = st.columns([0.5, 2, 0.7, 0.7, 0.7, 1.5])
                c[0].write(i+1); c[1].write(n); c[2].write(st.session_state.juegos_ganados[n])
