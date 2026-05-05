import streamlit as st
import math
import random

# Título
st.title("Sistema Suizo - Registro y Sorteo")

# Inicializar memorias (session_state)
if 'asistentes' not in st.session_state:
    st.session_state.asistentes = []
if 'registro_abierto' not in st.session_state:
    st.session_state.registro_abierto = True
if 'mesas_sorteadas' not in st.session_state:
    st.session_state.mesas_sorteadas = None

# Funciones de lógica
def registrar_y_limpiar():
    nombre = st.session_state.ingreso_nombre.strip().upper()
    if nombre:
        if nombre not in st.session_state.asistentes:
            st.session_state.asistentes.append(nombre)
            st.session_state.asistentes.sort()
            st.session_state.ingreso_nombre = ""
        else:
            st.warning(f"'{nombre}' ya está registrado.")

def finalizar_y_sortear():
    if len(st.session_state.asistentes) >= 4:
        st.session_state.registro_abierto = False
        # Sorteo aleatorio
        lista_sorteo = st.session_state.asistentes.copy()
        random.shuffle(lista_sorteo)
        
        # Agrupar en mesas de 4
        mesas = []
        for i in range(0, len(lista_sorteo), 4):
            mesas.append(lista_sorteo[i:i+4])
        st.session_state.mesas_sorteadas = mesas
    else:
        st.error("Se necesitan al menos 4 jugadores para iniciar.")

def abrir_registro():
    st.session_state.registro_abierto = True

# --- INTERFAZ DE REGISTRO ---
if st.session_state.registro_abierto:
    st.text_input("Escriba el nombre o nick del jugador:", 
                 key="ingreso_nombre", 
                 on_change=registrar_y_limpiar)

    col_reg1, col_reg2 = st.columns(2)
    with col_reg1:
        if st.button("Registrar Jugador"):
            registrar_y_limpiar()
    with col_reg2:
        if st.button("Finalizar registro"):
            finalizar_y_sortear()
            st.rerun()

# --- CÁLCULOS E INDICADORES ---
n_jugadores = len(st.session_state.asistentes)
if n_jugadores > 0:
    rondas = math.ceil(math.log2(n_jugadores))
    n_mesas = n_jugadores // 4
    receso = n_jugadores % 4
    
    st.markdown("---")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Jugadores", n_jugadores)
    c2.metric("Número de Rondas", rondas)
    c3.metric("Número de Mesas", n_mesas)
    c4.metric("En Receso", receso)

# --- MOSTRAR RESULTADOS O LISTA ---
if not st.session_state.registro_abierto and st.session_state.mesas_sorteadas:
    st.markdown("### 🎲 DISTRIBUCIÓN DE MESAS - RONDA 1")
    if st.button("⬅ Volver a agregar jugadores"):
        abrir_registro()
        st.rerun()
    
    for i, mesa in enumerate(st.session_state.mesas_sorteadas, 1):
        with st.expander(f"MESA {i}", expanded=True):
            for j, jugador in enumerate(mesa, 1):
                st.write(f"{j}. {jugador}")
    
    if n_jugadores % 4 != 0:
        st.warning(f"Nota: Los últimos {n_jugadores % 4} jugadores están en receso esta ronda.")

else:
    # Mostrar lista normal mientras se registra
    st.markdown("---")
    st.subheader("Lista de Asistentes")
    for i, jugador in enumerate(st.session_state.asistentes, 1):
        c_n, c_b = st.columns([0.8, 0.2])
        c_n.write(f"**{i}.** {jugador}")
        if c_b.button("Eliminar", key=f"del_{jugador}"):
            st.session_state.asistentes.remove(jugador)
            st.rerun()
