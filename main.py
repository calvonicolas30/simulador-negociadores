import streamlit as st
from st_gsheets_connection import GSheetsConnection
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
    st.title("Ingreso al Sistema")

    usuario = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")

    if st.button("ACCEDER"):
        try:
            _, df_usuarios = cargar_datos()

            credenciales = dict(zip(
                df_usuarios['usuario'].astype(str).str.strip(),
                df_usuarios['password'].astype(str).str.strip()
            ))

            if usuario.strip() in credenciales and credenciales[usuario.strip()] == password.strip():
                st.session_state.autenticado = True
                st.session_state.usuario_actual = usuario
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos")

        except Exception as e:
            st.error("No se pudo conectar con Google Sheets")
            st.code(e)

else:
    st.sidebar.title("👮 Panel")
    st.sidebar.write(f"Usuario: **{st.session_state.usuario_actual}**")

    if st.sidebar.button("Cerrar sesión"):
        st.session_state.autenticado = False
        st.rerun()

    df_preguntas, _ = cargar_datos()

    st.header("Examen de Certificación")

    nivel = st.selectbox("Seleccione nivel:", df_preguntas['Nivel'].dropna().unique())

    preguntas = df_preguntas[df_preguntas['Nivel'] == nivel].copy()

    if preguntas.empty:
        st.warning("No hay preguntas cargadas para este nivel.")
        st.stop()

    if "inicio" not in st.session_state:
        st.session_state.inicio = time.time()
        st.session_state.preguntas = preguntas.sample(frac=1).reset_index(drop=True)

    tiempo_limite = 10 * 60
    transcurrido = int(time.time() - st.session_state.inicio)
    restante = max(0, tiempo_limite - transcurrido)

    m, s = divmod(restante, 60)
    st.sidebar.warning(f"⏳ Tiempo restante: {m:02d}:{s:02d}")

    with st.form("examen"):
        respuestas = []
        for i, fila in st.session_state.preguntas.iterrows():
            st.write(f"**{i+1}. {fila['Pregunta']}**")
            r = st.radio(
                "Seleccione una opción:",
                [fila['Opción_A'], fila['Opción_B'], fila['Opción_C']],
                key=f"r{i}"
            )
            respuestas.append(r)

        enviar = st.form_submit_button("ENVIAR EXAMEN")

    if enviar:
        aciertos = sum(
            1 for i, r in enumerate(respuestas)
            if r == st.session_state.preguntas.iloc[i]['Correcta']
        )

        total = len(respuestas)
        porcentaje = (aciertos / total) * 100

        if porcentaje >= 70:
            st.success(f"APROBADO - {porcentaje:.0f}%")
            st.balloons()
        else:
            st.error(f"DESAPROBADO - {porcentaje:.0f}%")

        del st.session_state.inicio
