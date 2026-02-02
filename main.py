import streamlit as st
import pandas as pd
import time
from datetime import datetime

# ---------------- CONFIG ----------------

st.set_page_config(page_title="División Negociadores", layout="centered")

SHEET_ID = "1Xg4QZrUuF-r5rW5s8ZJJrIIHsNI5UzZ0taJ6CYcV-oA"
URL_BASE = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid="

GID_PREGUNTAS = "0"
GID_USUARIOS = "0"

TIEMPO_EXAMEN = 120  # 2 minutos

# ---------------- FUNCIONES ----------------

def leer_sheet(gid):
    return pd.read_csv(URL_BASE + gid)

def youtube_embed(url):
    if "watch?v=" in url:
        video_id = url.split("watch?v=")[1].split("&")[0]
    else:
        return None
    return f"https://www.youtube.com/embed/{video_id}?controls=0&disablekb=1&fs=0&modestbranding=1"

# ---------------- SESSION ----------------

if "login" not in st.session_state:
    st.session_state.login = False

if "inicio" not in st.session_state:
    st.session_state.inicio = None

if "respuestas" not in st.session_state:
    st.session_state.respuestas = {}

# ---------------- LOGIN ----------------

if not st.session_state.login:

    st.markdown("<div style='text-align:center'>", unsafe_allow_html=True)
    st.image("logo_policia.PNG", width=250)
    st.markdown("<h1>DIVISIÓN NEGOCIADORES</h1>", unsafe_allow_html=True)
    st.markdown("<h3>PROGRAMA DE CERTIFICACIÓN</h3></div>", unsafe_allow_html=True)

    usuario = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")

    if st.button("ACCEDER") or password:

        df_users = leer_sheet(GID_USUARIOS)
        df_users.columns = ["usuario", "password"]

        cred = dict(zip(df_users.usuario.astype(str), df_users.password.astype(str)))

        if usuario in cred and str(cred[usuario]) == password:
            st.session_state.login = True
            st.session_state.usuario = usuario
            st.session_state.inicio = time.time()
            st.rerun()
        else:
            st.error("Usuario o contraseña incorrectos")

# ---------------- SISTEMA ----------------

else:

    tiempo_restante = TIEMPO_EXAMEN - int(time.time() - st.session_state.inicio)

    st.sidebar.title("Panel de Control")
    st.sidebar.write(f"👮 Usuario: **{st.session_state.usuario}**")

    if tiempo_restante <= 0:
        st.sidebar.error("⏰ Tiempo agotado")
    else:
        m, s = divmod(tiempo_restante, 60)
        st.sidebar.warning(f"⏳ Tiempo restante: {m:02d}:{s:02d}")

    if st.sidebar.button("Cerrar sesión"):
        for k in st.session_state.keys():
            del st.session_state[k]
        st.rerun()

    df = leer_sheet(GID_PREGUNTAS)

    st.title("Evaluación")

    for i, fila in df.iterrows():

        st.markdown(f"### {i+1}. {fila['Pregunta']}")

        if pd.notna(fila.get("video", "")):
            embed = youtube_embed(str(fila["video"]))
            if embed:
                st.markdown(
                    f"""
                    <iframe width="100%" height="350" src="{embed}"
                    frameborder="0" allowfullscreen></iframe>
                    """,
                    unsafe_allow_html=True
                )

        opciones = [fila["Opción_A"], fila["Opción_B"], fila["Opción_C"]]

        key = f"preg_{i}"

        if key not in st.session_state.respuestas:

            r = st.radio("Seleccione:", opciones, key=key)

            if r:
                st.session_state.respuestas[key] = r
                st.rerun()

        else:
            seleccion = st.session_state.respuestas[key]

            if seleccion == fila["Correcta"]:
                st.success(f"✔ Respuesta correcta: {seleccion}")
            else:
                st.error(f"✖ Respuesta incorrecta: {seleccion}")

    if tiempo_restante <= 0 or len(st.session_state.respuestas) == len(df):

        correctas = sum(
            1 for i, fila in df.iterrows()
            if st.session_state.respuestas.get(f"preg_{i}") == fila["Correcta"]
        )

        total = len(df)
        porcentaje = int((correctas / total) * 100)

        st.divider()
        if porcentaje >= 70:
            st.success(f"RESULTADO: APROBADO — {porcentaje}%")
            st.balloons()
        else:
            st.error(f"RESULTADO: DESAPROBADO — {porcentaje}%")

        st.stop()
