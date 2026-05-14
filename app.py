import streamlit as st
import math
import random

# --- 1. CONFIGURACIÓN Y ESTADO INICIAL ---
st.set_page_config(layout="wide", page_title="SISTEMA ADEL")

# CSS: Mesas de Gran Tamaño (Diseño ADEL)
st.markdown("""
    <style>
    .mesa-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        margin-bottom: 50px;
        padding: 20px;
    }
    .mesa-centro {
        width: 160px; height: 160px;
        border: 6px solid black;
        background-color: #FFFF00;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        box-shadow: 5px 5px 15px rgba(0,0,0,0.3);
    }
    .adel-text { font-weight: bold; font-size: 32px; color: #003399; margin: 0; line-height: 1; }
    .n-mesa { font-weight: bold; font-size: 48px; color: #CC0000; margin: 0; line-height: 1; }
    .jugador { font-weight: bold; font-size: 20px; text-align: center; color: #000; }
    .norte { margin-bottom: 15px; }
    .sur { margin-top: 15px; }
    .fila-central { display: flex; align-items: center; justify-content: center; width: 100%; }
    .este-oeste { writing-mode: vertical-rl; text-orientation: mixed; padding: 0 25px; }
    </style>
    """, unsafe_allow_html=True)

if 'asistentes' not in st.session_state:
    st.session_state.update({
        'asistentes': [], 'estados': {}, 'juegos_ganados': {}, 'efectividad': {},
        'puntos_contra': {}, 'puntos_favor': {}, 'historial_completo': [],
        'meta_torneo': 100, 'seccion_activa': "INSCRIPCIÓN", 'editando': None
    })

def recalcular_baremo(atleta):
    pf, pc = st.session_state.puntos_favor.get(atleta, 0), st.session_state.puntos_contra.get(atleta, 0)
    st.session_state.efectividad[atleta] = math.log10(max(pf, 1) / max(pc, 1)) + 1

# --- 2. NAVEGACIÓN ---
with st.sidebar:
    st.title("🏆 MENÚ ADEL")
    opcion = st.radio("SECCIÓN:", ["INSCRIPCIÓN", "MESAS", "RESULTADOS", "RANKING"], 
                      index=["INSCRIPCIÓN", "MESAS", "RESULTADOS", "RANKING"].index(st.session_state.seccion_activa))
    st.session_state.seccion_activa = opcion

# --- 3. SECCIÓN: INSCRIPCIÓN ---
if st.session_state.seccion_activa == "INSCRIPCIÓN":
    st.caption("Creado por Poeta")
    st.header("ASOCIACIÓN DE DOMINÓ DEL ESTADO LARA ADEL")
    st.session_state.meta_torneo = st.radio("Meta del encuentro:", [100, 200], horizontal=True)
    
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
            st.session_state.asistentes.sort()
        st.session_state.campo_input = ""

    label_input = f"Corrigiendo a: {st.session_state.editando}" if st.session_state.editando else "Nombre del Atleta + ENTER:"
    st.text_input(label_input, key="campo_input", on_change=procesar_atleta)
    
    # Indicador de cantidad de jugadores
    activos = [n for n in st.session_state.asistentes if st.session_state.estados[n]]
    st.write(f"### ATLETAS: {len(st.session_state.asistentes)} (Activos: {len(activos)})")

    if st.button("🚀 SORTEAR E IR A RONDA 1"):
        if len(activos) >= 4:
            random.shuffle(activos)
            n_jug = (len(activos) // 4) * 4
            st.session_state.historial_completo.append({
                'ronda': 1, 'mesas': [activos[i:i+4] for i in range(0, n_jug, 4)], 'reposo': activos[n_jug:], 'listas': []
            })
            st.session_state.seccion_activa = "MESAS"
            st.rerun()

    for n in st.session_state.asistentes:
        c1, c2, c3, c4 = st.columns([3, 1, 1, 1])
        c1.text(f"• {n}")
        if c2.button("✅" if st.session_state.estados[n] else "❌", key=f"st_{n}"):
            st.session_state.estados[n] = not st.session_state.estados[n]; st.rerun()
        if c3.button("📝", key=f"ed_{n}"): # Botón de editar restaurado
            st.session_state.editando = n; st.rerun()
        if c4.button("🗑️", key=f"del_{n}"):
            st.session_state.asistentes.remove(n); st.rerun()

# --- 4. SECCIÓN: MESAS ---
elif st.session_state.seccion_activa == "MESAS":
    st.header("Organización de la Sala")
    if st.session_state.historial_completo:
        r = st.session_state.historial_completo[-1]
        cols = st.columns(4)
        for i, m in enumerate(r['mesas']):
            with cols[i % 4]:
                st.markdown(f"""
                <div class="mesa-container">
                    <div class="jugador norte">{m[0]}</div>
                    <div class="fila-central">
                        <div class="jugador este-oeste">{m[1]}</div>
                        <div class="mesa-centro"><p class="adel-text">ADEL</p><p class="n-mesa">{i+1}</p></div>
                        <div class="jugador este-oeste">{m[3]}</div>
                    </div>
                    <div class="jugador sur">{m[2]}</div>
                </div>
                """, unsafe_allow_html=True)

# --- 5. SECCIÓN: RESULTADOS ---
elif st.session_state.seccion_activa == "RESULTADOS":
    st.header("Resultados")
    if st.session_state.historial_completo:
        r = st.session_state.historial_completo[-1]
        for i, m in enumerate(r['mesas']):
            if i not in r['listas']:
                with st.expander(f"MESA {i+1}", expanded=True):
                    c1, c2 = st.columns(2)
                    v1 = c1.number_input(f"Pts A-C ({m[0]}/{m[2]}):", 0, 250, key=f"v1_{i}")
                    v2 = c2.number_input(f"Pts B-D ({m[1]}/{m[3]}):", 0, 250, key=f"v2_{i}")
                    if st.button(f"GUARDAR MESA {i+1}", key=f"b_{i}"):
                        for j in [m[0], m[2]]:
                            st.session_state.puntos_favor[j] += v1; st.session_state.puntos_contra[j] += v2
                            if v1 > v2: st.session_state.juegos_ganados[j] += 1
                        for j in [m[1], m[3]]:
                            st.session_state.puntos_favor[j] += v2; st.session_state.puntos_contra[j] += v1
                            if v2 > v1: st.session_state.juegos_ganados[j] += 1
                        for j in m: recalcular_baremo(j)
                        r['listas'].append(i); st.rerun()

# --- 6. SECCIÓN: RANKING ---
elif st.session_state.seccion_activa == "RANKING":
    st.header("Ranking")
    if st.session_state.asistentes:
        t = sorted(st.session_state.asistentes, key=lambda x: (st.session_state.juegos_ganados[x], st.session_state.efectividad[x]), reverse=True)
        st.table([{"Pos": i+1, "Atleta": n, "JJ": st.session_state.juegos_ganados[n], "PF": st.session_state.puntos_favor[n], "PC": st.session_state.puntos_contra[n], "Efec": f"{st.session_state.efectividad[n]:.4f}"} for i, n in enumerate(t)])
