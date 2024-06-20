import streamlit as st
from PIL import Image
import pandas as pd


st.set_page_config(
    page_title="Inicio",
    page_icon=Image.open('./assets/q.png'),
    layout="wide",
    initial_sidebar_state="auto",
    menu_items=None,
)

st.image(Image.open('./assets/logo_qcf_streamlit.png'), width=500)

st.title("¿Qué puedes construir con qcfinancial?")
st.subheader("Esta es una colección de ejemplos de uso")
st.write("---")
st.write("La tabla siguiente muestra el roadmap. A medida que se completen, "
         "nuevas páginas de ejemplos irán apareciendo en la barra lateral.")

col1, col2 = st.columns(2)

roadmap = [
    {"Nombre": "DAP", "Descripción": "Valorización de un depósito a plazo", "Status": "️✅"},
    {"Nombre": "BTU y BTP", "Descripción": "Valorización de renta fija chilena", "Status": "✅ "},
    {"Nombre": "FX Forward", "Descripción": "Valorización de un forward USDCLP", "Status": "⚠️"},
    {"Nombre": "Crédito ICPCLP", "Descripción": "Alta y Devengo de un Crédito ICPCLP", "Status": "⚠️"},
    {"Nombre": "Swap ICPCLP", "Descripción": "Alta y Valorización de un Swap ICPCLP", "Status": "✅ ⚠️"},
    {"Nombre": "CCS Fija CLF vs ICPCLP", "Descripción": "Alta y Valorización de un CCS CLFCLP Estándar",
     "Status": "✅ ⚠️"},
    {"Nombre": "CCS SOFR vs ICPCLP", "Descripción": "Alta y Valorización de un CCS USDCLP Estándar",
     "Status": "✅ ⚠️"},
    {"Nombre": "Sens. Swap ICPCLP", "Descripción": "Sensibilidad a la curva cero de un Swap ICPCLP", "Status": "⚠️"},
]

st.dataframe(pd.DataFrame(roadmap), hide_index=True, use_container_width=True)
