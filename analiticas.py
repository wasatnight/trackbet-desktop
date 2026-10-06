from calculos import (
    formatear_cuota_dual,
    formato_dinero,
    formato_monto,
)
from servicios_analiticas import (
    obtener_analisis_cuotas,
    obtener_analisis_parlays,
)


def mostrar_analisis_cuotas():
    """Muestra el rendimiento histórico por rangos de cuotas."""

    analisis = obtener_analisis_cuotas()

    if analisis["total_apuestas"] == 0:
        print("\nNo hay apuestas registradas.")
        return

    if analisis["apuestas_validas"] == 0:
        print("\nNo existen apuestas resueltas con cuotas válidas para analizar.")
        return

    print("\n===== ANÁLISIS POR RANGOS DE CUOTAS =====")

    for datos in analisis["rangos"]:
        diferencia = datos["diferencia_equilibrio"]

        print("\n" + "=" * 45)
        print("RANGO:", datos["rango"])
        print("-" * 45)
        print(
            "Apuestas resueltas:",
            datos["resueltas"],
        )
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
            "Cuota promedio:",
            formatear_cuota_dual(datos["cuota_promedio"]),
        )

        print(
            "Win Rate:",
            f'{datos["win_rate"]:.2f}%',
        )

        print(
            "Probabilidad implícita promedio:",
            f'{datos["probabilidad_implicita"]:.2f}%',
        )

        print(
            "Ventaja histórica sobre el equilibrio:",
            f"{diferencia:+.2f} " "puntos porcentuales",
        )

        if diferencia > 0:
            print(
                "Interpretación:",
                "tu porcentaje de aciertos estuvo "
                f"{diferencia:.2f} puntos porcentuales "
                "por encima del mínimo necesario.",
            )

        elif diferencia < 0:
            print(
                "Interpretación:",
                "tu porcentaje de aciertos estuvo "
                f"{abs(diferencia):.2f} puntos porcentuales "
                "por debajo del mínimo necesario.",
            )

        else:
            print(
                "Interpretación: tu porcentaje de "
                "aciertos coincidió con el punto "
                "de equilibrio."
            )

        print(
            "ROI:",
            f'{datos["roi"]:.2f}%',
        )
        print(
            "Tamaño de muestra:",
            datos["muestra"],
        )

        for alerta in datos["alertas"]:
            print("Aviso:", alerta)

    print("\n" + "=" * 45)
    print("Nota:", analisis["nota"])

    print("\n===== ¿QUÉ SIGNIFICAN ESTOS DATOS? =====")

    print(
        "\nWin Rate:"
        "\nPorcentaje de apuestas ganadas entre "
        "las apuestas ganadas y perdidas. "
        "Los push no se incluyen."
    )

    print(
        "\nProbabilidad implícita promedio:"
        "\nPorcentaje de aciertos que aproximadamente "
        "exigen las cuotas analizadas para llegar "
        "al punto de equilibrio."
    )

    print(
        "\nVentaja histórica sobre el equilibrio:"
        "\nDiferencia entre tu Win Rate y la "
        "probabilidad implícita promedio."
    )

    print(
        "\nROI:"
        "\nPorcentaje de dinero ganado o perdido "
        "respecto al total apostado."
    )

    print(
        "\nImportante:"
        "\nUna ventaja histórica positiva no garantiza "
        "que las siguientes apuestas sean ganadoras."
    )


def imprimir_resumen_parlays(
    titulo,
    resumen,
):
    """Muestra el rendimiento de categorías de parlays."""

    print(f"\n===== {titulo} =====")

    for categoria, datos in resumen.items():
        print(f"\n{categoria}")
        print("-" * 45)

        print(
            "Parlays registrados:",
            datos["registrados"],
        )
        print(
            "Parlays resueltos:",
            datos["resueltos"],
        )
        print(
            "Parlays pendientes:",
            datos["pendientes"],
        )
        print("Ganados:", datos["ganadas"])
        print("Perdidos:", datos["perdidas"])
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
            f'{datos["win_rate"]:.2f}%',
        )
        print(
            "ROI:",
            f'{datos["roi"]:.2f}%',
        )
        print(
            "Tamaño de muestra:",
            datos["muestra"],
        )

        if datos["decididas"] < 10:
            print(
                "Aviso: todavía hay muy pocos "
                "parlays para interpretar "
                "esta categoría."
            )


