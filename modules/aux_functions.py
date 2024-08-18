import qcfinancial as qcf
import holidays as hol
import pandas as pd

format_dict = {
    'nominal': '{0:,.2f}',
    'nocional': '{0:,.2f}',
    'amort': '{0:,.2f}',
    'amortizacion': '{0:,.2f}',
    'interes': '{0:,.2f}',
    'monto': '{0:,.2f}',
    'flujo': '{0:,.2f}',
    'flujo_moneda_pago': '{0:,.2f}',
    'flujo_en_clp': '{0:,.2f}',
    'icp_inicial': '{0:,.2f}',
    'icp_final': '{0:,.2f}',
    'uf_inicial': '{0:,.2f}',
    'uf_final': '{0:,.2f}',
    'valor_tasa': '{0:,.4%}',
    'valor_tasa_equivalente': '{0:,.4%}',
    'spread': '{0:,.4%}',
    'gearing': '{0:,.2f}',
    'amortizacion_moneda_pago': '{0:,.2f}',
    'interes_moneda_pago': '{0:,.2f}',
    'valor_indice_fx': '{0:,.2f}'
}


def leg_as_dataframe(leg: qcf.Leg):
    """
    Envuelve un objeto qcf.Leg en un pd.DataFrame
    """
    if leg.size() == 0:
        raise ValueError("No cashflows")
    type_cashflows = leg.get_cashflow_at(0).get_type()
    tabla = [qcf.show(leg.get_cashflow_at(i)) for i in range(0, leg.size())]
    df = pd.DataFrame(tabla, columns=qcf.get_column_names(type_cashflows, ''))
    return df


def get_business_calendar(which_holidays: str, years: range) -> qcf.BusinessCalendar:
    """
    Retorna un calendario en formato qcfinancial.
    """
    py_cal = hol.country_holidays(which_holidays, years=years)
    yrs = [y for y in years]
    qcf_cal = qcf.BusinessCalendar(qcf.QCDate(1, 1, yrs[0]), yrs[-1] - yrs[0])
    for d in py_cal.keys():
        qcf_cal.add_holiday(qcf.QCDate(d.isoformat()))
    if which_holidays == 'CL':
        for year in years:
            d = qcf.QCDate(31, 12, year)
            if d.week_day() == qcf.WeekDay.SAT:
                d = d.add_days(-1)
            if d.week_day() == qcf.WeekDay.SUN:
                d = d.add_days(-2)
            qcf_cal.add_holiday(d)
    return qcf_cal


def date_plus_tenor(fecha: qcf.QCDate, tenor: qcf.Tenor) -> qcf.QCDate:
    return fecha.add_months(tenor.get_years() * 12 + tenor.get_months()).add_days(tenor.get_days())


def get_fx_rate_index(fx_rate_index_name: str) -> qcf.FXRateIndex:
    match fx_rate_index_name:
        case "USDOBS":
            usd = qcf.QCUSD()
            clp = qcf.QCCLP()
            usdclp = qcf.FXRate(usd, clp)
            one_d = qcf.Tenor('1D')
            indice = qcf.FXRateIndex(
                usdclp,
                'USDOBS',
                one_d,
                one_d,
                get_business_calendar('CL', range(2024, 2035))
            )
        case "UF":
            clf = qcf.QCCLF()
            clp = qcf.QCCLP()
            clfclp = qcf.FXRate(clf, clp)
            zero_d = qcf.Tenor('0D')
            indice = qcf.FXRateIndex(
                clfclp,
                'UF',
                zero_d,
                zero_d,
                get_business_calendar('CL', range(2024, 2035))
            )
        case _:
            usd = qcf.QCUSD()
            clp = qcf.QCCLP()
            usdclp = qcf.FXRate(usd, clp)
            one_d = qcf.Tenor('1D')
            indice = qcf.FXRateIndex(
                usdclp,
                'USDOBS',
                one_d,
                one_d,
                get_business_calendar('CL', range(2024, 2035))
            )
    return indice
