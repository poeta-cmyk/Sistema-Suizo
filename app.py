import streamlit as st
import math
import random

# --- 1. CONFIGURACIÓN INICIAL ---
st.set_page_config(
    layout="wide", 
    page_title="SISTEMA ADEL"
)

# Memoria del torneo
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

# --- ESTILOS CSS: MESAS CUADRADAS CON LATERALES VERTICALES ---
st.markdown("""
    <style>
    .mesa-container {
        display: inline-flex; 
        flex-direction: column; 
        align-items: center; 
        justify-content: center;
        width: 260px !important;
        height: 260px !important;
        margin: 20px auto;
    }
    .mesa-centro {
        width: 110px !important; 
        height: 110px !important; 
        border: 5px solid black; 
        background-color: #FFFF00;
        display: flex; 
        flex-direction: column; 
        align-items: center; 
        justify-content: center;
        flex-shrink: 0;
    }
    .adel-text { 
        font-weight: bold; 
        font-size: 22px; 
        color: #003399; 
        margin: 0; 
        line-height: 1;
    }
    .n-mesa { 
        font-weight: bold; 
        font-size: 38px; 
        color: #CC0000; 
        margin: 0; 
        line-height: 1;
    }
    .jugador { 
        font-weight: bold; 
        font-size: 16px; 
        color: #000; 
        text-align: center;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }
    .norte { 
        width: 100%;
        margin-bottom: 8px; 
    } 
    .sur { 
        width: 100%;
        margin-top: 8px; 
    }
    .fila-central { 
        display: flex; 
        align-items: center; 
        justify-content: center; 
        width: 100%;
        height: 110px;
        gap: 5px;
    }
    .este-oeste { 
        width: 40px !important;
        max-width: 40px !important;
        writing-mode: vertical-rl !important;
        text-orientation: mixed !important;
        transform: rotate(180deg);
        padding: 4px 0;
    }
    .reposo-box {
        background-color: #f0f2f6; 
        border-left: 6px solid #CC0000;
        padding: 15px; 
        margin-top: 25px; 
        border-radius: 4px;
    }
    .bye-automatico {
        background-color: #e8f4fd; 
        border-left: 6px solid #003399;
        padding: 12px; 
        margin-bottom: 20px; 
        border-radius: 4px;
    }
    </style>
    """, unsafe_allow_html=True)

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
    
    meta = st.radio(
        "Meta del encuentro:", 
        [100, 200], 
        index=1, 
        horizontal=True
    )
    
    def procesar_atleta():
        raw_in = st.session_state.campo_input
        nom = raw_in.upper().strip()
        if nom:
            if st.session_state.editando:
                v = st.session_state.editando.upper().strip()
                if nom != v and v in st.session_state.asistentes:
                    pos = st.session_state.asistentes.index(v)
                    st.session_state.asistentes[pos] = nom
                    for rk in reg_keys:
                        if v in st.session_state[rk]:
                            info = st.session_state[rk].pop(v)
                            st.session_state[rk][nom] = info
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
            
            # Bonificación automática inmediata al jugador en reposo (Bye)
            pts_bye = meta // 2
            for j_bye in lista_reposo:
                st.session_state.juegos_ganados[j_bye] = st.session_state.juegos_ganados.get(j_bye, 0) + 1
                st.session_state.puntos_favor[j_bye] = st.session_state.puntos_favor.get(j_bye, 0) + pts_bye
                st.session_state.puntos_contra[j_bye] = st.session_state.puntos_contra.get(j_bye, 0) + 0

            nueva_ronda = {
                'ronda': num_ronda,
                'mesas': lista_mesas,
                'reposo': lista_reposo,
                'listas': [],
                'meta_actual': meta
            }
            
            st.session_state.historial_completo.append(nueva_ronda)
            st.session_state.seccion_activa = "MESAS"
            st.rerun()
        else:
            st.error("Mínimo se requieren 4 atletas activos.")

    for n in sorted(st.session_state.asistentes):
        c1, c2, c3, c4 = st.columns([3, 1, 1, 1])
        c1.text(f"• {n}")
        
        txt_est = "✅" if st.session_
    
