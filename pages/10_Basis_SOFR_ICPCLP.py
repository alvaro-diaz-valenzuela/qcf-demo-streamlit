import streamlit as st
from PIL import Image

import qcfinancial as qcf

from modules import aux_functions as aux

st.set_page_config(
    page_title="Basis SOFR ICPCLP",
    page_icon=Image.open('./assets/q.png'),
    layout="wide",
    initial_sidebar_state="auto",
    menu_items=None,
)

st.image(Image.open('./assets/logo_qcf_streamlit.png'), width=500)

st.markdown("# Basis USDCLP SOFR vs ICPCLP + Spread")
st.markdown("""En este ejemplo se utilizan los objetos:
- `QCLeg`
- `QCInterestRate`
- `BusinessCalendar`
- `LegFactory`
- `OvernightIndexCashflow`
- `CompoundedOvernightRateCashflow`

Se construye una operación de cross currency swap de SOFR flat vs ICPCLP + Spread con las convenciones usuales del mercado chileno.
""")
st.write("---")

trade_date = qcf.QCDate(14, 6, 2024)

calendario = qcf.BusinessCalendar(trade_date, 20)
calendarios = {
    'SANTIAGO': calendario,
    'NEW_YORK': calendario,
    'SIFMAUS': calendario,
    'SANTIAGO-NEW_YORK': calendario,
}

# FX Rate Index
usd = qcf.QCUSD()
clp = qcf.QCCLP()
usdclp = qcf.FXRate(usd, clp)
zero_d = qcf.Tenor('0D')
one_d = qcf.Tenor('1D')
usdobs = qcf.FXRateIndex(
    usdclp,
    'USDOBS',
    zero_d,
    one_d,
    calendarios['SANTIAGO'],
)

# Interest Rate Index
codigo = 'SOFR'
lin_act360 = qcf.QCInterestRate(.0, qcf.QCAct360(), qcf.QCLinearWf())
fixing_lag = qcf.Tenor('0d')
tenor = qcf.Tenor('1d')
fixing_calendar = calendario
settlement_calendar = calendario
usd = qcf.QCUSD()
sofr = qcf.InterestRateIndex(
    codigo,
    lin_act360,
    fixing_lag,
    tenor,
    calendarios['SIFMAUS'],
    calendarios['SIFMAUS'],
    usd
)

tenors = ['6M', '1Y', '18M'] + [f"{n}Y" for n in range(2, 11)]
tenors += ['12Y', '15Y', '20Y', '25Y', '30Y']

st.markdown("## Parámetros de la Operación")
st.write(f"Trade Date: {trade_date} ")
start_date = qcf.build_qcdate_from_string(st.date_input("Start Date").isoformat())

str_maturity = st.selectbox("Maturity", options=tenors)
maturity = qcf.Tenor(str_maturity)
meses = maturity.get_months() + 12 * maturity.get_years()

end_date = start_date.add_months(meses)
st.write(f"End Date:\n {end_date}")

initial_notional = float(st.number_input("Notional (USD)", min_value=1_000.00, step=1_000.00))
fx_rate = float(st.number_input("FX Rate (USDCLP)", min_value=500.00, step=1.00))
col1, col2, col3 = st.columns(3)
with col1:
    st.write(f"Notional in USD: {initial_notional:,.2f}")
with col2:
    st.write(f"FX Rate: {fx_rate:,.2f}")
with col3:
    st.write(f"Notional in CLP: {initial_notional * fx_rate:,.2f}")

spread = st.number_input("Spread on ICPCLP (%)", step=.0001, format="%0.4f")


def sofr_side_callback():
    st.session_state['icp_rate_side'] = 'Pay' if st.session_state['sofr_side'] == 'Receive' else 'Receive'


def icp_rate_side_callback():
    st.session_state['sofr_side'] = 'Pay' if st.session_state['icp_rate_side'] == 'Receive' else 'Receive'


col1, col2 = st.columns(2)
with col1:
    sofr_side = st.selectbox(
        "SOFR Side",
        options=["Receive", "Pay"],
        key='sofr_side',
        on_change=sofr_side_callback,
    )
with col2:
    icp_rate_side = st.selectbox(
        "ICPCLP Rate Side",
        options=["Pay", "Receive"],
        key='icp_rate_side',
        on_change=icp_rate_side_callback,
    )

settlement_periodicity = qcf.Tenor('2Y') if str_maturity in ['1M', '2M', '3M', '6M', '9M', '12M', '1Y', '18M'] else qcf.Tenor('6M')
if sofr_side == 'Receive':
    sofr_rec_pay = qcf.RecPay.RECEIVE
else:
    sofr_rec_pay = qcf.RecPay.PAY

if icp_rate_side == 'Receive':
    icp_rec_pay = qcf.RecPay.RECEIVE
else:
    icp_rec_pay = qcf.RecPay.PAY

# Both Default Values --------------------------------------------------------------------------------

