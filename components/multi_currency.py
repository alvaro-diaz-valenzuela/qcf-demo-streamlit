from typing import Any
import streamlit as st

from modules import aux_functions as aux
from modules import qcf_wrappers as qcw


def multi_currency() -> tuple[dict[str, Any], dict[str, Any]]:
    st.markdown("### Parámetros Multi Currency")
    with st.expander("👁️‍🗨️", expanded=True):
        mccy1, mccy2 = st.columns(2)
        parameters = {}
        parameters2 = {}
        with mccy1:
            settlement_currency = st.selectbox(
                    "Moneda de Pago",
                    options=set([m for m in qcw.Currency])-{'CL2'},
                )
            parameters["settlement_currency"] = qcw.Currency(settlement_currency).as_qcf()
            parameters2["settlement_currency"] = qcw.Currency(settlement_currency).as_qcf()

            fx_rate_index_name = st.selectbox("Índice FX", options=["USDOBS", "UF"])

            parameters["fx_rate_index"] = aux.get_fx_rate_index(fx_rate_index_name)
            parameters2["fx_rate_index"] = aux.get_fx_rate_index(fx_rate_index_name)
        with mccy2:
            fx_fixing_lag = st.number_input("Lag de Fixing FX", min_value=0)
            parameters["fx_rate_index_fixing_lag"] = fx_fixing_lag
            parameters2["fx_rate_index_fixing_lag"] = fx_fixing_lag

            fx_fixing_lag_pivot = st.selectbox("Pivot FX Fixing Lag", options=[f.value for f in qcw.FxFixingLagPivot])

            parameters["fx_fixing_lag_pivot"] = qcw.FxFixingLagPivot(fx_fixing_lag_pivot).as_qcf()
            parameters2["fx_fixing_lag_pivot"] = qcw.FxFixingLagPivot(fx_fixing_lag_pivot).as_qcf()

        return parameters, parameters2
