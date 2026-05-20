import streamlit as st
import pandas as pd
import random

# --- 1. CONFIGURACIÓN INICIAL ---
st.set_page_config(layout="wide", page_title="SISTEMA ADEL")

if 'asistentes' not in st.session_state:
    st.session_state.asistentes = []
if 'historial_completo' not in st.session_state:
    st.session_state.historial_completo = []
if 'meta_puntos' not in st.session_state:
    st.session_state.meta_puntos = 200

# Estructura histórica por atleta
if 'historial_atletas' not in st.session_state:
    st.session_state.historial_atletas = {}

# Diccionario para controlar el estatus del atleta ("ACTIVO" o "RETIRADO")
if 'estatus_atletas' not in st.session_state:
    st.session_state.estatus_atletas = {}

if 'seccion_activa' not in st.session_state:
    st.session_state.seccion_activa = "INSCRIPCIÓN"
if 'editando' not in st.session_state:
    st.session_state.editando = None

# Base de datos del Reglamento ADEL
DICCIONARIO_SANCIONES = {
    "Ninguna": {"tipo": "NADA", "valor": 0, "txt": "Sin infracción"},
    "Art. 67 - Retraso a la mesa": {"tipo": "CONCLUYE_PARTIDO", "valor": 1.0, "txt": "TR - Concluye el partido (Meta/Meta)"},
    "Art. 68 - Tiempo de jugadas 5/20/60": {"tipo": "PORCENTAJE", "valor": 0.20, "txt": "TA - Concluye la mano (–20%)"},
    "Art. 69 - Fumar, comer o tomar": {"tipo": "EXPULSION", "valor": 0.0, "txt": "TR - Concluye el partido (0/Meta)"},
    "Art. 70 - Hablar o uso de dispositivo": {"tipo": "PORCENTAJE", "valor": 0.20, "txt": "TA - Concluye la mano (–20%)"},
    "Art. 71 - Señas": {"tipo": "EXPULSION", "valor": 0.0, "txt": "TR - Concluye el partido (0/Meta)"},
    "Art. 72 - Quejas, recriminar conductas": {"tipo": "PORCENTAJE", "valor": 0.20, "txt": "TA - Concluye la mano (–20%)"},
    "Art. 73 - Hablar o alzar la voz": {"tipo": "PORCENTAJE", "valor": 0.20, "txt": "TA - Concluye la mano (–20%)"},
    "Art. 74 - Inicio de la partida": {"tipo": "PORCENTAJE", "valor": 0.20, "txt": "TA - Concluye la mano (–20%)"},
    "Art. 75 - Caída de las fichas": {"tipo": "PORCENTAJE", "valor": 0.20, "txt": "TA - Decide pareja contraria (–20%)"},
    "Art. 76 - Jugada adelantada": {"tipo": "PORCENTAJE", "valor": 0.20, "txt": "Decide pareja contraria (–20%)"},
    "Art. 77 - No entra la ficha tocada": {"tipo": "PORCENTAJE", "valor": 0.20, "txt": "Decide pareja contraria (–20%)"},
    "Art. 78 - Cabra": {"tipo": "PORCENTAJE", "valor": 0.40, "txt": "TA - Decide pareja contraria (–40%)"},
    "Art. 78 - Cabra (evitando cierre)": {"tipo": "EXPULSION", "valor": 0.0, "txt": "TR - Concluye el partido (0/Meta)"},
    "Art. 79 - Error al trancar": {"tipo": "PORCENTAJE", "valor": 0.20, "txt": "Decide pareja contraria (–20%)"},
    "Art. 80 - Notificación errónea pase": {"tipo": "PORCENTAJE", "valor": 0.20, "txt": "TA - Concluye la mano (–20%)"},
    "Art. 81 - Pasada con fichas": {"tipo": "PORCENTAJE", "valor": 0.40, "txt": "TA - Decide pareja contraria (–40%)"},
    "Art. 81 - Pase (evitando cierre)": {"tipo": "EXPULSION", "valor": 0.0, "txt": "TR - Concluye el partido (0/Meta)"},
    "Art. 82 - Voltear fichas antes": {"tipo": "PORCENTAJE", "valor": 0.20, "txt": "Decide pareja contraria (–20%)"},
    "Art. 83 - Romper esqueleto del juego": {"tipo": "PORCENTAJE", "valor": 0.20, "txt": "AV - (–20%)"},
    "Art. 84 - Alterar planilla intencional": {"tipo": "EXPULSION", "valor": 0.0, "txt": "TN - (0/Meta)"},
    "Art. 85/86 - Levantarse antes de la mesa": {"tipo": "EXPULSION", "valor": 0.0, "txt": "TR - (0/Meta)"},
    "Art. 90/91 - Agresión verbal/física": {"tipo": "EXPULSION", "valor": 0.0, "txt": "TN - (0/Meta)"},
    "Art. 92 - Desacatar al árbitro": {"tipo": "EXPULSION", "valor": 0.0, "txt": "TN - (0/Meta)"},
    "Art. 97 - Permanecer sala terminado": {"tipo": "PORCENTAJE", "valor": 0.20, "txt": "TA - (–20%)"}
}

