from calculos import (
    formato_dinero,
    formato_monto,
)
from servicios_estadisticas import obtener_estadisticas


def mostrar_estadisticas():
    """Calcula y muestra las estadísticas de las apuestas."""

    estadisticas = obtener_estadisticas()

    total_apostado = estadisticas["total_apostado"]
    ganadas = estadisticas["ganadas"]
    perdidas = estadisticas["perdidas"]
    push = estadisticas["push"]
    pendientes = estadisticas["pendientes"]

    stake_pendiente = estadisticas["stake_pendiente"]
    ganancia_neta = estadisticas["ganancia_neta"]
    win_rate = estadisticas["win_rate"]
    roi = estadisticas["roi"]

    bankroll_inicial = estadisticas["bankroll_inicial"]
    bankroll_actual = estadisticas["bankroll_actual"]
    cambio_bankroll = estadisticas["cambio_bankroll"]

    stakes_recomendados = estadisticas["stakes_recomendados"]

    stake_1 = stakes_recomendados["stake_1"]
    stake_2 = stakes_recomendados["stake_2"]
    stake_3 = stakes_recomendados["stake_3"]

    rendimiento_deportes = estadisticas["rendimiento_deportes"]
    rendimiento_casas = estadisticas["rendimiento_casas"]
    rendimiento_modalidad = estadisticas["rendimiento_modalidades"]
    rendimiento_mercados = estadisticas["rendimiento_mercados"]
    rendimiento_ligas = estadisticas["rendimiento_ligas"]
    rendimiento_momentos = estadisticas["rendimiento_momentos"]

    mejor_apuesta = estadisticas["mejor_apuesta"]
    peor_apuesta = estadisticas["peor_apuesta"]

    mejor_ganancia = mejor_apuesta["ganancia"] if mejor_apuesta is not None else None

    peor_ganancia = peor_apuesta["ganancia"] if peor_apuesta is not None else None

    print("\n===== ESTADÍSTICAS =====")
    print("\n------------------------")
    print(
        "Total apostado en apuestas resueltas:",
        formato_monto(total_apostado),
    )
    print("Ganadas:", ganadas)
    print("Perdidas:", perdidas)
    print("Push:", push)
    print("Pendientes:", pendientes)
    print(
        "Stake actualmente en juego:",
        formato_monto(stake_pendiente),
    )
    print("Win Rate: ", round(win_rate, 2), "%")
    print("Ganancia Neta Total:", formato_dinero(ganancia_neta))
    print("ROI (Retorno de Inversión):", round(roi, 2), "%")
    if bankroll_inicial > 0:
        print("\n===== BANKROLL =====")
        print("Bankroll inicial:", formato_monto(bankroll_inicial))
        print("Bankroll actual:", formato_monto(bankroll_actual))
        print("Stake recomendado 1%:", formato_monto(stake_1))
        print("Stake recomendado 2%:", formato_monto(stake_2))
        print("Stake recomendado 3%:", formato_monto(stake_3))
    else:
        print(
            "\nConfigura tu bankroll en la opción 4 para ver recomendaciones de stake."
        )

    print("\n===== RENDIMIENTO POR DEPORTE =====")
    for deporte, ganancia in sorted(
        rendimiento_deportes.items(), key=lambda item: item[1], reverse=True
    ):
        print(deporte, ":", formato_dinero(ganancia))
    if len(rendimiento_casas) > 1:
        print("\n===== RENDIMIENTO POR CASA DE APUESTAS =====")
        for casa, ganancia in sorted(
            rendimiento_casas.items(), key=lambda item: item[1], reverse=True
        ):
            print(casa, ":", formato_dinero(ganancia))
    if len(rendimiento_modalidad) > 1:
        print("\n===== RENDIMIENTO POR MODALIDAD =====")
        for modalidad, ganancia in sorted(
            rendimiento_modalidad.items(),
            key=lambda item: item[1],
            reverse=True,
        ):
            print(modalidad.capitalize(), ":", formato_dinero(ganancia))
    print("\n===== RENDIMIENTO POR MERCADO =====")
    for mercado, ganancia in sorted(
        rendimiento_mercados.items(), key=lambda item: item[1], reverse=True
    ):
        print(mercado, ":", formato_dinero(ganancia))

    if len(rendimiento_ligas) > 1:
        print("\n===== RENDIMIENTO POR LIGA =====")

        for liga, ganancia in sorted(
            rendimiento_ligas.items(), key=lambda item: item[1], reverse=True
        ):
            print(liga, ":", formato_dinero(ganancia))

    print("\n===== PREPARTIDO VS EN VIVO =====")

    orden_momentos = [
        "prepartido",
        "en_vivo",
        "no_registrado",
    ]

    for momento in orden_momentos:
        if momento not in rendimiento_momentos:
            continue

        datos = rendimiento_momentos[momento]

        apuestas_decididas_momento = datos["ganadas"] + datos["perdidas"]

        if apuestas_decididas_momento > 0:
            win_rate_momento = (datos["ganadas"] / apuestas_decididas_momento) * 100
        else:
            win_rate_momento = 0

        if datos["stake"] > 0:
            roi_momento = (datos["ganancia"] / datos["stake"]) * 100
        else:
            roi_momento = 0

        nombre_momento = momento.replace(
            "_",
            " ",
        ).capitalize()

        print(f"\n{nombre_momento}")
        print("-" * 35)
        print("Apuestas resueltas:", datos["apuestas"])
        print("Ganadas:", datos["ganadas"])
        print("Perdidas:", datos["perdidas"])
        print("Push:", datos["push"])
        print(
            "Total apostado:",
            formato_monto(datos["stake"]),
        )

        print(
            "Ganancia neta:",
            formato_dinero(datos["ganancia"]),
        )
        print(
            "Win Rate:",
            f"{win_rate_momento:.2f}%",
        )
        print(
            "ROI:",
            f"{roi_momento:.2f}%",
        )

    print("\n===== RESUMEN INTELIGENTE =====")
    if len(rendimiento_deportes) > 0:
        mejor_deporte = max(rendimiento_deportes, key=rendimiento_deportes.get)
        peor_deporte = min(rendimiento_deportes, key=rendimiento_deportes.get)
        print(
            f"Mejor deporte: {mejor_deporte} {formato_dinero(rendimiento_deportes[mejor_deporte])}"
        )
        print(
            f"Peor deporte: {peor_deporte} {formato_dinero(rendimiento_deportes[peor_deporte])}"
        )
    if len(rendimiento_mercados) > 0:
        mejor_mercado = max(rendimiento_mercados, key=rendimiento_mercados.get)
        peor_mercado = min(rendimiento_mercados, key=rendimiento_mercados.get)
        print(
            f"Mejor mercado: {mejor_mercado} {formato_dinero(rendimiento_mercados[mejor_mercado])}"
        )
        print(
            f"Peor mercado: {peor_mercado} {formato_dinero(rendimiento_mercados[peor_mercado])}"
        )

    if mejor_apuesta is not None:
        print("\nMejor apuesta:")
        print(
            "Evento:",
            mejor_apuesta["evento"],
        )
        print(
            "Mercado:",
            mejor_apuesta["mercado"],
        )
        print(
            "Ganancia:",
            formato_dinero(mejor_ganancia),
        )

    if peor_apuesta is not None:
        print("\nPeor apuesta:")
        print(
            "Evento:",
            peor_apuesta["evento"],
        )
        print(
            "Mercado:",
            peor_apuesta["mercado"],
        )
        print(
            "Ganancia:",
            formato_dinero(peor_ganancia),
        )

    print("\n===== ALERTAS INTELIGENTES =====")

    if roi < 0:
        print(
            "Atención: tu ROI es negativo, estás perdiendo dinero respecto a la cantidad de dinero apostado."
        )
    elif roi > 0:
        print("Buen rendimiento: tu ROI es positivo.")
    else:
        print("Tu ROI está en punto de equilibrio.")

    if ganancia_neta < 0:
        print("Actualmente tienes pérdida neta.")
    elif ganancia_neta > 0:
        print("Actualmente tienes ganancia neta positiva.")

    if bankroll_inicial > 0:
        if cambio_bankroll <= -10:
            print("Alerta: has perdido más del 10% de tu bankroll inicial.")
        elif cambio_bankroll >= 10:
            print("Buen avance: has aumentado más del 10% tu bankroll inicial.")
        else:
            print("Tu bankroll se mantiene dentro de un rango controlado.")

    if "parlay" in rendimiento_modalidad and rendimiento_modalidad["parlay"] < 0:
        print(
            "Tus parlays están generando pérdida, podrias considerar reducirlos o analizarlos mejor."
        )

    if "straight" in rendimiento_modalidad and rendimiento_modalidad["straight"] > 0:
        print("Tus straight bets están funcionando mejor que otras modalidades.")

    if rendimiento_mercados:
        peor_mercado = min(rendimiento_mercados, key=rendimiento_mercados.get)

        if rendimiento_mercados[peor_mercado] < 0:
            print(f"Tu mercado más débil actualmente es {peor_mercado}.")
