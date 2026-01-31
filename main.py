import streamlit as st
import pandas as pd
from PIL import Image
from datetime import datetime
import time

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="División Negociadores - Certificación", layout="centered")

# --- ID DE TU GOOGLE SHEET ---
SHEET_ID = "1Xg4QZrUuF-r5rW5s8ZJJrIIHsNI5UzZ0taJ6CYcV-oA"

# --- FUNCIÓN PARA LEER DATOS DESDE GOOGLE SHEET ---
def cargar_datos():
    url_preguntas = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=preguntas"
    url_usuarios = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=usuarios"

    df_p = pd.read_csv(url_preguntas)
    df_u = pd.read_csv(url_usuarios)

    return df_p, df_u

# --- SISTEMA DE LOGUEO ---
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        try:
            st.image("logo_policia.png", width=200)
        except:
            st.info("Sistema de Certificación - División Negociadores")
        
        st.title("Ingreso")
        usuario_ingresado = st.text_input("Usuario Oficial")
        clave_ingresada = st.text_input("Contraseña", type="password")
        
        if st.button("ACCEDER"):
            try:
                _, df_usuarios = cargar_datos()
                credenciales = dict(zip(df_usuarios['usuario'].astype(str), df_usuarios['password'].astype(str)))
                
                if usuario_ingresado in credenciales and str(credenciales[usuario_ingresado]) == clave_ingresada:
                    st.session_state.autenticado = True
                    st.session_state.usuario_actual = usuario_ingresado
                    st.rerun()
                else:
                    st.error("Usuario o clave incorrectos")
            except Exception as e:
                st.error("No se pudo conectar con Google Sheets.")
                st.code(str(e))

else:
    # --- INTERFAZ PRINCIPAL ---
    st.sidebar.title("👮 Panel de Control")
    st.sidebar.write(f"Usuario: **{st.session_state.usuario_actual}**")
    
    menu = ["Realizar Examen"]
    opcion = st.sidebar.selectbox("Seleccione acción:", menu)

    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.autenticado = False
        st.rerun()

    df_preguntas, _ = cargar_datos()

    if opcion == "Realizar Examen":
        st.header("Certificación de Competencias")
        nivel_elegido = st.selectbox("Elija Nivel:", ["Inicial", "Experto"])
        
        preguntas_filtradas = df_preguntas[df_preguntas['Nivel'] == nivel_elegido].copy()
        
        if not preguntas_filtradas.empty:
            if "shuffled_db" not in st.session_state or st.session_state.get("last_level") != nivel_elegido:
                st.session_state.shuffled_db = preguntas_filtradas.sample(frac=1).reset_index(drop=True)
                st.session_state.last_level = nivel_elegido
                st.session_state.hora_inicio = time.time()

            tiempo_limite = 10 * 60
            transcurrido = time.time() - st.session_state.hora_inicio
            restante = max(0, tiempo_limite - int(transcurrido))
            
            m, s = divmod(restante, 60)
            st.sidebar.warning(f"⏳ Tiempo restante: {m:02d}:{s:02d}")

            if restante <= 0:
                st.error("⚠️ TIEMPO AGOTADO.")
            else:
                with st.form("form_examen"):
                    respuestas = []
                    for idx, fila in st.session_state.shuffled_db.iterrows():
                        st.write(f"**{idx+1}. {fila['Pregunta']}**")
                        opciones = [fila['Opción_A'], fila['Opción_B'], fila['Opción_C']]
                        r = st.radio("Seleccione una opción:", opciones, key=f"q_{idx}")
                        respuestas.append(r)
                    
                    if st.form_submit_button("ENVIAR EXAMEN"):
                        aciertos = sum(1 for i, r in enumerate(respuestas)
                                     if r == st.session_state.shuffled_db.iloc[i]['Correcta'])
                        total = len(respuestas)
                        porcentaje = (aciertos / total) * 100
                        resultado = "APROBADO" if porcentaje >= 70 else "DESAPROBADO"
                        
                        st.divider()
                        if resultado == "APROBADO":
                            st.success(f"Puntaje: {porcentaje:.0f}% — {resultado}")
                            st.balloons()
                        else:
                            st.error(f"Puntaje: {porcentaje:.0f}% — {resultado}")
                        
                        del st.session_state.shuffled_db
        else:
            st.warning("No hay preguntas cargadas para este nivel.")
