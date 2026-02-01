import streamlit as st
import pandas as pd
import time

# ================= CONFIG ==================

st.set_page_config(
    page_title="División Negociadores",
    page_icon="🛡",
    layout="centered"
)

SHEET_ID = "1Xg4QZrUuF-r5rW5s8ZJJrIIHsNI5UzZ0taJ6CYcV-oA"
USUARIOS_CSV = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&gid=0"
PREGUNTAS_CSV = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&gid=275635797"

TIEMPO_TOTAL = 120  # 2 minutos

# ================ FUNCIONES =================

@st.cache_data
def leer_sheet_csv(url):
    return pd.read_csv(url)

# ============== SESSION STATE ===============

if "login" not in st.session_state:
    st.session_state.login = False

if "inicio" not in st.session_state:
    st.session_state.inicio = None

if "preguntas" not in st.session_state:
    st.session_state.preguntas = None

if "indice" not in st.session_state:
    st.session_state.indice = 0

if "puntaje" not in st.session_state:
    st.session_state.puntaje = 0

# ================= LOGIN =====================

if not st.session_state.login:

    st.markdown("<br><br>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        try:
            st.image("logo_policia.PNG", width=320)
        except:
            pass

    st.markdown("""
    <h1 style='text-align:center;margin-bottom:0;'>DIVISIÓN NEGOCIADORES</h1>
    <h3 style='text-align:center;margin-top:5px;'>PROGRAMA DE CERTIFICACIÓN</h3>
    <hr style='margin-top:15px;margin-bottom:25px;'>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        with st.form("login_form"):
            usuario = st.text_input("Usuario")
            clave = st.text_input("Contraseña", type="password")
            ingresar = st.form_submit_button("ACCEDER", use_container_width=True)

            if ingresar:
                df_users = leer_sheet_csv(USUARIOS_CSV)
                df_users.columns = ["usuario", "password"]

                cred = dict(zip(
                    df_users["usuario"].astype(str).str.strip(),
                    df_users["password"].astype(str).str.strip()
                ))

                if usuario.strip() in cred and cred[usuario.strip()] == clave.strip():
                    st.session_state.login = True
                    st.session_state.inicio = time.time()
                    st.session_state.preguntas = None
                    st.session_state.indice = 0
                    st.session_state.puntaje = 0
                    st.rerun()
                else:
                    st.error("Usuario o contraseña incorrectos")

    st.stop()

# ================= EXAMEN ===================

df = leer_sheet_csv(PREGUNTAS_CSV)
df.columns = ["Nivel", "Pregunta", "Opción_A", "Opción_B", "Opción_C", "Correcta"]

if st.session_state.preguntas is None:
    st.session_state.preguntas = df.sample(frac=1).reset_index(drop=True)

preguntas = st.session_state.preguntas

# ================ TEMPORIZADOR ===============

tiempo_restante = TIEMPO_TOTAL - int(time.time() - st.session_state.inicio)

minutos = max(tiempo_restante,0) // 60
segundos = max(tiempo_restante,0) % 60

st.markdown(f"""
<h2 style='text-align:center;color:red;'>⏳ {minutos:02d}:{segundos:02d}</h2>
""", unsafe_allow_html=True)

if tiempo_restante <= 0:
    st.error("⛔ Tiempo agotado")
    st.subheader(f"Puntaje final: {st.session_state.puntaje} / {len(preguntas)}")
    st.stop()

# ================= PREGUNTAS =================

if st.session_state.indice < len(preguntas):

    fila = preguntas.iloc[st.session_state.indice]

    st.subheader(f"Pregunta {st.session_state.indice + 1} de {len(preguntas)}")
    st.write(f"**{fila['Pregunta']}**")

    opciones = [fila['Opción_A'], fila['Opción_B'], fila['Opción_C']]

    respuesta = st.radio("Seleccione una opción:", opciones, key=st.session_state.indice)

    if st.button("Siguiente", use_container_width=True):

        if respuesta == fila["Correcta"]:
            st.session_state.puntaje += 1

        st.session_state.indice += 1
        st.rerun()

else:
    st.success("🎉 Examen finalizado")
    st.subheader(f"Puntaje final: {st.session_state.puntaje} / {len(preguntas)}")

