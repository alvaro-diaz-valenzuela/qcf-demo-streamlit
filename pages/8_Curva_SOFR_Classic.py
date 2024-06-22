import streamlit as st
from PIL import Image
import pandas as pd

import qcfinancial as qcf

from modules import aux_functions as aux

st.set_page_config(
    page_title="Curva SOFR",
    page_icon=Image.open('./assets/q.png'),
    layout="wide",
    initial_sidebar_state="auto",
    menu_items=None,
)

st.image(Image.open('./assets/logo_qcf_streamlit.png'), width=500)

st.markdown("# Bootstrapping Curva SOFR - Versión Classic")
st.markdown("""En este ejemplo se utilizan los objetos:
- `QCLeg`
- `QCInterestRate`
- `BusinessCalendar`
- `LegFactory`
- `FixedRateCashflow`

Se construye la curva cupón cero asociada a los swaps de SOFR vs tasa fija:

- Se utiliza el procedimiento *clásico* que consiste en:
  - Resolver el sistema de ecuaciones que iguala el valor presente de las patas fijas (en `start_date`) con el valor 
  del nocional.
  - Se considera como flujo el nocional al vencimiento.
  - Es importante notar que para que estas ecuaciones sean válidas se debe suponer que el settlement lag es siempre igual a 0.
""")
st.write("---")

st.markdown("## Data")
st.write("Son datos de swaps SOFR  vs Fija al 2024-06-21")
expander_0 = st.expander("Lectura de Datos", expanded=False)
expander_0.code("""
data = pd.read_excel("input/20240621_sofr_data.xlsx")
""")
data = pd.read_excel("input/20240621_sofr_data.xlsx")
st.dataframe(data.style.format({'rate': '{:.4%}'}))

st.markdown("## Input")
st.write("Al seleccionar un tenor se despliega la estructura de la pata fija del swap correspondiente. Por "
         "simplicidad se está utilizando un calendario que sólo considera los días sábado y domingo como feriados.")

trade_date = qcf.QCDate(21, 6, 2024)
yf = qcf.QCAct360()
wf = qcf.QCLinearWf()
common_params = {
    "rec_pay": qcf.RecPay.RECEIVE,
    "start_date": qcf.QCDate(25, 6, 2024),
    "bus_adj_rule": qcf.BusyAdjRules.MODFOLLOW,
    "settlement_stub_period": qcf.StubPeriod.SHORTFRONT,
    "settlement_calendar": qcf.BusinessCalendar(trade_date, 50),
    "settlement_lag": 0,
    "initial_notional": 1_000_000,
    "amort_is_cashflow": True,
    "notional_currency": qcf.QCUSD(),
    "is_bond": False,
    "sett_lag_behaviour": qcf.SettLagBehaviour.DONT_MOVE,
}

expander_1 = st.expander("Construcción FixedRateLegs", expanded=False)
expander_1.code("""
fixed_rate_legs = []
for t in data.itertuples():
    tenor = qcf.Tenor(t.tenor)
    months = tenor.get_months() + 12 * tenor.get_years()
    if (days:=tenor.get_days()) > 0:
        end_date = common_params["start_date"].add_days(days)
    else:
        end_date = common_params["start_date"].add_months(months)
    other_params = {
        "end_date": end_date,
        "settlement_periodicity": qcf.Tenor(t.pay_freq),
        "interest_rate": qcf.QCInterestRate(t.rate, yf, wf),
    }
    fixed_rate_legs.append(
        qcf.LegFactory.build_bullet_fixed_rate_leg(
            **(common_params | other_params),
        )
    )
""")

fixed_rate_legs = []
for t in data.itertuples():
    tenor = qcf.Tenor(t.tenor)
    months = tenor.get_months() + 12 * tenor.get_years()
    if (days := tenor.get_days()) > 0:
        end_date = common_params["start_date"].add_days(days)
    else:
        end_date = common_params["start_date"].add_months(months)
    other_params = {
        "end_date": end_date,
        "settlement_periodicity": qcf.Tenor(t.pay_freq),
        "interest_rate": qcf.QCInterestRate(t.rate, yf, wf),
    }
    fixed_rate_legs.append(
        qcf.LegFactory.build_bullet_fixed_rate_leg(
            **(common_params | other_params),
        )
    )

tenors = list(data['tenor'])
tenor = st.selectbox("Tenor", options=tenors)

leg_df = aux.leg_as_dataframe(fixed_rate_legs[tenors.index(tenor)])
FLOAT_FORMAT = '{:,.2f}'
st.dataframe(leg_df.style.format({
    'nominal': FLOAT_FORMAT,
    'amortizacion': FLOAT_FORMAT,
    'interes': FLOAT_FORMAT,
    'valor_tasa': '{:.4%}'})
)

st.markdown("## Bootstrapping")
st.write("Se construye una curva cero cupón inicial que servirá como punto de entrada de todos los pasos del "
         "Bootstrapping. Las tasas de dichas coinciden con las cotizaciones de swap.")

