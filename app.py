import streamlit as st
import math
import random

# --- 1. CONFIGURACIÓN ---
st.set_page_config(
    layout="wide", 
    page_title="SISTEMA ADEL"
)

# Inicialización segura de variables
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
    
    # Meta del encuentro ajustable a 100 o 200 puntos
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
                v = st.session_state.editando
                if nom != v:
                    i = st.session_state.asistentes.index(v)
                    st.session_state.asistentes[i] = nom
                    for reg in reg_keys:
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

    # Botón que genera el sorteo y salta automáticamente a MESAS
    if st.button("🚀 GENERAR SORTEO DE SALA"):
        if len(at_act) >= 4:
            random.shuffle(at_act)
            lim = (len(at_act) // 4) * 4
            st.session_state.historial_completo.append({
                'ronda': len(st.session_state.historial_completo) + 1,
                'mesas': [at_act[i:i+4] for i in range(0, lim, 4)],
                'reposo': at_act[lim:],
                'listas': []
            })
            st.session_state.seccion_activa = "MESAS"
            st.rerun()
        else:
            st.error("Mínimo se requieren 4 atletas activos para abrir sala.")

    # Listado con controles individuales de arbitraje
    for n in sorted(st.session_state.asistentes):
        c1, c2, c3, c4 = st.columns([3, 1, 1, 1])
        c1.text(f"• {n}")
        
        # Activar/Desactivar para la ronda (Asistencia)
        if c2.button("✅" if st.session_state.estados[n] else "❌", key=f"st_{n}"):
            st.session_state.estados[n] = not st.session_state.estados[n]
            st.rerun()
            
        # Editar nombre por error ortográfico
        if c3.button("📝", key=f"ed_{n}"):
            st.session_state.editando = n
            st.rerun()
            
        # Eliminar definitivamente del torneo (Sanción o Retiro)
        if c4.button("🗑️", key=f"del_{n}"):
            st.session_state.asistentes.remove(n)
            for reg in reg_keys:
                st.session_state[reg].pop(n, None)
            st.rerun()

# --- Marcadores de posición temporales para no romper el programa ---
elif st.session_state.seccion_activa == "MESAS":
    st.info("Estructura de MESAS en pausa hasta consolidar Inscripción.")
elif st.session_state.seccion_activa == "RESULTADOS":
    st.info("Estructura de RESULTADOS en pausa hasta consolidar Inscripción.")
elif st.session_state.seccion_activa == "RANKING":
    st.info("Estructura de RANKING en pausa hasta consolidar Inscripción.")
