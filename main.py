import streamlit as st
import pandas as pd
import time

# ================= CONFIG ==================

st.set_page_config(page_title="División Negociadores", layout="centered")

PREGUNTAS_CSV = "https://docs.google.com/spreadsheets/d/1Xg4QZrUuF-r5rW5s8ZJJrIIHsNI5UzZ0taJ6CYcV-oA/export?format=csv&gid=0"
USUARIOS_CSV   = "https://docs.google.com/spreadsheets/d/1Xg4QZrUuF-r5rW5s8ZJJrIIHsNI5UzZ0taJ6CYcV-oA/export?format=csv&gid=275635797"

TIEMPO_EXAMEN = 2 * 60   # 2 minutos

# ==========================================

@st.cache_data
def leer_preguntas():
    return pd.read_csv(PREGUNTAS_CSV)

@st.cache_data
def leer_usuarios():
    df = pd.read_csv(USUARIOS_CSV, header=None)
    df = df.iloc[:, :2]
    df.columns = ["usuario", "password"]
    return df

# ==========================================

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:

    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.image("logo_policia.PNG", width=320)

    st.markdown("<h1 style='text-align:center;'>DIVISIÓN NEGOCIADORES</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center;'>PROGRAMA DE CERTIFICACIÓN</h3>", unsafe_allow_html=True)
    st.divider()

    with st.form("login_form", clear_on_submit=False):
        usuario = st.text_input("Usuario")
        clave   = st.text_input("Contraseña", type="password")
        entrar  = st.form_submit_button("ACCEDER")

    if entrar:

        try:
            df_users = leer_usuarios()
            cred = dict(zip(df_users["usuario"].astype(str), df_users["password"].astype(str)))

            if usuario in cred and str(cred[usuario]) == clave:
                st.session_state.autenticado = True
                st.session_state.usuario_actual = usuario
                st.session_state.inicio = time.time()
                st.session_state.respuestas = {}
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos")

        except Exception:
            st.error("No se pudo conectar con Google Sheets")

# ==========================================

else:

    st.sidebar.title("Panel de Control")
    st.sidebar.write(f"👮 Usuario: **{st.session_state.usuario_actual}**")

    if st.sidebar.button("Cerrar sesión"):
        st.session_state.clear()
        st.rerun()

    df = leer_preguntas()

    nivel = st.selectbox("Seleccione nivel:", sorted(df["Nivel"].dropna().unique()))
    preguntas = df[df["Nivel"] == nivel].reset_index(drop=True)

    if preguntas.empty:
        st.warning("No hay preguntas para este nivel.")
        st.stop()

    if "inicio" not in st.session_state:
        st.session_state.inicio = time.time()

    tiempo_restante = TIEMPO_EXAMEN - int(time.time() - st.session_state.inicio)

    if tiempo_restante <= 0:
        st.error("⏰ TIEMPO AGOTADO")
        st.stop()

    m, s = divmod(tiempo_restante, 60)
    st.sidebar.warning(f"⏳ Tiempo restante: {m:02d}:{s:02d}")

    st.header("Evaluación")

    for i, fila in preguntas.iterrows():

        st.subheader(f"{i+1}. {fila['Pregunta']}")

        opciones = [fila["Opción_A"], fila["Opción_B"], fila["Opción_C"]]

        if i in st.session_state.respuestas:
            st.radio("Respuesta:", opciones,
                     index=opciones.index(st.session_state.respuestas[i]),
                     disabled=True, key=f"q{i}")
        else:
            r = st.radio("Respuesta:", opciones, key=f"q{i}")
            if st.button("Confirmar", key=f"b{i}"):
                st.session_state.respuestas[i] = r
                st.rerun()

    if len(st.session_state.respuestas) == len(preguntas):

        aciertos = sum(
            1 for i, fila in preguntas.iterrows()
            if st.session_state.respuestas[i] == fila["Correcta"]
        )

        total = len(preguntas)
        porcentaje = aciertos / total * 100

        st.divider()

        if porcentaje >= 70:
            st.success(f"RESULTADO: APROBADO — {porcentaje:.0f}%")
            st.balloons()
        else:
            st.error(f"RESULTADO: DESAPROBADO — {porcentaje:.0f}%")
