import streamlit as st
import random

st.set_page_config(layout="wide", page_title="SISTEMA ADEL")

# --- MEMORIA DEL TORNEO ---
if 'asistentes' not in st.session_state: st.session_state.asistentes = []
if 'historial_completo' not in st.session_state: st.session_state.historial_completo = []

keys = ['estados', 'juegos_ganados', 'puntos_favor', 'puntos_contra', 'efectividad']
for k in keys:
    if k not in st.session_state: st.session_state[k] = {}

if 'seccion_activa' not in st.session_state: st.session_state.seccion_activa = "INSCRIPCIÓN"
if 'editando' not in st.session_state: st.session_state.editando = None

# --- ESTILOS CSS ---
st.markdown("""
    <style>
    .mesa-container { display: inline-flex; flex-direction: column; align-items: center; justify-content: center; width: 260px!important; height: 260px!important; margin: 20px auto; }
    .mesa-centro { width: 110px!important; height: 110px!important; border: 5px solid black; background-color: #FFFF00; display: flex; flex-direction: column; align-items: center; justify-content: center; flex-shrink: 0; }
    .adel-text { font-weight: bold; font-size: 22px; color: #003399; margin: 0; line-height: 1; }
    .n-mesa { font-weight: bold; font-size: 38px; color: #CC0000; margin: 0; line-height: 1; }
    .jugador { font-weight: bold; font-size: 16px; color: #000; text-align: center; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    .norte { width: 100%; margin-bottom: 8px; } .sur { width: 100%; margin-top: 8px; }
    .fila-central { display: flex; align-items: center; justify-content: center; width: 100%; height: 110px; gap: 5px; }
    .este-oeste { width: 40px!important; max-width: 40px!important; writing-mode: vertical-rl!important; text-orientation: mixed!important; transform: rotate(180deg); padding: 4px 0; }
    .reposo-box { background-color: #f0f2f6; border-left: 6px solid #CC0000; padding: 15px; margin-top: 25px; border-radius: 4px; }
    .bye-automatico { background-color: #e8f4fd; border-left: 6px solid #003399; padding: 12px; margin-bottom: 20px; border-radius: 4px; }
    </style>
    """, unsafe_allow_html=True)

# --- NAVEGACIÓN ---
with st.sidebar:
    st.title("🏆 MENÚ ADEL")
    opc = ["INSCRIPCIÓN", "MESAS", "RESULTADOS", "RANKING"]
    st.session_state.seccion_activa = st.radio("SECCIÓN:", opc, index=opc.index(st.session_state.seccion_activa))

