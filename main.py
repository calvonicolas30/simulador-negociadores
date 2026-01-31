import streamlit as st
from st_gsheets_connection import GSheetsConnection
import pandas as pd
from datetime import datetime
import time

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="División Negociadores - Certificación", layout="centered")

# --- CONEXIÓN A GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

def cargar_datos():
    df_p = conn.read(worksheet="preguntas", ttl="5m")
    df_u = conn.read(worksheet="usuarios", ttl="5m")

    # Normalizamos nombres de columnas
    df_p.columns = [c.strip() for c in df_p.columns]
    df_u.columns = [c.strip() for c in df_u.columns]

    return df_p, df_u

# --- REGISTRO DE RESULTADOS ---
def registrar_en_historial(usuario, nivel, aciertos, total, estado):
    fecha_actual = datetime.now().strftime("%d/%m/%Y %H:%M")
    st.success(f"📝 Registro generado: {usuario} - {nivel} - {aciertos}/{total} - {estado}")

# --- LOGIN ---
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        try:
            st.image("logo_policia.png", width=200)
        except:
            st.info("Sistema de Certificación - División Negociadores")

        st.title("Ingreso al Sistema")

        usuario_ingresado = st.text_input("Usuario Oficial")
        clave_ingresada = st.text_input("Contraseña", type="password")

        if st.button("ACCEDER"):
            try:
                _, df_usuarios = cargar_datos()

                df_usuarios.columns = ["usuario", "password"]

                credenciales = dict(zip(
                    df_usuarios['usuario'].astype(str).str.strip(),
                    df_usuarios['password'].astype(str).str.strip()
                ))

                if usuario_ingresado.strip() in credenciales and credenciales[usuario_ingresado.strip()] == clave_ingresada.strip():
                    st.session_state.autenticado = True
                    st.session_state.usuario_actual = usuario_ingresado
                    st.rerun()
                else:
                    st.error("Usuario o contraseña incorrectos")

            except Exception as e:
                st.error("No se pudo conectar con Google Sheets.")
                st.code(e)

else:
    # --- PANEL ---
    st.sidebar.title("👮 Panel de Control")
    st.sidebar.write(f"Usuario: **{st.session_state.usuario_actual}**")

    menu = ["Realizar Examen"]
    if st.session_state.usuario_actual.lower() == "admin":
        menu.append("Ver Historial")

    opcion = st.sidebar.selectbox("Seleccione acción:", menu)

    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.autenticado = False
        st.rerun()

    df_preguntas, _ = cargar_datos()

    # ---

