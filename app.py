import streamlit as st
import math
import random

# --- 1. CONFIGURACIÓN E INICIALIZACIÓN SEGURA (SU BASE INTACTA) ---
st.set_page_config(layout="wide", page_title="SISTEMA ADEL")

# Bloque de inicialización para prevenir errores de 'AttributeError'
if 'asistentes' not in st.session_state:
    st.session_state.asistentes = []
if 'estados' not in st.session_state:
    st.session_state.estados = {}
if 'juegos_ganados' not in st.session_state:
    st.session_state.juegos_ganados = {}
if 'puntos_favor' not in st.session_state:
    st.session_state.puntos_favor = {}
if 'puntos_contra' not in st.session_state:
    st.session_state.puntos_contra = {}
if 'efectividad' not in st.session_state:
    st.session_state.efectividad = {}
if 'historial_completo' not in st.session_state:
    st.session_state.historial_completo = []
if 'seccion_activa' not in st.session_state:
    st.session_state.seccion_activa = "INSCRIPCIÓN"
if 'editando' not in st.session_state:
    st.session_state.editando = None

# --- CSS REFORMADO: MESAS CUADRADAS Y SIMÉTRICAS ---
st.markdown("""
    <style>
    .mesa-container {
        display: flex; 
        flex-direction: column; 
        align-items: center; 
        margin-bottom: 50px; 
    }
    .mesa-centro {
        width: 160px; 
        height: 160px; 
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
    .norte {
        margin-bottom: 15px; 
    } 
    .sur { 
        margin-top: 15px; 
    }
    .fila-central {
        display: flex; 
        align-items: center; 
        justify-content: center; 
        width: 100%; 
    }
    .este-oeste {
        writing-mode: vertical-rl; 
        text-orientation: mixed; 
        padding: 0 30px; 
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
    pf, pc = st.session_state.puntos_favor.get(atleta, 0), st.session_state.puntos_contra.get(atleta, 0)
    st.session_state.efectividad[atleta] = math.log10(max(pf, 1) / max(pc, 1)) + 1

# --- 2. NAVEGACIÓN LATERAL ---
with st.sidebar:
    st.title("🏆 MENÚ ADEL")
    opciones = ["INSCRIPCIÓN", "MESAS", "RESULTADOS", "RANKING"]
    idx_actual = opciones.index(st.session_state.seccion_activa) if st.session_state.seccion_activa in opciones else 0
    st.session_state.seccion_activa = st.radio("SECCIÓN:", opciones, index=idx_actual)

# --- 3. SECCIÓN: INSCRIPCIÓN (100% INTACTA) ---
if st.session_state.seccion_activa == "INSCRIPCIÓN":
    st.markdown("<h1 style='text-align: center;'>ASOCIACIÓN DE DOMINÓ DEL ESTADO LARA “ADEL”</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center;'>SISTEMA SUIZO</h2>", unsafe_allow_html=True)
    st.divider()
    
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
        else:
            st.error("Se necesitan al menos 4 atletas activos para generar las mesas.")

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
            st.rerun()

# --- 4. SECCIÓN: MESAS (CON RECUADRO CUADRADO PERFECTO) ---
elif st.session_state.seccion_activa == "MESAS":
    st.markdown("<h1 style='text-align: center;'>Organización de la Sala</h1>", unsafe_allow_html=True)
    st.divider()
    
    if st.session_state.historial_completo:
        r = st.session_state.historial_completo[-1]
        st.subheader(f"Distribución de la RONDA {r['ronda']}")
        
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
                <h3 style="color: #CC0000; margin-top: 0;">💤 EN REPOSO:</h3>
                <p style="font-size: 22px; font-weight: bold;">{', '.join(r['reposo'])}</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Aún no se ha generado el sorteo. Vaya a la sección 'INSCRIPCIÓN' y presione el botón de Sorteo.")

# --- 5. SECCIÓN: RESULTADOS ---
elif st.session_state.seccion_activa == "RESULTADOS":
    st.markdown("<h1 style='text-align: center;'>Carga de Resultados</h1>", unsafe_allow_html=True)
    st.divider()
    if st.session_state.historial_completo:
        r = st.session_state.historial_completo[-1]
        for i, m in enumerate(r['mesas']):
            if i not in r['listas']:
                with st.expander(f"MESA {i+1}", expanded=True):
                    c1, c2 = st.columns(2)
                    v1 = c1.number_input(f"A-C ({m[0]}/{m[2]}):", 0, 250, key=f"v1_{i}")
                    v2 = c2.number_input(f"B-D ({m[1]}/{m[3]}):", 0, 250, key=f"v2_{i}")
                    if st.button(f"GUARDAR MESA {i+1}", key=f"b_{i}"):
                        for j in [m[0], m[2]]:
                            st.session_state.puntos_favor[j] += v1
                            st.session_state.puntos_contra[j] += v2
                            if v1 > v2: st.session_state.juegos_ganados[j] += 1
                        for j in [m[1], m[3]]:
                            st.session_state.puntos_favor[j] += v2
                            st.session_state.puntos_contra[j] += v1
                            if v2 > v1: st.session_state.juegos_ganados[j] += 1
                        for j in m: recalcular_baremo(j)
                        r['listas'].append(i)
                        st.rerun()
    else:
        st.info("Debe realizar el sorteo primero.")

# --- 6. SECCIÓN: RANKING ---
elif st.session_state.seccion_activa == "RANKING":
    st.markdown("<h1 style='text-align: center;'>Ranking General ADEL</h1>", unsafe_allow_html=True)
    st.divider()
    if st.session_state.asistentes:
        t = sorted(st.session_state.asistentes, key=lambda x: (st.session_state.juegos_ganados[x], st.session_
