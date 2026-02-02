import streamlit as st
import pandas as pd
import time

# ================== CONFIG ==================

st.set_page_config(page_title="División Negociadores", layout="centered")

LOGO = "logo.PNG"

USUARIOS_URL = "PEGÁ_ACÁ_TU_CSV_DE_USUARIOS"
PREGUNTAS_URL = "PEGÁ_ACÁ_TU_CSV_DE_PREGUNTAS"

TIEMPO_POR_PREGUNTA = 120  # 2 minutos

# ================== FUNCIONES ==================

@st.cache_data(ttl=60)
def cargar_datos():
    df_users = pd.read_csv(USUARIOS_URL)
    df_preg = pd.read_csv(PREGUNTAS_URL)
    return df_users, df_preg

def iniciar_timer():
    if "fin" not in st.session_state:
        st.session_state.fin = time.time() + TIEMPO_POR_PREGUNTA

def tiempo_restante():
    return max(0, int(st.session_state.fin - time.time()))

# ================== SESIÓN ==================

if "login" not in st.session_state:
    st.session_state.login = False

if "idx" not in st.session_state:
    st.session_state.idx = 0

if "bloqueada" not in st.session_state:
    st.session_state.bloqueada = False

# ================== LOGIN ==================

if not st.session_state.login:

    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.image(LOGO, width=260)

    st.markdown("<h1 style='text-align:center'>DIVISIÓN NEGOCIADORES</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center'>PROGRAMA DE CERTIFICACIÓN</h3>", unsafe_allow_html=True)

    st.divider()

    usuario = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")

    if st.button("Ingresar") or (usuario and password and st.session_state.get("enter", False)):

        df_users, _ = cargar_datos()

        if ((df_users["usuario"] == usuario) & (df_users["password"] == password)).any():
            st.session_state.login = True
            st.session_state.fin = time.time() + TIEMPO_POR_PREGUNTA
            st.experimental_rerun()
        else:
            st.error("Usuario o contraseña incorrectos")

    st.stop()

# ================== PREGUNTAS ==================

df_users, df_preg = cargar_datos()

if st.session_state.idx >= len(df_preg):
    st.success("🎯 Examen finalizado")
    st.stop()

preg = df_preg.iloc[st.session_state.idx]

# ================== TIMER ==================

iniciar_timer()
restante = tiempo_restante()

mins = restante // 60
secs = restante % 60

st.markdown(f"⏳ Tiempo restante: **{mins:02}:{secs:02}**")

if restante <= 0:
    st.session_state.idx += 1
    st.session_state.bloqueada = False
    del st.session_state.fin
    st.experimental_rerun()

# ================== MOSTRAR VIDEO ==================

if "Video" in preg and isinstance(preg["Video"], str) and preg["Video"].startswith("http"):

    video_html = f"""
    <iframe width="100%" height="315"
    src="{preg['Video']}?controls=0&disablekb=1&modestbranding=1&rel=0"
    frameborder="0"
    allowfullscreen></iframe>
    """
    st.components.v1.html(video_html, height=340)

# ================== PREGUNTA ==================

st.subheader(f"Nivel: {preg['Nivel']}")
st.markdown(f"### {preg['Pregunta']}")

opciones = {
    "A": preg["Opcion_A"],
    "B": preg["Opcion_B"],
    "C": preg["Opcion_C"]
}

for letra, texto in opciones.items():

    if st.session_state.bloqueada:
        st.button(f"{letra}) {texto}", disabled=True)
    else:
        if st.button(f"{letra}) {texto}"):

            if letra == str(preg["Correcta"]).strip():
                st.success("✅ Correcto")
                st.session_state.idx += 1
                st.session_state.bloqueada = False
                del st.session_state.fin
                time.sleep(1)
                st.experimental_rerun()
            else:
                st.error("❌ Incorrecto")
                st.session_state.bloqueada = True

    st.success("Sistema operativo")

