import streamlit as st
import pandas as pd
import time

st.set_page_config(page_title="División Negociadores", layout="centered")

# ---------- LINKS DIRECTOS CSV ----------
BASE = "https://docs.google.com/spreadsheets/d/1Xg4QZrUuF-r5rW5s8ZJJrIIHsNI5UzZ0taJ6CYcV-oA"

URL_PREGUNTAS = BASE + "/gviz/tq?tqx=out:csv&sheet=preguntas"
URL_USUARIOS   = BASE + "/gviz/tq?tqx=out:csv&sheet=usuarios"

def cargar_datos():
    df_p = pd.read_csv(URL_PREGUNTAS)
    df_u = pd.read_csv(URL_USUARIOS)
    return df_p, df_u

# ---------- SESSION ----------
if "login" not in st.session_state:
    st.session_state.login = False

if "inicio" not in st.session_state:
    st.session_state.inicio = None

# ---------- LOGIN ----------
if not st.session_state.login:

    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.image("logo_policia.PNG", use_container_width=True)

    st.markdown("<h1 style='text-align:center'>DIVISIÓN NEGOCIADORES</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center'>PROGRAMA DE CERTIFICACIÓN</h3>", unsafe_allow_html=True)

    usuario = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")

    if st.button("ACCEDER"):

        df_p, df_u = cargar_datos()
        df_u.columns = [c.strip().lower() for c in df_u.columns]

        cred = dict(zip(df_u["usuario"].astype(str),
                        df_u["password"].astype(str)))

        if usuario in cred and cred[usuario] == password:
            st.session_state.login = True
            st.session_state.usuario = usuario
            st.session_state.inicio = time.time()
            st.rerun()
        else:
            st.error("Usuario o contraseña incorrectos")

# ---------- SISTEMA ----------
else:

    st.sidebar.success(f"Usuario: {st.session_state.usuario}")
    if st.sidebar.button("Cerrar sesión"):
        st.session_state.clear()
        st.rerun()

    df, _ = cargar_datos()

    TIEMPO_TOTAL = 2 * 60
    restante = TIEMPO_TOTAL - int(time.time() - st.session_state.inicio)

    if restante <= 0:
        st.error("⛔ TIEMPO AGOTADO")
        st.stop()

    m, s = divmod(restante, 60)
    st.sidebar.warning(f"⏳ Tiempo restante: {m:02d}:{s:02d}")

    st.header("Evaluación")

    for i, row in df.iterrows():

        st.subheader(f"{i+1}. {row['Pregunta']}")

        if "video" in df.columns and pd.notna(row["video"]):
            if "v=" in row["video"]:
                vid = row["video"].split("v=")[1].split("&")[0]
                st.components.v1.html(f"""
                <iframe width="100%" height="360"
                src="https://www.youtube.com/embed/{vid}?controls=0&disablekb=1&modestbranding=1&rel=0"
                frameborder="0"
                allowfullscreen>
                </iframe>
                """, height=380)

        opciones = [row["Opción_A"], row["Opción_B"], row["Opción_C"]]
        st.radio("Respuesta:", opciones, key=i)

    st.success("Sistema operativo")

