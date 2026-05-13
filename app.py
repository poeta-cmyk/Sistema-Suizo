import streamlit as st
import math

# --- 1. CONFIGURACIÓN ---
st.set_page_config(layout="wide", page_title="SISTEMA ADEL")

# BLINDAJE DE MEMORIA: Se inicializan todas las variables para evitar el error de la imagen
if 'asistentes' not in st.session_state:
    st.session_state.update({
        'asistentes': [], 
        'estados': {}, 
        'juegos_ganados': {}, 
        'efectividad': {}, 
        'puntos_contra': {}, 
        'puntos_favor': {}, 
        'historial_completo': [],
        'editando': None  # Esta es la que causó el error en la imagen
    })

# --- 2. BAREMO LOGARÍTMICO ---
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
    
    # LÓGICA DE PROCESAMIENTO (REGISTRO Y EDICIÓN)
    def procesar_entrada():
        texto = st.session_state.campo_input.upper().strip()
        if texto:
            if st.session_state.editando:
                # Caso: Estamos corrigiendo un nombre existente
                viejo = st.session_state.editando
                if texto != viejo:
                    idx = st.session_state.asistentes.index(viejo)
                    st.session_state.asistentes[idx] = texto
                    # Movemos los datos al nuevo nombre
                    for k in ['estados', 'juegos_ganados', 'puntos_contra', 'puntos_favor', 'efectividad']:
                        st.session_state[k][texto] = st.session_state[k].pop(viejo)
                st.session_state.editando = None
            elif texto not in st.session_state.asistentes:
                # Caso: Es un atleta nuevo
                st.session_state.asistentes.append(texto)
                st.session_state.estados[texto] = True
                for k in ['juegos_ganados', 'puntos_contra', 'puntos_favor']: 
                    st.session_state[k][texto] = 0
                st.session_state.efectividad[texto] = 1.0
            
            st.session_state.asistentes.sort()
        st.session_state.campo_input = "" # Limpia el cuadro siempre

    # Cuadro de entrada de datos
    label_dinamico = f"Corrigiendo a: {st.session_state.editando}" if st.session_state.editando else "Agregar Atleta nuevo:"
    st.text_input(label_dinamico, key="campo_input", on_change=procesar_entrada)
    
    if st.session_state.asistentes:
        activos = [n for n in st.session_state.asistentes if st.session_state.estados[n]]
        st.write(f"### Atletas en Nómina: {len(st.session_state.asistentes)} (Activos: {len(activos)})")
        
        for n in st.session_state.asistentes:
            c_nom, c_act, c_edit, c_del = st.columns([3, 1, 1, 1])
            c_nom.text(f"• {n}")
            
            # Botón Activo/Retirado
            est = st.session_state.estados[n]
            if c_act.button("✅ ACTIVO" if est else "❌ RETIRADO", key=f"st_{n}"):
                st.session_state.estados[n] = not est; st.rerun()

            # Botón Editar (Lápiz)
            if c_edit.button("📝", key=f"ed_{n}"):
                st.session_state.editando = n
                # No podemos asignar directamente a campo_input por reglas de Streamlit,
                # pero el label dinámico le indicará que el sistema está listo para el cambio.
                st.rerun()

            # Botón Borrar (Solo para errores de carga inicial)
            if c_del.button("🗑️", key=f"br_{n}"):
                st.session_state.asistentes.remove(n)
                for k in ['estados', 'juegos_ganados', 'puntos_contra', 'puntos_favor', 'efectividad']:
                    del st.session_state[k][n]
                st.rerun()

# --- LAS DEMÁS SECCIONES (MESAS, PANTALLA, RANKING) SE MANTIENEN IGUAL ---
