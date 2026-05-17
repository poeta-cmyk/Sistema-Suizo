import streamlit as st
import math
import random

# --- 1. CONFIGURACIÓN INICIAL ---
st.set_page_config(
    layout="wide", 
    page_title="SISTEMA ADEL"
)

# Inicialización segura de memoria
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

# --- ESTILOS CSS PARA LAS MESAS ---
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
    v_favor = max(pf, 1)
    v_contra = max(pc, 1)
    ratio = v_favor / v_contra
    log_ratio = math.log10(ratio)
    st.session_state.efectividad[atleta] = log_ratio + 1

# --- 2. NAVEGACIÓN ---
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
        raw_input = st.session_state.campo_input
        nom = raw_input.upper().strip()
        if nom:
            if st.session_state.editando:
                v = st.session_state.editando.upper().strip()
                if nom != v and v in st.session_state.asistentes:
                    pos = st.session_state.asistentes.index(v)
                    st.session_state.asistentes[pos] = nom
                    for reg in reg_keys:
                        if v in st.session_state[reg]:
                            info = st.session_state[reg].pop(v)
                            st.session_state[reg][nom] = info
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
    
    total_ins = len(st.session_state.asistentes)
    total_act = len(at_act)
    st.subheader(f"INSCRITOS: {total_ins} | ACTIVOS: {total_act}")

    if st.button("🚀 GENERAR SORTEO DE SALA"):
        if total_act >= 4:
            random.shuffle(at_act)
            lim = (total_act // 4) * 4
            
            lista_mesas = []
            for i in range(0, lim, 4):
                grupo = at_act[i:i+4]
                lista_mesas.append(grupo)
                
            lista_reposo = at_act[lim:]
            num_ronda = len(st.session_state.historial_completo) + 1
            
            nueva_ronda = {
                'ronda': num_ronda,
                'mesas': lista_mesas,
                'reposo': lista_reposo,
                'listas': []
            }
            
            st.session_state.historial_completo.append(nueva_ronda)
            st.session_state.seccion_activa = "MESAS"
            st.rerun()
        else:
            st.error("Mínimo se requieren 4 atletas activos para abrir sala.")

    for n in sorted(st.session_state.asistentes):
        c1, c2, c3, c4 = st.columns([3, 1, 1, 1])
        c1.text(f"• {n}")
        
        txt_est = "✅" if st.session_state.estados[n] else "❌"
        if c2.button(txt_est, key=f"st_{n}"):
            st.session_
