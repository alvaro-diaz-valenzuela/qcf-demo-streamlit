import qcfinancial as qcf
from datetime import date

tasa = .01


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
    }
