import streamlit as st
import pandas as pd
import time
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# ---------------- CONFIG ----------------

st.set_page_config(
    page_title="División Negociadores - Certificación",
    layout="centered"
)

LOGO = "logo.PNG"
SPREADSHEET_ID = "PONÉ_ACÁ_TU_ID_REAL"

TIEMPO_EXAMEN = 2 * 60  # 2 minutos

# ---------------- CONEXIÓN ----------------

conn = st.connection(
    "gsheets",
    type=GSheetsConnection,
    spreadsheet=SPREADSHEET_ID
)

# ---------------- FUNCIONES ----------------

@st.cache_data(ttl=60)
def cargar_datos():
    preguntas = conn.read(worksheet="preguntas")
    usuarios = conn.read(worksheet="usuarios")
    return preguntas, usuarios


def centrar_logo():
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.image(LOGO, width=260)


# ---------------- SESSION ----------------

if "login" not in st.session_state:
    st.session_state.login = False

if "inicio" not in st.session_state:
    st.session_state.inicio = None

if "respuestas" not in st.session_state:
    st.session_state.respuestas = {}

# ---------------- LOGIN ----------------

if not st.session_state.login:

    centrar_logo()

    st.markdown("<h1 style='text-align:center;'>DIVISIÓN NEGOCIADORES</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center;'>PROGRAMA DE CERTIFICACIÓN</h3>", unsafe_allow_html=True)

    with st.form("login_form", clear_on_submit=False):
        usuario = st.text_input("Usuario")
        clave = st.text_input("Contraseña", type="password")
        ingresar = st.form_submit_button("INGRESAR")

    if ingresar:
        try:
            _, df_users = cargar_datos()
            df_users.columns = ["usuario", "password"]

            credenciales = dict(zip(df_users["usuario"].astype(str),
                                     df_users["password"].astype(str)))

            if usuario in credenciales and str(credenciales[usuario]) == clave:
                st.session_state.login = True
                st.session_state.usuario = usuario
                st.session_state.inicio = time.time()
                st.experimental_rerun()
            else:
                st.error("Usuario o contraseña incorrectos")

        except Exception as e:
            st.error(f"No se pudo conectar con Google Sheets: {e}")

# ---------------- SISTEMA ----------------

else:

    st.sidebar.success(f"Usuario: {st.session_state.usuario}")

    if st.sidebar.button("Cerrar sesión"):
        st.session_state.clear()
        st.experimental_rerun()

    df_preguntas, _ = cargar_datos()

    nivel = st.selectbox("Seleccione nivel:", df_preguntas["Nivel"].unique())

    preguntas = df_preguntas[df_preguntas["Nivel"] == nivel].reset_index(drop=True)

    # ---------------- TIMER REAL ----------------

    if st.session_state.inicio is None:
        st.session_state.inicio = time.time()

    restante = int(TIEMPO_EXAMEN - (time.time() - st.session_state.inicio))

    if restante <= 0:
        st.error("⛔ TIEMPO FINALIZADO")
        st.stop()

    min, seg = divmod(restante, 60)
    st.sidebar.warning(f"⏳ Tiempo restante: {min:02d}:{seg:02d}")
    time.sleep(1)
    st.experimental_rerun()

    # ---------------- PREGUNTAS ----------------

    for i, fila in preguntas.iterrows():

        st.markdown(f"### {i+1}. {fila['Pregunta']}")

        # VIDEO OPCIONAL
        if "Video" in fila and pd.notna(fila["Video"]):

            video_html = f"""
            <iframe width="100%" height="350"
            src="{fila['Video']}?controls=0&rel=0&modestbranding=1"
            frameborder="0"
            allowfullscreen>
            </iframe>
            """
            st.components.v1.html(video_html, height=360)

        opciones = [fila["Opción_A"], fila["Opción_B"], fila["Opción_C"]]

        key = f"preg_{i}"

        if key not in st.session_state.respuestas:

            respuesta = st.radio("Seleccione:", opciones, key=key)

            if st.button(f"Confirmar {i+1}"):
                st.session_state.respuestas[key] = respuesta
                st.experimental_rerun()

        else:
            marcada = st.session_state.respuestas[key]

            if marcada == fila["Correcta"]:
                st.success(f"✔ Correcta: {marcada}")
            else:
                st.error(f"✖ Incorrecta: {marcada}")
                st.info(f"✔ Correcta: {fila['Correcta']}")

    # ---------------- RESULTADO FINAL ----------------

    if len(st.session_state.respuestas) == len(preguntas):

        aciertos = sum(
            1 for i, fila in preguntas.iterrows()
            if st.session_state.respuestas[f"preg_{i}"] == fila["Correcta"]
        )

        porcentaje = aciertos / len(preguntas) * 100

        st.divider()

        if porcentaje >= 70:
            st.success(f"APROBADO — {porcentaje:.0f}%")
            st.balloons()
        else:
            st.error(f"DESAPROBADO — {porcentaje:.0f}%")
