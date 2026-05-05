import streamlit as st
import math

# Título
st.title("Sistema Suizo - Registro de Asistentes")

# Memoria para los nombres
if 'asistentes' not in st.session_state:
    st.session_state.asistentes = []

# Función para registrar y limpiar
def registrar_y_limpiar():
    nombre = st.session_state.ingreso_nombre.strip() 
    if nombre:
        if nombre not in st.session_state.asistentes:
            st.session_state.asistentes.append(nombre)
            st.session_state.asistentes.sort()
            st.session_state.ingreso_nombre = ""
        else:
            st.warning(f"'{nombre}' ya está en la lista.")
    else:
        st.error("Escribe un nombre.")

# Cuadro de texto
st.text_input("Escriba el nombre o nick del jugador:", 
             key="ingreso_nombre", 
             on_change=registrar_y_limpiar)

# Botón de registro
if st.button("Registrar Jugador"):
    registrar_y_limpiar()

# --- SECCIÓN DE CÁLCULOS ---
n_jugadores = len(st.session_state.asistentes)

if n_jugadores > 0:
    # Cálculo matemático de rondas para Sistema Suizo
    rondas = math.ceil(math.log2(n_jugadores))
    
    st.markdown("---")
    # Indicadores visuales
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Jugadores", n_jugadores)
    with col2:
        st.metric("Rondas Sugeridas", rondas)
    
    st.info(f"Para un torneo de {n_jugadores} jugadores, el sistema recomienda realizar {rondas} rondas para determinar un ganador único.")

# Lista visual
st.markdown("---")
st.subheader(f"Lista de Asistentes")
for i, jugador in enumerate(st.session_state.asistentes, 1):
    st.write(f"**{i}.** {jugador}")
