import streamlit as st
import math
import random

# --- 1. CONFIGURACIÓN E INICIALIZACIÓN (Obligatorio al inicio) ---
st.set_page_config(layout="wide", page_title="SISTEMA ADEL")

# Inicializamos la memoria del sistema para evitar el NameError
if 'asistentes' not in st.session_state:
    st.session_state.update({
        'asistentes': [], 
        'estados': {}, 
        'jg': {}, 
        'jj': {}, 
        'iep': {}, 
        'efec': {}, 
        'dif': {}, 
        'editando': None,
        'historial_completo': [], 
        'seccion_activa': "INSCRIPCIÓN", 
        'meta_encuentro': 200
    })

# --- 2. FUNCIONES TÉCNICAS ADEL ---
def actualizar_baremos_adel(atleta):
    jg = st.session_state.jg.get(atleta, 0)
    jj = st.session_state.jj.get(atleta, 0)
    st.session_state.iep[atleta] = (jg / jj * 1000) if jj > 0 else 0

# --- 3. NAVEGACIÓN LATERAL ---
with st.sidebar:
    st.title("🏆 MENÚ ADEL")
    opciones = ["INSCRIPCIÓN", "MESAS", "RESULTADOS", "RANKING"]
    # Esta línea ya no dará error porque la memoria se inicializó arriba
    st.session_state.seccion_activa = st.radio("SECCIÓN:", opciones, 
                                              index=opciones.index(st.session_state.seccion_activa))

# --- 4. SECCIÓN: INSCRIPCIÓN (Con Monitor de Atletas y Activos) ---
if st.session_state.seccion_activa == "INSCRIPCIÓN":
    st.header("ASOCIACIÓN DE DOMINÓ DEL ESTADO LARA ADEL")
    
    st.session_state.meta_encuentro = st.radio("Meta del encuentro:", [100, 200], 
                                              index=1 if st.session_state.meta_encuentro == 200 else 0, 
                                              horizontal=True)

    def agregar_atleta():
        nom = st.session_state.campo_nom.upper().strip()
        if nom and nom not in st.session_state.asistentes:
            st.session_state.asistentes.append(nom)
            st.session_state.estados[nom] = True
            for k in ['jg', 'jj', 'iep', 'efec', 'dif']:
                st.session_state[k][nom] = 0
            st.session_state.asistentes.sort()
        st.session_state.campo_nom = ""

    st.text_input("Nombre del Atleta + ENTER:", key="campo_nom", on_change=agregar_atleta)

    # --- MONITOR SOLICITADO: ATLETAS Y ACTIVOS ---
    total_inscritos = len(st.session_state.asistentes)
    total_activos = sum(1 for n in st.session_state.asistentes if st.session_state.estados[n])
    
    st.subheader(f"📊 ATLETAS: {total_inscritos} | ACTIVOS: {total_activos}")
    st.divider()

    # Listado de Atletas con botones
    for nombre in st.session_state.asistentes:
        col_nom, col_check, col_edit, col_del = st.columns([3, 1, 1, 1])
        
        status_label = "👤" if st.session_state.estados[nombre] else "❌ (RETIRADO)"
        col_nom.markdown(f"**{nombre}** {status_label}")
        
        # Botón para Activar/Retirar (Actualiza el conteo de ACTIVOS)
        if col_check.button("✅" if st.session_state.estados[nombre] else "💤", key=f"st_{nombre}"):
            st.session_state.estados[nombre] = not st.session_state.estados[nombre]
            st.rerun()
        
        if col_edit.button("📝", key=f"ed_{nombre}"):
            st.session_state.editando = nombre
            st.rerun()
            
        if col_del.button("🗑️", key=f"del_{nombre}"):
            st.session_state.asistentes.remove(nombre)
            st.rerun()

    # Edición de nombres
    if st.session_state.editando:
        with st.container(border=True):
            nuevo_n = st.text_input("Corregir nombre:", value=st.session_state.editando).upper()
            if st.button("ACEPTAR"):
                v = st.session_state.editando
                idx = st.session_state.asistentes.index(v)
                st.session_state.asistentes[idx] = nuevo_n
                for k in ['estados', 'jg', 'jj', 'iep', 'efec', 'dif']:
                    st.session_state[k][nuevo_n] = st.session_state[k].pop(v)
                st.session_state.editando = None
                st.session_state.asistentes.sort()
                st.rerun()

    if st.button("🚀 SORTEAR E IR A MESAS"):
        activos = [n for n in st.session_state.asistentes if st.session_state.estados[n]]
        if len(activos) >= 4:
            random.shuffle(activos)
            n_m = (len(activos) // 4) * 4
            st.session_state.historial_completo.append({
                'mesas': [activos[i:i+4] for i in range(0, n_m, 4)],
                'reposo': activos[n_m:], 'listas': [], 'reposo_ok': False
            })
            st.session_state.seccion_activa = "MESAS"; st.rerun()

# --- 5. SECCIÓN: RESULTADOS (Cálculo de Efectividad ADEL) ---
elif st.session_state.seccion_activa == "RESULTADOS":
    st.header("Carga de Resultados")
    if st.session_state.historial_completo:
        r = st.session_state.historial_completo[-1]
        meta = st.session_state.meta_encuentro
        
        # Reposo: Victoria automática (IEP=1000, EFEC=Meta/2)
        if r.get('reposo') and not r.get('reposo_ok'):
            for p in r['reposo']:
                st.session_state.jj[p] += 1; st.session_state.jg[p] += 1
                st.session_state.efec[p] += (meta // 2)
                actualizar_baremos_adel(p)
            r['reposo_ok'] = True

        for i, m in enumerate(r['mesas']):
            if i not in r['listas']:
                with st.expander(f"MESA {i+1}", expanded=True):
                    c1, c2 = st.columns(2)
                    v1 = c1.number_input(f"Pareja A-C ({m[0]}/{m[2]}):", 0, 300, key=f"v1_{i}")
                    v2 = c2.number_input(f"Pareja B-D ({m[1]}/{m[3]}):", 0, 300, key=f"v2_{i}")
                    if st.button(f"GUARDAR MESA {i+1}", key=f"b_{i}"):
                        gan, perd, p_gan, p_perd = ([m[0], m[2]], [m[1], m[3]], v1, v2) if v1 > v2 else ([m[1], m[3]], [m[0], m[2]], v2, v1)
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

# --- 6. SECCIÓN: RANKING (Según Modelo de Imagen) ---
elif st.session_state.seccion_activa == "RANKING":
    st.header("Ranking General")
    if st.session_state.asistentes:
        orden = sorted(st.session_state.asistentes, 
                       key=lambda x: (st.session_state.iep[x], st.session_state.efec[x], st.session_state.dif[x]), 
                       reverse=True)
        
        # Tabla limpia: IEP, EFEC, DIF
        datos_tabla = []
        for i, n in enumerate(orden):
            datos_tabla.append({
                "Pos": i + 1, "Atleta": n,
                "IEP": int(st.session_state.iep[n]),
                "EFEC": st.session_state.efec[n],
                "DIF": st.session_state.dif[n]
            })
        st.table(datos_tabla)
