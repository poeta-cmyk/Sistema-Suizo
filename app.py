import streamlit as st

# Configuración inicial
st.title("Sistema Suizo - Registro de Asistentes")

# Crear la memoria del programa (si no existe)
if 'asistentes' not in st.session_state:
    st.session_state.asistentes = []

# Cuadro de entrada para el nombre o nick
nuevo_jugador = st.text_input("Escriba el nombre o nick del jugador:")

# Botón para registrar y ordenar
if st.button("Registrar"):
    if nuevo_jugador:
        if nuevo_jugador not in st.session_state.asistentes:
            st.session_state.asistentes.append(nuevo_jugador)
            st.session_state.asistentes.sort() # Orden alfabético instantáneo
            st.success(f"'{nuevo_jugador}' ha sido registrado.")
        else:
            st.warning("Este jugador ya está en la lista.")
    else:
        st.error("El cuadro no puede estar vacío.")

# Mostrar la lista ordenada
st.write("---")
st.subheader("Lista de Jugadores (A-Z)")
for i, jugador in enumerate(st.session_state.asistentes, 1):
    st.text(f"{i}. {jugador}")