def mostrar_analisis_parlays():
    """Muestra las estadísticas específicas de parlays."""

    analisis = obtener_analisis_parlays()

    if analisis["total_apuestas"] == 0:
        print("\nNo hay apuestas registradas.")
        return

    if analisis["parlays_registrados"] == 0:
        print("\nNo hay parlays registrados.")
        return

    print("\n===== ANÁLISIS DE PARLAYS =====")
    print(
        "Parlays registrados:",
        analisis["parlays_registrados"],
    )
    print(
        "Parlays resueltos:",
        analisis["parlays_resueltos"],
    )
    print(
        "Parlays pendientes:",
        analisis["parlays_pendientes"],
    )

    imprimir_resumen_parlays(
        "RENDIMIENTO POR NÚMERO DE SELECCIONES",
        analisis["rendimiento_piernas"],
    )

    imprimir_resumen_parlays(
        "UN SOLO DEPORTE VS MULTIDEPORTE",
        analisis["rendimiento_deportes"],
    )

    imprimir_resumen_parlays(
        "MISMO EVENTO VS EVENTOS DIFERENTES",
        analisis["rendimiento_eventos"],
    )

    resultados = analisis["resultados_selecciones"]

    print("\n===== RESULTADOS DE LAS SELECCIONES =====")
    print(
        "Selecciones ganadas:",
        resultados["ganadas"],
    )
    print(
        "Selecciones perdidas:",
        resultados["perdidas"],
    )
    print(
        "Selecciones push:",
        resultados["push"],
    )
    print(
        "Selecciones pendientes:",
        resultados["pendientes"],
    )
    print(
        "Selecciones antiguas sin resultado:",
        resultados["sin_resultado"],
    )

    mercados_perdidos = analisis["mercados_perdidos"]

    if mercados_perdidos:
        print("\n===== MERCADOS CON MÁS SELECCIONES PERDIDAS =====")

        for mercado, cantidad in sorted(
            mercados_perdidos.items(),
            key=lambda elemento: elemento[1],
            reverse=True,
        ):
            print(f"{mercado}: " f"{cantidad} selección(es) perdida(s)")

    deportes_perdidos = analisis["deportes_perdidos"]

    if deportes_perdidos:
        print("\n===== DEPORTES CON MÁS SELECCIONES PERDIDAS =====")

        for deporte, cantidad in sorted(
            deportes_perdidos.items(),
            key=lambda elemento: elemento[1],
            reverse=True,
        ):
            print(f"{deporte}: " f"{cantidad} selección(es) perdida(s)")

    print("\n===== PRODUCTO DE CUOTAS VS CUOTA OFRECIDA =====")

    comparaciones = analisis["comparaciones_cuotas"]

    if not comparaciones:
        print("Todavía no hay parlays con todas sus cuotas individuales registradas.")

    else:
        for comparacion in comparaciones:
            print("\n" + "-" * 45)
            print(
                "ID del parlay:",
                comparacion["id"],
            )
            print(
                "Número de selecciones:",
                comparacion["selecciones"],
            )
            print(
                "Tipo de parlay:",
                comparacion["tipo_eventos"],
            )
            print(
                "Producto de cuotas individuales:",
                formatear_cuota_dual(
                    comparacion["cuota_producto"],
                    decimales=2,
                ),
            )
            print(
                "Cuota ofrecida por la casa:",
                formatear_cuota_dual(
                    comparacion["cuota_ofrecida"],
                    decimales=2,
                ),
            )
            print(
                "Diferencia:",
                f'{comparacion["diferencia"]:+.2f}%',
            )

            if comparacion["diferencia"] > 0:
                print(
                    "Interpretación: la cuota ofrecida "
                    "fue mayor que el producto de las "
                    "cuotas individuales."
                )

            elif comparacion["diferencia"] < 0:
                print(
                    "Interpretación: la cuota ofrecida "
                    "fue menor que el producto de las "
                    "cuotas individuales."
                )

            else:
                print(
                    "Interpretación: la cuota ofrecida "
                    "coincidió con el producto calculado."
                )

            if comparacion["tipo_eventos"] == "Mismo evento":
                print(
                    "Aviso: las selecciones del mismo "
                    "evento pueden estar correlacionadas."
                )

    print("\n" + "=" * 45)
    print("Nota:", analisis["nota"])


def mostrar_menu_analiticas():
    """Muestra el menú de herramientas analíticas."""

    while True:
        print("\n===== ANALÍTICAS AVANZADAS =====")
        print("1. Análisis por rangos de cuotas")
        print("2. Análisis de parlays")
        print("3. Volver al menú principal")

        opcion = input("Elige una opción: ").strip()

        if opcion == "1":
            mostrar_analisis_cuotas()

        elif opcion == "2":
            mostrar_analisis_parlays()

        elif opcion == "3":
            return

        else:
            print("Opción no válida.")
