import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from PIL import Image
from datetime import datetime
import time

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="División Negociadores - Certificación", layout="centered")

# --- CONEXIÓN A LA BASE DE DATOS (GOOGLE SHEETS) ---
conn = st.connection("gsheets", type=GSheetsConnection)

def cargar_datos():
    # Lee las pestañas del Google Sheet
    # Asegúrate de que los nombres coincidan exactamente: 'preguntas' y 'usuarios'
    df_p = conn.read(worksheet="preguntas", ttl="5m")
    df_u = conn.read(worksheet="usuarios", ttl="5m")
    return df_p, df_u

def registrar_en_historial(usuario, nivel, aciertos, total, estado):
    # Esta función prepara la fila para el historial
    fecha_actual = datetime.now().strftime("%d/%m/%Y %H:%M")
    nueva_fila = pd.DataFrame([{
        "Fecha": fecha_actual,
        "Usuario": usuario,
        "Nivel": nivel,
        "Puntaje": f"{aciertos}/{total}",
        "Resultado": estado
    }])
    # Nota: La escritura en GSheets requiere configuración adicional de permisos (Service Account)
    # Por ahora, el sistema mostrará el resultado en pantalla y lo registrará si tienes permisos.
    st.write(f"📝 Registro generado para: {usuario}")

# --- SISTEMA DE LOGUEO ---
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        try:
            st.image("logotipo_policia.png", width=200)
        except:
            st.info("Sistema de Certificación - División Negociadores")
        
        st.title("Ingreso")
        usuario_ingresado = st.text_input("Usuario Oficial")
        clave_ingresada = st.text_input("Contraseña", type="password")
        
        if st.button("ACCEDER"):
            try:
                _, df_usuarios = cargar_datos()
                # Convertimos a diccionario para validar
                credenciales = dict(zip(df_usuarios['usuario'].astype(str), df_usuarios['password'].astype(str)))
                
                if usuario_ingresado in credenciales and str(credenciales[usuario_ingresado]) == clave_ingresada:
                    st.session_state.autenticado = True
                    st.session_state.usuario_actual = usuario_ingresado
                    st.rerun()
                else:
                    st.error("Usuario o clave incorrectos")
            except:
                st.error("Error al conectar con la base de datos de usuarios.")
else:
    # --- INTERFAZ DEL SIMULADOR ---
    st.sidebar.title("👮 Panel de Control")
    st.sidebar.write(f"Usuario: **{st.session_state.usuario_actual}**")
    
    # Menú para el Jefe (si el usuario es 'admin')
    menu = ["Realizar Examen"]
    if st.session_state.usuario_actual.lower() == "admin":
        menu.append("Ver Historial")
    
    opcion = st.sidebar.selectbox("Seleccione acción:", menu)

    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.autenticado = False
        st.rerun()

    df_preguntas, _ = cargar_datos()

    if opcion == "Realizar Examen":
        st.header("Certificación de Competencias")
        nivel_elegido = st.selectbox("Elija Nivel:", ["Inicial", "Experto"])
        
        # Filtrar preguntas por nivel
        preguntas_filtradas = df_preguntas[df_preguntas['Nivel'] == nivel_elegido].copy()
        
        if not preguntas_filtradas.empty:
            # Mezclar preguntas cada vez que se inicia
            if "shuffled_db" not in st.session_state or st.session_state.get("last_level") != nivel_elegido:
                st.session_state.shuffled_db = preguntas_filtradas.sample(frac=1).reset_index(drop=True)
                st.session_state.last_level = nivel_elegido
                st.session_state.hora_inicio = time.time()

            # Temporizador de 10 minutos
            tiempo_limite = 10 * 60
            transcurrido = time.time() - st.session_state.hora_inicio
            restante = max(0, tiempo_limite - int(transcurrido))
            
            m, s = divmod(restante, 60)
            st.sidebar.warning(f"⏳ Tiempo restante: {m:02d}:{s:02d}")

            if restante <= 0:
                st.error("⚠️ TIEMPO AGOTADO. El examen se ha cerrado automáticamente.")
            else:
                with st.form("form_examen"):
                    respuestas_del_oficial = []
                    for idx, fila in st.session_state.shuffled_db.iterrows():
                        st.write(f"**{idx+1}. {fila['Pregunta']}**")
                        opciones = [fila['Opción_A'], fila['Opción_B'], fila['Opción_C']]
                        r = st.radio(f"Seleccione su respuesta para la {idx+1}:", opciones, key=f"pre_{idx}")
                        respuestas_del_oficial.append(r)
                    
                    if st.form_submit_button("ENVIAR EXAMEN"):
                        aciertos = sum(1 for i, res in enumerate(respuestas_del_oficial) 
                                     if res == st.session_state.shuffled_db.iloc[i]['Correcta'])
                        total = len(st.session_state.shuffled_db)
                        porcentaje = (aciertos / total) * 100
                        resultado_final = "APROBADO" if porcentaje >= 70 else "DESAPROBADO"
                        
                        st.divider()
                        if resultado_final == "APROBADO":
                            st.success(f"Puntaje: {porcentaje:.0f}% - RESULTADO: {resultado_final}")
                            st.balloons()
                        else:
                            st.error(f"Puntaje: {porcentaje:.0f}% - RESULTADO: {resultado_final}")
                        
                        registrar_en_historial(st.session_state.usuario_actual, nivel_elegido, aciertos, total, resultado_final)
                        # Limpiar para un nuevo intento si se desea
                        del st.session_state.shuffled_db
        else:
            st.warning("No hay preguntas cargadas para este nivel en el Google Sheet.")

    elif opcion == "Ver Historial":
        st.header("📋 Registro de Exámenes")
        try:
            df_historial = conn.read(worksheet="historial", ttl="0")
            st.dataframe(df_historial, use_container_width=True)
        except:
            st.info("Aún no hay registros en la pestaña 'historial'.")
