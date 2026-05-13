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
        'editando': None 
    })

# --- 2. BAREMO LOGARÍTMICO ---
def recalcular_baremo(atleta):
    pf = st.session_state.puntos_favor.get(atleta, 0)
    pc = st.session_state.puntos_contra.get(atleta, 0)
    v_f = pf if pf > 0 else 1
    v_c = pc if pc > 0 else 1
    st.session_state.efectividad[atleta] = math.log10(v_f / v_c) + 1

# --- 3. MENÚ ---
with st.sidebar:
    st.title("🏆 MENÚ ADEL")
    opcion = st.radio("SECCIÓN:", ["INSCRIPCIÓN", "MESAS", "RESULTADOS", "RANKING"])

# --- 4. SECCIÓN: INSCRIPCIÓN ---
if opcion == "INSCRIPCIÓN":
    st.caption("Creado por Poeta")
    st.header("ASOCIACIÓN DE DOMINÓ DEL ESTADO LARA ADEL SISTEMA SUIZO")
    st.subheader("Control de Nómina y Asistencia")
    
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

    label_dinamico = f"Corrigiendo a: {st.session_state.editando}" if st.session_state.editando else "ATLETA"
    st.text_input(label_dinamico, key="campo_input", on_change=procesar_entrada)
    
    if st.session_state.asistentes:
        activos = [n for n in st.session_state.asistentes if st.session_state.estados[n]]
        st.write(f"### Atletas inscritos: {len(st.session_state.asistentes)} - Activos: {len(activos)}")
        for n in st.session_state.asistentes:
            c_nom, c_act, c_edit, c_del = st.columns([3, 1, 1, 1])
            c_nom.text(f"• {n}")
            if c_act.button("✅ ACTIVO" if st.session_state.estados[n] else "❌ RETIRADO", key=f"st_{n}"):
                st.session_state.estados[n] = not st.session_state.estados[n]; st.rerun()
            if c_edit.button("📝", key=f"ed_{n}"):
                st.session_state.editando = n; st.rerun()
            if c_del.button("🗑️", key=f"br_{n}"):
                st.session_state.asistentes.remove(n); st.rerun()

# --- 5. SECCIÓN: RESULTADOS (LA MESA TÉCNICA) ---
elif opcion == "RESULTADOS":
    st.caption("Creado por Poeta")
    st.header("ASOCIACIÓN DE DOMINÓ DEL ESTADO LARA ADEL SISTEMA SUIZO")
    st.subheader("Carga de Resultados Técnicos")
    
    activos = [n for n in st.session_state.asistentes if st.session_state.estados[n]]
    
    if st.button("🚀 SORTEAR SIGUIENTE RONDA"):
        if len(activos) < 4:
            st.error("Se necesitan al menos 4 atletas activos.")
        else:
            random.shuffle(activos)
            n_jug = (len(activos) // 4) * 4
            mesas = [activos[i:i+4] for i in range(0, n_jug, 4)]
            st.session_state.historial_completo.append({
                'ronda': len(st.session_state.historial_completo) + 1, 
                'mesas': mesas, 
                'reposo': activos[n_jug:],
                'procesadas': [] 
            })
            st.rerun()

    if st.session_state.historial_completo:
        r = st.session_state.historial_completo[-1]
        st.write(f"## RONDA {r['ronda']}")
        
        for idx, mj in enumerate(r['mesas']):
            # Si la mesa ya fue guardada, no mostramos los controles de entrada
            if idx in r['procesadas']:
                st.success(f"MESA {idx+1}: RESULTADO REGISTRADO")
                continue

            with st.container(border=True):
                st.write(f"### MESA {idx+1}")
                c1, c2 = st.columns(2)
                
                # Pareja A+C vs Pareja B+D
                puntos_ac = c1.number_input(f"Puntos {mj[0]} y {mj[2]} (A+C):", min_value=0, max_value=100, key=f"ac_{r['ronda']}_{idx}")
                puntos_bd = c2.number_input(f"Puntos {mj[1]} y {mj[3]} (B+D):", min_value=0, max_value=100, key=f"bd_{r['ronda']}_{idx}")
                
                if st.button(f"GUARDAR MESA {idx+1}", key=f"btn_{r['ronda']}_{idx}"):
                    # Sumar puntos y juegos ganados
                    for j in [mj[0], mj[2]]:
                        st.session_state.puntos_favor[j] += puntos_ac
                        st.session_state.puntos_contra[j] += puntos_bd
                        if puntos_ac > puntos_bd: st.session_state.juegos_ganados[j] += 1
                    
                    for j in [mj[1], mj[3]]:
                        st.session_state.puntos_favor[j] += puntos_bd
                        st.session_state.puntos_contra[j] += puntos_ac
                        if puntos_bd > puntos_ac: st.session_state.juegos_ganados[j] += 1
                    
                    # Recalcular baremo de todos en la mesa
                    for j in mj: recalcular_baremo(j)
                    
                    r['procesadas'].append(idx)
                    st.rerun()

# --- 6. SECCIÓN: MESAS (PANTALLA PÚBLICA) ---
elif opcion == "MESAS":
    st.caption("Creado por Poeta")
    st.header("ASOCIACIÓN DE DOMINÓ DEL ESTADO LARA ADEL SISTEMA SUIZO")
    st.subheader("Distribución de Mesas")
    if st.session_state.historial_completo:
        r = st.session_state.historial_completo[-1]
        if r['reposo']: st.warning(f"⌛ EN REPOSO: {', '.join(r['reposo'])}")
        for idx, mj in enumerate(r['mesas']):
            with st.container(border=True):
                st.write(f"**MESA {idx+1}**")
                st.write(f"Pareja 1 (A+C): {mj[0]} y {mj[2]}")
                st.write(f"Pareja 2 (B+D): {mj[1]} y {mj[3]}")
    else:
        st.info("No hay sorteo activo.")

# --- 7. SECCIÓN: RANKING ---
elif opcion == "RANKING":
    st.caption("Creado por Poeta")
    st.header("ASOCIACIÓN DE DOMINÓ DEL ESTADO LARA ADEL SISTEMA SUIZO")
    st.subheader("Clasificación Oficial")
    if st.session_state.asistentes:
        # Ordenar por Juegos Ganados y luego por Efectividad
        tabla = sorted(st.session_state.asistentes, 
                       key=lambda x: (st.session_state.juegos_ganados[x], st.session_state.efectividad[x]), 
                       reverse=True)
        
        cols = st.columns([1, 3, 1, 1, 1, 2])
        headers = ["Pos", "Atleta", "JJ", "PF", "PC", "Efectividad"]
        for col, h in zip(cols, headers): col.bold(h)
        
        for i, nom in enumerate(tabla):
            c = st.columns([1, 3, 1, 1, 1, 2])
            c[0].text(i+1)
            c[1].text(nom)
            c[2].text(st.session_state.juegos_ganados[nom])
            c[3].text(st.session_state.puntos_favor[nom])
            c[4].text(st.session_state.puntos_contra[nom])
            c[5].text(f"{st.session_state.efectividad[nom]:.4f}")
