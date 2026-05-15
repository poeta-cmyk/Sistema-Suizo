import streamlit as st
import random

# --- 1. CONFIGURACIÓN E INICIALIZACIÓN (Intacta) ---
st.set_page_config(layout="wide", page_title="ADEL SISTEMA SUIZO")

if 'asistentes' not in st.session_state:
    st.session_state.update({
        'asistentes': [],
        'estados': {},
        'meta_puntos': 200,
        'seccion': "INSCRIPCIÓN",
        'editando': None,
        'mesas_ronda1': []  # Almacena el sorteo de las posiciones
    })

# --- 2. MENÚ LATERAL ---
with st.sidebar:
    st.title("🏆 MENÚ ADEL")
    st.session_state.seccion = st.radio("VENTANAS:", ["INSCRIPCIÓN", "MESAS", "RESULTADOS", "RANKING"])

# --- 3. SECCIÓN DE INSCRIPCIÓN (SU PORTADA - SIN TOCAR NADA) ---
if st.session_state.seccion == "INSCRIPCIÓN":
    st.markdown("<h1 style='text-align: center;'>ASOCIACIÓN DE DOMINÓ DEL ESTADO LARA “ADEL”</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center;'>SISTEMA SUIZO</h2>", unsafe_allow_html=True)
    st.divider()

    col_reg, col_meta = st.columns([2, 1])

    with col_reg:
        def registrar():
            nom = st.session_state.input_nombre.upper().strip()
            if nom and nom not in st.session_state.asistentes:
                st.session_state.asistentes.append(nom)
                st.session_state.estados[nom] = True
                st.session_state.asistentes.sort()
            st.session_state.input_nombre = ""

        st.text_input("Nombre del Atleta + ENTER:", key="input_nombre", on_change=registrar)

    with col_meta:
        st.session_state.meta_puntos = st.radio("Meta del encuentro:", [100, 200], 
                                                index=1 if st.session_state.meta_puntos == 200 else 0, 
                                                horizontal=True)

    st.divider()
    
    total = len(st.session_state.asistentes)
    activos = sum(1 for a in st.session_state.asistentes if st.session_state.estados[a])
    st.markdown(f"### 📋 INSCRITOS: {total} | ✅ ACTIVOS: {activos}")

    if st.session_state.asistentes:
        h1, h2, h3, h4 = st.columns([4, 1, 1, 1])
        h1.write("**NOMBRE DEL ATLETA**")
        h2.write("**ESTADO**")
        h3.write("**EDITAR**")
        h4.write("**BORRAR**")
        st.divider()

        for atleta in st.session_state.asistentes:
            c1, c2, c3, c4 = st.columns([4, 1, 1, 1])
            
            if st.session_state.estados[atleta]:
                c1.markdown(f"**{atleta}**")
            else:
                c1.markdown(f"~~{atleta}~~ (Retirado)")

            if c2.button("✅" if st.session_state.estados[atleta] else "💤", key=f"st_{atleta}"):
                st.session_state.estados[atleta] = not st.session_state.estados[atleta]
                st.rerun()
                
            if c3.button("📝", key=f"ed_{atleta}"):
                st.session_state.editando = atleta
                st.rerun()
                
            if c4.button("🗑️", key=f"del_{atleta}"):
                st.session_state.asistentes.remove(atleta)
                st.session_state.estados.pop(atleta)
                st.rerun()

    if st.session_state.editando:
        with st.form("form_editar"):
            nuevo_nom = st.text_input("Corregir nombre:", value=st.session_state.editando).upper()
            if st.form_submit_button("GUARDAR"):
                idx = st.session_state.asistentes.index(st.session_state.editando)
                st.session_state.asistentes[idx] = nuevo_nom
                st.session_state.estados[nuevo_nom] = st.session_state.estados.pop(st.session_state.editando)
                st.session_state.editando = None
                st.session_state.asistentes.sort()
                st.rerun()

    st.divider()
    
    # --- CONEXIÓN DEL BOTÓN CREAR SORTEO ---
    if st.button("🚀 GENERAR SORTEO"):
        atlet_activos = [a for a in st.session_state.asistentes if st.session_state.estados[a]]
        if len(atlet_activos) >= 4:
            # Mezclar atletas aleatoriamente para la Ronda 1
            random.shuffle(atlet_activos)
            
            # Agrupar de 4 en 4 para formar las mesas
            mesas = []
            for i in range(0, len(atlet_activos), 4):
                grupo = atlet_activos[i:i+4]
                if len(grupo) == 4:
                    mesas.append(grupo)
                else:
                    # Si sobran (quedan 1, 2 o 3), se guardan como atletas en reposo temporal
                    st.session_state['reposo_actual'] = grupo
            
            st.session_state.mesas_ronda1 = mesas
            # El truco: cambiamos la sección activa y forzamos el reinicio para ir a "MESAS"
            st.session_state.seccion = "MESAS"
            st.rerun()
        else:
            st.error("Se necesitan al menos 4 atletas activos para generar las mesas.")

# --- 4. SECCIÓN DE MESAS (DIBUJA LAS POSICIONES) ---
elif st.session_state.seccion == "MESAS":
    st.markdown("<h1 style='text-align: center;'>Distribución de Mesas - Ronda 1</h1>", unsafe_allow_html=True)
    st.divider()
    
    if not st.session_state.mesas_ronda1:
        st.info("Aún no se ha generado el sorteo. Vaya a la ventana 'INSCRIPCIÓN' y presione GENERAR SORTEO.")
    else:
        # Dibujamos de forma ordenada cada mesa y sus posiciones de juego
        for idx, mesa in enumerate(st.session_state.mesas_ronda1):
            with st.container(border=True):
                st.markdown(f"### 🂓 MESA {idx + 1}")
                
                # Formato clásico de posiciones cruzadas en dominó
                c_izq, c_centro, c_der = st.columns([1, 2, 1])
                
                with c_centro:
                    st.write(f"**Posición 1 (Salida):** {mesa[0]}")
                    st.write(f"**Posición 2 (Derecha):** {mesa[1]}")
                    st.write(f"**Posición 3 (Compañero):** {mesa[2]}")
                    st.write(f"**Posición 4 (Izquierda):** {mesa[3]}")
                    st.markdown(f"*Parejas: **{mesa[0]} y {mesa[2]}** VS **{mesa[1]} y {mesa[3]}***")
        
        # Mostrar si alguien quedó en reposo por número impar
        if 'reposo_actual' in st.session_state and st.session_state['reposo_actual']:
            st.warning(f"Atletas en Repeso esta ronda: {', '.join(st.session_state['reposo_actual'])}")

# --- OTRAS SECCIONES EN ESPERA ---
elif st.session_state.seccion == "RESULTADOS":
    st.header("Carga de Resultados y Sanciones")
    st.info("Aquí colocaremos las teclas de sanciones para descontar puntos, tal como lo planeamos.")

elif st.session_state.seccion == "RANKING":
    st.header("Ranking General ADEL")
    st.info("Aquí se desplegará la lista del ranking dinámico en la próxima sesión.")
