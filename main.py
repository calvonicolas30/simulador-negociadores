import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import time

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="División Negociadores - Certificación", layout="centered")

# --- CONEXIÓN A GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

def cargar_datos():
    df_p = conn.read(worksheet="preguntas", ttl="5m")
    df_u = conn.read(worksheet="usuarios", ttl="5m")

    df_p.columns = [c.strip() for c in df_p.columns]
    df_u.columns = [c.strip() for c in df_u.columns]

    return df_p, df_u

# --- LOGIN ---
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.title("Ingreso al Sistema")

        usuario_ingresado = st.text_input("Usuario Oficial")
        clave_ingresada = st.text_input("Contraseña", type="password")

        if st.button("ACCEDER"):
            try:
                _, df_usuarios = cargar_datos()

                credenciales = dict(zip(
                    df_usuarios['usuario'].astype(str).str.strip(),
                    df_usuarios['password'].astype(str).str.strip()
                ))

                if usuario_ingresado.strip() in credenciales and credenciales[usuario_ingresado.strip()] == clave_ingresada.strip():
                    st.session_state.autenticado = True
                    st.session_state.usuario_actual = usuario_ingresado
                    st.rerun()
                else:
                    st.error("Usuario o contraseña incorrectos")

            except Exception as e:
                st.error("No se pudo conectar con Google Sheets.")
                st.code(e)

else:
    st.sidebar.title("👮 Panel de Control")
    st.sidebar.write(f"Usuario: **{st.session_state.usuario_actual}**")

    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.autenticado = False
        st.rerun()

    df_preguntas, _ = cargar_datos()

    st.header("Certificación de Competencias")

    nivel_elegido = st.selectbox("Seleccione Nivel:", df_preguntas['Nivel'].dropna().unique())

    preguntas_filtradas = df_preguntas[df_preguntas['Nivel'] == nivel_elegido].copy()

    if preguntas_filtradas.empty:
        st.warning("No hay preguntas cargadas para este nivel.")
        st.stop()

    if "inicio" not in st.session_state or st.session_state.get("nivel_anterior") != nivel_elegido:
        st.session_state.inicio = time.time()
        st.session_state.nivel_anterior = nivel_elegido
        st.session_state.preguntas = preguntas_filtradas.sample(frac=1).reset_index(drop=True)

    tiempo_limite = 10 * 60
    transcurrido = int(time.time() - st.session_state.inicio)
    restante = max(0, tiempo_limite - transcurrido)

    m, s = divmod(restante, 60)
    st.sidebar.warning(f"⏳ Tiempo restante: {m:02d}:{s:02d}")
    time.sleep(1)
    st.rerun()

    with st.form("form_examen"):
        respuestas = []

        for i, fila in st.session_state.preguntas.iterrows():
            st.write(f"**{i+1}. {fila['Pregunta']}**")
            opciones = [
                str(fila['Opción_A']),
                str(fila['Opción_B']),
                str(fila['Opción_C'])
            ]
            r = st.radio("Seleccione:", opciones, key=f"r{i}")
            respuestas.append(r)

        enviado = st.form_submit_button("ENVIAR EXAMEN")

    if enviado:
        aciertos = sum(
            1 for i, r in enumerate(respuestas)
            if r == st.session_state.preguntas.iloc[i]['Correcta']
        )

        total = len(respuestas)
        porcentaje = (aciertos / total) * 100
        resultado = "APROBADO" if porcentaje >= 70 else "DESAPROBADO"

        st.divider()

        if resultado == "APROBADO":
            st.success(f"Resultado: {porcentaje:.0f}% - {resultado}")
            st.balloons()
        else:
            st.error(f"Resultado: {porcentaje:.0f}% - {resultado}")
