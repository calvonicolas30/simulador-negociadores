import streamlit as st
import pandas as pd
import time

# ---------------- CONFIG ----------------

st.set_page_config(page_title="División Negociadores", layout="centered")

LOGO = "logo.PNG"

URL_USUARIOS = "PEGÁ_ACÁ_EL_LINK_CSV_DE_USUARIOS"
URL_PREGUNTAS = "PEGÁ_ACÁ_EL_LINK_CSV_DE_PREGUNTAS"

TIEMPO_EXAMEN = 2 * 60  # 2 minutos

# ---------------- FUNCIONES ----------------

@st.cache_data(ttl=60)
def cargar_datos():
    usuarios = pd.read_csv(URL_USUARIOS)
    preguntas = pd.read_csv(URL_PREGUNTAS)
    return usuarios, preguntas

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

    with st.form("login_form"):
        usuario = st.text_input("Usuario")
        clave = st.text_input("Contraseña", type="password")
        ingresar = st.form_submit_button("INGRESAR")

    if ingresar:
        try:
            df_users, _ = cargar_datos()
            df_users.columns = ["usuario", "password"]

            cred = dict(zip(df_users["usuario"].astype(str),
                             df_users["password"].astype(str)))

            if usuario in cred and str(cred[usuario]) == clave:
                st.session_state.login = True
                st.session_state.usuario = usuario
                st.session_state.inicio = time.time()
                st.experimental_rerun()
            else:
                st.error("Usuario o contraseña incorrectos")

        except Exception as e:
            st.error(f"No se pudo conectar con la base: {e}")

# ---------------- SISTEMA ----------------

else:

    st.sidebar.success(f"Usuario: {st.session_state.usuario}")

    if st.sidebar.button("Cerrar sesión"):
        st.session_state.clear()
        st.experimental_rerun()

    _, df = cargar_datos()

    nivel = st.selectbox("Seleccione nivel:", df["Nivel"].unique())

    preguntas = df[df["Nivel"] == nivel].reset_index(drop=True)

    # ---------------- TIMER REAL ----------------

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

        if "Video" in fila and pd.notna(fila["Video"]):
            video_html = f"""
            <iframe width="100%" height="350"
            src="{fila['Video']}?controls=0&rel=0"
            frameborder="0"
            allowfullscreen></iframe>
            """
            st.components.v1.html(video_html, height=360)

        opciones = [fila["Opción_A"], fila["Opción_B"], fila["Opción_C"]]

        key = f"preg_{i}"

        if key not in st.session_state.respuestas:

            r = st.radio("Seleccione:", opciones, key=key)

            if st.button(f"Confirmar {i+1}"):
                st.session_state.respuestas[key] = r
                st.experimental_rerun()

        else:
            marcada = st.session_state.respuestas[key]

            if marcada == fila["Correcta"]:
                st.success(f"✔ Correcta: {marcada}")
            else:
                st.error(f"✖ Incorrecta: {marcada}")
                st.info(f"✔ Correcta: {fila['Correcta']}")

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

