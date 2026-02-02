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

# ---------------- LOGIN ----------------
if not st.session_state.login:

    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.image("logo_policia.PNG", use_container_width=True)

    st.markdown("<h1 style='text-align:center'>DIVISIÓN NEGOCIADORES</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center'>PROGRAMA DE CERTIFICACIÓN</h3>", unsafe_allow_html=True)

    usuario = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")

    if st.button("ACCEDER"):

        try:
            _, df_users = cargar_datos()
            df_users.columns = [c.strip().lower() for c in df_users.columns]

            cred = dict(zip(df_users["usuario"].astype(str),
                            df_users["password"].astype(str)))

            if usuario in cred and cred[usuario] == password:
                st.session_state.login = True
                st.session_state.usuario = usuario
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
        st.session_state.login = False
        st.session_state.clear()
        st.rerun()

    df, _ = cargar_datos()

    if "inicio" not in st.session_state:
        st.session_state.inicio = time.time()

    TIEMPO_TOTAL = 2 * 60  # 2 minutos

    restante = TIEMPO_TOTAL - int(time.time() - st.session_state.inicio)
    if restante < 0:
        restante = 0

    m, s = divmod(restante, 60)
    st.sidebar.warning(f"⏳ Tiempo restante: {m:02d}:{s:02d}")

    if restante == 0:
        st.error("⛔ TIEMPO AGOTADO")
        st.stop()

    st.header("Evaluación")

    for i, row in df.iterrows():

        st.subheader(f"{i+1}. {row['Pregunta']}")

        # Video bloqueado
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
        st.radio("Seleccione:", opciones, key=f"q{i}")

    st.success("Sistema funcionando correctamente")

