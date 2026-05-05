import streamlit as st
import math
import random

# Configuración de página ancha para que el diseño de espejo quepa bien
st.set_page_config(layout="wide")

st.title("Sistema Suizo - Geometría de Mesas")

# --- MEMORIA DEL PROGRAMA ---
if 'asistentes' not in st.session_state:
    st.session_state.asistentes = []
if 'registro_abierto' not in st.session_state:
    st.session_state.registro_abierto = True
if 'lista_sorteada' not in st.session_state:
    st.session_state.lista_sorteada = []

# --- FUNCIONES ---
def registrar_y_limpiar():
    nombre = st.session_state.ingreso_nombre.strip().upper()
    if nombre and nombre not in st.session_state.asistentes:
        st.session_state.asistentes.append(nombre)
        st.session_state.asistentes.sort()
        st.session_state.ingreso_nombre = ""

def realizar_sorteo():
    if len(st.session_state.asistentes) >= 4:
        st.session_state.registro_abierto = False
        # Sorteo real: mezclamos toda la lista para que el receso sea azaroso
        temp_lista = st.session_state.asistentes.copy()
        random.shuffle(temp_lista)
        st.session_state.lista_sorteada = temp_lista

# --- INTERFAZ DE REGISTRO ---
if st.session_state.registro_abierto:
    st.text_input("Escriba el nombre o nick del jugador:", key="ingreso_nombre", on_change=registrar_y_limpiar)
    col_reg1, col_reg2 = st.columns(2)
    with col_reg1:
        if st.button("Registrar Jugador"): registrar_y_limpiar()
    with col_reg2:
        if st.button("Finalizar registro y Sortear"):
            realizar_sorteo()
            st.rerun()

# --- CÁLCULOS ---
n_jugadores = len(st.session_state.asistentes)
if n_jugadores > 0:
    rondas = math.ceil(math.log2(n_jugadores))
    n_mesas = n_jugadores // 4
    en_pausa_num = n_jugadores % 4
    
    st.markdown("---")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Jugadores", n_jugadores)
    c2.metric("Número de Rondas", rondas)
    c3.metric("Número de Mesas", n_mesas)
    c4.metric("En Pausa", en_pausa_num)

# --- VISTA DE MESAS (EL ESPEJO) ---
if not st.session_state.registro_abierto and st.session_state.lista_sorteada:
    if st.button("⬅ Volver al Registro (Sin perder el sorteo)"):
        st.session_state.registro_abierto = True
        st.rerun()

    st.markdown("### 🗠 DISTRIBUCIÓN DE MESAS - RONDA 1")
    
    # Separamos jugadores de mesas y jugadores en pausa
    total_en_mesas = n_mesas * 4
    jugadores_mesas = st.session_state.lista_sorteada[:total_en_mesas]
    jugadores_pausa = st.session_state.lista_sorteada[total_en_mesas:]

    # Encabezado de la tabla de espejo
    st.markdown("---")
    h1, h2, h3, h4, h5 = st.columns([4, 1, 1, 1, 4])
    h1.write("**PAREJA A/C (Izquierda)**")
    h2.write("**Puntos**")
    h3.markdown("<center><b>MESA</b></center>", unsafe_allow_html=True)
    h4.write("**Puntos**")
    h5.write("**PAREJA B/D (Derecha)**")

    # Generar cada fila (Mesa)
    for i in range(n_mesas):
        # Tomamos 4 jugadores para esta mesa
        m = jugadores_mesas[i*4 : i*4+4]
        
        col_izq, pts_izq, num_mesa, pts_der, col_der = st.columns([4, 1, 1, 1, 4])
        
        with col_izq:
            st.info(f"{m[0]} / {m[2]}") # Jugador A y C
        with pts_izq:
            st.number_input("", key=f"p_izq_{i}", min_value=0, max_value=100, step=1, label_visibility="collapsed")
        with num_mesa:
            st.markdown(f"<h3 style='text-align: center; margin: 0;'>{i+1}</h3>", unsafe_allow_html=True)
        with pts_der:
            st.number_input("", key=f"p_der_{i}", min_value=0, max_value=100, step=1, label_visibility="collapsed")
        with col_der:
            st.success(f"{m[1]} / {m[3]}") # Jugador B y D

    if jugadores_pausa:
        st.markdown("---")
        st.warning(f"**EN PAUSA:** {', '.join(jugadores_pausa)}")

else:
    # Mostrar lista alfabética solo durante el registro
    st.markdown("---")
    st.subheader("Lista de Asistentes (Orden Alfabético)")
    for i, jugador in enumerate(st.session_state.asistentes, 1):
        c_n, c_b = st.columns([0.8, 0.2])
        c_n.write(f"**{i}.** {jugador}")
        if c_b.button("Eliminar", key=f"del_{jugador}"):
            st.session_state.asistentes.remove(jugador)
            st.rerun()
