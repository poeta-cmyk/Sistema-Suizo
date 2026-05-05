import streamlit as st
import math

# Título
st.title("Sistema Suizo - Registro de Asistentes")

# Memoria para los nombres
if 'asistentes' not in st.session_state:
    st.session_state.asistentes = []

# Función para registrar y limpiar
def registrar_y_limpiar():
    nombre = st.session_state.ingreso_nombre.strip().upper() # Convertimos a mayúsculas para evitar duplicados por minúsculas
    if nombre:
        if nombre not in st.session_state.asistentes:
            st.session_state.asistentes.append(nombre)
            st.session_state.asistentes.sort()
            st.session_state.ingreso_nombre = ""
        else:
            st.warning(f"'{nombre}' ya está en la lista.")
    else:
        st.error("Escribe un nombre.")

# Función para eliminar jugador
def eliminar_jugador(nombre):
    st.session_state.asistentes.remove(nombre)

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
    rondas = math.ceil(math.log2(n_jugadores))
    
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Jugadores", n_jugadores)
    with col2:
        st.metric("Número de Rondas", rondas)

# --- LISTA VISUAL CON OPCIÓN DE ELIMINAR ---
st.markdown("---")
st.subheader("Lista de Asistentes")

for i, jugador in enumerate(st.session_state.asistentes, 1):
    # Creamos una fila con dos columnas: una para el nombre y otra para el botón de borrar
    col_nombre, col_boton = st.columns([0.8, 0.2])
    
    with col_nombre:
        st.write(f"**{i}.** {jugador}")
    
    with col_boton:
        # El botón de eliminar
        if st.button("Eliminar", key=f"del_{jugador}"):
            eliminar_jugador(jugador)
            st.rerun() # Esto refresca la página para mostrar la lista actualizada
