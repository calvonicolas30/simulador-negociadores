import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import time

# ---------------- CONFIG ----------------
st.set_page_config(page_title="División Negociadores", layout="centered")

# ---------------- CONEXIÓN GOOGLE ----------------
conn = st.connection("gsheets", type=GSheetsConnection)

def cargar_datos():
    df_p = conn.read(worksheet="preguntas", ttl="1m")
    df_u = conn.read(worksheet="usuarios", ttl="1m")
    return df_p, df_u

# ---------------- SESSION ----------------
if "login" not in st.session_state:
    st.session_state.login = False

if "inicio" not in st.session_state:
    st.session_state.inicio = None

if "respuestas" not in st.session_state:
    st.session_state.respuestas = {}

# ---------------- LOGIN ----------------
if not st.session_state.login:

    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.image("logo_policia.PNG", use_container_width=True)

    st.markdown("<h1 style='text-align:center'>DIVISIÓN NEGOCIADORES</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center'>PROGRAMA DE CERTIFICACIÓN</h3>", unsafe_allow_html=True)

    usuario = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")

    if st.button("ACCEDER") or password:

        try:
            _, df_users = cargar_datos()
            df_users.columns = [c.strip().lower() for c in df_users.columns]

            cred = dict(zip(df_users["usuario"].astype(str),
                            df_users["password"].astype(str)))

            if usuario in cred and cred[usuario] == password:
                st.session_state.login = True
                st.session_state.usuario = usuario
                st.session_state.inicio = time.time()
                st.session_state.respuestas = {}
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos")

        except Exception as e:
            st.error("No se pudo conectar con Google Sheets")
            st.write(e)

# ---------------- SISTEMA ----------------
else:

    st.sidebar.success(f"Usuario: {st.session_state.usuario}")
    if st.sidebar.button("Cerrar sesión"):
        st.session_state.clear()
        st.rerun()

    df, _ = cargar_datos()

    # ---------- TIMER ----------
    TIEMPO_TOTAL = 2 * 60  # 2 minutos
    transcurrido = int(time.time() - st.session_state.inicio)
    restante = TIEMPO_TOTAL - transcurrido

    if restante <= 0:
        st.error("⛔ TIEMPO AGOTADO")
        st.stop()

    m, s = divmod(restante, 60)
    st.sidebar.warning(f"⏳ Tiempo restante: {m:02d}:{s:02d}")

    st.header("Evaluación")

    # ---------- PREGUNTAS ----------
    for i, row in df.iterrows():

        st.subheader(f"{i+1}. {row['Pregunta']}")

        # ---- VIDEO BLOQUEADO ----
        if "video" in df.columns and pd.notna(row["video"]):
            if "v=" in row["video"]:
                vid = row["video"].split("v=")[1].split("&")[0]
                st.components.v1.html(f"""
                <iframe width="100%" height="360"
                src="https://www.youtube.com/embed/{vid}?controls=0&disablekb=1&modestbranding=1&rel=0"
                frameborder="0"
                allow="autoplay; encrypted-media"
                allowfullscreen>
                </iframe>
                """, height=380)

        opciones = [row["Opción_A"], row["Opción_B"], row["Opción_C"]]

        if i in st.session_state.respuestas:
            st.radio("Respuesta:", opciones, 
                     index=opciones.index(st.session_state.respuestas[i]),
                     key=f"q{i}", disabled=True)
        else:
            r = st.radio("Respuesta:", opciones, key=f"q{i}")
            if r:
                st.session_state.respuestas[i] = r

    # ---------- FINAL ----------
    if st.button("FINALIZAR EXAMEN"):
        aciertos = 0
        for i, row in df.iterrows():
            if i in st.session_state.respuestas:
                if st.session_state.respuestas[i] == row["Correcta"]:
                    aciertos += 1

        total = len(df)
        porcentaje = int((aciertos / total) * 100)

        if porcentaje >= 70:
            st.success(f"✅ APROBADO — {porcentaje}%")
            st.balloons()
        else:
            st.error(f"❌ DESAPROBADO — {porcentaje}%")

        st.stop()