amort_default_values = {
    "bus_adj_rule": qcf.BusyAdjRules.MODFOLLOW,
    "settlement_calendar": calendarios['SANTIAGO-NEW_YORK'],
    "settlement_lag": 0,
    "amort_is_cashflow": True,
    "settlement_periodicity": qcf.Tenor('40Y'),
    "settlement_stub_period": qcf.StubPeriod.NO,
    "is_bond": False,
    "sett_lag_behaviour": qcf.SettLagBehaviour.DONT_MOVE,
    "interest_rate": qcf.QCInterestRate(0.0, qcf.QCAct360(), qcf.QCLinearWf()),
}

interest_default_values = {
    "bus_adj_rule": qcf.BusyAdjRules.MODFOLLOW,
    "settlement_periodicity": qcf.Tenor('6M'),
    "settlement_calendar": calendarios['SANTIAGO-NEW_YORK'],
    "settlement_lag": 2,
    "sett_lag_behaviour": qcf.SettLagBehaviour.DONT_MOVE
}

# Lado SOFR

amort_sofr_other_values = {
    "rec_pay": sofr_rec_pay,
    "initial_notional": initial_notional,
    "start_date": start_date,
    "end_date": end_date,
    "notional_currency": usd,
    "settlement_currency": clp,
    "fx_rate_index": usdobs,
    "fx_rate_index_fixing_lag": 1,
}

amort_sofr_leg = qcf.LegFactory.build_bullet_fixed_rate_mccy_leg(
    **(amort_default_values | amort_sofr_other_values)
)

interest_sofr_default_values = {
    "notional_currency": qcf.QCUSD(),
    "settlement_currency": qcf.QCCLP(),
    "settlement_stub_period": qcf.StubPeriod.NO,
    "fx_rate_index": usdobs,
    "fx_rate_index_fixing_lag": 1,
    "eq_rate_decimal_places": 10,
    "fixing_calendar": calendarios['SIFMAUS'],
    "spread": 0.0,
    "gearing": 1.0,
    "lookback": 0,
    "lockout": 0,
    "interest_rate_index": sofr,
    "amort_is_cashflow": False,
    "interest_rate": qcf.QCInterestRate(0.0, qcf.QCAct360(), qcf.QCLinearWf()),
}

interest_sofr_other_values = {
    "rec_pay": sofr_rec_pay,
    "initial_notional": initial_notional,
    "start_date": start_date,
    "end_date": end_date,
}

interest_sofr_leg = qcf.LegFactory.build_bullet_compounded_overnight_rate_mccy_leg_2(
    **(interest_default_values | interest_sofr_default_values | interest_sofr_other_values)
)

# Lado ICPCLP

amort_icp_other_values = {
    "rec_pay": icp_rec_pay,
    "initial_notional": initial_notional * fx_rate,
    "start_date": start_date,
    "end_date": end_date,
    "notional_currency": clp,
}

amort_icp_leg = qcf.LegFactory.build_bullet_fixed_rate_leg(
    **(amort_default_values | amort_icp_other_values)
)

interest_icp_default_values = {
    "notional_currency": qcf.QCCLP(),
    "eq_rate_decimal_places": 6,
    "fixing_calendar": calendarios['SANTIAGO'],
    "gearing": 1.0,
    "interest_rate": qcf.QCInterestRate(0.0, qcf.QCAct360(), qcf.QCLinearWf()),
    "dates_for_eq_rate": qcf.DatesForEquivalentRate.ACCRUAL,
    "fix_adj_rule": qcf.BusyAdjRules.MODFOLLOW,
    "amort_is_cashflow": False,
    "settlement_stub_period": qcf.StubPeriod.NO,
    "index_name": "ICPCLP",
}

interest_icp_other_values = {
    "rec_pay": icp_rec_pay,
    "initial_notional": initial_notional * fx_rate,
    "start_date": start_date,
    "end_date": end_date,
    "spread": spread / 100,
}

interest_icp_leg = qcf.LegFactory.build_bullet_overnight_index_leg(
    **(interest_default_values | interest_icp_default_values | interest_icp_other_values)

)

df_amort_sofr_leg = aux.leg_as_dataframe(amort_sofr_leg)
df_interest_sofr_leg = aux.leg_as_dataframe(interest_sofr_leg)

df_amort_icp_leg = aux.leg_as_dataframe(amort_icp_leg)
df_interest_icp_leg = aux.leg_as_dataframe(interest_icp_leg)

tab1, tab2 = st.tabs(["SOFR Cashflows", "ICPCLP Cashflows"])
with tab1:
    st.markdown("Interest")
    st.dataframe(df_interest_sofr_leg.style.format(aux.format_dict), hide_index=True)
    st.markdown("Amortization")
    st.dataframe(df_amort_sofr_leg.style.format(aux.format_dict), hide_index=True)
with tab2:
    st.markdown("Interest")
    st.dataframe(df_interest_icp_leg.style.format(aux.format_dict), hide_index=True)
    st.markdown("Amortization")
    st.dataframe(df_amort_icp_leg.style.format(aux.format_dict), hide_index=True)
