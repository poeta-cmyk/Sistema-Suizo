import streamlit as st
import math

# --- 1. CONFIGURACIÓN E INICIALIZACIÓN (BLINDADA) ---
st.set_page_config(layout="wide", page_title="SISTEMA ADEL")

if 'asistentes' not in st.session_state:
    st.session_state.update({
        'asistentes': [], 
        'estados': {}, 
        'juegos_ganados': {}, 
        'efectividad': {}, 
        'puntos_contra': {}, 
        'puntos_favor': {}, 
        'historial_completo': [],
        'editando': None 
    })

# --- 2. BAREMO LOGARÍTMICO ---
def recalcular_baremo(atleta):
    pf = st.session_state.puntos_favor[atleta]
    pc = st.session_state.puntos_contra[atleta]
    v_f = pf if pf > 0 else 1
    v_c = pc if pc > 0 else 1
    st.session_state.efectividad[atleta] = math.log10(v_f / v_c) + 1

# --- 3. MENÚ REORDENADO ---
with st.sidebar:
    st.title("🏆 MENÚ ADEL")
    # Cambiamos los nombres según su instrucción
    opcion = st.radio("SECCIÓN:", ["INSCRIPCIÓN", "MESAS", "RESULTADOS", "RANKING"])

# --- 4. SECCIÓN: INSCRIPCIÓN (INTACTA) ---
if opcion == "INSCRIPCIÓN":
    st.caption("Creado por Poeta")
    st.header("ASOCIACIÓN DE DOMINÓ DEL ESTADO LARA ADEL SISTEMA SUIZO")
    st.subheader("Control de Nómina y Asistencia")
    
    def procesar_entrada():
        texto = st.session_state.campo_input.upper().strip()
        if texto:
            if st.session_state.editando:
                viejo = st.session_state.editando
                if texto != viejo:
                    idx = st.session_state.asistentes.index(viejo)
                    st.session_state.asistentes[idx] = texto
                    for k in ['estados', 'juegos_ganados', 'puntos_contra', 'puntos_favor', 'efectividad']:
                        st.session_state[k][texto] = st.session_state[k].pop(viejo)
                st.session_state.editando = None
            elif texto not in st.session_state.asistentes:
                st.session_state.asistentes.append(texto)
                st.session_state.estados[texto] = True
                for k in ['juegos_ganados', 'puntos_contra', 'puntos_favor']: 
                    st.session_state[k][texto] = 0
                st.session_state.efectividad[texto] = 1.0
            st.session_state.asistentes.sort()
        st.session_state.campo_input = "" 

    label_dinamico = f"Corrigiendo a: {st.session_state.editando}" if st.session_state.editando else "ATLETA"
    st.text_input(label_dinamico, key="campo_input", on_change=procesar_entrada)
    
    if st.session_state.asistentes:
        activos = [n for n in st.session_state.asistentes if st.session_state.estados[n]]
        st.write(f"### Atletas inscritos: {len(st.session_state.asistentes)} - Activos: {len(activos)}")
        for n in st.session_state.asistentes:
            c_nom, c_act, c_edit, c_del = st.columns([3, 1, 1, 1])
            c_nom.text(f"• {n}")
            if c_act.button("✅ ACTIVO" if st.session_state.estados[n] else "❌ RETIRADO", key=f"st_{n}"):
                st.session_state.estados[n] = not st.session_state.estados[n]; st.rerun()
            if c_edit.button("📝", key=f"ed_{n}"):
                st.session_state.editando = n; st.rerun()
            if c_del.button("🗑️", key=f"br_{n}"):
                st.session_state.asistentes.remove(n); st.rerun()

# --- 5. SECCIÓN: MESAS (CARA AL PÚBLICO) ---
elif opcion == "MESAS":
    st.caption("Creado por Poeta")
    st.header("ASOCIACIÓN DE DOMINÓ DEL ESTADO LARA ADEL SISTEMA SUIZO")
    st.subheader("Distribución de Mesas")
    
    if not st.session_state.historial_completo:
        st.info("Esperando el sorteo de la primera ronda...")
    else:
        r = st.session_state.historial_completo[-1]
        if r['reposo']:
            st.warning(f"⌛ EN REPOSO: {', '.join(r['reposo'])}")
        
        for idx, mj in enumerate(r['mesas']):
            with st.container(border=True):
                st.markdown(f"<h3 style='text-align:center;'>MESA {idx+1}</h3>", unsafe_allow_html=True)
                ca, cm, cd = st.columns([1, 1, 1])
                cm.markdown(f"<div style='text-align:center;'><b>A</b><br>{mj[0]}<br><br><b>C</b><br>{mj[2]}</div>", unsafe_allow_html=True)
                ca.markdown(f"<div style='text-align:right;'><br><b>B</b><br>{mj[1]}</div>", unsafe_allow_html=True)
                cd.markdown(f"<div style='text-align:left;'><br><b>D</b><br>{mj[3]}</div>", unsafe_allow_html=True)

# --- 6. SECCIÓN: RESULTADOS (CONTROL TÉCNICO) ---
elif opcion == "RESULTADOS":
    st.caption("Creado por Poeta")
    st.header("ASOCIACIÓN DE DOMINÓ DEL ESTADO LARA ADEL SISTEMA SUIZO")
    st.subheader("Carga de Resultados Técnicos")
    
    jugadores_disponibles = [n for n in st.session_state.asistentes if st.session_state.estados[n]]
    
    if st.button("🚀 SORTEAR SIGUIENTE RONDA"):
        # Lógica de sorteo (aquí implementaremos su algoritmo de rotación)
        n_jug = (len(jugadores_disponibles) // 4) * 4
        mesas = [jugadores_disponibles[i:i+4] for i in range(0, n_jug, 4)]
        st.session_state.historial_completo.append({
            'ronda': len(st.session_state.historial_completo) + 1, 
            'mesas': mesas, 
            'reposo': jugadores_disponibles[n_jug:]
        })
        st.rerun()

    if st.session_state.historial_completo:
        r = st.session_state.historial_completo[-1]
        st.write(f"### RONDA {r['ronda']}")
        # Aquí irá el formulario para anotar los puntos...

# --- 7. SECCIÓN: RANKING ---
elif opcion == "RANKING":
    st.caption("Creado por Poeta")
    st.header("ASOCIACIÓN DE DOMINÓ DEL ESTADO LARA ADEL SISTEMA SUIZO")
    st.subheader("Clasificación Oficial")
    # ... Lógica del Baremo ...
