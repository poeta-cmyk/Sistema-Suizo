import streamlit as st
import math
import random

# --- 1. CONFIGURACIÓN INICIAL ---
st.set_page_config(layout="wide", page_title="SISTEMA ADEL")

# Memoria interna del torneo
if 'asistentes' not in st.session_state:
    st.session_state.asistentes = []
if 'historial_completo' not in st.session_state:
    st.session_state.historial_completo = []
if 'meta_puntos' not in st.session_state:
    st.session_state.meta_puntos = 200

reg_keys = ['estados', 'juegos_ganados', 'puntos_favor', 'puntos_contra', 'efectividad']
for k in reg_keys:
    if k not in st.session_state:
        st.session_state[k] = {}

if 'seccion_activa' not in st.session_state:
    st.session_state.seccion_activa = "INSCRIPCIÓN"
if 'editando' not in st.session_state:
    st.session_state.editando = None

# --- 2. ESTILOS CSS ORIGINALES ---
st.markdown("""
    <style>
    .mesa-container {
        display: inline-flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        width: 260px!important;
        height: 260px!important;
        margin: 20px auto;
    }
    .mesa-centro {
        width: 110px!important;
        height: 110px!important;
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
    .norte { width: 100%; margin-bottom: 8px; }
    .sur { width: 100%; margin-top: 8px; }
    .fila-central {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 100%;
        height: 110px;
        gap: 5px;
    }
    .este-oeste {
        width: 40px!important;
        max-width: 40px!important;
        writing-mode: vertical-rl!important;
        text-orientation: mixed!important;
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
    .bye-oficial {
        background-color: #e8f4fd;
        border-left: 6px solid #003399;
        padding: 15px;
        margin-bottom: 20px;
        border-radius: 4px;
    }
    </style>
    """, unsafe_allow_html=True)

def recalcular_baremo(atleta):
    pf = st.session_state.puntos_favor.get(atleta, 0)
    pc = st.session_state.puntos_contra.get(atleta, 0)
    st.session_state.efectividad[atleta] = math.log10(max(pf, 1) / max(pc, 1)) + 1

# --- 3. NAVEGACIÓN ---
with st.sidebar:
    st.title("🏆 MENÚ ADEL")
    opc = ["INSCRIPCIÓN", "MESAS", "RESULTADOS", "RANKING"]
    st.session_state.seccion_activa = st.radio("SECCIÓN:", opc, index=opc.index(st.session_state.seccion_activa))

