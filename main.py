import streamlit as st
import pandas as pd
import time

# ---------- CONFIG ----------

st.set_page_config(page_title="DIVISION NEGOCIADORES", layout="centered")

LOGO = "logo.PNG"
USUARIOS = "usuarios.xlsx"
PREGUNTAS = "preguntas.xlsx"
TIEMPO_POR_PREGUNTA = 30

# ---------- SESION ----------

if "login" not in st.session_state:
    st.session_state.login = False

if "pregunta_actual" not in st.session_state:
    st.session_state.pregunta_actual = 0

if "bloqueadas" not in st.session_state:
    st.session_state.bloqueadas = set()

if "tiempo_inicio" not in st.session_state:
    st.session_state.tiempo_inicio = time.time()

# ---------- LOGIN ----------

if not st.session_state.login:

    st.markdown("<h1 style='text-align:center;'>DIVISION NEGOCIADORES</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center;'>PROGRAMA DE CERTIFICACION</h3>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.image(LOGO, width=260)

    usuario = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")

    if st.button("Ingresar") or st.session_state.get("enter"):
        df = pd.read_excel(USUARIOS)

        ok = ((df["usuario"] == usuario) & (df["password"] == password)).any()

        if ok:
            st.session_state.login = True
            st.rerun()
        else:
            st.error("Usuario o contraseña incorrectos")

    st.stop()

# ---------- CARGA ----------

df = pd.read_excel(PREGUNTAS)

if st.session_state.pregunta_actual >= len(df):
    st.success("Evaluación finalizada")
    st.stop()

fila = df.iloc[st.session_state.pregunta_actual]

# ---------- TIMER ----------

restante = TIEMPO_POR_PREGUNTA - int(time.time() - st.session_state.tiempo_inicio)

st.metric("Tiempo restante", f"{restante}s")

if restante <= 0:
    st.session_state.pregunta_actual += 1
    st.session_state.tiempo_inicio = time.time()
    st.rerun()

# ---------- PREGUNTA ----------

st.subheader(f"Pregunta {st.session_state.pregunta_actual+1}")
st.write(fila["pregunta"])

# ---------- VIDEO ----------

if pd.notna(fila["video"]):
    st.video(fila["video"], start_time=0)

# ---------- OPCIONES ----------

opciones = {
    "A": fila["A"],
    "B": fila["B"],
    "C": fila["C"]
}

if st.session_state.pregunta_actual in st.session_state.bloqueadas:
    st.warning("Pregunta bloqueada")
    st.stop()

resp = st.radio("Seleccione:", list(opciones.keys()), format_func=lambda x: f"{x}: {opciones[x]}")

if st.button("Confirmar"):

    if resp == fila["correcta"]:
        st.success("Correcto")
        st.session_state.pregunta_actual += 1
    else:
        st.error("Incorrecto")
        st.session_state.bloqueadas.add(st.session_state.pregunta_actual)
        st.session_state.pregunta_actual += 1

    st.session_state.tiempo_inicio = time.time()
    st.rerun()


