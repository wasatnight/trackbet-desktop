from calculos import calcular_ganancia_apuesta


def convertir_numero(valor, valor_defecto=0.0):
    """Convierte un valor a float de forma segura."""

    try:
        return float(valor)
    except (TypeError, ValueError):
        return valor_defecto


def obtener_resumen_apuesta(
    apuesta,
    ganancia,
):
    """Devuelve información resumida de una apuesta."""

    selecciones = apuesta.get(
        "selecciones",
        [],
    )

    primera_seleccion = {}

    if (
        isinstance(selecciones, list)
        and selecciones
        and isinstance(selecciones[0], dict)
    ):
        primera_seleccion = selecciones[0]

    return {
        "id": apuesta.get("id"),
        "evento": primera_seleccion.get(
            "evento",
            "No registrado",
        ),
        "mercado": primera_seleccion.get(
            "tipo_apuesta",
            "No registrado",
        ),
        "seleccion": primera_seleccion.get(
            "seleccion",
            "No registrada",
        ),
        "ganancia": ganancia,
    }


def calcular_estadisticas(
    apuestas,
    bankroll_inicial=0,
):
    """Calcula las estadísticas generales sin imprimirlas."""

    total_apostado = 0.0
    ganadas = 0
    perdidas = 0
    push = 0
    pendientes = 0
    stake_pendiente = 0.0
    ganancia_neta = 0.0

    rendimiento_deportes = {}
    rendimiento_casas = {}
    rendimiento_modalidades = {}
    rendimiento_mercados = {}
    rendimiento_ligas = {}
    rendimiento_momentos = {}

    mejor_apuesta = None
    peor_apuesta = None
    mejor_ganancia = None
    peor_ganancia = None

    for apuesta in apuestas:
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

        stake = convertir_numero(
            apuesta.get(
                "stake",
                0,
            )
        )

        if resultado == "pendiente":
            pendientes += 1
            stake_pendiente += stake
            continue

        total_apostado += stake

        ganancia_apuesta = convertir_numero(calcular_ganancia_apuesta(apuesta))

        ganancia_neta += ganancia_apuesta

        if resultado == "ganada":
            ganadas += 1
        elif resultado == "perdida":
            perdidas += 1
        elif resultado == "push":
            push += 1

        momento = (
            str(
                apuesta.get(
                    "momento_apuesta",
                    "no_registrado",
                )
            )
            .strip()
            .lower()
        )

        if momento not in rendimiento_momentos:
            rendimiento_momentos[momento] = {
                "apuestas": 0,
                "stake": 0.0,
                "ganadas": 0,
                "perdidas": 0,
                "push": 0,
                "ganancia": 0.0,
            }

        datos_momento = rendimiento_momentos[momento]

        datos_momento["apuestas"] += 1
        datos_momento["stake"] += stake
        datos_momento["ganancia"] += ganancia_apuesta

        if resultado == "ganada":
            datos_momento["ganadas"] += 1
        elif resultado == "perdida":
            datos_momento["perdidas"] += 1
        elif resultado == "push":
            datos_momento["push"] += 1

        deporte = str(
            apuesta.get(
                "deporte",
                "No registrado",
            )
        ).strip()

        casa = str(
            apuesta.get(
                "casa",
                "No registrada",
            )
        ).strip()

        modalidad = (
            str(
                apuesta.get(
                    "modalidad",
                    "straight",
                )
            )
            .strip()
            .lower()
        )

        liga = str(
            apuesta.get(
                "liga",
                "No registrada",
            )
        ).strip()

        if modalidad == "parlay":
            mercado = "Parlay"
        else:
            selecciones = apuesta.get(
                "selecciones",
                [],
            )

            if (
                isinstance(selecciones, list)
                and selecciones
                and isinstance(
                    selecciones[0],
                    dict,
                )
            ):
                mercado = selecciones[0].get(
                    "tipo_apuesta",
                    "No registrado",
                )
            else:
                mercado = "No registrado"

        rendimiento_deportes[deporte] = (
            rendimiento_deportes.get(
                deporte,
                0.0,
            )
            + ganancia_apuesta
        )

        rendimiento_casas[casa] = (
            rendimiento_casas.get(
                casa,
                0.0,
            )
            + ganancia_apuesta
        )

        rendimiento_modalidades[modalidad] = (
            rendimiento_modalidades.get(
                modalidad,
                0.0,
            )
            + ganancia_apuesta
        )

        rendimiento_mercados[mercado] = (
            rendimiento_mercados.get(
                mercado,
                0.0,
            )
            + ganancia_apuesta
        )

        rendimiento_ligas[liga] = (
            rendimiento_ligas.get(
                liga,
                0.0,
            )
            + ganancia_apuesta
        )

        if mejor_ganancia is None or ganancia_apuesta > mejor_ganancia:
            mejor_ganancia = ganancia_apuesta
            mejor_apuesta = obtener_resumen_apuesta(
                apuesta,
                ganancia_apuesta,
            )

        if peor_ganancia is None or ganancia_apuesta < peor_ganancia:
            peor_ganancia = ganancia_apuesta
            peor_apuesta = obtener_resumen_apuesta(
                apuesta,
                ganancia_apuesta,
            )

    apuestas_decididas = ganadas + perdidas

    if apuestas_decididas > 0:
        win_rate = (ganadas / apuestas_decididas) * 100
    else:
        win_rate = 0.0

    if total_apostado > 0:
        roi = (ganancia_neta / total_apostado) * 100
    else:
        roi = 0.0

    bankroll_inicial = convertir_numero(bankroll_inicial)

    bankroll_actual = bankroll_inicial + ganancia_neta

    stakes_recomendados = {
        "stake_1": bankroll_actual * 0.01,
        "stake_2": bankroll_actual * 0.02,
        "stake_3": bankroll_actual * 0.03,
    }

    if bankroll_inicial > 0:
        cambio_bankroll = (ganancia_neta / bankroll_inicial) * 100
    else:
        cambio_bankroll = 0.0

    for datos in rendimiento_momentos.values():
        decididas_momento = datos["ganadas"] + datos["perdidas"]

        if decididas_momento > 0:
            datos["win_rate"] = (datos["ganadas"] / decididas_momento) * 100
        else:
            datos["win_rate"] = 0.0

        if datos["stake"] > 0:
            datos["roi"] = (datos["ganancia"] / datos["stake"]) * 100
        else:
            datos["roi"] = 0.0

    resumen_inteligente = {
        "mejor_deporte": None,
        "peor_deporte": None,
        "mejor_mercado": None,
        "peor_mercado": None,
    }

    if rendimiento_deportes:
        mejor_deporte = max(
            rendimiento_deportes,
            key=rendimiento_deportes.get,
        )

        peor_deporte = min(
            rendimiento_deportes,
            key=rendimiento_deportes.get,
        )

        resumen_inteligente["mejor_deporte"] = {
            "nombre": mejor_deporte,
            "ganancia": rendimiento_deportes[mejor_deporte],
        }

        resumen_inteligente["peor_deporte"] = {
            "nombre": peor_deporte,
            "ganancia": rendimiento_deportes[peor_deporte],
        }

    if rendimiento_mercados:
        mejor_mercado = max(
            rendimiento_mercados,
            key=rendimiento_mercados.get,
        )

        peor_mercado = min(
            rendimiento_mercados,
            key=rendimiento_mercados.get,
        )

        resumen_inteligente["mejor_mercado"] = {
            "nombre": mejor_mercado,
            "ganancia": rendimiento_mercados[mejor_mercado],
        }

        resumen_inteligente["peor_mercado"] = {
            "nombre": peor_mercado,
            "ganancia": rendimiento_mercados[peor_mercado],
        }

    alertas = []

    if roi < 0:
        alertas.append("Tu ROI es negativo.")
    elif roi > 0:
        alertas.append("Tu ROI es positivo.")
    else:
        alertas.append("Tu ROI está en punto de equilibrio.")

    if ganancia_neta < 0:
        alertas.append("Actualmente tienes pérdida neta.")
    elif ganancia_neta > 0:
        alertas.append("Actualmente tienes ganancia neta positiva.")

    if bankroll_inicial > 0:
        if cambio_bankroll <= -10:
            alertas.append("Has perdido más del 10% de tu bankroll inicial.")
        elif cambio_bankroll >= 10:
            alertas.append("Has aumentado más del 10% tu bankroll inicial.")
        else:
            alertas.append("Tu bankroll se mantiene dentro de un rango controlado.")

    if (
        rendimiento_modalidades.get(
            "parlay",
            0,
        )
        < 0
    ):
        alertas.append("Tus parlays están generando pérdida.")

    if (
        rendimiento_modalidades.get(
            "straight",
            0,
        )
        > 0
    ):
        alertas.append("Tus straight bets están funcionando favorablemente.")

    if rendimiento_mercados:
        peor_mercado = min(
            rendimiento_mercados,
            key=rendimiento_mercados.get,
        )

        if rendimiento_mercados[peor_mercado] < 0:
            alertas.append("Tu mercado más débil actualmente " f"es {peor_mercado}.")

    return {
        "total_apostado": total_apostado,
        "ganadas": ganadas,
        "perdidas": perdidas,
        "push": push,
        "pendientes": pendientes,
        "stake_pendiente": stake_pendiente,
        "ganancia_neta": ganancia_neta,
        "apuestas_decididas": apuestas_decididas,
        "win_rate": win_rate,
        "roi": roi,
        "bankroll_inicial": bankroll_inicial,
        "bankroll_actual": bankroll_actual,
        "cambio_bankroll": cambio_bankroll,
        "stakes_recomendados": stakes_recomendados,
        "rendimiento_deportes": rendimiento_deportes,
        "rendimiento_casas": rendimiento_casas,
        "rendimiento_modalidades": (rendimiento_modalidades),
        "rendimiento_mercados": rendimiento_mercados,
        "rendimiento_ligas": rendimiento_ligas,
        "rendimiento_momentos": rendimiento_momentos,
        "mejor_apuesta": mejor_apuesta,
        "peor_apuesta": peor_apuesta,
        "resumen_inteligente": resumen_inteligente,
        "alertas": alertas,
    }
