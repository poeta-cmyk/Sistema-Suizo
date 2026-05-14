import streamlit as st
import math
import random

# --- 1. CONFIGURACIÓN Y ESTADO INICIAL ---
st.set_page_config(layout="wide", page_title="SISTEMA ADEL")

if 'asistentes' not in st.session_state:
    st.session_state.update({
        'asistentes': [], 'estados': {}, 'juegos_ganados': {}, 'efectividad': {},
        'puntos_contra': {}, 'puntos_favor': {}, 'historial_completo': [],
        'seccion_activa': "INSCRIPCIÓN", 'editando': None
    })

# CSS: Diseño de mesas ADEL (Gran tamaño)
st.markdown("""
    <style>
    .mesa-container { display: flex; flex-direction: column; align-items: center; margin-bottom: 50px; }
    .mesa-centro {
        width: 160px; height: 160px; border: 6px solid black; background-color: #FFFF00;
        display: flex; flex-direction: column; align-items: center; justify-content: center;
    }
    .adel-text { font-weight: bold; font-size: 32px; color: #003399; margin: 0; }
    .n-mesa { font-weight: bold; font-size: 48px; color: #CC0000; margin: 0; }
    .jugador { font-weight: bold; font-size: 20px; color: #000; text-align: center; }
    .norte { margin-bottom: 10px; } .sur { margin-top: 10px; }
    .fila-central { display: flex; align-items: center; justify-content: center; width: 100%; }
    .este-oeste { writing-mode: vertical-rl; text-orientation: mixed; padding: 0 25px; }
    .reposo-box {
        background-color: #f0f2f6;
        border-left: 5px solid #CC0000;
        padding: 15px;
        margin-top: 20px;
        border-radius: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. NAVEGACIÓN ---
with st.sidebar:
    st.title("🏆 MENÚ ADEL")
    opciones = ["INSCRIPCIÓN", "MESAS", "RESULTADOS", "RANKING"]
    idx_actual = opciones.index(st.session_state.seccion_activa) if st.session_state.seccion_activa in opciones else 0
    st.session_state.seccion_activa = st.radio("SECCIÓN:", opciones, index=idx_actual)

# --- 3. SECCIÓN: INSCRIPCIÓN ---
if st.session_state.seccion_activa == "INSCRIPCIÓN":
    st.header("ASOCIACIÓN DE DOMINÓ DEL ESTADO LARA ADEL SISTEMA SUIZO")
    
    def procesar_atleta():
        nom = st.session_state.campo_input.upper().strip()
        if nom:
            if st.session_state.editando:
                viejo = st.session_state.editando
                if nom != viejo:
                    idx = st.session_state.asistentes.index(viejo)
                    st.session_state.asistentes[idx] = nom
                    for k in ['estados', 'juegos_ganados', 'puntos_contra', 'puntos_favor', 'efectividad']:
                        st.session_state[k][nom] = st.session_state[k].pop(viejo)
                st.session_state.editando = None
            elif nom not in st.session_state.asistentes:
                st.session_state.asistentes.append(nom)
                st.session_state.estados[nom] = True
                st.session_state.juegos_ganados[nom], st.session_state.puntos_favor[nom], st.session_state.puntos_contra[nom], st.session_state.efectividad[nom] = 0, 0, 0, 1.0
        st.session_state.campo_input = ""

    label = f"Corrigiendo a: {st.session_state.editando}" if st.session_state.editando else "Nombre del Atleta + ENTER:"
    st.text_input(label, key="campo_input", on_change=procesar_atleta)
    
    activos = [n for n in st.session_state.asistentes if st.session_state.estados.get(n, False)]
    st.subheader(f"REGISTRADOS: {len(st.session_state.asistentes)} (Activos: {len(activos)})")

    if st.button("🚀 REALIZAR SORTEO Y VER MESAS"):
        if len(activos) >= 4:
            random.shuffle(activos)
            n_jug = (len(activos) // 4) * 4
            st.session_state.historial_completo.append({
                'ronda': len(st.session_state.historial_completo) + 1,
                'mesas': [activos[i:i+4] for i in range(0, n_jug, 4)],
                'reposo': activos[n_jug:],
                'listas': []
            })
            st.session_state.seccion_activa = "MESAS"
            st.rerun()

    for n in sorted(st.session_state.asistentes):
        c1, c2, c3, c4 = st.columns([3, 1, 1, 1])
        c1.text(f"• {n}")
        if c2.button("✅" if st.session_state.estados[n] else "❌", key=f"st_{n}"):
            st.session_state.estados[n] = not st.session_state.estados[n]; st.rerun()
        if c3.button("📝", key=f"ed_{n}"):
            st.session_state.editando = n; st.rerun()
        if c4.button("🗑️", key=f"del_{n}"):
            st.session_state.asistentes.remove(n); st.rerun()

# --- 4. SECCIÓN: MESAS (Reposo simplificado) ---
elif st.session_state.seccion_activa == "MESAS":
    st.header("Organización de la Sala")
    if st.session_state.historial_completo:
        r = st.session_state.historial_completo[-1]
        st.subheader(f"Distribución de la RONDA {r['ronda']}")
        
        cols = st.columns(4)
        for i, m in enumerate(r['mesas']):
            with cols[i % 4]:
                st.markdown(f"""
                <div class="mesa-container">
