import streamlit as st
import pandas as pd
import time
from streamlit_autorefresh import st_autorefresh

# ---------------- CONFIG ----------------

SHEET_ID = "1Xg4QZrUuF-r5rW5s8ZJJrIIHsNI5UzZ0taJ6CYcV-oA"

def leer_sheet(nombre):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={nombre}"
    return pd.read_csv(url)

# ---------------- PAGE ----------------

st.set_page_config(
    page_title="División Negociadores - Certificación",
    layout="centered"
)

# ---------------- SESSION ----------------

if "login" not in st.session_state:
    st.session_state.login = False

if "inicio" not in st.session_state:
    st.session_state.inicio = None

if "preguntas" not in st.session_state:
    st.session_state.preguntas = None

# ---------------- LOGIN ----------------

if not st.session_state.login:

    st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)

    try:
        st.image("logo_policia.png", width=260)
    except:
        pass

    st.markdown("""
    <h1 style='text-align:center; margin-bottom:0;'>DIVISIÓN NEGOCIADORES</h1>
    <h3 style='text-align:center; margin-top:5px;'>PROGRAMA DE CERTIFICACIÓN</h3>
    <hr style='margin-top:15px; margin-bottom:25px;'>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1,2,1])

    with col2:
        with st.form("login_form"):
            usuario = st.text_input("Usuario")
            clave = st.text_input("Contraseña", type="password")

            ingresar = st.form_submit_button("ACCEDER", use_container_width=True)

            if ingresar:
                df_users = leer_sheet("usuarios")
                df_users.columns = ["usuario", "password"]

                cred = dict(zip(
                    df_users["usuario"].astype(str).str.strip(),
                    df_users["password"].astype(str).str.strip()
                ))

                if usuario.strip() in cred and cred[usuario.strip()] == clave.strip():
                    st.session_state.login = True
                    st.session_state.usuario = usuario
                    st.session_state.inicio = None
                    st.session_state.preguntas = None
                    st.rerun()
                else:
                    st.error("Usuario o contraseña incorrectos")

    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- SISTEMA ----------------

else:

    st_autorefresh(interval=1000, key="timer")

    st.sidebar.title("👮 Panel de Control")
    st.sidebar.write(f"Usuario: **{st.session_state.usuario}**")

    if st.sidebar.button("Cerrar Sesión"):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()

    st.title("Certificación de Competencias")

    df_preg = leer_sheet("preguntas")
    df_preg.columns = ["Nivel","Pregunta","Opción_A","Opción_B","Opción_C","Correcta"]

    nivel = st.selectbox("Seleccione Nivel:", df_preg["Nivel"].unique())

    if st.session_state.preguntas is None:
        st.session_state.preguntas = (
            df_preg[df_preg["Nivel"] == nivel]
            .sample(frac=1)
            .reset_index(drop=True)
        )

    preguntas = st.session_state.preguntas

    # ---------------- TIMER ----------------

    TIEMPO_LIMITE = 2 * 60   # 2 minutos

    if st.session_state.inicio is None:
        st.session_state.inicio = time.time()

    restante = int(TIEMPO_LIMITE - (time.time() - st.session_state.inicio))

    if restante <= 0:
        st.sidebar.error("⛔ TIEMPO AGOTADO")
        st.error("⛔ TIEMPO FINALIZADO — EXAMEN BLOQUEADO")
        st.session_state.inicio = None
        st.session_state.preguntas = None
        st.stop()

    m, s = divmod(restante, 60)
    st.sidebar.warning(f"⏳ Tiempo restante: {m:02d}:{s:02d}")

    # ---------------- EXAMEN ----------------

    with st.form("examen_form"):

        respuestas = []

        for i, fila in preguntas.iterrows():
            st.write(f"**{i+1}. {fila['Pregunta']}**")
            r = st.radio(
                "Seleccione una opción:",
                [fila['Opción_A'], fila['Opción_B'], fila['Opción_C']],
                key=f"p_{i}"
            )
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
            st.success(f"✅ APROBADO – {porcentaje:.0f}%")
            st.balloons()
        else:
            st.error(f"❌ DESAPROBADO – {porcentaje:.0f}%")

        st.session_state.inicio = None
        st.session_state.preguntas = None