expander_2 = st.expander("Construcción Curva Inicial", expanded=False)
expander_2.code("""
plazos = qcf.long_vec()
tasas = qcf.double_vec()
for leg in fixed_rate_legs:
    num_cup = leg.size()
    cashflow = leg.get_cashflow_at(num_cup - 1)
    plazo = common_params["start_date"].day_diff(cashflow.get_settlement_date())
    plazos.append(plazo)
    tasa = cashflow.get_rate().get_value()
    tasas.append(tasa)
curva = qcf.QCCurve(plazos, tasas)
interpolator = qcf.QCLinearInterpolator(curva)
initial_zcc = qcf.ZeroCouponCurve(
    interpolator,
    rate := (qcf.QCInterestRate(
        0.0,
        qcf.QCAct365(),
        qcf.QCContinousWf()
    ))
)
""")

plazos = qcf.long_vec()
tasas = qcf.double_vec()
for leg in fixed_rate_legs:
    num_cup = leg.size()
    cashflow = leg.get_cashflow_at(num_cup - 1)
    plazo = common_params["start_date"].day_diff(cashflow.get_settlement_date())
    plazos.append(plazo)
    tasa = cashflow.get_rate().get_value()
    tasas.append(tasa)
curva = qcf.QCCurve(plazos, tasas)
interpolator = qcf.QCLinearInterpolator(curva)
initial_zcc = qcf.ZeroCouponCurve(
    interpolator,
    rate:=(qcf.QCInterestRate(
        0.0,
        qcf.QCAct365(),
        qcf.QCContinousWf()
    ))
)

df_curva_inicial = pd.concat([pd.DataFrame(plazos), pd.DataFrame(tasas)], axis=1)
df_curva_inicial.columns = ['plazo', 'tasa']

col1, col2 = st.columns([1, 3])
with col1:
    st.dataframe(df_curva_inicial.style.format({'tasa': '{:.4%}'}))
with col2:
    st.markdown("### Curva Inicial")
    st.line_chart(
        df_curva_inicial.style.format({'tasa': '{:.4%}'}),
        x='plazo',
        y='tasa'
    )

st.markdown("Se procede al cálculo. Es importante notar que las tasas y plazos se construyen a partir de "
            "**start_date**. La convención utilizada para las tasas cero es Exp Act/365.")

expander_3 = st.expander("Procedimiento del Bootstrapping", expanded=False)
expander_3.code("""
pv = qcf.PresentValue()
for i, leg in enumerate(fixed_rate_legs):
    def obj(zcc):
        return pv.pv(common_params["start_date"], leg, zcc) - common_params["initial_notional"]
    error = 1_000
    epsilon = .00001
    x = initial_zcc.get_rate_at(i)
    new_zcc = initial_zcc
    while error > epsilon:
        x = x - obj(new_zcc) / pv.get_derivatives()[i]
        tasas[i] = x
        curva = qcf.QCCurve(plazos, tasas)
        interpolator = qcf.QCLinearInterpolator(curva)
        new_zcc = qcf.ZeroCouponCurve(
            interpolator,
            rate,
        )
        error = abs(obj(new_zcc))
""")


pv = qcf.PresentValue()
for i, leg in enumerate(fixed_rate_legs):
    def obj(zcc):
        return pv.pv(common_params["start_date"], leg, zcc) - common_params["initial_notional"]
    error = 1_000
    epsilon = .00001
    x = initial_zcc.get_rate_at(i)
    new_zcc = initial_zcc
    while error > epsilon:
        x = x - obj(new_zcc) / pv.get_derivatives()[i]
        tasas[i] = x
        curva = qcf.QCCurve(plazos, tasas)
        interpolator = qcf.QCLinearInterpolator(curva)
        new_zcc = qcf.ZeroCouponCurve(
            interpolator,
            rate,
        )
        error = abs(obj(new_zcc))

df_curva = pd.concat([pd.DataFrame(tenors), pd.DataFrame(plazos), pd.DataFrame(tasas)], axis=1)
df_curva.columns = ['tenor', 'plazo', 'tasa']

col3, col4 = st.columns([1, 3])
with col3:
    st.dataframe(df_curva.style.format({'tasa': '{:.4%}'}))
with col4:
    st.markdown("### Curva Final (Output del Bootstrapping)")
    st.line_chart(
        df_curva.style.format({'tasa': '{:.4%}'}),
        x='plazo',
        y='tasa'
    )

st.markdown("Eligiendo el tenor se puede comprobar que el valor presente de todas las patas fijas coincide con el "
            "nominal.")

tenor = st.selectbox(" Tenor", options=tenors)
leg = fixed_rate_legs[tenors.index(tenor)]
st.markdown(f"El valor presente de la pata a {tenor} es: {pv.pv(common_params['start_date'], leg, new_zcc):,.4f}")
