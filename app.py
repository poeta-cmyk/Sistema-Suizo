import streamlit as st
import math

# --- 1. CONFIGURACIÓN ---
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
        'editando': None # Memoria para saber quién se está corrigiendo
    })

# --- 2. BAREMO ---
def recalcular_baremo(atleta):
    pf = st.session_state.puntos_favor[atleta]
    pc = st.session_state.puntos_contra[atleta]
    v_f = pf if pf > 0 else 1
    v_c = pc if pc > 0 else 1
    st.session_state.efectividad[atleta] = math.log10(v_f / v_c) + 1

# --- 3. MENÚ ---
with st.sidebar:
    st.title("🏆 MENÚ ADEL")
    opcion = st.radio("SECCIÓN:", ["INSCRIPCIÓN", "MESAS", "PANTALLA ADEL", "RANKING"])

# --- 4. SECCIÓN: INSCRIPCIÓN ---
if opcion == "INSCRIPCIÓN":
    st.caption("Creado por Poeta")
    st.header("ASOCIACIÓN DE DOMINÓ DEL ESTADO LARA ADEL SISTEMA SUIZO")
    st.subheader("Control de Nómina y Asistencia")
    
    # LÓGICA DE EDICIÓN Y REGISTRO
    def procesar_entrada():
        texto = st.session_state.campo_input.upper().strip()
        if texto:
            if st.session_state.editando:
                # Si estábamos editando, reemplazamos el nombre viejo por el nuevo
                viejo = st.session_state.editando
                if texto != viejo:
                    idx = st.session_state.asistentes.index(viejo)
                    st.session_state.asistentes[idx] = texto
                    # Transferimos los puntos al nuevo nombre
                    for k in ['estados', 'juegos_ganados', 'puntos_contra', 'puntos_favor', 'efectividad']:
                        st.session_state[k][texto] = st.session_state[k].pop(viejo)
                st.session_state.editando = None
            elif texto not in st.session_state.asistentes:
                # Si es nuevo, lo agregamos normal
                st.session_state.asistentes.append(texto)
                st.session_state.estados[texto] = True
                for k in ['juegos_ganados', 'puntos_contra', 'puntos_favor']: st.session_state[k][texto] = 0
                st.session_state.efectividad[texto] = 1.0
            
            st.session_state.asistentes.sort()
            st.session_state.campo_input = "" # Limpiamos el cuadro

    # El cuadro de texto
    label_input = f"Corrigiendo a: {st.session_state.editando}" if st.session_state.editando else "Agregar Atleta nuevo:"
    st.text_input(label_input, key="campo_input", on_change=procesar_entrada)
    
    if st.session_state.asistentes:
        activos = [n for n in st.session_state.asistentes if st.session_state.estados[n]]
        st.write(f"### Atletas en Nómina: {len(st.session_state.asistentes)} (Activos para sorteo: {len(activos)})")
        
        for n in st.session_state.asistentes:
            c_nom, c_act, c_edit, c_del = st.columns([3, 1, 1, 1])
            c_nom.text(f"• {n}")
            
            # BOTÓN ESTADO
            est = st.session_state.estados[n]
            if c_act.button("✅ ACTIVO" if est else "❌ RETIRADO", key=f"st_{n}"):
                st.session_state.estados[n] = not est; st.rerun()

            # BOTÓN LÁPIZ (EDICIÓN) - AHORA VISIBLE
            if c_edit.button("📝", key=f"ed_{n}"):
                st.session_state.editando = n
                st.session_state.campo_input = n # Ponemos el nombre en el cuadro de arriba
                st.rerun()

            # BOTÓN BORRAR
            if c_del.button("🗑️", key=f"br_{n}"):
                st.session_state.asistentes.remove(n)
                for k in ['estados', 'juegos_ganados', 'puntos_contra', 'puntos_favor', 'efectividad']:
                    del st.session_state[k][n]
                st.rerun()

# --- 5. SECCIÓN: MESAS (RESTO DEL CÓDIGO IGUAL...) ---
