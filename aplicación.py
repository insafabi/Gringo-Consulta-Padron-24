import base64
import glob
import os
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Consulta Padrón - Seccional 43",
    page_icon="🔴",
    layout="centered",
)


def obtener_imagen_base64():
  for archivo in ["portada.jpg", "portada.png", "portada.JPG", "portada.PNG"]:
    if os.path.exists(archivo):
      with open(archivo, "rb") as f:
        data = f.read()
      ext = archivo.split(".")[-1].lower()
      mime = "image/jpeg" if ext in ["jpg", "jpeg"] else "image/png"
      return f"data:{mime};base64,{base64.b64encode(data).decode()}"
  return None


img_base64 = obtener_imagen_base64()

css_movil = (
    f"""
    <style>
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    
    .stApp {{
        background-image: url("{img_base64}");
        background-size: cover;
        background-position: top center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    
    .stApp::before {{
        content: "";
        position: fixed;
        top: 0; left: 0; width: 100%; height: 100%;
        background-color: rgba(0, 0, 0, 0.45);
        pointer-events: none;
        z-index: 0;
    }}

    .block-container {{
        position: relative;
        z-index: 1;
        padding-top: 23rem;
        padding-bottom: 3rem;
        max-width: 420px;
    }}
    
    div.stButton > button:first-child {{
        background-color: #e53935 !important;
        color: white !important;
        font-weight: bold;
        font-size: 1.05rem;
        border-radius: 12px;
        border: none;
        padding: 0.75rem 1rem;
        width: 100%;
        box-shadow: 0px 4px 12px rgba(229, 57, 53, 0.4);
        transition: all 0.2s ease;
    }}
    div.stButton > button:first-child:hover {{
        background-color: #c62828 !important;
    }}
    </style>
    """
    if img_base64
    else """
    <style>
    .stApp { background-color: #f4f6f9; }
    </style>
    """
)

st.markdown(css_movil, unsafe_allow_html=True)


@st.cache_data
def cargar_padron():
  archivos_excel = glob.glob("*.xlsx") + glob.glob("*.XLSX")
  lista_df = []

  for archivo in archivos_excel:
    try:
      excel_file = pd.ExcelFile(archivo)
      for hoja in excel_file.sheet_names:
        df_hoja = pd.read_excel(archivo, sheet_name=hoja)
        df_hoja.columns = df_hoja.columns.astype(str).str.strip()
        lista_df.append(df_hoja)
    except Exception:
      pass

  if lista_df:
    df_consolidado = pd.concat(lista_df, ignore_index=True)

    if "Nº de Documento" in df_consolidado.columns:
      df_consolidado = df_consolidado.rename(
          columns={"Nº de Documento": "cedula"}
      )
    elif "N° de Documento" in df_consolidado.columns:
      df_consolidado = df_consolidado.rename(
          columns={"N° de Documento": "cedula"}
      )

    if "cedula" in df_consolidado.columns:
      df_consolidado["cedula_limpia"] = (
          df_consolidado["cedula"].astype(str).str.replace(".", "").str.strip()
      )
      return df_consolidado

  return pd.DataFrame()


try:
  df = cargar_padron()

  if not df.empty:
    if "resultado_persona" not in st.session_state:
      st.session_state.resultado_persona = None

    if st.session_state.resultado_persona is None:
      cedula_input = st.text_input(
          "Número de cédula",
          placeholder="Ej: 123456",
          label_visibility="collapsed",
          key="input_cedula_unico",
      )

      buscar_clic = st.button("Consultar", key="btn_consultar_unico")

      if buscar_clic:
        if cedula_input:
          clean_input = (
              cedula_input.replace(".", "").replace("-", "").strip()
          )
          resultado = df[df["cedula_limpia"] == clean_input]

          if not resultado.empty:
            st.session_state.resultado_persona = resultado.iloc[0].to_dict()
            st.rerun()
          else:
            st.warning("No se encontró esa cédula en el padrón.")
        else:
          st.warning("Por favor, ingresa un número de cédula.")

    else:
      p = st.session_state.resultado_persona

      nombre_completo = f"{p.get('NOMBRE', '')} {p.get('APELLIDO', '')}".strip()
      desc_local = str(p.get("DESC_LOCAL", p.get("local", "")))
      mesa = str(p.get("mesa", "-"))
      orden = str(p.get("orden", "-"))
      cedula_str = f"{int(p['cedula']):,}".replace(",", ".")

      html_resultado = f"""<div style="background: rgba(255, 255, 255, 0.88); backdrop-filter: blur(14px); -webkit-backdrop-filter: blur(14px); padding: 24px 20px; border-radius: 20px; box-shadow: 0px 15px 35px rgba(0, 0, 0, 0.4); margin-top: 15px; border: 1px solid rgba(255, 255, 255, 0.8);">
<h3 style="color: #111; text-align: center; margin-top: 0; margin-bottom: 15px; font-size: 1.15rem; font-weight: 800;">Datos del elector</h3>
<div style="font-size: 0.75rem; font-weight: 800; color: #c62828; text-transform: uppercase; margin-top: 10px; margin-bottom: 3px;">👤 Nombre y Apellido</div>
<div style="background: #ffffff; color: #111111; padding: 10px 14px; border-radius: 10px; font-weight: 700; font-size: 0.95rem; border: 1px solid #ced4da;">{nombre_completo}</div>
<div style="font-size: 0.75rem; font-weight: 800; color: #c62828; text-transform: uppercase; margin-top: 10px; margin-bottom: 3px;">🆔 Cédula de Identidad</div>
<div style="background: #ffffff; color: #111111; padding: 10px 14px; border-radius: 10px; font-weight: 700; font-size: 0.95rem; border: 1px solid #ced4da;">{cedula_str}</div>
<div style="font-size: 0.75rem; font-weight: 800; color: #c62828; text-transform: uppercase; margin-top: 10px; margin-bottom: 3px;">📍 Local de Votación</div>
<div style="background: #ffffff; color: #111111; padding: 10px 14px; border-radius: 10px; font-weight: 700; font-size: 0.95rem; border: 1px solid #ced4da;">{desc_local}</div>
<div style="display: flex; gap: 10px; margin-top: 10px;">
<div style="flex: 1;">
<div style="font-size: 0.75rem; font-weight: 800; color: #c62828; text-transform: uppercase; margin-bottom: 3px;">🗳️ Mesa</div>
<div style="background: #ffffff; color: #111111; padding: 10px 14px; border-radius: 10px; font-weight: 700; font-size: 0.95rem; text-align: center; border: 1px solid #ced4da;">{mesa}</div>
</div>
<div style="flex: 1;">
<div style="font-size: 0.75rem; font-weight: 800; color: #c62828; text-transform: uppercase; margin-bottom: 3px;">📋 Orden</div>
<div style="background: #ffffff; color: #111111; padding: 10px 14px; border-radius: 10px; font-weight: 700; font-size: 0.95rem; text-align: center; border: 1px solid #ced4da;">{orden}</div>
</div>
</div>
</div>"""
      st.markdown(html_resultado, unsafe_allow_html=True)

      st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
      if st.button("VOLVER", key="btn_volver_unico"):
        st.session_state.resultado_persona = None
        st.rerun()

  else:
    st.error(
        "⚠️ No se detectó el archivo Excel o la columna de cédula requerida."
    )

except Exception as e:
  st.error(f"Error al procesar la información: {e}")
