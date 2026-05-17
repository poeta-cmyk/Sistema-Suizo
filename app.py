import streamlit as st
import math
import random

# --- 1. CONFIGURACIÓN ---
st.set_page_config(
    layout="wide", 
    page_title="SISTEMA ADEL"
)

# Inicialización segura de variables en session_state
if 'asistentes' not in st.session_state:
    st.session_state.asistentes = []
if 'historial_completo' not in st.session_state:
    st.session_state.historial_completo = []

reg_keys = [
    'estados',
    'juegos_ganados',
    'puntos_favor',
    'puntos_contra',
    'efectividad'
]

for k in reg_keys:
    if k not in st.session_state:
        st.session_state[k] = {}

if 'seccion_activa' not in st.session_state:
    st.session_state.seccion_activa = "INSCRIPCIÓN"
if 'editando' not in st.session_state:
    st.session_state.editando = None

# --- CSS: MESAS CUADRADAS SIMÉTRICAS EN SALA ---
st.markdown("""
    <style>
    .mesa-container {
        display: flex; 
        flex-direction: column; 
        align-items: center; 
        margin-bottom: 40px; 
    }
    .mesa-centro {
        width: 160px !important; 
        height: 160px !important; 
        border: 6px solid black; 
        background-color: #FFFF00;
        display: flex; 
        flex-direction: column; 
        align-items: center; 
        justify-content: center;
        flex-shrink: 0;
    }
    .adel-text { 
        font-weight: bold; 
        font-size: 32px; 
        color: #003399; 
        margin: 0; 
    }
    .n-mesa { 
        font-weight: bold; 
        font-size: 48px; 
        color: #CC0000; 
        margin: 0; 
    }
    .jugador { 
        font-weight: bold; 
        font-size: 20px; 
        color: #000; 
        text-align: center; 
    }
    .norte { margin-bottom: 12px; } 
    .sur { margin-top: 12px; }
    .fila-central { 
        display: flex; 
        align-items: center; 
        justify-content: center; 
        width: 100%; 
        gap: 10px;
    }
    .este-oeste { 
        writing-mode: vertical-rl; 
        text-orientation: mixed; 
        padding: 5px 0; 
        min-width: 80px; 
        text-align: center;
    }
    .reposo-box {
        background-color: #f0f2f6; 
        border-left: 5px solid #CC0000;
        padding: 15px; 
        margin-top: 20px; 
        border-radius: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

def recalcular_baremo(atleta):
    pf = st.session_state.puntos_favor.get(atleta, 0)
    pc = st.session_state.puntos_contra.get(atleta, 0)
    ratio = max(pf, 1) / max(pc, 1)
    st.session_state.efectividad[atleta] = math.log10(ratio) + 1

# --- 2. NAVEGACIÓN LATERAL ---
with st.sidebar:
    st.title("🏆 MENÚ ADEL")
    opc = ["INSCRIPCIÓN", "MESAS", "RESULTADOS", "RANKING"]
    act = st.session_state.seccion_activa
    idx = opc.index(act) if act in opc else 0
    st.session_state.seccion_activa = st.radio("SECCIÓN:", opc, index=idx)

# --- 3. SECCIÓN: INSCRIPCIÓN ---
if st.session_state.seccion_activa == "INSCRIPCIÓN":
    st.markdown(
        "<h2 style='text-align:center;'>SISTEMA SUIZO ADEL</h2>", 
        unsafe_allow_html=True
    )
    
    st.radio(
        "Meta del encuentro:", 
        [100, 200], 
        index=1, 
        horizontal=True
    )
    
    def procesar_atleta():
        nom = st.session_state.campo_input.upper().strip()
        if nom:
            if st.session_state.editando:
                v = st.session_state.editando.upper().strip()
                if nom != v and v in st.session_state.asistentes:
                    i = st.session_state.asistentes.index(v)
                    st.session_state.asistentes[i] = nom
                    for reg in reg_keys:
                        if v in st.session_state[reg]:
                            st.session_state[reg][nom] = st.session_state[reg].pop(v)
                st.session_state.editando = None
            elif nom not in st.session_state.asistentes:
                st.session_state.asistentes.append(nom)
                st.session_state.estados[nom] = True
                st.session_state.juegos_ganados[nom] = 0
                st.session_state.puntos_favor[nom] = 0
                st.session_state.puntos_contra[nom] = 0
                st.session_state.efectividad[nom] = 1.0
        st.session_state.campo_input = ""

    ed = st.session_state.editando
    msg = f"Corrigiendo a: {ed}" if ed else "Nombre del Atleta + ENTER:"
    st.text_input(msg, key="campo_input", on_change=procesar_atleta)
    
    at_act = [
        x for x in st.session_state.asistentes 
        if st.session_state.estados.get(x, False)
    ]
    
    st.subheader(
        f"INSCRITOS: {len(st.session_state.asistentes)} | "
        f"ACTIVOS: {len(at_act)}"
    )

    if st.button("🚀 GENERAR SORTEO DE SALA"):
        if len(at_act) >= 4:
            random.shuffle(at_act)
            lim = (len(at_act) // 4) * 4
            st.session_state.historial_completo.append({
                'ronda': len(st.
