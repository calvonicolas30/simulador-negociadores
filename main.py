import streamlit as st
import pandas as pd

st.set_page_config(page_title="Simulador Negociadores", layout="centered")

# ---------------- CONFIG ----------------
LOGO = "logo_policia.PNG"
EXCEL = "Base_Negociador.xlsx"

# ---------------- SESSION ----------------
if "login" not in st.session_state:
    st.session_state.login = False

# ---------------- LOGIN ----------------
if not st.session_state.login:

    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.image(LOGO, use_container_width=True)

    st.markdown("<h1 style='text-align:center'>DIVISIÓN NEGOCIADORES</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center'>PROGRAMA DE CERTIFICACIÓN</h3>", unsafe_allow_html=True)

    usuario = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")

    if st.button("ACCEDER"):

        df_users = pd.read_excel(EXCEL, sheet_name="usuarios")
        df_users = df_users.iloc[:, :2]
        df_users.columns = ["usuario", "password"]

        if ((df_users["usuario"] == usuario) & 
            (df_users["password"] == password)).any():

            st.session_state.login = True
            st.rerun()
        else:
            st.error("Usuario o contraseña incorrectos")

# ---------------- PANEL ----------------
else:

    st.sidebar.success("Sesión iniciada")
    if st.sidebar.button("Cerrar sesión"):
        st.session_state.login = False
        st.rerun()

    df = pd.read_excel(EXCEL, sheet_name="preguntas")

    st.title("Evaluación")

    for i, row in df.iterrows():
        st.subheader(f"{i+1}. {row['Pregunta']}")

        # video bloqueado
        st.components.v1.html(f"""
        <iframe width="100%" height="360"
        src="https://www.youtube.com/embed/{row['video'].split('v=')[1]}?controls=0&disablekb=1&modestbranding=1&rel=0"
        frameborder="0"
        allow="autoplay; encrypted-media"
        allowfullscreen>
        </iframe>
        """, height=380)

        opciones = [row["Opción A"], row["Opción B"], row["Opción C"]]
        st.radio("Seleccione:", opciones, key=i)

    st.success("Sistema funcionando correctamente")

