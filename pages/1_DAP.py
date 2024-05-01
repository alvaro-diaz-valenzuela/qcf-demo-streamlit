import streamlit as st
from PIL import Image

import qcfinancial as qcf

from modules import dap

st.set_page_config(
    page_title="New Operation",
    page_icon=Image.open('./assets/favicon-32x32.png'),
    layout="wide",
    initial_sidebar_state="auto",
    menu_items=None,
)

st.title("DAP")
st.markdown("""En este ejemplo se utilizan los objetos:
- `QCDate`
- `QCInterestRate`
- `BusinessCalendar`

Para el cálculo de los intereses de utiliza un único valor, pero si el depósito es en CLP la tasa se asume Lineal 
Act/30, mientras que si es en UF, se asume Lineal Act/360.
""")
st.write("---")

st.subheader("Características del Depósito")
col1, col2, col3 = st.columns(3)
with col1:
    moneda = st.selectbox("Elige la moneda", options=["CLP", "UF"])
    qcf_moneda = qcf.QCCLP() if moneda == "CLP" else qcf.QCCLF()
with col2:
    if moneda == "CLP":
        monto = st.number_input("Ingresa el monto", min_value=100_000, step=1_000)
    else:
        monto = st.number_input("Ingresa el monto", min_value=3.000, step=.0100, format="%.4f")
with col3:
    plazo = st.number_input("Ingresa el plazo en días", min_value=7 if moneda == "CLP" else 90, max_value=365, step=1)
simular = st.button("Simular")
st.subheader("Resultados")
expander = st.expander("Desplegar ...", expanded=False)
result = "No ha simulado ..."
if simular:
    temp = dap.simulate(monto, plazo, qcf_moneda)
    mf = temp["monto_final"]
    monto_final_format = f"{mf:,.0f}" if moneda == "CLP" else f"{mf:,.4f}"
    result = f"""
    Monto inicial: {monto:,.0f}\n
    Moneda: {moneda}\n
    Plazo: {temp["plazo"]:,.0f}\n
    Tasa: {temp["tasa"]:.2%}\n
    Tipo de Tasa: {temp["tipo_tasa"]}\n
    Monto final: {monto_final_format}
    """
expander.write(result)

