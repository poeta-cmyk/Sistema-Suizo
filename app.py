import streamlit as st
import math
import random

# --- 1. CONFIGURACIÓN ---
st.set_page_config(
    layout="wide", 
    page_title="SISTEMA ADEL"
)

# Inicialización segura de listas
if 'asistentes' not in st.session_state:
    st.session_state.asistentes = []
if 'historial_completo' not in st.session_state:
    st.session_state.historial_completo = []

# Variables de atletas en líneas independientes
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

# --- CSS: MESAS CUADRADAS SIMÉTRICAS ---
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

# --- 3. SECCIÓN: INSCRIPCIÓN (100% INTACTA) ---
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
            st.error("Mínimo 4 atletas activos.")

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
            st.session_state.estados.pop(n, None)
            st.rerun()

# --- 4. SECCIÓN: MESAS (DISEÑO PERFECTAMENTE CUADRADO) ---
elif st.session_state.seccion_activa == "MESAS":
    st.header("Organización de la Sala")
    if st.session_state.historial_completo:
        r = st.session_state.historial_completo[-1]
        st.subheader(f"Ronda Actual: {r['ronda']}")
        cols = st.columns(4)
        for i, m in enumerate(r['mesas']):
            with cols[i % 4]:
                st.markdown(f"""
                <div class="mesa-container">
                    <div class="jugador norte">{m[0]}</div>
                    <div class="fila-central">
                        <div class="jugador este-oeste">{m[1]}</div>
                        <div class="mesa-centro">
                            <p class="adel-text">ADEL</p>
                            <p class="n-mesa">{i+1}</p>
                        </div>
                        <div class="jugador este-oeste">{m[3]}</div>
                    </div>
                    <div class="jugador sur">{m[2]}</div>
                </div>
                """, unsafe_allow_html=True)
        if r.get('reposo'):
            st.markdown(f"""
            <div class="reposo-box">
                <h4>💤 EN REPOSO:</h4>
                <p><b>{', '.join(r['reposo'])}</b></p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Genere el sorteo en Inscripción.")

# --- 5. SECCIÓN: RESULTADOS (CON GENERADOR DE SIGUIENTE RONDA) ---
elif st.session_state.seccion_activa == "RESULTADOS":
    st.header("Carga de Puntuaciones")
    if st.session_state.historial_completo:
        r = st.session_state.historial_completo[-1]
        
        # Si ya se cargaron todas las mesas de la ronda actual
        if len(r['listas']) == len(r['mesas']) and len(r['mesas']) > 0:
            st.success(f"¡Ronda {r['ronda']} completada con éxito!")
            
            if st.button("🔄 GENERAR SIGUIENTE RONDA (SISTEMA SUIZO)"):
                jg = st.session_state.juegos_ganados
                ef = st.session_state.efectividad
                
                # Clasificación estricta según sus baremos para el emparejamiento
                ordenados = sorted(
                    [x for x in st.session_state.asistentes if st.session_state.estados.get(x, False)],
                    key=lambda x: (jg.get(x, 0), ef.get(x, 1.0)),
                    reverse=True
                )
                
                lim = (len(ordenados) // 4) * 4
                st.session_state.historial_completo.append({
                    'ronda': len(st.session_state.historial_completo) + 1,
                    'mesas': [ordenados[i:i+4] for i in range(0, lim, 4)],
                    'reposo': ordenados[lim:],
                    'listas': []
                })
                st.session_state.seccion_activa = "MESAS"
                st.rerun()
        else:
            # Muestra las mesas pendientes por registrar
            for i, m in enumerate(r['mesas']):
                if i not in r['listas']:
                    with st.expander(f"MESA {i+1}", expanded=True):
                        c1, c2 = st.columns(2)
                        
                        lbl_ac = f"A-C ({m[0]}/{m[2]}):"
                        lbl_bd = f"B-D ({m[1]}/{m[3]}):"
                        
                        v1 = c1.number_input(lbl_ac, 0, 250, key=f"v1_{i}")
                        v2 = c2.number_input(lbl_bd, 0, 250, key=f"v2_{i}")
                        
                        if st.button(f"GUARDAR MESA {i+1}", key=f"b_{i}"):
                            for j in [m[0], m[2]]:
                                st.session_state.puntos_favor[j] = st.session_state.puntos_favor.get(j, 0) + v1
                                st.session_state.puntos_contra[j] = st.session_state.puntos_contra.get(j, 0) + v2
                                if v1 > v2:
                                    cur_jg = st.session_state.juegos_ganados.get(j, 0)
                                    st.session_state.juegos_ganados[j] = cur_jg + 1
                                    
                            for j in [m[1], m[3]]:
                                st.session_state.puntos_favor[j] = st.session_state.puntos_favor.get(j, 0) + v2
                                st.session_state.puntos_contra[j] = st.session_state.puntos_contra.get(j, 0) + v1
                                if v2 > v1:
                                    cur_jg = st.session_state.juegos_ganados.get(j, 0)
                                    st.session_state.juegos_ganados[j] = cur_jg + 1
                                    
                            for j in m:
                                recalcular_baremo(j)
                                
                            r['listas'].append(i)
                            st.rerun()
    else:
        st.info("No hay rondas activas.")

# --- 6. SECCIÓN: RANKING (BAREMOS OFICIALES RESTAURADOS) ---
elif st.session_state.seccion_activa == "RANKING":
    st.header("Ranking General")
    if st.session_state.asistentes:
        jg = st.session_state.juegos_ganados
        ef = st.session_state.efectividad
        
        t = sorted(
            st.session_state.asistentes, 
            key=lambda x: (jg.get(x, 0), ef.get(x, 1.0)), 
            reverse=True
        )
        
        db = []
        for idx, n in enumerate(t):
            fila = {
                "Pos": idx + 1,
                "Atleta": n,
                "JJ": jg.get(n, 0),
                "PF": st.session_state.puntos_favor.get(n, 0),
                "PC": st.session_state.puntos_contra.get(n, 0),
                "Efec": f"{ef.get(n, 1.0):.4f}"
            }
            db.append(fila)
            
        st.table(db)
