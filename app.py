import streamlit as st

# Título del programa
st.title("Sistema Suizo - Registro de Asistentes")

# Memoria para guardar los nombres
if 'asistentes' not in st.session_state:
    st.session_state.asistentes = []

# Función para registrar al jugador y limpiar el cuadro
def registrar_y_limpiar():
    nombre = st.session_state.ingreso_nombre.strip() 
    if nombre:
        if nombre not in st.session_state.asistentes:
            st.session_state.asistentes.append(nombre)
            st.session_state.asistentes.sort() # Ordenar A-Z
            st.session_state.ingreso_nombre = "" # Limpia el cuadro
        else:
            st.warning(f"El nick '{nombre}' ya está registrado.")
    else:
        st.error("Por favor, escribe un nombre.")

# Cuadro de texto
st.text_input("Escriba el nombre o nick del jugador:", 
             key="ingreso_nombre", 
             on_change=registrar_y_limpiar)

# Botón de respaldo
if st.button("Registrar Jugador"):
    registrar_y_limpiar()

# Lista visual de asistentes
st.markdown("---")
st.subheader(f"Lista de Asistentes ({len(st.session_state.asistentes)})")
for i, jugador in enumerate(st.session_state.asistentes, 1):
    st.write(f"**{i}.** {jugador}")
