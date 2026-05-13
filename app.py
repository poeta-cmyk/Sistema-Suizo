import streamlit as st
import math

# --- 1. CONFIGURACIÓN ---
st.set_page_config(layout="wide", page_title="SISTEMA ADEL")

if 'asistentes' not in st.session_state:
    st.session_state.update({
        'asistentes': [], 
        'estados': {}, # Nuevo: Para saber quién sigue jugando y quién se retiró
        'juegos_ganados': {}, 
        'efectividad': {}, 
        'puntos_contra': {}, 
        'puntos_favor': {}, 
        'historial_completo': []
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

# --- 4. SECCIÓN: INSCRIPCIÓN (SIEMPRE ABIERTA) ---
if opcion == "INSCRIPCIÓN":
    st.caption("Creado por Poeta")
    st.header("ASOCIACIÓN DE DOMINÓ DEL ESTADO LARA ADEL SISTEMA SUIZO")
    st.subheader("Control de Nómina y Asistencia")
    
    def procesar_registro():
        nuevo = st.session_state.campo_nombre.upper().strip()
        if nuevo and nuevo not in st.session_state.asistentes:
            st.session_state.asistentes.append(nuevo)
            st.session_state.asistentes.sort()
            st.session_state.estados[nuevo] = True # Por defecto entra ACTIVO
            for k in ['juegos_ganados', 'puntos_contra', 'puntos_favor']: 
                st.session_state[k][nuevo] = 0
            st.session_state.efectividad[nuevo] = 1.0
        st.session_state.campo_nombre = ""

    st.text_input("Agregar Atleta nuevo:", key="campo_nombre", on_change=procesar_registro)
    
    if st.session_state.asistentes:
        # Contamos solo los que están marcados como Activos para el sorteo
        activos = [n for n in st.session_state.asistentes if st.session_state.estados[n]]
        st.write(f"### Atletas en Nómina: {len(st.session_state.asistentes)} (Activos para sorteo: {len(activos)})")
        
        for n in st.session_state.asistentes:
            col_n, col_st, col_br = st.columns([3, 1, 1])
            col_n.text(f"• {n}")
            
            # Switch para retirar sin eliminar sus números
            estado_actual = st.session_state.estados[n]
            label_st = "✅ ACTIVO" if estado_actual else "❌ RETIRADO"
            if col_st.button(label_st, key=f"st_{n}"):
                st.session_state.estados[n] = not estado_actual
                st.rerun()

            # El botón borrar solo se usa si se cargó a alguien por error total
            if col_br.button("🗑️", key=f"br_{n}"):
                st.session_state.asistentes.remove(n)
                del st.session_state.estados[n]
                st.rerun()

# --- 5. SECCIÓN: MESAS (SORTEO) ---
elif opcion == "MESAS":
    st.caption("Creado por Poeta")
    st.header("Generación de Rondas")
    
    # Solo sorteamos a los que están "ACTIVOS"
    jugadores_disponibles = [n for n in st.session_state.asistentes if st.session_state.estados[n]]
    
    if st.button("🚀 SORTEAR SIGUIENTE RONDA"):
        n_jug = (len(jugadores_disponibles) // 4) * 4
        mesas = [jugadores_disponibles[i:i+4] for i in range(0, n_jug, 4)]
        st.session_state.historial_completo.append({
            'ronda': len(st.session_state.historial_completo) + 1, 
            'mesas': mesas, 
            'reposo': jugadores_disponibles[n_jug:]
        })
        st.rerun()

    if st.session_state.historial_completo:
        r = st.session_state.historial_completo[-1]
        st.subheader(f"Carga de Resultados - Ronda {r['ronda']}")
        for i, m in enumerate(r['mesas']):
            with st.expander(f"MESA {i+1}: {', '.join(m)}", expanded=True):
                c1, c2 = st.columns(2)
                p_ac = c1.number_input(f"Puntos A+C", key=f"ac_{r['ronda']}_{i}", min_value=0)
                p_bd = c2.number_input(f"Puntos B+D", key=f"bd_{r['ronda']}_{i}", min_value=0)
                if st.button(f"GUARDAR MESA {i+1}", key=f"btn_{r['ronda']}_{i}"):
                    # (Lógica de guardado de puntos igual a la anterior...)
                    st.success("Guardado")

# --- 6. SECCIÓN: RANKING (PANTALLA DE RESULTADOS) ---
elif opcion == "RANKING":
    st.caption("Creado por Poeta")
    st.header("Ranking General del Torneo")
    # Aquí aparecen TODOS (activos y retirados) ordenados por mérito
    lista_ranking = sorted(st.session_state.asistentes, 
                          key=lambda x: (st.session_state.juegos_ganados[x], st.session_state.efectividad[x]), 
                          reverse=True)
    for n in lista_ranking:
        status = "" if st.session_state.estados[n] else " (RETIRADO)"
        st.write(f"**{n}{status}** | JG: {st.session_state.juegos_ganados[n]} | Ef: {st.session_state.efectividad[n]:.4f}")

# --- 7. SECCIÓN: PANTALLA ADEL ---
elif opcion == "PANTALLA ADEL":
    st.caption("Creado por Poeta")
    st.header("Monitor Oficial ADEL")
    # (Misma lógica de visualización de mesas anterior...)
