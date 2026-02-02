import streamlit as st
import pandas as pd
import time

st.set_page_config(page_title="División Negociadores", layout="centered")

# ---------------- CONEXIÓN GOOGLE SHEETS ----------------
conn = st.connection("gsheets", type="gspread")

def cargar_datos():
    df_p = conn.read(worksheet="preguntas")
    df_u = conn.read(worksheet="usuarios")
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

            cred = dict(zip(df_users["usuario"].astype(str), df_users["password"].astype(str)))

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
        if "video" in row and str(row["video"]).startswith("http"):
            vid = row["video"].split("v=")[1]
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

    st.success("Sistema operativo")
