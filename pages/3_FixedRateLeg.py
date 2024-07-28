import streamlit as st
from PIL import Image

import qcfinancial as qcf

from modules import aux_functions as aux
from modules import qcf_wrappers as qcw

st.set_page_config(
    page_title="FixedRateLeg",
    page_icon=Image.open('./assets/q.png'),
    layout="wide",
    initial_sidebar_state="auto",
    menu_items=None,
)

st.image(Image.open('./assets/logo_qcf_streamlit.png'), width=500)

st.markdown("# FixedRateLeg")
st.markdown("""En este ejemplo se utilizan los objetos:
- `Leg`
- `QCInterestRate`
- `BusinessCalendar`
- `LegFactory`
- `FixedRateCashflow`

Se busca demostrar la funcionalidad hoy disponible para construir patas a tasa fija.
""")
st.write("---")


st.markdown("### Parámetros - Amortización Bullet")
col1, col2 = st.columns(2)

parameters = {}
with col1:
    rec_pay = st.selectbox("Activo o Pasivo", options=[rp for rp in qcw.AP])
    parameters['rec_pay'] = qcw.AP(rec_pay).as_qcf()

    start_date = st.date_input("Fecha de Inicio")
    parameters['start_date'] = qcf.QCDate(start_date.isoformat())

    end_date = st.date_input("Fecha Final")
    parameters['end_date'] = qcf.QCDate(end_date.isoformat())

    bus_adj_rule = st.selectbox("Regla para Ajuste de Fechas", options=[r for r in qcw.BusAdjRules])
    parameters['bus_adj_rule'] = qcw.BusAdjRules(bus_adj_rule).as_qcf()

    settlement_periodicity = st.text_input("Periodicidad de Pago", value="5Y", help="Ej: 5Y3M, 10Y, 6M")
    parameters['settlement_periodicity'] = qcf.Tenor(settlement_periodicity)


    settlement_stub_period = st.selectbox("Período Irregular", options=[p for p in qcw.StubPeriods])
    parameters['settlement_stub_period'] = qcw.StubPeriods(settlement_stub_period).as_qcf()

    settlement_calendar = st.selectbox(
        "Calendario de Pago",
        options=['CL', 'USD'],
        help="Se limita a 2 calendarios sólo para el ejemplo"
    )
    parameters['settlement_calendar'] = aux.get_business_calendar(settlement_calendar, range(2024, 2035))

    settlement_lag = st.number_input("Lag de Pago", min_value=0)
    parameters['settlement_lag'] = settlement_lag

with col2:
    initial_notional = st.number_input("Nocional Inicial", min_value=0.0)
    parameters['initial_notional'] = initial_notional

    amort_is_cashflow = st.selectbox("Amort es Cashflow", options=[True, False])
    parameters['amort_is_cashflow'] = amort_is_cashflow

    interest_rate_value = st.number_input("Interest Rate Value (%)", format='%.4f')
    year_fraction = st.selectbox("Fracción de año de la Tasa", options=[yf for yf in qcw.YearFraction])
    wealth_function = st.selectbox("Función de Capitalización de la Tasa", options=[wf for wf in qcw.WealthFactor])
    parameters["interest_rate"] = qcf.QCInterestRate(
        interest_rate_value / 100,
        qcw.YearFraction(year_fraction).as_qcf(),
        qcw.WealthFactor(wealth_function).as_qcf(),
    )

    notional_currency = st.selectbox(
        "Moneda del Nocional",
        options=set([m for m in qcw.Currency])-{'CL2'},
    )
    parameters["notional_currency"] = qcw.Currency(notional_currency).as_qcf()

    is_bond = st.selectbox("Es Bono", options=[True, False])
    parameters["is_bond"] = is_bond

    sett_lag_behaviour = st.selectbox(
        "Comportamiento del Lag de Pago",
        options=[s for s in qcw.SettLagBehaviour],
    )
    parameters["sett_lag_behaviour"] = qcw.SettLagBehaviour(sett_lag_behaviour).as_qcf()

st.markdown("---")
st.markdown("### Estructura de la Pata (Cashflows)")
fixed_rate_leg = qcf.LegFactory.build_bullet_fixed_rate_leg(**parameters)

if fixed_rate_leg.size() > 0:
    df = aux.leg_as_dataframe(fixed_rate_leg)
    st.dataframe(
        df.style.format(aux.format_dict),
        hide_index=True,
        use_container_width=True,
        height=500,
    )
