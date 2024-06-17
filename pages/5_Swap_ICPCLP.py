import streamlit as st
from PIL import Image

import qcfinancial as qcf

from modules import aux_functions as aux

st.set_page_config(
    page_title="Swap ICPCLP",
    page_icon=Image.open('./assets/q.png'),
    layout="wide",
    initial_sidebar_state="auto",
    menu_items=None,
)

st.image(Image.open('./assets/logo_qcf_streamlit.png'), width=500)

st.markdown("# Swap ICPCLP")
st.markdown("""En este ejemplo se utilizan los objetos:
- `QCLeg`
- `QCInterestRate`
- `BusinessCalendar`
- `LegFactory`
- `FixedRateCashflow`
- `OvernightIndexCashflow`

Se construye una operación Swap de tasa fija vs ICPCLP con las convenciones usuales del mercado chileno.
""")
st.write("---")

trade_date = qcf.QCDate(14, 6, 2024)

both_default_values = {
    "bus_adj_rule": qcf.BusyAdjRules.MODFOLLOW,
    "settlement_calendar": qcf.BusinessCalendar(trade_date, 20),
    "settlement_lag": 1,
    "amort_is_cashflow": False,
    "notional_currency": qcf.QCCLP(),
    "sett_lag_behaviour": qcf.SettLagBehaviour.DONT_MOVE
}

icpclp_default_values = {
    "stub_period": qcf.StubPeriod.NO,
    "fix_adj_rule": qcf.BusyAdjRules.MODFOLLOW,
    "fixing_calendar": qcf.BusinessCalendar(trade_date, 20),
    "dates_for_eq_rate": qcf.DatesForEquivalentRate.ACCRUAL,
    "interest_rate": qcf.QCInterestRate(.0, qcf.QCAct360(), qcf.QCLinearWf()),
    "eq_rate_decimal_places": 4,
}

fixed_rate_default_values = {
    "settlement_stub_period": qcf.StubPeriod.NO,
    "is_bond":False,
}
tenors = ['1M', '2M', '3M', '6M', '9M', '1Y', '18M'] + [f"{n}Y" for n in range(2, 11)]
tenors += ['12Y', '15Y', '20Y', '25Y', '30Y']

st.markdown("## Parámetros de la Operación")
st.write(f"Trade Date: {trade_date} ")
start_date = qcf.build_qcdate_from_string(st.date_input("Start Date").isoformat())

str_maturity = st.selectbox("Maturity", options=tenors)
maturity = qcf.Tenor(str_maturity)
meses = maturity.get_months() + 12 * maturity.get_years()

end_date = start_date.add_months(meses)
st.write(f"End Date:\n {end_date}")

initial_notional = float(st.number_input("Notional", min_value=1_000_000, step=1_000_000))

fixed_rate_value = st.number_input("Fixed Rate Value (%)", step=.0001, format="%0.4f")

col1, col2 = st.columns(2)
with col1:
    fixed_rate_side = st.selectbox("Fixed Rate Side", options=["Receive", "Pay"])
with col2:
    icp_rate_side = st.selectbox("ICPCLP Rate Side", options=["Pay", "Receive"])

settlement_periodicity = qcf.Tenor('2Y') if str_maturity in ['1M', '2M', '3M', '6M', '9M', '12M', '1Y', '18M'] else qcf.Tenor('6M')
if fixed_rate_side == 'Receive':
    fixed_rec_pay = qcf.RecPay.RECEIVE
else:
    fixed_rec_pay = qcf.RecPay.PAY

if icp_rate_side == 'Receive':
    icp_rec_pay = qcf.RecPay.RECEIVE
else:
    icp_rec_pay = qcf.RecPay.PAY

fixed_rate_leg_other_values = {
    "settlement_periodicity": settlement_periodicity,
    "rec_pay": fixed_rec_pay,
    "initial_notional": initial_notional,
    "start_date": start_date,
    "end_date": end_date,
    "interest_rate": qcf.QCInterestRate(fixed_rate_value / 100.0, qcf.QCAct360(), qcf.QCLinearWf()),
}

icpclp_leg_other_values = {
    "rec_pay": icp_rec_pay,
    "initial_notional": initial_notional,
    "start_date": start_date,
    "end_date": end_date,
    "settlement_periodicity": settlement_periodicity,
    "interest_rate": qcf.QCInterestRate(0.0, qcf.QCAct360(), qcf.QCLinearWf()),
    "index_name": "ICPCLP",
    "spread": 0.0,
    "gearing": 1.0,
}

fixed_rate_leg = qcf.LegFactory.build_bullet_fixed_rate_leg(
    **(both_default_values | fixed_rate_default_values | fixed_rate_leg_other_values)
)

on_index_leg = qcf.LegFactory.build_bullet_overnight_index_leg(
    **(both_default_values | icpclp_default_values | icpclp_leg_other_values)
)

df_fixed_rate_leg = aux.leg_as_dataframe(fixed_rate_leg)
df_on_index_leg = aux.leg_as_dataframe(on_index_leg)

tab1, tab2 = st.tabs(["Fixed Rate Cashflows", "ICPCLP Cashflows"])
with tab1:
    st.dataframe(df_fixed_rate_leg.style.format(aux.format_dict), hide_index=True)
with tab2:
    st.dataframe(df_on_index_leg.style.format(aux.format_dict), hide_index=True)