# --- INSCRIPCIÓN ---
if st.session_state.seccion_activa == "INSCRIPCIÓN":
    st.markdown("<h2 style='text-align:center;'>SISTEMA SUIZO ADEL</h2>", unsafe_allow_html=True)
    meta = st.radio("Meta del encuentro:", [100, 200], index=1, horizontal=True)
    
    def proc():
        nom = st.session_state.c_in.upper().strip()
        if nom:
            if st.session_state.editando:
                v = st.session_state.editando.upper().strip()
                if nom != v and v in st.session_state.asistentes:
                    st.session_state.asistentes[st.session_state.asistentes.index(v)] = nom
                    for rk in keys:
                        if v in st.session_state[rk]: st.session_state[rk][nom] = st.session_state[rk].pop(v)
                st.session_state.editando = None
            elif nom not in st.session_state.asistentes:
                st.session_state.asistentes.append(nom)
                st.session_state.estados[nom], st.session_state.juegos_ganados[nom], st.session_state.puntos_favor[nom], st.session_state.puntos_contra[nom], st.session_state.efectividad[nom] = True, 0, 0, 0, 1.0
        st.session_state.c_in = ""

    ed = st.session_state.editando
    st.text_input(f"Corrigiendo a: {ed}" if ed else "Nombre del Atleta + ENTER:", key="c_in", on_change=proc)
    
    at_act = [x for x in st.session_state.asistentes if st.session_state.estados.get(x, False)]
    st.subheader(f"INSCRITOS: {len(st.session_state.asistentes)} | ACTIVOS: {len(at_act)}")

    if st.button("🚀 GENERAR SORTEO DE SALA"):
        if len(at_act) >= 4:
            random.shuffle(at_act)
            lim = (len(at_act) // 4) * 4
            mesas = [at_act[i:i+4] for i in range(0, lim, 4)]
            reposo = at_act[lim:]
            
            # Registro inmediato del Bye
            for jb in reposo:
                st.session_state.juegos_ganados[jb] = st.session_state.juegos_ganados.get(jb, 0) + 1
                st.session_state.puntos_favor[jb] = st.session_state.puntos_favor.get(jb, 0) + (meta // 2)

            st.session_state.historial_completo.append({'ronda': len(st.session_state.historial_completo) + 1, 'mesas': mesas, 'reposo': reposo, 'listas': [], 'meta': meta})
            st.session_state.seccion_activa, st.session_state.editando = "MESAS", None
            st.rerun()
        else: st.error("Mínimo 4 atletas activos.")

    for n in sorted(st.session_state.asistentes):
        c1, c2, c3, c4 = st.columns([3, 1, 1, 1])
        c1.text(f"• {n}")
        if c2.button("✅" if st.session_state.estados[n] else "❌", key=f"st_{n}"):
            st.session_state.estados[n] = not st.session_state.estados[n]; st.rerun()
        if c3.button("📝", key=f"ed_{n}"): st.session_state.editando = n; st.rerun()
        if c4.button("🗑️", key=f"del_{n}"):
            st.session_state.asistentes.remove(n)
            for rk in keys: st.session_state[rk].pop(n, None)
            st.rerun()

# --- MESAS ---
elif st.session_state.seccion_activa == "MESAS":
    st.header("Organización de la Sala")
    if st.session_state.historial_completo:
        r = st.session_state.historial_completo[-1]
        st.subheader(f"Ronda Actual: {r['ronda']}")
        cols = st.columns(4)
        for i, m in enumerate(r['mesas']):
            with cols[i % 4]:
                st.markdown(f"""
                <div style='text-align: center;'>
                    <div class="mesa-container">
                        <div class="jugador norte">{m[0]}</div>
                        <div class="fila-central">
                            <div class="jugador este-oeste">{m[1]}</div>
                            <div class="mesa-centro"><p class="adel-text">ADEL</p><p class="n-mesa">{i+1}</p></div>
                            <div class="jugador este-oeste">{m[3]}</div>
                        </div>
                        <div class="jugador sur">{m[2]}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        if r.get('reposo'): st.markdown(f'<div class="reposo-box"><h4>💤 EN REPOSO:</h4><p><b>{", ".join(r["reposo"])}</b></p></div>', unsafe_allow_html=True)
    else: st.info("Sorteo vacío. Vaya a Inscripción.")

# --- RESULTADOS ---
elif st.session_state.seccion_activa == "RESULTADOS":
    st.header("Carga de Puntuaciones de Sala")
    if st.session_state.historial_completo:
        r = st.session_state.historial_completo[-1]
        pts_b = r.get('meta', 200) // 2
        
        if r.get('reposo'):
            for jb in r['reposo']:
                st.markdown(f'<div class="bye-automatico">⚙️ <b>BYE AUTOMÁTICO:</b> El atleta <b>{jb}</b> gana <b>1 JJ</b> con marcador de <b>{pts_b} a 0</b>.</div>', unsafe_allow_html=True)
                
        pendientes = [idx for idx, _ in enumerate(r['mesas']) if idx not in r['listas']]
        if pendientes:
            for i in pendientes:
                m = r['mesas'][i]
                with st.expander(f"MESA {i+1}", expanded=True):
                    c1, c2 = st.columns(2)
                    v1 = c1.number_input(f"Puntos A-C ({m[0]} / {m[2]}):", 0, 250, key=f"v1_{i}")
                    v2 = c2.number_input(f"
