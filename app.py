import streamlit as st
import math
import json

# --- 1. CONFIGURACIÓN E INICIALIZACIÓN ---
st.set_page_config(layout="wide", page_title="SISTEMA ADEL - PRO")

# Memoria del Torneo (Caja Fuerte)
for key, default in {
    'asistentes': [], 'juegos_ganados': {}, 'efectividad': {}, 
    'puntos_contra': {}, 'ronda_actual': 1, 'registro_abierto': True, 
    'meta_puntos': 100, 'historial_completo': [], 'parejas_jugadas': [],
    'tarjetas': {} # Memoria para las amonestaciones
}.items():
    if key not in st.session_state: st.session_state[key] = default

# --- 2. LÓGICA DE CONTROL ---
def procesar_registro():
    n = st.session_state.nuevo_atleta.strip().upper()
    if n and n not in st.session_state.asistentes:
        st.session_state.asistentes.append(n)
        st.session_state.tarjetas[n] = "NINGUNA" # Inicializa sin tarjetas
    st.session_state.nuevo_atleta = ""

def finalizar_ronda():
    meta = st.session_state.meta_puntos
    r_idx = st.session_state.ronda_actual - 1
    r_data = st.session_state.historial_completo[r_idx]
    
    for i, mesa in enumerate(r_data['mesas']):
        p1 = st.session_state.get(f"p1_r{st.session_state.ronda_actual}_m{i}", 0)
        p2 = st.session_state.get(f"p2_r{st.session_state.ronda_actual}_m{i}", 0)
        
        # Lógica de Ganadores/Perdedores y Efectividad
        if p1 >= p2:
            ef, gan, per, cp = meta-p2, [mesa[0], mesa[2]], [mesa[1], mesa[3]], p2
            cg = p1 # Puntos a favor del ganador para registro
        else:
            ef, gan, per, cp = meta-p1, [mesa[1], mesa[3]], [mesa[0], mesa[2]], p1
            cg = p2

        for g in gan:
            st.session_state.juegos_ganados[g] = st.session_state.juegos_ganados.get(g, 0) + 1
            st.session_state.efectividad[g] = st.session_state.efectividad.get(g, 0) + ef
            st.session_state.puntos_contra[g] = st.session_state.puntos_contra.get(g, 0) + cp
        for p in per:
            st.session_state.efectividad[p] = st.session_state.efectividad.get(p, 0) - ef
            st.session_state.puntos_contra[p] = st.session_state.puntos_contra.get(p, 0) + cg

    st.session_state.ronda_actual += 1
    # Aquí iría la lógica de generación de siguiente ronda
    st.rerun()

# --- 3. NAVEGACIÓN ---
with st.sidebar:
    st.title("🏆 MENÚ ADEL")
    pagina = st.radio("Sección:", ["🎮 MESA TÉCNICA", "📺 PANTALLA ADEL"])
    st.markdown("---")
    if st.button("📥 GUARDAR TORNEO"):
        # Lógica de backup...
        pass

# --- HOJA: MESA TÉCNICA (CONTROL) ---
if pagina == "🎮 MESA TÉCNICA":
    st.title("Control de Torneo y Justicia")
    
    if st.session_state.registro_abierto:
        st.subheader("Registro de Atletas")
        st.text_input("Nombre del Atleta:", key="nuevo_atleta", on_change=procesar_registro)
        if st.button("🚀 INICIAR") and len(st.session_state.asistentes) >= 4:
            st.session_state.registro_abierto = False
            # generar_ronda_adel()...
            st.rerun()
    else:
        tab1, tab2 = st.tabs(["📝 CARGA DE RESULTADOS", "📊 BAREMO Y TARJETAS"])
        
        with tab1:
            st.info(f"Ronda Actual: {st.session_state.ronda_actual}")
            # Bloque para ingresar puntos...
            if st.button("CERRAR RONDA"): finalizar_ronda()

        with tab2:
            st.subheader("Baremo Oficial de Clasificación")
            # Ordenar por el baremo ADEL
            rk = sorted(st.session_state.asistentes, 
                        key=lambda x: (st.session_state.juegos_ganados.get(x, 0), 
                                       st.session_state.efectividad.get(x, 0), 
                                       -st.session_state.puntos_contra.get(x, 0)), reverse=True)
            
            # CABECERA DEL BAREMO (Según imagen 66d9d7)
            cols_h = st.columns([0.5, 2, 0.5, 0.5, 0.5, 1.5])
            cols_h[0].write("**Pos**")
            cols_h[1].write("**Atleta**")
            cols_h[2].write("**JG**")
            cols_h[3].write("**Efect**")
            cols_h[4].write("**PC**")
            cols_h[5].write("**TARJETAS (Manual)**")

            for i, nombre in enumerate(rk):
                cols = st.columns([0.5, 2, 0.5, 0.5, 0.5, 1.5])
                cols[0].write(f"{i+1}")
                cols[1].write(f"**{nombre}**")
                cols[2].write(f"{st.session_state.juegos_ganados.get(nombre, 0)}")
                cols[3].write(f"{st.session_state.efectividad.get(nombre, 0)}")
                cols[4].write(f"{st.session_state.puntos_contra.get(nombre, 0)}")
                
                # CUADRO DE DESPLIEGUE PARA TARJETAS (Petición del Poeta)
                st.session_state.tarjetas[nombre] = cols[5].selectbox(
                    "Sanción", 
                    ["NINGUNA", "AMARILLA 🟨", "ROJA 🟥", "NEGRA ⬛"],
                    key=f"tj_{nombre}",
                    label_visibility="collapsed",
                    index=["NINGUNA", "AMARILLA 🟨", "ROJA 🟥", "NEGRA ⬛"].index(st.session_state.tarjetas.get(nombre, "NINGUNA"))
                )

# --- HOJA: PANTALLA ADEL (MONITOR) ---
elif pagina == "📺 PANTALLA ADEL":
    st.title("Monitor Oficial ADEL")
    # Aquí se visualizan las mesas con el nombre "ADEL" central y el Ranking público
    st.write("Visualización de Mesas ADEL en construcción...")