# --- 4. SECCIÓN: INSCRIPCIÓN ---
if st.session_state.seccion_activa == "INSCRIPCIÓN":
    st.markdown("<h2 style='text-align:center;'>SISTEMA SUIZO ADEL</h2>", unsafe_allow_html=True)
    
    st.session_state.meta_puntos = st.radio(
        "Meta del encuentro:", 
        [100, 200], 
        index=0 if st.session_state.meta_puntos == 100 else 1, 
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
                            st.session_state[rk][nom] = st.session_state[rk].pop(v)
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
    st.text_input(
        f"Corrigiendo a: {ed}" if ed else "Nombre del Atleta + ENTER:", 
        key="campo_input", 
        on_change=procesar_atleta
    )
    
    at_act = [x for x in st.session_state.asistentes if st.session_state.estados.get(x, False)]
    st.subheader(f"INSCRITOS: {len(st.session_state.asistentes)} | ACTIVOS: {len(at_act)}")

    if st.button("🚀 GENERAR SORTEO DE SALA"):
        if len(at_act) >= 4:
            random.shuffle(at_act)
            lim = (len(at_act) // 4) * 4
            lista_mesas = [at_act[i:i+4] for i in range(0, lim, 4)]
            lista_reposo = at_act[lim:]
            
            # EJECUCIÓN ARBITRAL: Marcador de Meta Completa vs Mitad de la Meta para el Bye
            meta_actual = st.session_state.meta_puntos
            mitad_actual = meta_actual // 2
            
            for j_bye in lista_reposo:
                st.session_state.juegos_ganados[j_bye] = st.session_state.juegos_ganados.get(j_bye, 0) + 1
                st.session_state.puntos_favor[j_bye] = st.session_state.puntos_favor.get(j_bye, 0) + meta_actual
                st.session_state.puntos_contra[j_bye] = st.session_state.puntos_contra.get(j_bye, 0) + mitad_actual
                recalcular_baremo(j_bye)
            
            st.session_state.historial_completo.append({
                'ronda': len(st.session_state.historial_completo) + 1,
                'mesas': lista_mesas,
                'reposo': lista_reposo,
                'listas': []
            })
            st.session_state.seccion_activa = "MESAS"
            st.rerun()
        else:
            st.error("Mínimo se requieren 4 atletas activos.")

    for n in sorted(st.session_state.asistentes):
        c1, c2, c3, c4 = st.columns([3, 1, 1, 1])
        c1.text(f"• {n}")
        if c2.button("✅" if st.session_state.estados[n] else "❌", key=f"st_{n}"):
            st.session_state.estados[n] = not st.session_state.estados[n]
            st.rerun()
        if c3.button("📝", key=f"ed_{n}"):
            st.session_state.editando = n
            st.rerun()
        if c4.button("🗑️", key=f"del_{n}"):
            st.session_state.asistentes.remove(n)
            for rk in reg_keys:
                st.session_state[rk].pop(n, None)
            st.rerun()

# --- 5. SECCIÓN: MESAS ---
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
        if r.get('reposo'):
            st.markdown(f'<div class="reposo-box"><h4>💤 EN REPOSO EN ESTA RONDA:</h4><p><b>{", ".join(r["reposo"])}</b></p></div>', unsafe_allow_html=True)
    else:
        st.info("La sala está vacía. Genere el sorteo en Inscripción.")

# --- 6. SECCIÓN: RESULTADOS ---
elif st.session_state.seccion_activa == "RESULTADOS":
    st.header("Carga de Puntuaciones de Sala")
    if st.session_state.historial_completo:
        r = st.session_state.historial_completo[-1]
        
        # VISUALIZACIÓN EN PANTALLA: Reporte explícito del marcador del jugador en reposo
        if r.get('reposo'):
            meta_actual = st.session_state.meta_puntos
            mitad_actual = meta_actual // 2
            for jb in r['reposo']:
                st.markdown(f"""
                <div class="bye-oficial">
                    🎯 <b>REPORTE ARBITRAL DE REPOSO (BYE):</b><br>
                    El atleta <b>{jb}</b> gana esta ronda de forma automática. <br>
                    Marcador asignado: <b>{meta_actual}</b> puntos a favor / <b>{mitad_actual}</b> puntos en contra. (+1 Juego Ganado)
                </div>
                """, unsafe_allow_html=True)
                
        pendientes = [idx for idx, _ in enumerate(r['mesas']) if idx not in r['listas']]
        if pendientes:
            for i in pendientes:
                m = r['mesas'][i]
                with st.expander(f"MESA {i+1}", expanded=True):
                    c1, c2 = st.columns(2)
                    v1 = c1.number_input(f"Puntos A-C ({m[0]} / {m[2]}):", 0, 250, key=f"v1_{i}")
                    v2 = c2.number_input(f"Puntos B-D ({m[1]} / {m[3]}):", 0, 250, key=f"v2_{i}")
                    if st.button(f"Guardar Resultados Mesa {i+1}", key=f"b_{i}"):
                        for j in [m[0], m[2]]:
                            st.session_state.puntos_favor[j] = st.session_state.puntos_favor.get(j, 0) + v1
                            st.session_state.puntos_contra[j] = st.session_state.puntos_contra.get(j, 0) + v2
                            if v1 > v2:
                                st.session_state.juegos_ganados[j] = st.session_state.juegos_ganados.get(j, 0) + 1
                        for j in [m[1], m[3]]:
                            st.session_state.puntos_favor[j] = st.session_state.puntos_favor.get(j, 0) + v2
                            st.session_state.puntos_contra[j] = st.session_state.puntos_contra.get(j, 0) + v1
                            if v2 > v1:
                                st.session_state.juegos_ganados[j] = st.session_state.juegos_ganados.get(j, 0) + 1
                        for j in m:
                            recalcular_baremo(j)
                        r['listas'].append(i)
                        st.rerun()
        else:
            st.success(f"¡Ronda {r['ronda']} finalizada!")
    else:
        st.info("La sala está vacía. Genere el sorteo en Inscripción.")

# --- 7. SECCIÓN: RANKING ---
elif st.session_state.seccion_activa == "RANKING":
    st.info("Módulo de RANKING en espera.")
