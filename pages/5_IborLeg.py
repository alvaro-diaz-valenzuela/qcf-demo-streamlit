import pandas as pd
import streamlit as st
from PIL import Image

import qcfinancial as qcf

from components import (
    ibor_leg as frl,
    ibor_leg as ibl,
)
from modules import aux_functions as aux

st.set_page_config(
    page_title="IborLeg",
    page_icon=Image.open('./assets/q.png'),
    layout="wide",
    initial_sidebar_state="auto",
    menu_items=None,
)

st.image(Image.open('./assets/logo_qcf_streamlit.png'), width=500)

st.markdown("# IborLeg")
st.markdown("""En este ejemplo se utilizan los objetos:
- `Leg`
- `QCInterestRate`
- `BusinessCalendar`
- `LegFactory`
- `IborCashflow`

Se  muestra la funcionalidad hoy disponible para construir patas a tasa flotante (TERMSOFR).
""")
st.write("---")
try:
    parameters, parameters2 = ibl.ibor_leg()
    st.markdown("---")
    st.markdown("### Estructura de la Pata (Cashflows)")
    ibor_leg = qcf.LegFactory.build_bullet_ibor_leg(**parameters)

    tab1, tab2 = st.tabs(["Bullet", "Amortizable"])
    with tab1:
        if ibor_leg.size() > 0:
            df = aux.leg_as_dataframe(ibor_leg)
            st.dataframe(
                df.style.format(aux.format_dict),
                hide_index=True,
                use_container_width=True,
                height=500,
            )
    with tab2:
        if ibor_leg.size() > 0:
            data = pd.DataFrame([{
                "notional": parameters["initial_notional"],
                "amortization": parameters["initial_notional"] if i == ibor_leg.size() - 1 else 0.0,
            } for i in range(ibor_leg.size())])
            col11, col22 = st.columns([2, 7])
            with col11:
                df_amorts = st.data_editor(data, hide_index=True, height=500, use_container_width=True)
                custom_notional_amort = qcf.CustomNotionalAmort()
                custom_notional_amort.set_size(ibor_leg.size())
                for i, t in enumerate(df_amorts.itertuples()):
                    custom_notional_amort.set_notional_amort_at(i, t.notional, t.amortization)
                parameters2["notional_and_amort"] = custom_notional_amort
            ibor_leg_amort = qcf.LegFactory.build_custom_amort_ibor_leg(**parameters2)
            with col22:
                df_custom = aux.leg_as_dataframe(ibor_leg_amort)
                st.dataframe(
                    df_custom.style.format(aux.format_dict),
                    hide_index=True,
                    use_container_width=True,
                    height=500,
                )

except Exception as e:
    st.error(e)
