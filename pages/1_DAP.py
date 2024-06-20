import streamlit as st
from PIL import Image

import qcfinancial as qcf

from modules import dap

st.set_page_config(
    page_title="DAP",
    page_icon=Image.open('./assets/q.png'),
    layout="wide",
    initial_sidebar_state="auto",
    menu_items=None,
)

st.image(Image.open('./assets/logo_qcf_streamlit.png'), width=500)

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
col1, col2 = st.columns(2)
with col1:
    moneda = st.selectbox("Elige la moneda", options=["CLP", "UF"])
    qcf_moneda = qcf.QCCLP() if moneda == "CLP" else qcf.QCCLF()
    if moneda == "CLP":
        monto = st.number_input("Ingresa el monto", min_value=100_000, step=1_000)
    else:
        monto = st.number_input("Ingresa el monto", min_value=3.000, step=.0100, format="%.4f")
with col2:
    plazo = st.number_input("Ingresa el plazo en días", min_value=7 if moneda == "CLP" else 90, max_value=365, step=1)
    type_of_rate = "Lin Act/30" if moneda == "CLP" else "Lin Act/360"
    valor_tasa = st.number_input(f"Ingresa el valor de la tasa (% {type_of_rate})", step=.01)

simular = st.button("Simular")
st.subheader("Resultados")
expander = st.expander("Desplegar ...", expanded=False)
result = "No ha simulado ..."
if simular:
    temp = dap.simulate(monto, plazo, qcf_moneda, valor_tasa)
    mf = temp["monto_final"]
    monto_final_format = f"{mf:,.0f}" if moneda == "CLP" else f"{mf:,.4f}"
    result = f"""
    Monto inicial: {monto:,.0f}\n
    Moneda: {moneda}\n
    Plazo: {temp["plazo"]:,.0f}\n
    Tasa: {temp["tasa"] / 100:.2%}\n
    Tipo de Tasa: {temp["tipo_tasa"]}\n
    Monto final: {monto_final_format}
    """
expander.write(result)
expander2 = st.expander("Código", expanded=False)
expander2.write('El "Backend" de este ejemplo es la siguiente función:')
expander2.code("""
def simulate(monto: float, plazo: int, moneda: qcf.QCCLP | qcf.QCCLF):
    hoy = date.today()
    qcf_hoy = qcf.QCDate(hoy.day, hoy.month, hoy.year)
    scl = qcf.BusinessCalendar(qcf_hoy, 2)
    end_date = scl.next_busy_day(qcf_hoy.add_days(plazo))
    plazo_real = qcf_hoy.day_diff(end_date)
    if isinstance(moneda, qcf.QCCLP):
        rate = qcf.QCInterestRate(tasa, qcf.QCAct30(), qcf.QCLinearWf())
        tipo_tasa = "Lineal Act/30"
    else:
        rate = qcf.QCInterestRate(tasa, qcf.QCAct360(), qcf.QCLinearWf())
        tipo_tasa = "Lineal Act/360"
    wf = rate.wf(plazo_real)
    monto_final = moneda.amount(monto * wf)
    return {
        "tasa": tasa, 
        "monto_final": monto_final,
        "end_date": end_date,
        "plazo": plazo_real,
        "tipo_tasa": tipo_tasa,
    }""",
               )
