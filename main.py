import streamlit as st
import pandas as pd
import time
from datetime import datetime

# =================== CONFIG ===================

SHEET_ID = "1Xg4QZrUuF-r5rW5s8ZJJrIIHsNI5UzZ0taJ6CYcV-oA"

URL_USERS = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=usuarios"
URL_QUESTIONS = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=preguntas"

TIEMPO_EXAMEN = 2 * 60  # 2 minutos

# =================== FUNCIONES ===================

@st.cache_data(ttl=300)
def cargar_datos():
    return pd.read_csv(URL_USERS), pd.read_csv(URL_QUESTIONS)

# =================== SESION ===================

if "login" not in st.session_state:
    st.session_state.login = False

if "inicio" not in st.session_state:
    st.session_state.inicio = time.time()

# =================== LOGIN ===================

if not st.session_state.login:

    st.markdown("<div style='text-align:center'>", unsafe_allow_html=True)
    st.image("logo.PNG", width=220)
    st.markdown("<h1>DIVISIÓN NEGOCIADORES</h1>", unsafe_allow_html=True)
    st.markdown("<h3>PROGRAMA DE CERTIFICACIÓN</h3>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    with st.form("login_form"):
        usuario = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        submit = st.form_submit_button("ACCEDER")

    if submit:
        df_users, _ = cargar_datos()
        df_users.columns = ["usuario", "password"]

        if usuario in df_users["usuario"].astype(str).values:
            pwd = df_users[df_users["usuario"] == usuario]["password"].values[0]

            if str(pwd) == password:
                st.session_state.login = True
                st.session_state.user = usuario
                st.session_state.inicio = time.time()
                st.rerun()
            else:
                st.error("Contraseña incorrecta")
        else:
            st.error("Usuario incorrecto")

# =================== EXAMEN ===================

else:

    df_users, df_q = cargar_datos()

    st.sidebar.write(f"👮 Usuario: **{st.session_state.user}**")

    restante = max(0, TIEMPO_EXAMEN - int(time.time() - st.session_state.inicio))
    m, s = divmod(restante, 60)
    st.sidebar.warning(f"⏳ Tiempo restante: {m:02d}:{s:02d}")

    if restante <= 0:
        st.error("⏰ TIEMPO AGOTADO")
        st.stop()

    nivel = st.selectbox("Seleccione nivel:", sorted(df_q["Nivel"].dropna().unique()))

    preguntas = df_q[df_q["Nivel"] == nivel].reset_index(drop=True)

    if "bloqueadas" not in st.session_state:
        st.session_state.bloqueadas = set()

    if "respuestas" not in st.session_state:
        st.session_state.respuestas = {}

    for idx, fila in preguntas.iterrows():

        st.divider()
        st.subheader(f"{idx+1}. {fila['Pregunta']}")

        # VIDEO BLOQUEADO
        if "video" in fila and pd.notna(fila["video"]) and fila["video"].endswith(".mp4"):

            st.video(fila["video"])

            duracion = 60  # segundos del video

            key = f"video_{idx}_start"
            if key not in st.session_state:
                st.session_state[key] = time.time()

            elapsed = time.time() - st.session_state[key]

            if elapsed < duracion:
                st.warning(f"🎥 Debe ver el video completo — faltan {int(duracion-elapsed)}s")
                st.stop()

        opciones = [fila["Opción_A"], fila["Opción_B"], fila["Opción_C"]]

        if idx in st.session_state.bloqueadas:
            st.error("❌ Pregunta bloqueada — respuesta incorrecta")
            continue

        r = st.radio("Seleccione:", opciones, key=f"q_{idx}")

        if st.button("Confirmar", key=f"btn_{idx}"):

            if r == fila["Correcta"]:
                st.success("✅ Respuesta correcta")
                st.session_state.respuestas[idx] = True
            else:
                st.error("❌ Respuesta incorrecta — pregunta bloqueada")
                st.session_state.bloqueadas.add(idx)

    # =================== RESULTADO ===================

    total = len(preguntas)
    correctas = len(st.session_state.respuestas)

    if st.button("FINALIZAR EXAMEN"):
        porcentaje = (correctas / total) * 100

        if porcentaje >= 70:
            st.success(f"APROBADO — {porcentaje:.0f}%")
            st.balloons()
        else:
            st.error(f"DESAPROBADO — {porcentaje:.0f}%")

        st.stop()

