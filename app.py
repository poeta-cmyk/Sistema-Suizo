import streamlit as st
import math

# --- 1. INICIALIZACIÓN ---
if 'asistentes' not in st.session_state:
    st.session_state.update({
        'asistentes': [],
        'estados': {},
        'meta_puntos': 200,
        'n_rondas': 1,
        'seccion': "INSCRIPCIÓN"
    })

# --- 2. LÓGICA DE CÁLCULO (Su fórmula) ---
def calcular_rondas_sugeridas(n_atletas):
    if n_atletas < 2: return 1
    # Fórmula: Log2(N) + 1
    return math.ceil(math.log2(n_atletas)) + 1

# --- 3. INTERFAZ ---
st.set_page_config(layout="wide")

with st.sidebar:
    st.title("🏆 MENÚ ADEL")
    st.session_state.seccion = st.radio("SECCIÓN:", ["INSCRIPCIÓN", "MESAS", "RESULTADOS", "RANKING"])

if st.session_state.seccion == "INSCRIPCIÓN":
    st.markdown("<h1 style='text-align: center;'>ASOCIACIÓN DE DOMINÓ DEL ESTADO LARA ADEL</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center;'>SISTEMA SUIZO</h2>", unsafe_allow_html=True)

    col_izq, col_der = st.columns([2, 1])

    with col_izq:
        st.session_state.meta_puntos = st.radio("Meta del encuentro:", [100, 200], 
                                                index=1 if st.session_state.meta_puntos == 200 else 0, 
                                                horizontal=True)
        
        def registrar():
            txt = st.session_state.nuevo_atleta.upper().strip()
            if txt and txt not in st.session_state.asistentes:
                st.session_state.asistentes.append(txt)
                st.session_state.estados[txt] = True
                st.session_state.asistentes.sort()
            st.session_state.nuevo_atleta = ""

        st.text_input("Nombre del Atleta + ENTER:", key="nuevo_atleta", on_change=registrar)

    # --- AQUÍ APLICAMOS SU FÓRMULA ---
    n_total = len(st.session_state.asistentes)
    sugeridas = calcular_rondas_sugeridas(n_total)

    with col_der:
        st.markdown("<h3 style='text-align: center;'>RONDAS (N)</h3>", unsafe_allow_html=True)
        # El sistema propone el valor basado en la fórmula, pero usted puede cambiarlo
        st.session_state.n_rondas = st.number_input(
            f"Sugeridas: {sugeridas}", 
            min_value=1, 
            max_value=20, 
            value=int(st.session_state.n_rondas) if st.session_state.n_rondas > sugeridas else sugeridas
        )

    st.divider()
    
    num_activos = sum(1 for a in st.session_state.asistentes if st.session_state.estados[a])
    st.subheader(f"📊 ATLETAS: {n_total} | ACTIVOS: {num_activos}")

    for atleta in st.session_state.asistentes:
        c1, c2, c3 = st.columns([5, 1, 1])
        c1.write(f"**{atleta}**")
        if c2.button("✅" if st.session_state.estados[atleta] else "💤", key=f"st_{atleta}"):
            st.session_state.estados[atleta] = not st.session_state.estados[atleta]
            st.rerun()
        if c3.button("🗑️", key=f"del_{atleta}"):
            st.session_state.asistentes.remove(atleta)
            st.rerun()

    if st.button("🚀 SORTEAR E IR A MESAS"):
        st.success(f"Iniciando torneo de {st.session_state.n_rondas} rondas.")
