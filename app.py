import streamlit as st
import math
import random

# --- 1. CONFIGURACIÓN E INICIALIZACIÓN ---
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
        'editando': None,
        'meta': 100,
        'pagina_actual': "INSCRIPCIÓN"
    })

def recalcular_baremo(atleta):
    pf = st.session_state.puntos_favor.get(atleta, 0)
    pc = st.session_state.puntos_contra.get(atleta, 0)
    v_f = pf if pf > 0 else 1
    v_c = pc if pc > 0 else 1
    st.session_state.efectividad[atleta] = math.log10(v_f / v_c) + 1

# --- 2. MENÚ DINÁMICO ---
with st.sidebar:
    st.title("🏆 MENÚ ADEL")
    # El radio button ahora se sincroniza con la navegación automática
    opcion = st.radio("SECCIÓN:", ["INSCRIPCIÓN", "MESAS", "RESULTADOS", "RANKING"], 
                      index=["INSCRIPCIÓN", "MESAS", "RESULTADOS", "RANKING"].index(st.session_state.pagina_actual),
                      key="navegacion")
    st.session_state.pagina_actual = opcion

# --- 3. SECCIÓN: INSCRIPCIÓN ---
if st.session_state.pagina_actual == "INSCRIPCIÓN":
    st.caption("Creado por Poeta")
    st.header("ASOCIACIÓN DE DOMINÓ DEL ESTADO LARA ADEL SISTEMA SUIZO")
    
    # NUEVO: Selección de Meta
    st.subheader("Configuración del Evento")
    st.session_state.meta = st.radio("Meta del encuentro (Puntos):", [100, 200], horizontal=True)
    
    def procesar_entrada():
        texto = st.session_state.campo_input.upper().strip()
        if texto:
            if st.session_state.editando:
                viejo = st.session_state.editando
                if texto != viejo:
                    idx = st.session_state.asistentes.index(viejo)
                    st.session_state.asistentes[idx] = texto
                    for k in ['estados', 'juegos_ganados', 'puntos_contra', 'puntos_favor', 'efectividad']:
                        st.session_state[k][texto] = st.session_state[k].pop(viejo)
                st.session_state.editando = None
            elif texto not in st.session_state.asistentes:
                st.session_state.asistentes.append(texto)
                st.session_state.estados[texto] = True
                st.session_state.juegos_ganados[texto] = 0
                st.session_state.puntos_contra[texto] = 0
                st.session_state.puntos_favor[texto] = 0
                st.session_state.efectividad[texto] = 1.0
            st.session_state.asistentes.sort()
        st.session_state.campo_input = "" 

    st.text_input("ATLETA", key="campo_input", on_change=procesar_entrada)
    
    activos = [n for n in st.session_state.asistentes if st.session_state.estados[n]]
    st.write(f"### Atletas inscritos: {len(st.session_state.asistentes)} - Activos: {len(activos)}")
    
    # BOTÓN DE SORTEO AUTOMÁTICO (Lleva a Resultados)
    if st.button("🚀 REALIZAR SORTEO Y IR A RESULTADOS"):
        if len(activos) < 4:
            st.error("Mínimo 4 atletas activos.")
        else:
            random.shuffle(activos)
            n_jug = (len(activos) // 4) * 4
            mesas = [activos[i:i+4] for i in range(0, n_jug, 4)]
            reposo = activos[n_jug:]
            
            # Lógica de Reposo: Ganan mitad de meta a cero
            puntos_reposo = st.session_state.meta / 2
            for r in reposo:
                st.session_state.puntos_favor[r] += puntos_reposo
                st.session_state.puntos_contra[r] += 0
                st.session_state.juegos_ganados[r] += 1
                recalcular_baremo(r)
            
            st.session_state.historial_completo.append({
                'ronda': len(st.session_state.historial_completo) + 1, 
                'mesas': mesas, 
                'reposo': reposo,
                'procesadas': []
            })
            st.session_state.pagina_actual = "RESULTADOS"
            st.rerun()

    # Lista de atletas (Igual que antes)
    for n in st.session_state.asistentes:
        c_nom, c_act, c_edit = st.columns([4, 1, 1])
        c_nom.text(f"• {n}")
        if c_act.button("✅" if st.session_state.estados[n] else "❌", key=f"st_{n}"):
            st.session_state.estados[n] = not st.session_state.estados[n]; st.rerun()
        if c_edit.button("📝", key=f"ed_{n}"):
            st.session_state.editando = n; st.rerun()

# --- 4. SECCIÓN: RESULTADOS ---
elif st.session_state.pagina_actual == "RESULTADOS":
    st.header("Carga de Resultados Técnicos")
    if st.session_state.historial_completo:
        r = st.session_state.historial_completo[-1]
        st.write(f"## RONDA {r['ronda']} (Meta: {st.session_state.meta} pts)")
        
        if r['reposo']:
            st.info(f"💤 REPOSO (Bonificado con {st.session_state.meta/2} pts): {', '.join(r['reposo'])}")

        for idx, mj in enumerate(r['mesas']):
            if idx in r['procesadas']:
                st.success(f"MESA {idx+1} FINALIZADA")
            else:
                with st.container(border=True):
                    st.write(f"### MESA {idx+1}")
                    col1, col2 = st.columns(2)
                    # Formato solicitado: Nombre (Silla)
                    p1_label = f"{mj[0]} (A) y {mj[2]} (C)"
                    p2_label = f"{mj[1]} (B) y {mj[3]} (D)"
                    
                    p_ac = col1.number_input(f"Puntos {p1_label}:", 0, 250, key=f"ac_{idx}")
                    p_bd = col2.number_input(f"Puntos {p2_label}:", 0, 250, key=f"bd_{idx}")
                    
                    if st.button(f"GUARDAR MESA {idx+1}", key=f"sv_{idx}"):
                        for j in [mj[0], mj[2]]:
                            st.session_state.puntos_favor[j] += p_ac
                            st.session_state.puntos_contra[j] += p_bd
                            if p_ac > p_bd: st.session_state.juegos_ganados[j] += 1
                        for j in [mj[1], mj[3]]:
                            st.session_state.puntos_favor[j] += p_bd
                            st.session_state.puntos_contra[j] += p_ac
                            if p_bd > p_ac: st.session_state.juegos_ganados[j] += 1
                        for j in mj: recalcular_baremo(j)
                        r['procesadas'].append(idx)
                        st.rerun()
    else:
        st.warning("Debe realizar el sorteo en la pestaña de INSCRIPCIÓN.")

# --- 5. SECCIÓN: MESAS (VISTA PÚBLICA) ---
elif st.session_state.pagina_actual == "MESAS":
    st.header("Distribución de Mesas")
    if st.session_state.historial_completo:
        r = st.session_state.historial_completo[-1]
        for idx, mj in enumerate(r['mesas']):
            with st.container(border=True):
                st.write(f"### MESA {idx+1}")
                st.write(f"**Norte-Sur:** {mj[0]} (A) y {mj[2]} (C)")
                st.write(f"**Este-Oeste:** {mj[1]} (B) y {mj[3]} (D)")
    else:
        st.info("No hay sorteo activo.")

# --- 6. SECCIÓN: RANKING ---
elif st.session_state.pagina_actual == "RANKING":
    st.header("Clasificación Oficial")
    if st.session_state.asistentes:
        tabla = sorted(st.session_state.asistentes, 
                       key=lambda x: (st.session_state.juegos_ganados[x], st.session_state.efectividad[x]), 
                       reverse=True)
        st.table([{"Pos": i+1, "Atleta": n, "JJ": st.session_state.juegos_ganados[n], 
                   "PF": st.session_state.puntos_favor[n], "PC": st.session_state.puntos_contra[n], 
                   "Efectividad": f"{st.session_state.efectividad[n]:.4f}"} for i, n in enumerate(tabla)])
