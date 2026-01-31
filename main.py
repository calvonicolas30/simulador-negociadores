import streamlit as st
import pandas as pd
import time

# ---------- CONFIG ----------

SHEET_ID = "1Xg4QZrUuF-r5rW5s8ZJJrIIHsNI5UzZ0taJ6CYcV-oA"

def leer_sheet(nombre):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={nombre}"
    return pd.read_csv(url)

# ---------- PAGE ----------

st.set_page_config(page_title="División Negociadores - Certificación", layout="centered")

# ---------- LOGIN ----------

if "login" not in st.session_state:
    st.session_state.login = False

if not st.session_state.login:

    st.image("logo_policia.png", width=180)

    st.title("Ingreso al Sistema")

    user = st.text_input("Usuario")
    pwd = st.text_input("Contraseña", type="password")

    if st.button("ACCEDER"):
        try:
            df_users = leer_sheet("usuarios")
            df_users.columns = ["usuario", "password"]

            cred = dict(zip(
                df_users["usuario"].astype(str).str.strip(),
                df_users["password"].astype(str).str.strip()
            ))

            if user.strip() in cred and cred[user.strip()] == pwd.strip():
                st.session_state.login = True
                st.session_state.usuario = user
                st.session_state.inicio = time.time()
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos")

        except Exception as e:
            st.error("No se pudo conectar con Google Sheets")
            st.code(e)

# ---------- SISTEMA ----------

else:

    st.sidebar.title("👮 Panel")
    st.sidebar.write(f"Usuario: **{st.session_state.usuario}**")

    if st.sidebar.button("Cerrar sesión"):
        for k in ["login", "inicio", "preguntas"]:
            if k in st.session_state:
                del st.session_state[k]
        st.rerun()

    st.title("Certificación de Competencias")

    df_preg = leer_sheet("preguntas")
    df_preg.columns = ["Nivel","Pregunta","Opción_A","Opción_B","Opción_C","Correcta"]

    nivel = st.selectbox("Seleccione Nivel:", df_preg["Nivel"].unique())

    if "preguntas" not in st.session_state:
        st.session_state.preguntas = df_preg[df_preg["Nivel"] == nivel].sample(frac=1).reset_index(drop=True)

    preguntas = st.session_state.preguntas

    # -------- TEMPORIZADOR 2 MINUTOS --------

    TIEMPO_LIMITE = 2 * 60   # 2 minutos

    if "inicio" not in st.session_state:
        st.session_state.inicio = time.time()

    transcurrido = int(time.time() - st.session_state.inicio)
    restante = max(0, TIEMPO_LIMITE - transcurrido)

    reloj = st.sidebar.empty()

    m, s = divmod(restante, 60)
    reloj.warning(f"⏳ Tiempo restante: {m:02d}:{s:02d}")

    if restante <= 0:
        st.error("⛔ Tiempo agotado")
        st.stop()

    # -------- FORMULARIO --------

    with st.form("examen"):
        respuestas = []

        for i, fila in preguntas.iterrows():
            st.write(f"**{i+1}. {fila['Pregunta']}**")
            r = st.radio("Seleccione:", [
                fila['Opción_A'],
                fila['Opción_B'],
                fila['Opción_C']
            ], key=i)
            respuestas.append(r)

        enviar = st.form_submit_button("ENVIAR EXAMEN")

    if enviar:

        aciertos = sum(
            1 for i, r in enumerate(respuestas)
            if r == preguntas.iloc[i]["Correcta"]
        )

        total = len(respuestas)
        porcentaje = aciertos / total * 100

        if porcentaje >= 70:
            st.success(f"APROBADO – {porcentaje:.0f}%")
            st.balloons()
        else:
            st.error(f"DESAPROBADO – {porcentaje:.0f}%")

        for k in ["inicio", "preguntas"]:
            if k in st.session_state:
                del st.session_state[k]

