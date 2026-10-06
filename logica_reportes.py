from calculos import calcular_ganancia_apuesta


def calcular_resumen_financiero(apuestas, bankroll_inicial):
    """Calcula un resumen financiero general."""

    stake_total = 0
    stake_resuelto = 0
    stake_pendiente = 0
    ganancia_neta = 0
    apuestas_pendientes = 0
    apuestas_resueltas = 0

    for apuesta in apuestas:
        try:
            stake = float(
                apuesta.get(
                    "stake",
                    0,
                )
            )
        except (TypeError, ValueError):
            stake = 0

        resultado = (
            str(
                apuesta.get(
                    "resultado",
                    "pendiente",
                )
            )
            .strip()
            .lower()
        )

        stake_total += stake

        if resultado == "pendiente":
            apuestas_pendientes += 1
            stake_pendiente += stake
        else:
            apuestas_resueltas += 1
            stake_resuelto += stake
            ganancia_neta += calcular_ganancia_apuesta(apuesta)

    bankroll_actual = bankroll_inicial + ganancia_neta

    if stake_resuelto > 0:
        roi = (ganancia_neta / stake_resuelto) * 100
    else:
        roi = 0

    return {
        "bankroll_inicial": bankroll_inicial,
        "bankroll_actual": bankroll_actual,
        "stake_total": stake_total,
        "stake_resuelto": stake_resuelto,
        "stake_pendiente": stake_pendiente,
        "ganancia_neta": ganancia_neta,
        "roi": roi,
        "apuestas_totales": len(apuestas),
        "apuestas_resueltas": apuestas_resueltas,
        "apuestas_pendientes": apuestas_pendientes,
    }
