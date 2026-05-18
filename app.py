import streamlit as st
import math
import random

# --- 1. CONFIGURACIÓN INICIAL ---
st.set_page_config(layout="wide", page_title="SISTEMA ADEL")

# Memoria interna del torneo
if 'asistentes' not in st.session_state: 
    st.session_state.asistentes = []
if 'historial_completo' not in st.session_state: 
    st.session_state.historial_completo = []
if 'meta_puntos' not in st.session_state: 
    st.session_state.meta_puntos = 200

reg_keys = ['estados', 'juegos_ganados', 'puntos_favor', 'puntos_contra', 'efectividad']
for k in reg_keys:
    if k not in st.session_state: 
        st.session_state[k] = {}

if 'seccion_activa' not in st.session_state: 
    st.session_state.seccion_activa = "INSCRIPCIÓN"
if 'editando' not in st.session_state: 
    st.session_state.editando = None

# --- ESTILOS CSS ORIGINALES ---
st.markdown("""
    <style>
    .mesa-container { display: inline-flex; flex-direction: column; align-items: center; justify-content: center; width: 260px!important; height: 260px!important; margin: 20px auto; }
    .mesa-centro { width: 110px!important; height: 110px!important; border: 5px solid black; background-color: #FFFF00; display: flex; flex-direction: column; align-items: center; justify-content: center; flex-shrink: 0; }
    .adel-text { font-weight: bold; font-size: 22px; color: #003
