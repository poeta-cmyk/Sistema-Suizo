import streamlit as st
import math
import random

# --- 1. CONFIGURACIÓN E INICIALIZACIÓN ---
st.set_page_config(layout="wide", page_title="SISTEMA ADEL")

if 'asistentes' not in st.session_state:
    st.session_state.update({
        'asistentes': [], 'estados': {}, 'jg': {}, 'jj': {}, 
        'iep': {}, 'efec': {}, 'dif': {},
        'puntos_favor': {}, 'puntos_contra': {}, 'historial_completo': [],
        'seccion_activa': "INSCRIPCIÓN", 'meta_encuentro': 200
    })

# --- 2. LÓGICA DE BAREMOS ADEL ---
def actualizar_baremos_adel(atleta):
    # 1er Baremo: IEP (JG / JJ * 1000)
    jg = st.session_state.jg.get(atleta, 0)
    jj = st.session_state.jj.get(atleta, 0)
    st.session_state.iep[atleta] = (jg / jj * 1000) if jj > 0 else 0
    
    # El 2do (EFEC) y 3er (DIF) baremo se calculan directo en la carga de resultados

# --- 3. NAVEGACIÓN ---
with st.sidebar:
    st.title("🏆 MENÚ ADEL")
    opciones = ["INSCRIPCIÓN", "MESAS", "RESULTADOS", "RANKING"]
    st.session_state.seccion_activa = st.radio("SECCIÓN:", opciones, 
                                              index=opciones.index(st.session_state.seccion_activa))

# --- 4. SECCIÓN: INSCRIPCIÓN ---
if st.session_state.seccion_activa == "INSCRIPCIÓN":
    st.header("ASOCIACIÓN DE DOMINÓ DEL ESTADO LARA ADEL")
    st.session_state.meta_encuentro = st.radio("Meta del encuentro:", [100, 200], index=1, horizontal=True)

    nom = st.text_input("Nombre del Atleta + ENTER:").upper().strip()
    if nom and nom not in st.session_state.asistentes:
        st.session_state.asistentes.append(nom)
        st.session_state.estados[nom] = True
        for k in ['jg', 'jj', 'iep', 'efec', 'dif', 'puntos_favor', 'puntos_contra']:
            st.session_state[k][nom] = 0
        st.rerun()

    if st.button("🚀 SORTEAR E IR A MESAS"):
        activos = [n for n in st.session_state.asistentes if st.session_state.estados[n]]
        if len(activos) >= 4:
            random.shuffle(activos)
            n_jug = (len(activos) // 4) * 4
            st.session_state.historial_completo.append({
                'ronda': len(st.session_state.historial_completo) + 1,
                'mesas': [activos[i:i+4] for i in range(0, n_jug, 4)],
                'reposo': activos[n_jug:], 'listas': [], 'reposo_procesado': False
            })
            st.session_state.seccion_activa = "MESAS"; st.rerun()

# --- 5. SECCIÓN: RESULTADOS (Lógica de Meta, EFEC y DIF) ---
elif st.session_state.seccion_activa == "RESULTADOS":
    st.header("Carga de Resultados")
    if st.session_state.historial_completo:
        r = st.session_state.historial_completo[-1]
        meta = st.session_state.meta_encuentro
        
        # Procesar Reposo (Victoria IEP=1000, EFEC=+Meta/2, DIF=0)
        if r.get('reposo') and not r['reposo_procesado']:
            for p in r['reposo']:
                st.session_state.jj[p] += 1; st.session_state.jg[p] += 1
                st.session_state.efec[p] += (meta // 2)
                actualizar_baremos_adel(p)
            r['reposo_procesado'] = True

        for i, m in enumerate(r['mesas']):
            if i not in r['listas']:
                with st.expander(f"MESA {i+1}", expanded=True):
                    c1, c2 = st.columns(2)
                    v1 = c1.number_input(f"Pareja A-C ({m[0]}/{m[2]}):", 0, 300, key=f"v1_{i}")
                    v2 = c2.number_input(f"Pareja B-D ({m[1]}/{m[3]}):", 0, 300, key=f"v2_{i}")
                    if st.button(f"GUARDAR MESA {i+1}", key=f"b_{i}"):
                        gan, perd, p_gan, p_perd = ([m[0], m[2]], [m[1], m[3]], v1, v2) if v1 > v2 else ([m[1], m[3]], [m[0], m[2]], v2, v1)
                        # Aplicar Baremos
                        for p in gan:
                            st.session_state.jj[p] += 1; st.session_state.jg[p] += 1
                            st.session_state.efec[p] += (meta - p_perd)
                            st.session_state.dif[p] += (p_gan - p_perd)
                            actualizar_baremos_adel(p)
                        for p in perd:
                            st.session_state.jj[p] += 1
                            st.session_state.efec[p] -= (meta - p_perd)
                            st.session_state.dif[p] -= (p_gan - p_perd)
                            actualizar_baremos_adel(p)
                        r['listas'].append(i); st.rerun()

# --- 6. SECCIÓN: RANKING (Según Modelo del Usuario) ---
elif st.session_state.seccion_activa == "RANKING":
    st.header("Ranking General")
    if st.session_state.asistentes:
        # Orden de prioridad: IEP -> EFEC -> DIF
        ranking = sorted(st.session_state.asistentes, 
                         key=lambda x: (st.session_state.iep[x], st.session_state.efec[x], st.session_state.dif[x]), 
                         reverse=True)
        
        # TABLA SEGÚN MODELO image_757575.png
        tabla_modelo = []
        for i, nom in enumerate(ranking):
            tabla_modelo.append({
                "Pos": i + 1,
                "Atleta": nom,
                "IEP": int(st.session_state.iep[nom]),
                "EFEC": st.session_state.efec[nom],
                "DIF": st.session_state.dif[nom]
            })
        st.table(tabla_modelo)
