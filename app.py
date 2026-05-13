import streamlit as st
import math
import random

# --- 1. CONFIGURACIÓN Y ESTADO INICIAL ---
st.set_page_config(layout="wide", page_title="SISTEMA ADEL")

# Inicialización segura para evitar el error de la captura image_2d80ef.png
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
        'meta_torneo': 100,
        'seccion_activa': "INSCRIPCIÓN"
    })

def recalcular_baremo(atleta):
    pf = st.session_state.puntos_favor.get(atleta, 0)
    pc = st.session_state.puntos_contra.get(atleta, 0)
    v_f = pf if pf > 0 else 1
    v_c = pc if pc > 0 else 1
    st.session_state.efectividad[atleta] = math.log10(v_f / v_c) + 1

# --- 2. NAVEGACIÓN ---
with st.sidebar:
    st.title("🏆 MENÚ ADEL")
    # Sincronización de navegación para el salto automático
    lista_paginas = ["INSCRIPCIÓN", "MESAS", "RESULTADOS", "RANKING"]
    idx_actual = lista_paginas.index(st.session_state.seccion_activa)
    opcion = st.radio("SECCIÓN:", lista_paginas, index=idx_actual)
    st.session_state.seccion_activa = opcion

# --- 3. SECCIÓN: INSCRIPCIÓN ---
if st.session_state.seccion_activa == "INSCRIPCIÓN":
    st.caption("Creado por Poeta")
    st.header("ASOCIACIÓN DE DOMINÓ DEL ESTADO LARA ADEL SISTEMA SUIZO")
    
    # Selector de Meta solicitado
    st.subheader("Configuración de la Partida")
    st.session_state.meta_torneo = st.radio("Meta del encuentro:", [100, 200], horizontal=True)
    
    def agregar_atleta():
        nom = st.session_state.nuevo_atleta.upper().strip()
        if nom and nom not in st.session_state.asistentes:
            st.session_state.asistentes.append(nom)
            st.session_state.estados[nom] = True
            st.session_state.juegos_ganados[nom] = 0
            st.session_state.puntos_favor[nom] = 0
            st.session_state.puntos_contra[nom] = 0
            st.session_state.efectividad[nom] = 1.0
            st.session_state.asistentes.sort()
        st.session_state.nuevo_atleta = ""

    st.text_input("Nombre del Atleta + ENTER:", key="nuevo_atleta", on_change=agregar_atleta)
    
    activos = [n for n in st.session_state.asistentes if st.session_state.estados[n]]
    st.write(f"### Atletas en Nómina: {len(st.session_state.asistentes)} (Activos: {len(activos)})")

    # BOTÓN DE SORTEO Y SALTO AUTOMÁTICO
    if st.button("🚀 REALIZAR SORTEO Y IR A RESULTADOS"):
        if len(activos) < 4:
            st.error("Se necesitan al menos 4 atletas activos.")
        else:
            random.shuffle(activos)
            n_jug = (len(activos) // 4) * 4
            mesas = [activos[i:i+4] for i in range(0, n_jug, 4)]
            reposo = activos[n_jug:]
            
            # Bonificación de Reposo: Mitad de meta a cero
            bono = st.session_state.meta_torneo / 2
            for r in reposo:
                st.session_state.puntos_favor[r] += bono
                st.session_state.juegos_ganados[r] += 1
                recalcular_baremo(r)
            
            st.session_state.historial_completo.append({
                'ronda': len(st.session_state.historial_completo) + 1, 
                'mesas': mesas, 
                'reposo': reposo,
                'listas': []
            })
            st.session_state.seccion_activa = "RESULTADOS"
            st.rerun()

    # Visualización de lista
    for n in st.session_state.asistentes:
        c1, c2, c3 = st.columns([4, 1, 1])
        c1.text(f"• {n}")
        if c2.button("✅" if st.session_state.estados[n] else "❌", key=f"st_{n}"):
            st.session_state.estados[n] = not st.session_state.estados[n]; st.rerun()
        if c3.button("🗑️", key=f"del_{n}"):
            st.session_state.asistentes.remove(n); st.rerun()

# --- 4. SECCIÓN: RESULTADOS ---
elif st.session_state.seccion_activa == "RESULTADOS":
    st.header("Carga de Resultados Técnicos")
    if not st.session_state.historial_completo:
        st.warning("Primero realice el sorteo en INSCRIPCIÓN.")
    else:
        r = st.session_state.historial_completo[-1]
        st.subheader(f"RONDA {r['ronda']} (Meta: {st.session_state.meta_torneo})")
        
        if r['reposo']:
            st.info(f"💤 REPOSO: {', '.join(r['reposo'])} (+{st.session_state.meta_torneo/2} pts)")

        for i, m in enumerate(r['mesas']):
            if i in r['listas']:
                st.success(f"MESA {i+1} PROCESADA")
            else:
                with st.container(border=True):
                    st.write(f"### MESA {i+1}")
                    col1, col2 = st.columns(2)
                    # Formato Nombre (Silla) solicitado
                    val_ac = col1.number_input(f"Puntos {m[0]} (A) y {m[2]} (C):", 0, 250, key=f"ac_{i}")
                    val_bd = col2.number_input(f"Puntos {m[1]} (B) y {m[3]} (D):", 0, 250, key=f"bd_{i}")
                    
                    if st.button(f"GUARDAR MESA {i+1}", key=f"btn_{i}"):
                        for j in [m[0], m[2]]:
                            st.session_state.puntos_favor[j] += val_ac
                            st.session_state.puntos_contra[j] += val_bd
                            if val_ac > val_bd: st.session_state.juegos_ganados[j] += 1
                        for j in [m[1], m[3]]:
                            st.session_state.puntos_favor[j] += val_bd
                            st.session_state.puntos_contra[j] += val_ac
                            if val_bd > val_ac: st.session_state.juegos_ganados[j] += 1
                        for j in m: recalcular_baremo(j)
                        r['listas'].append(i)
                        st.rerun()

# --- 5. SECCIÓN: RANKING ---
elif st.session_state.seccion_activa == "RANKING":
    st.header("Clasificación Oficial")
    if st.session_state.asistentes:
        tabla = sorted(st.session_state.asistentes, 
                       key=lambda x: (st.session_state.juegos_ganados[x], st.session_state.efectividad[x]), 
                       reverse=True)
        st.table([{"Pos": i+1, "Atleta": n, "JJ": st.session_state.juegos_ganados[n], 
                   "PF": st.session_state.puntos_favor[n], "PC": st.session_state.puntos_contra[n], 
                   "Efectividad": f"{st.session_state.efectividad[n]:.4f}"} for i, n in enumerate(tabla)])
