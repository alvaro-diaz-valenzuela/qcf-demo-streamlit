import streamlit as st
from PIL import Image
import pandas as pd

st.set_page_config(
    page_title="Inicio",
    page_icon=Image.open('./assets/favicon-32x32.png'),
    layout="wide",
    initial_sidebar_state="auto",
    menu_items=None,
)

st.title("¿Qué puedes construir con qcfinancial?")
st.subheader("Esta es una colección de ejemplos de uso")
st.write("---")
st.write("La tabla siguiente muestra el roadmap. A medida que se completen, "
         "nuevas páginas de ejemplos irán apareciendo en la barra lateral.")

col1, col2 = st.columns(2)

roadmap = [
    {"Nombre": "DAP", "Descripción": "Valorización de un depósito a plazo", "Status": "⚠️"},
    {"Nombre": "BTU y BTP", "Descripción": "Valorización de renta fija chilena", "Status": "⚠️"},
]

st.dataframe(pd.DataFrame(roadmap), hide_index=True)
