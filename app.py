import streamlit as st
import random

# --- 1. CONFIGURACIÓN E INICIALIZACIÓN ---
st.set_page_config(layout="wide", page_title="SISTEMA SUIZO ADEL")

if 'asistentes' not in st.session_state:
    st.session_state.update({
        'asistentes': [], 'estados': {}, 'jg': {}, 'jj': {}, 
        'iep': {}, 'efec': {}, 'dif': {}, 'editando': None,
        'historial_completo': [], 'seccion_activa': "INSCRIPCIÓN", 
        'meta_encuentro': 200, 'n_rondas': 4
    })

# --- 2. NAVEGACIÓN LATERAL (MENÚ ADEL) ---
with st.sidebar:
    st.title("🏆 MENÚ ADEL")
    opciones = ["INSCRIPCIÓN", "MESAS", "RESULTADOS", "RANKING"]
    st.session_state.seccion_activa = st.radio("VENTANAS:", opciones, 
                                              index=opciones.index(st.session_state.seccion_activa))

# --- 3. CUERPO PRINCIPAL: INSCRIPCIÓN ---
if st.session_state.seccion_activa == "INSCRIPCIÓN":
    # 1. Nombre Institucional
    st.markdown("<h1 style='text-align: center;'>ASOCIACIÓN DE DOMINÓ DEL ESTADO LARA “ADEL”</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center;'>SISTEMA SUIZO</h2>", unsafe_allow_html=True)
    st.divider()

    col_config1, col_config2 = st.columns(2)
    
    # 2. Número de rondas: N
    st.session_state.n_rondas = col_config1.number_input("Número de rondas (N):", min_value=1, max_value=20, value=st.session_state.n_rondas)
    
    # 3. Selector de la meta del encuentro
    st.session_state.meta_encuentro = col_config2.radio("Meta del encuentro (Puntos):", [100, 200], 
                                                       index=1 if st.session_state.meta_encuentro == 200 else 0, 
                                                       horizontal=True)

    # 4. Recuadro para anotar jugador con ENTER
    def agregar_atleta():
        nom = st.session_state.campo_nom.upper().strip()
        if nom and nom not in st.session_state.asistentes:
            st.session_state.asistentes.append(nom)
            st.session_state.estados[nom] = True
            for k in ['jg', 'jj', 'iep', 'efec', 'dif']: st.session_state[k][nom] = 0
            st.session_state.asistentes.sort() # Orden alfabético automático
        st.session_state.campo_nom = "" # Blanquea para el siguiente

    st.text_input("Ingrese nombre del atleta y presione ENTER:", key="campo_nom", on_change=agregar_atleta)

    # 5. Aviso de atletas inscritos y activos
    n_total = len(st.session_state.asistentes)
    n_activos = sum(1 for n in st.session_state.asistentes if st.session_state.estados[n])
    st.info(f"📋 ATLETAS INSCRITOS: {n_total} | ✅ ATLETAS ACTIVOS: {n_activos}")

    st.divider()

    # 6. Lista de atletas con Eliminar, Editar o Borrar
    st.subheader("Nómina de Atletas")
    for nombre in st.session_state.asistentes:
        c_nom, c_est, c_ed, c_el = st.columns([3, 1, 1, 1])
        
        c_nom.write(f"**{nombre}**")
        
        # Botón Estado (Para Retiros)
        if c_est.button("✅" if st.session_state.estados[nombre] else "💤", key=f"st_{nombre}", help="Activo/Retirado"):
            st.session_state.estados[nombre] = not st.session_state.estados[nombre]
            st.rerun()
            
        # Botón Editar
        if c_ed.button("📝", key=f"ed_{nombre}", help="Editar nombre"):
            st.session_state.editando = nombre
            st.rerun()
            
        # Botón Eliminar (Borrar por completo)
        if c_el.button("🗑️", key=f"del_{nombre}", help="Eliminar atleta"):
            st.session_state.asistentes.remove(nombre)
            # Limpiar sus datos
            for k in ['estados', 'jg', 'jj', 'iep', 'efec', 'dif']: st.session_state[k].pop(nombre)
            st.rerun()

    # Modal de Edición
    if st.session_state.editando:
        with st.container(border=True):
            nuevo_n = st.text_input("Corregir nombre:", value=st.session_state.editando).upper()
            if st.button("GUARDAR CAMBIO"):
                v = st.session_state.editando
                idx = st.session_state.asistentes.index(v)
                st.session_state.asistentes[idx] = nuevo_n
                for k in ['estados', 'jg', 'jj', 'iep', 'efec', 'dif']:
                    st.session_state[k][nuevo_n] = st.session_state[k].pop(v)
                st.session_state.editando = None
                st.session_state.asistentes.sort()
                st.rerun()

    st.divider()

    # 7. Botón de Sorteo y remisión a MESAS
    if st.button("🚀 GENERAR SORTEO RONDA 1 E IR A MESAS"):
        activos = [n for n in st.session_state.asistentes if st.session_state.estados[n]]
        if len(activos) >= 4:
            random.shuffle(activos)
            n_m = (len(activos) // 4) * 4
            st.session_state.historial_completo.append({
                'mesas': [activos[i:i+4] for i in range(0, n_m, 4)],
                'reposo': activos[n_m:], 'listas': [], 'reposo_ok': False
            })
            st.session_state.seccion_activa = "MESAS"
            st.rerun()
        else:
            st.error("Se necesitan al menos 4 atletas activos para el sorteo.")

# --- SECCIONES RESTANTES (Mantenidas para estructura) ---
elif st.session_state.seccion_activa == "MESAS":
    st.header("Distribución de Mesas - Ronda 1")
    if st.session_state.historial_completo:
        r = st.session_state.historial_completo[-1]
        for i, m in enumerate(r['mesas']):
            st.write(f"**MESA {i+1}:** {m[0]} - {m[2]} vs {m[1]} - {m[3]}")
        if r['reposo']: st.warning(f"En reposo: {', '.join(r['reposo'])}")
    else:
        st.info("Esperando el sorteo de la Ronda 1...")

elif st.session_state.seccion_activa == "RESULTADOS":
    st.header("Carga de Resultados")
    st.info("Módulo en desarrollo para la siguiente fase.")

elif st.session_state.seccion_activa == "RANKING":
    st.header("Ranking General ADEL")
    st.info("El ranking se actualizará al cargar resultados.")
