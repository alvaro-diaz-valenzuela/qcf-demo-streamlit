import streamlit as st
from PIL import Image

import qcfinancial as qcf

from modules import btp_btu

st.set_page_config(
    page_title="BTP y BTU",
    page_icon=Image.open('./assets/q.png'),
    layout="wide",
    initial_sidebar_state="auto",
    menu_items=None,
)

st.image(Image.open('./assets/logo_qcf_streamlit.png'), width=500)

st.title("BTP y BTU: Renta Fija Chilena")
st.markdown("""En este ejemplo se utilizan los objetos:
- `QCLeg`
- `QCInterestRate`
- `BusinessCalendar`
- `LegFactory`
- `FixedRateCashflow`
- `ChileanFixedRateBond`

Se valoriza a TIR de mercado según las convenciones de la Bolsa de Comercio de Santiago.
""")
st.write("---")

st.subheader("Características de la Operación a Valorizar")
col1, col2 = st.columns(2)
with col1:
    nemotecnico = st.selectbox("Elige el bono", options=btp_btu.nemotecnicos.keys())
    qcf_moneda = qcf.QCCLP() if nemotecnico[0:3] == "BTP" else qcf.QCCLF()
    fecha_valorizacion = st.date_input("Ingresa la fecha de valorización")
    fecha_valorizacion = qcf.QCDate(
        fecha_valorizacion.day,
        fecha_valorizacion.month,
        fecha_valorizacion.year,
    )
with col2:
    if isinstance(qcf_moneda, qcf.QCCLP):
        monto = st.number_input("Ingresa el monto", min_value=1_000_000, step=100_000)
    else:
        monto = st.number_input("Ingresa el monto", min_value=10_000.000, step=10.0000, format="%.4f")
    tir_mercado = st.number_input(
        "Ingresa la TIR de mercado",
        min_value=-2.0000,
        step=.0001,
        value=0.0000,
        format="%.4f",
    )

valorizar = st.button("Valorizar")
st.subheader("Resultados")
expander = st.expander("Desplegar ...", expanded=False)
result = "No ha simulado ..."
if valorizar:
    temp = btp_btu.valorizar(nemotecnico, monto, fecha_valorizacion, tir_mercado)
    vp = temp["valor_presente"]
    vp_format = f"{vp:,.0f}" if qcf_moneda.get_iso_code() == "CLP" else f"{vp:,.4f}"
    result = f"""
    Precio: {temp["precio"] * 100:,.4f} %\n
    Valor Par (Base 100): {temp["valor_par"]:.8f}\n
    Valor Presente (UM): {vp_format}\n
    """
expander.write(result)

expander2 = st.expander("Código", expanded=False)
expander2.write('El "Backend" de este ejemplo son las siguientes funciones:')
expander2.code("""
import qcfinancial as qcf

# Dict con las características de los bonos
nemotecnicos = {...}

def build_fixed_rate_bond(nemotecnico: str):
    params = nemotecnicos[nemotecnico]
    rp = qcf.RecPay.RECEIVE
    fecha_inicio = params['fecha_inicial']
    fecha_final = params['fecha_final']
    bus_adj_rule = params['bus_adj_rule']
    periodicidad = params['periodicidad']
    periodo_irregular = params['periodo_irregular']
    calendario = params['calendario']
    lag_pago = params['lag_pago']
    nominal = params['nominal']
    amort_es_flujo = params['amort_es_flujo']
    tasa_cupon = params['tasa_cupon']
    moneda = params['moneda']
    es_bono = True

    return qcf.LegFactory.build_bullet_fixed_rate_leg(
        rp,
        fecha_inicio,
        fecha_final,
        bus_adj_rule,
        periodicidad,
        periodo_irregular,
        calendario,
        lag_pago,
        nominal,
        amort_es_flujo,
        tasa_cupon,
        moneda,
        es_bono
    )

def valorizar(nemotecnico: str, monto: float, fecha_valorizacion: qcf.QCDate, tir_mercado: float):
    fixed_rate_bond = build_fixed_rate_bond(nemotecnico)
    tera = nemotecnicos[nemotecnico]['tera']
    bono_chileno = qcf.ChileanFixedRateBond(fixed_rate_bond, tera)
    moneda = nemotecnicos[nemotecnico]['moneda']

    # En la Bolsa de Comercio las TIR de mercado de la renta fija se usan en esta convención
    tir_mercado = qcf.QCInterestRate(tir_mercado, qcf.QCAct365(),  qcf.QCCompoundWf())

    return {
        "valor_presente": moneda.amount(
            bono_chileno.present_value(fecha_valorizacion, tir_mercado) * monto / 100.0),
        "precio": bono_chileno.precio2(fecha_valorizacion, tir_mercado, 6),
        "valor_par": bono_chileno.valor_par(fecha_valorizacion),
    }

""",
               )
