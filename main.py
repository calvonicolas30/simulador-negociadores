import streamlit as st
import pandas as pd
import time
from st_gsheets_connection import GSheetsConnection

# ---------------- CONFIG ----------------
st.set_page_config(page_title="División Negociadores", layout="centered")

LOGO = "logo_policia.PNG"
TIEMPO_LIMITE = 120  # 2 minutos

# ID DE TU GOOGLE SHEET
SHEET_ID = "1Xg4QZrUuF-r5rW5s8ZJJrIIHsNI5UzZ0taJ6CYcV-oA"

# ---------------------------------------

@st.cache_data(ttl=60)
def cargar_datos():
    conn = st.connection("gsheets", type=GSheetsConnection, spreadsheet=SHEET_ID)
    preguntas = conn.read(worksheet="preguntas")
    usuarios = conn.read(worksheet="usuarios")
    return preguntas, usuarios

# ----------- SESSION STATE -------------
if "login" not in st.session_state:
    st.session_state.login = False

if "inicio" not in st.session_state:
    st.session_state.inicio = None

if "idx" not in st.session_state:
    st.session_state.idx = 0

if "bloqueadas" not in st.session_state:
    st.session_state.bloqueadas = set()

# ---------------------------------------

def login():
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.image(LOGO, width=260)
        st.markdown("<h1 style='text-align:center'>DIVISIÓN NEGOCIADORES</h1>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align:center'>PROGRAMA DE CERTIFICACIÓN</h3>", unsafe_allow_html=True)

        usuario = st.text_input("Usuario", key="user")
        password = st.text_input("Contraseña", type="password", key="pass")

        if st.button("Ingresar") or (usuario and password):
            df_p, df_u = cargar_datos()
            df_u.columns = ["usuario", "password"]

            ok = df_u[(df_u.usuario == usuario) & (df_u.password == password)]
            if not ok.empty:
                st.session_state.login = True
                st.session_state.inicio = time.time()
                st.experimental_rerun()
            else:
                st.error("Usuario o contraseña incorrectos")

# ---------------------------------------

def temporizador():
    tiempo_restante = TIEMPO_LIMITE - int(time.time() - st.session_state.inicio)
    if tiempo_restante <= 0:
        st.error("⏰ Tiempo agotado")
        st.stop()

    minutos = tiempo_restante // 60
    segundos = tiempo_restante % 60
    st.markdown(f"## ⏳ {minutos:02}:{segundos:02}")

    time.sleep(1)
    st.experimental_rerun()

# ---------------------------------------

def preguntas():
    df, _ = cargar_datos()
    fila = df.iloc[st.session_state.idx]

    st.subheader(f"Nivel: {fila['Nivel']}")
    st.markdown(f"### {fila['Pregunta']}")

    if pd.notna(fila.get("Video", None)):
        st.video(fila["Video"])

    opciones = [fila['Opción_A'], fila['Opción_B'], fila['Opción_C']]

    bloqueada = st.session_state.idx in st.session_state.bloqueadas

    seleccion = st.radio(
        "Seleccione una opción:",
        opciones,
        disabled=bloqueada
    )

    if st.button("Confirmar respuesta") and not bloqueada:
        if seleccion == fila["Correcta"]:
            st.success("✅ Correcto")
            st.session_state.idx += 1
            st.experimental_rerun()
        else:
            st.error("❌ Incorrecto – Pregunta bloqueada")
            st.session_state.bloqueadas.add(st.session_state.idx)

# ---------------------------------------

if not st.session_state.login:
    login()
else:
    temporizador()
    preguntas()



