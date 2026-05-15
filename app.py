import streamlit as st
import math
import random

# --- 1. INICIALIZACIÓN (Blindaje total) ---
if 'asistentes' not in st.session_state:
    st.session_state.update({
        'asistentes': [],
        'estados': {},
        'meta_puntos': 200,
        'n_rondas': 5, # Valor inicial estándar
        'seccion': "INSCRIPCIÓN",
        'editando': None
    })

# --- 2. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(layout="wide", page_title="ADEL - SISTEMA SUIZO")

# --- 3. MENÚ ADEL ---
with st.sidebar:
    st.title("🏆 MENÚ ADEL")
    st.session_state.seccion = st.radio("VENTANAS:", ["INSCRIPCIÓN", "MESAS", "RESULTADOS", "RANKING"])

# --- 4. CUERPO: INSCRIPCIÓN ---
if st.session_state.seccion == "INSCRIPCIÓN":
    st.markdown("<h1 style='text-align: center;'>ASOCIACIÓN DE DOMINÓ DEL ESTADO LARA “ADEL”</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center;'>SISTEMA SUIZO</h2>", unsafe_allow_html=True)
    st.divider()

    col_izq, col_der = st.columns([2, 1])

    with col_izq:
        # Selector de Meta
        st.session_state.meta_puntos = st.radio("Meta del encuentro:", [100, 200], 
                                                index=1 if st.session_state.meta_puntos == 200 else 0, 
                                                horizontal=True)
        
        # Registro con ENTER
        def registrar():
            txt = st.session_state.nuevo_atleta.upper().strip()
            if txt and txt not in st.session_state.asistentes:
                st.session_state.asistentes.append(txt)
                st.session_state.estados[txt] = True
                st.session_state.asistentes.sort()
            st.session_state.nuevo_atleta = ""

        st.text_input("Nombre del Atleta + ENTER:", key="nuevo
