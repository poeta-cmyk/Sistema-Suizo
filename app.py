import streamlit as st
import math
import random

# --- 1. CONFIGURACIÓN E INICIALIZACIÓN ---
st.set_page_config(layout="wide", page_title="SISTEMA ADEL")

if 'asistentes' not in st.session_state:
    st.session_state.update({
        'asistentes': [], 'estados': {}, 'juegos_ganados': {}, 'efectividad': {},
        'puntos_contra': {}, 'puntos_favor': {}, 'historial_completo': [],
        'seccion_activa': "INSCRIPCIÓN", 'editando': None, 'meta_encuentro': 200
    })

# CSS: Diseño Institucional ADEL
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
        background-color: #f0f2f6; border-left: 5px solid #CC0000;
        padding: 15px; margin-top: 20px; border-radius: 5px;
    }
    .victoria-reposo {
        color: #155724; background-color: #d4edda; border: 1px solid #c3e6cb;
        padding: 10px; border-radius: 5px; font-weight: bold; margin-bottom: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

def recalcular_baremo(atleta):
    pf = st.session_state.puntos_favor.get(atleta, 0)
    pc = st.session_state.puntos_contra.get(atleta, 0)
    st.session_state.efectividad[atleta] = math.log10(max(pf, 1) / max(pc, 1)) + 1

# --- 2. NAVEGACIÓN ---
with st.sidebar:
    st.title("🏆 MENÚ ADEL")
    opciones = ["INSCRIPCIÓN", "MESAS", "RESULTADOS", "RANKING"]
    idx_actual = opciones.index(st.session_state.seccion_activa) if st.session_state.seccion_activa in opciones else 0
    st.session_state.seccion_activa = st.radio("SECCIÓN:", opciones, index=idx_actual)

# --- 3. SECCIÓN: INSCRIPCIÓN ---
if st.session_state.seccion_activa == "INSCRIPCIÓN":
    st.header("ASOCIACIÓN DE DOMINÓ DEL ESTADO LARA ADEL")
    
    # Selector de Meta
    st.session_state.meta_encuentro = st.radio("Meta del encuentro:", [100, 200], index=1 if st.session_state.meta_encuentro == 200 else 0, horizontal=True)

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

    st.text_input("Nombre del Atleta + ENTER:", key="campo_input", on_change=procesar_atleta)
    activos = [n for n in st.session_state.asistentes if st.session_state.estados.get(n, False)]
    
    if st.button("🚀 REALIZAR SORTEO E IR A MESAS"):
        if len(activos) >= 4:
            random.shuffle(activos)
            n_jug = (len(activos) // 4) * 4
            st.session_state.historial_completo.append({
                'ronda': len(st.session_state.historial_completo) + 1,
                'mesas': [activos[i:i+4] for i in range(0, n_jug, 4)],
                'reposo': activos[n_jug:],
                'listas': [],
                'reposo_procesado': False
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

# --- 4. SECCIÓN: MESAS ---
elif st.session_state.seccion_activa == "MESAS":
    st.header("Organización de la Sala")
    if st.session_state.historial_completo:
        r = st.session_state.historial_completo[-1]
        cols = st.columns(4)
        for i, m in enumerate(r['mesas']):
            with cols[i % 4]:
                st.markdown(f"""<div class="mesa-container"><div class="jugador norte">{m[0]}</div><div class="fila-central"><div class="jugador este-oeste">{m[1]}</div><div class="mesa-centro"><p class="adel-text">ADEL</p><p class="n-mesa">{i+1}</p></div><div class="jugador este-oeste">{m[3]}</div></div><div class="jugador sur">{m[2]}</div></div>""", unsafe_allow_html=True)
        if r.get('reposo'):
            st.markdown(f'<div class="reposo-box"><h3 style="color: #CC0000; margin:0;">💤 EN REPOSO:</h3><p style="font-size: 20px; font-weight: bold;">{", ".join(r["reposo"])}</p></div>', unsafe_allow_html=True)

# --- 5. SECCIÓN: RESULTADOS (Con Victoria por Reposo Calculada) ---
elif st.session_state.seccion_activa == "RESULTADOS":
    st.header("Carga de Resultados")
    if st.session_state.historial_completo:
        r = st.session_state.historial_completo[-1]
        pts_v = st.session_state.meta_encuentro // 2 # Regla de la Mitad

        if r.get('reposo') and not r.get('reposo_procesado'):
            for p in r['reposo']:
                st.session_state.juegos_ganados[p] += 1
                st.session_state.puntos_favor[p] += pts_v
                recalcular_baremo(p)
            r['reposo_procesado'] = True

        if r.get('reposo'):
            for p in r['reposo']:
                st.markdown(f'<div class="victoria-reposo">🏆 {p}: Gana por Reposo ({pts_v} a 0)</div>', unsafe_allow_html=True)
            st.divider()

        for i, m in enumerate(r['mesas']):
            if i not in r['listas']:
                with st.expander(f"MESA {i+1}", expanded=True):
                    c1, c2 = st.columns(2)
                    v1 = c1.number_input(f"Pareja A-C ({m[0]}/{m[2]}):", 0, 250, key=f"v1_{i}")
                    v2 = c2.number_input(f"Pareja B-D ({m[1]}/{m[3]}):", 0, 250, key=f"v2_{i}")
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
    st.header("Ranking General")
    if st.session_state.asistentes
