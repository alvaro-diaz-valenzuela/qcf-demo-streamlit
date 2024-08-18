from typing import Any
import streamlit as st

from modules import aux_functions as aux
from modules import qcf_wrappers as qcw
import qcfinancial as qcf


def ibor_leg() -> tuple[dict[str, Any], dict[str, Any]]:
    """
    Despliega los inputs necesarios para dar de alta una pata con flujos de tipo Ibor (eg. TERMSOFR)
    """
    st.markdown("### Parámetros Pata Ibor")
    with st.expander("👁️‍🗨️", expanded=True):
        col1, col2 = st.columns(2)

        parameters = {}
        parameters2 = {}
        with col1:
            rec_pay = st.selectbox("Activo o Pasivo", options=[rp for rp in qcw.AP])
            parameters['rec_pay'] = qcw.AP(rec_pay).as_qcf()
            parameters2['rec_pay'] = qcw.AP(rec_pay).as_qcf()

            start_date = st.date_input("Fecha de Inicio")
            parameters['start_date'] = qcf.QCDate(start_date.isoformat())
            parameters2['start_date'] = qcf.QCDate(start_date.isoformat())

            c1, c2 = st.columns([1, 2])
            with c1:
                plazo = st.text_input("Plazo (Tenor)", value="1Y", help="6M, 5Y, 5Y6M, 5Y6M15D")
                try:
                    tenor = qcf.Tenor(plazo)
                except:
                    tenor = None
                    st.error("No es un Tenor válido. El formato es aYbMcD, con a, b y c enteros positivos.")
            with c2:
                if tenor is not None:
                    end_date = aux.date_plus_tenor(parameters['start_date'], tenor)
                    parameters['end_date'] = end_date
                    parameters2['end_date'] = end_date
                    st.text_input(f"Fecha Final", disabled=True, value=f"{end_date}")
                else:
                    st.text_input(f"Fecha Final: ", disabled=True)

            bus_adj_rule = st.selectbox("Regla para Ajuste de Fechas", options=[r for r in qcw.BusAdjRules])
            parameters['bus_adj_rule'] = qcw.BusAdjRules(bus_adj_rule).as_qcf()
            parameters2['bus_adj_rule'] = qcw.BusAdjRules(bus_adj_rule).as_qcf()

            settlement_periodicity = st.text_input("Periodicidad de Pago", value="5Y", help="Ej: 5Y3M, 10Y, 6M")
            parameters['settlement_periodicity'] = qcf.Tenor(settlement_periodicity)
            parameters2['settlement_periodicity'] = qcf.Tenor(settlement_periodicity)

            settlement_stub_period = st.selectbox("Período Irregular de Pago", options=[p for p in qcw.StubPeriods])
            parameters['settlement_stub_period'] = qcw.StubPeriods(settlement_stub_period).as_qcf()
            parameters2['settlement_stub_period'] = qcw.StubPeriods(settlement_stub_period).as_qcf()

            settlement_calendar = st.selectbox(
                "Calendario de Pago",
                options=['CL', 'US'],
                help="Se limita a 2 calendarios sólo para el ejemplo"
            )
            parameters['settlement_calendar'] = aux.get_business_calendar(settlement_calendar, range(2024, 2035))
            parameters2['settlement_calendar'] = aux.get_business_calendar(settlement_calendar, range(2024, 2035))

            settlement_lag = st.number_input("Lag de Pago", min_value=0)
            parameters['settlement_lag'] = settlement_lag
            parameters2['settlement_lag'] = settlement_lag

            fixing_periodicity = st.text_input("Periodicidad de Fijación", value="3M", help="Ej: 3M, 6M")
            parameters['fixing_periodicity'] = qcf.Tenor(fixing_periodicity)
            parameters2['fixing_periodicity'] = qcf.Tenor(fixing_periodicity)

            fixing_stub_period = st.selectbox("Período Irregular de Fijación", options=[p for p in qcw.StubPeriods])
            parameters['fixing_stub_period'] = qcw.StubPeriods(fixing_stub_period).as_qcf()
            parameters2['fixing_stub_period'] = qcw.StubPeriods(fixing_stub_period).as_qcf()

        with col2:
            fixing_calendar = st.selectbox(
                "Calendario de Fijación",
                options=['CL', 'US'],
                help="Se limita a 2 calendarios sólo para el ejemplo"
            )
            parameters['fixing_calendar'] = aux.get_business_calendar(fixing_calendar, range(2024, 2035))
            parameters2['fixing_calendar'] = aux.get_business_calendar(fixing_calendar, range(2024, 2035))

            fixing_lag = st.number_input("Lag de Fijación", min_value=0)
            parameters['fixing_lag'] = fixing_lag
            parameters2['fixing_lag'] = fixing_lag

            interest_rate_index = st.selectbox(
                "Índice de Tasa de Interés",
                options=[indice.value for indice in qcw.InterestRateIndex]
            )
            parameters['interest_rate_index'] = qcw.InterestRateIndex(interest_rate_index).as_qcf()
            parameters2['interest_rate_index'] = qcw.InterestRateIndex(interest_rate_index).as_qcf()

            initial_notional = st.number_input("Nocional Inicial", min_value=0.0)
            parameters['initial_notional'] = initial_notional
            parameters2['notional_and_amort'] = initial_notional

            amort_is_cashflow = st.selectbox("Amort es Cashflow", options=[True, False])
            parameters['amort_is_cashflow'] = amort_is_cashflow
            parameters2['amort_is_cashflow'] = amort_is_cashflow

            notional_currency = st.selectbox(
                "Moneda del Nocional",
                options=set([m for m in qcw.Currency]) - {'CL2'},
            )
            parameters["notional_currency"] = qcw.Currency(notional_currency).as_qcf()
            parameters2["notional_currency"] = qcw.Currency(notional_currency).as_qcf()

            spread = st.number_input("Spread", format='%.4f')
            parameters["spread"] = spread
            parameters2["spread"] = spread

            gearing = st.number_input("Gearing", format='%.4f')
            parameters["gearing"] = gearing
            parameters2["gearing"] = gearing

            sett_lag_behaviour = st.selectbox(
                "Comportamiento del Lag de Pago",
                options=[s for s in qcw.SettLagBehaviour],
            )
            parameters["sett_lag_behaviour"] = qcw.SettLagBehaviour(sett_lag_behaviour).as_qcf()
            parameters2["sett_lag_behaviour"] = qcw.SettLagBehaviour(sett_lag_behaviour).as_qcf()

        return parameters, parameters2
