import qcfinancial as qcf

# Dict con las características de los bonos
nemotecnicos = {
    "BTU0150326": {
        "fecha_inicial": qcf.QCDate(1, 3, 2015),
        "fecha_final": qcf.QCDate(1, 3, 2026),
        "bus_adj_rule": qcf.BusyAdjRules.NO,
        "periodicidad": qcf.Tenor('6M'),
        "periodo_irregular": qcf.StubPeriod.NO,
        "calendario": qcf.BusinessCalendar(qcf.QCDate(1, 3, 2015), 20),
        "lag_pago" : 0,
        "nominal": 100.0,
        "amort_es_flujo": True,
        "tasa_cupon": qcf.QCInterestRate(
            .015,
            qcf.QC30360(),
            qcf.QCLinearWf(),
        ),
        "moneda": qcf.QCCLF(),
        "tera": qcf.QCInterestRate(.015044, qcf.QCAct365(), qcf.QCCompoundWf()),
    }
}


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