# --- 2. ESTILOS CSS ---
st.markdown("""
    <style>
    .mesa-container { display: inline-flex; flex-direction: column; align-items: center; justify-content: center; width: 260px!important; height: 260px!important; margin: 20px auto; }
    .mesa-centro { width: 110px!important; height: 110px!important; border: 5px solid black; background-color: #FFFF00; display: flex; flex-direction: column; align-items: center; justify-content: center; flex-shrink: 0; }
    .adel-text { font-weight: bold; font-size: 22px; color: #003399; margin: 0; line-height: 1; }
    .n-mesa { font-weight: bold; font-size: 38px; color: #CC0000; margin: 0; line-height: 1; }
    .jugador { font-weight: bold; font-size: 16px; color: #00; text-align: center; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    .norte { width: 100%; margin-bottom: 8px; } .sur { width: 100%; margin-top: 8px; }
    .fila-central { display: flex; align-items: center; justify-content: center; width: 100%; height: 110px; gap: 5px; }
    .este-oeste { width: 40px!important; max-width: 40px!important; writing-mode: vertical-rl!important; text-orientation: mixed!important; transform: rotate(180deg); padding: 4px 0; }
    .reposo-box { background-color: #f0f2f6; border-left: 6px solid #CC0000; padding: 15px; margin-top: 25px; border-radius: 4px; }
    .panel-arbitral { background-color: #fff8e1; border: 1px dashed #ffa000; padding: 10px; border-radius: 4px; margin-top: 10px; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIÓN: GENERAR RANKING GENERAL ---
def obtener_ranking_ordenado():
    datos = []
    for atleta in st.session_state.asistentes:
        partidas = st.session_state.historial_atletas.get(atleta, [])
        tot_jg = sum(p['jg'] for p in partidas)
        tot_jj = sum(p['jj'] for p in partidas)
        tot_pf = sum(p['pf'] for p in partidas)
        tot_pc = sum(p['pc'] for p in partidas)
        tot_efec = sum(p['efec'] for p in partidas)
        
        iep = int((tot_jg / tot_jj) * 1000) if tot_jj > 0 else 0
        dif = tot_pf - tot_pc
        est = st.session_state.estatus_atletas.get(atleta, "ACTIVO")
        
        datos.append({
            "ATLETA": atleta, "ESTATUS": est, "JJ": tot_jj, "JG": tot_jg,
            "IEP": iep, "EFEC": tot_efec, "DIF": dif, "PF": tot_pf, "PC": tot_pc
        })
    if not datos: return []
    df = pd.DataFrame(datos)
    return df.sort_values(by=["IEP", "EFEC", "DIF"], ascending=[False, False, False]).reset_index(drop=True).to_dict(orient="records")

# --- 3. NAVEGACIÓN ---
with st.sidebar:
    st.title("🏆 MENÚ ADEL")
    opc = ["INSCRIPCIÓN", "MESAS", "RESULTADOS", "RANKING"]
    st.session_state.seccion_activa = st.radio("SECCIÓN:", opc, index=opc.index(st.session_state.seccion_activa))

# --- 4. SECCIÓN: INSCRIPCIÓN Y CONTROL DE BAJAS ---
if st.session_state.seccion_activa == "INSCRIPCIÓN":
    st.markdown("<h2 style='text-align:center;'>SISTEMA SUIZO ADEL</h2>", unsafe_allow_html=True)
    st.session_state.meta_puntos = st.radio("Meta del encuentro:", [100, 200], index=0 if st.session_state.meta_puntos == 100 else 1, horizontal=True)
    
    def registrar_atleta():
        raw_in = st.session_state.campo_input
        nom = raw_in.upper().strip()
        if nom:
            if st.session_state.editando:
                v = st.session_state.editando.upper().strip()
                if nom != v and v in st.session_state.asistentes:
                    pos = st.session_state.asistentes.index(v)
                    st.session_state.asistentes[pos] = nom
                    if v in st.session_state.historial_atletas:
                        st.session_state.historial_atletas[nom] = st.session_state.historial_atletas.pop(v)
                    st.session_state.estatus_atletas[nom] = st.session_state.estatus_atletas.pop(v, "ACTIVO")
                st.session_state.editando = None
            elif nom not in st.session_state.asistentes:
                st.session_state.asistentes.append(nom)
                st.session_state.historial_atletas[nom] = []
                st.session_state.estatus_atletas[nom] = "ACTIVO"
        st.session_state.campo_input = ""

    ed = st.session_state.editando
    st.text_input(f"Corrigiendo a: {ed}" if ed else "Nombre del Atleta + ENTER:", key="campo_input", on_change=registrar_atleta)
    
    activos = [a for a in st.session_state.asistentes if st.session_state.estatus_atletas.get(a, "ACTIVO") == "ACTIVO"]
    st.subheader(f"ATLETAS INSCRITOS EN SALA: {len(st.session_state.asistentes)} ({len(activos)} ACTIVOS)")

    if st.button("🚀 GENERAR SORTEO DE SALA (RONDA 1)"):
        if len(activos) >= 4:
            st.session_state.historial_completo = []
            for a in st.session_state.asistentes: st.session_state.historial_atletas[a] = []
            
            random.shuffle(activos)
            lim = (len(activos) // 4) * 4
            st.session_state.historial_completo.append({
                'ronda': 1, 'mesas': [activos[i:i+4] for i in range(0, lim, 4)],
                'reposo': activos[lim:], 'listas': [], 'reposo_asentado': False
            })
            st.session_state.seccion_activa = "MESAS"; st.rerun()
        else: st.error("Mínimo se requieren 4 atletas activos para iniciar.")

    for n in sorted(st.session_state.asistentes):
        estatus_actual = st.session_state.estatus_atletas.get(n, "ACTIVO")
        c1, c2, c3, c4 = st.columns([3, 1, 1, 1])
        
        if estatus_actual == "ACTIVO":
            c1.markdown(f"• **{n}** <span style='color:green;'>[Activo]</span>", unsafe_allow_html=True)
            if c2.button("📝", key=f"ed_{n}"): st.session_state.editando = n; st.rerun()
            if c3.button("🏳️ Retirar", key=f"ret_{n}"):
                st.session_state.estatus_atletas[n] = "RETIRADO"
                st.toast(f"{n} ha sido marcado como RETIRADO/EXPULSADO del torneo.")
                st.rerun()
        else:
            c1.markdown(f"• ~~{n}~~ <span style='color:red;'>[Retirado/Tarjeta Negra]</span>", unsafe_allow_html=True)
            st.empty() # Espacio muerto para alinear
            if c4.button("♻️ Reincorporar", key=f"reinc_{n}"):
                st.session_state.estatus_atletas[n] = "ACTIVO"
                st.rerun()

# --- 5. SECCIÓN: MESAS ---
elif st.session_state.seccion_activa == "MESAS":
    st.header("Organización de la Sala")
    if st.session_state.historial_completo:
        r = st.session_state.historial_completo[-1]
        st.subheader(f"Ronda Actual: {r['ronda']}")
        cols = st.columns(4)
        for i, m in enumerate(r['mesas']):
            with cols[i % 4]:
                st.markdown(f"""
                <div style='text-align: center;'>
                    <div class="mesa-container">
                        <div class="jugador norte">{m[0]}</div>
                        <div class="fila-central">
                            <div class="jugador este-oeste">{m[1]}</div>
                            <div class="mesa-centro"><p class="adel-text">ADEL</p><p class="n-mesa">{i+1}</p></div>
                            <div class="jugador este-oeste">{m[3]}</div>
                        </div>
                        <div class="jugador sur">{m[2]}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        if r.get('reposo'):
            st.markdown(f'<div class="reposo-box"><h4>💤 EN REPOSO EN ESTA RONDA (BYE):</h4><p><b>{", ".join(r["reposo"])}</b></p></div>', unsafe_allow_html=True)
    else: st.info("La sala está vacía. Genere el sorteo en Inscripción.")

# --- 6. SECCIÓN: RESULTADOS ---
elif st.session_state.seccion_activa == "RESULTADOS":
    st.header("Carga de Puntuaciones de Sala")
    if st.session_state.historial_completo:
        r = st.session_state.historial_completo[-1]
        meta_global = st.session_state.meta_puntos
        mitad_global = meta_global // 2
        
        # Planilla de Reposo
        if r.get('reposo') and not r.get('reposo_asentado', False):
            with st.expander("💤 ATLETAS EN REPOSO (BYE)", expanded=True):
                cols_bye = st.columns(len(r['reposo']))
                for idx, jb in enumerate(r['reposo']):
                    with cols_bye[idx]:
                        st.markdown(f"**Atleta:** {jb}")
                        st.number_input("Puntos a Favor:", value=meta_global, disabled=True, key=f"pf_b_{idx}")
                        st.number_input("Puntos en Contra:", value=mitad_global, disabled=True, key=f"pc_b_{idx}")
                if st.button("Asentar Puntuación de Reposo", key="btn_asentar_reposo"):
                    for jb in r['reposo']:
                        st.session_state.historial_atletas[jb].append({
                            'ronda': r['ronda'], 'jg': 1, 'jj': 1, 'pf': meta_global, 'pc': mitad_global, 'efec': meta_global - mitad_global, 'sancionado': False
                        })
                    r['reposo_asentado'] = True; st.rerun()
        
        # Mesas
        pendientes = [idx for idx, _ in enumerate(r['mesas']) if idx not in r['listas']]
        if pendientes:
            for i in pendientes:
                m = r['mesas'][i]
                with st.expander(f"MESA {i+1}", expanded=True):
                    c1, c2 = st.columns(2)
                    v1 = c1.number_input(f"Puntos Reales A-C ({m[0]} / {m[2]}):", 0, 300, key=f"v1_{i}")
                    v2 = c2.number_input(f"Puntos Reales B-D ({m[1]} / {m[3]}):", 0, 300, key=f"v2_{i}")
                    
                    st.markdown('<div class="panel-arbitral"><b>⚖纽 INFRACCIONES INDIVIDUALES EN ESTA MESA</b></div>', unsafe_allow_html=True)
                    sanciones_ronda = {}
                    cols_sanc = st.columns(4)
                    for idx_j, jugador_mesa in enumerate(m):
                        with cols_sanc[idx_j]:
                            sanciones_ronda[jugador_mesa] = st.selectbox(f"Falta de {jugador_mesa}:", list(DICCIONARIO_SANCIONES.keys()), key=f"sanc_{jugador_mesa}_{i}")
                    
                    if st.button(f"Guardar Resultados Mesa {i+1}", key=f"b_{i}"):
                        datos_mesa = {
                            m[0]: {"pf_real": v1, "pc_real": v2, "pf_ind": v1, "pc_ind": v2, "g_real": v1 > v2, "sanc": False},
                            m[2]: {"pf_real": v1, "pc_real": v2, "pf_ind": v1, "pc_ind": v2, "g_real": v1 > v2, "sanc": False},
                            m[1]: {"pf_real": v2, "pc_real": v1, "pf_ind": v2, "pc_ind": v1, "g_real": v2 > v1, "sanc": False},
                            m[3]: {"pf_real": v2, "pc_real": v1, "pf_ind": v2, "pc_ind": v1, "g_real": v2 > v1, "sanc": False}
                        }
                        
                        for j in m:
                            s_sel = sanciones_ronda[j]
                            s_info = DICCIONARIO_SANCIONES[s_sel]
                            if s_info["tipo"] != "NADA":
                                datos_mesa[j]["sanc"] = True
                                if s_info["tipo"] == "PORCENTAJE":
                                    descuento = int(meta_global * s_info["valor"])
                                    datos_mesa[j]["pf_ind"] = max(0, datos_mesa[j]["pf_real"] - descuento)
                                elif s_info["tipo"] == "EXPULSION":
                                    datos_mesa[j]["pf_ind"] = 0
                                    datos_mesa[j]["pc_ind"] = meta_global
                                elif s_info["tipo"] == "CONCLUYE_PARTIDO":
                                    datos_mesa[j]["pf_ind"] = meta_global
                                    datos_mesa[j]["pc_ind"] = meta_global

                        for j in m:
                            pf_f = datos_mesa[j]["pf_ind"]
                            pc_f = datos_mesa[j]["pc_ind"]
                            pc_rival_real = datos_mesa[j]["pc_real"]
                            ganador_final = pf_f > pc_rival_real
                            jg_atleta = 1 if ganador_final else 0
                            
                            if datos_mesa[j]["sanc"]:
                                efec_atleta = (meta_global - pc_rival_real) if ganador_final else (pf_f - meta_global)
                            else:
                                efec_atleta = (meta_global - pc_rival_real) if datos_mesa[j]["g_real"] else -(meta_global - pf_f)

                            st.session_state.historial_atletas[j].append({
                                'ronda': r['ronda'], 'jg': jg_atleta, 'jj': 1, 'pf': pf_f, 'pc': pc_f, 'efec': efec_atleta, 'sancionado': datos_mesa[j]["sanc"]
                            })
                        r['listas'].append(i); st.rerun()
        else:
            if r.get('reposo_asentado', True): st.success(f"¡Ronda {r['ronda']} finalizada por completo!")
            else: st.warning("Falta asentar la planilla de los atletas en reposo arriba.")
    else: st.info("La sala está vacía. Genere el sorteo en Inscripción.")

# --- 7. SECCIÓN: RANKING GENERAL Y MOTOR SUIZO CON EXCLUSIONES ---
elif st.session_state.seccion_activa == "RANKING":
    st.markdown("<h2 style='text-align:center;'>🏆 TABLA DE POSICIONES OFICIAL (RANKING)</h2>", unsafe_allow_html=True)
    lista_ranking = obtener_ranking_ordenado()
    
    if lista_ranking:
        df = pd.DataFrame(lista_ranking)
        df.index = df.index + 1
        st.dataframe(df, use_container_width=True)
        
        r_actual = st.session_state.historial_completo[-1]
        mesas_listas = len(r_actual['listas']) == len(r_actual['mesas'])
        reposo_listo = r_actual.get('reposo_asentado', True)
        
        st.markdown("---")
        if mesas_listas and reposo_listo:
            st.success(f"⚙️ Gestión Arbitral: Ronda {r_actual['ronda']} totalmente cerrada. El Sistema Suizo está listo.")
            if st.button("🚀 GENERAR SIGUIENTE RONDA (SISTEMA SUIZO)"):
                
                # FILTRADO CRÍTICO: El motor suizo solo toma a los atletas que siguen con estatus "ACTIVO"
                atletas_activos_ordenados = [x["ATLETA"] for x in lista_ranking if x["ESTATUS"] == "ACTIVO"]
                total_activos = len(atletas_activos_ordenados)
                lista_reposo_nueva = []
                
                # Control del Bye para el número impar de sobrevivientes
                if total_activos % 4 != 0:
                    for alt in reversed(atletas_activos_ordenados):
                        historial = st.session_state.historial_atletas.get(alt, [])
                        ya_tuvo_bye = any(p['jj'] == 1 and p['pf'] == st.session_state.meta_puntos and p['pc'] == (st.session_state.meta_puntos // 2) and not p['sancionado'] and p['efec'] == (st.session_state.meta_puntos // 2) for p in historial)
                        if not ya_tuvo_bye:
                            lista_reposo_nueva.append(alt)
                            atletas_activos_ordenados.remove(alt)
                            if len(atletas_activos_ordenados) % 4 == 0: break
                
                nuevas_mesas = []
                for idx in range(0, len(atletas_activos_ordenados), 4):
                    bloque_mesa = atletas_activos_ordenados[idx:idx+4]
                    random.shuffle(bloque_mesa)
                    nuevas_mesas.append(bloque_mesa)
                
                st.session_state.historial_completo.append({
                    'ronda': r_actual['ronda'] + 1, 'mesas': nuevas_mesas, 'reposo': lista_reposo_nueva, 'listas': [], 'reposo_asentado': False
                })
                st.session_state.seccion_activa = "MESAS"; st.rerun()
        else: st.warning(f"⚠️ El Sorteo Suizo está bloqueado. Debe culminar la carga del 100% de los resultados de la Ronda {r_actual['ronda']} para avanzar.")
