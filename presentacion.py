from calculos import (
    calcular_cuota_liquidada_parlay,
    calcular_ganancia_apuesta,
    formatear_cuota_dual,
    formato_dinero,
    formato_monto,
    obtener_cuota_decimal,
)


def obtener_retorno_total_real(apuesta):
    """Obtiene el retorno oficial como número válido."""

    retorno_total_real = apuesta.get("retorno_total_real")

    if retorno_total_real is None:
        return None

    try:
        return float(retorno_total_real)
    except (TypeError, ValueError):
        return None


def mostrar_detalle_apuesta(apuesta):
    """Muestra todos los datos y la liquidación de una apuesta."""

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

    momento = str(
        apuesta.get(
            "momento_apuesta",
            "no_registrado",
        )
    )

    ganancia = calcular_ganancia_apuesta(apuesta)

    retorno_total_real = obtener_retorno_total_real(apuesta)

    print("\n" + "=" * 50)
    print(
        "ID:",
        apuesta.get(
            "id",
            "No registrado",
        ),
    )
    print(
        "Fecha:",
        apuesta.get(
            "fecha",
            "No registrada",
        ),
    )
    print(
        "Casa:",
        apuesta.get(
            "casa",
            "No registrada",
        ),
    )
    print(
        "Deporte:",
        apuesta.get(
            "deporte",
            "No registrado",
        ),
    )
    print(
        "Liga:",
        apuesta.get(
            "liga",
            "No registrada",
        ),
    )
    print(
        "Momento:",
        momento.replace(
            "_",
            " ",
        ).capitalize(),
    )
    print(
        "Modalidad:",
        modalidad.capitalize(),
    )

    selecciones = apuesta.get(
        "selecciones",
        [],
    )

    if modalidad == "straight":
        print("\nAPUESTA")
        print("-" * 50)

        if selecciones:
            seleccion = selecciones[0]

            print(
                "Evento:",
                seleccion.get(
                    "evento",
                    "No registrado",
                ),
            )
            print(
                "Mercado:",
                seleccion.get(
                    "tipo_apuesta",
                    "No registrado",
                ),
            )
            print(
                "Selección:",
                seleccion.get(
                    "seleccion",
                    "No registrada",
                ),
            )
        else:
            print("No hay información de la selección.")

    else:
        print("\nSELECCIONES")
        print("-" * 50)

        if not selecciones:
            print("No hay selecciones registradas.")

        for numero, seleccion in enumerate(
            selecciones,
            start=1,
        ):
            deporte_seleccion = seleccion.get(
                "deporte",
                apuesta.get(
                    "deporte",
                    "No registrado",
                ),
            )

            liga_seleccion = seleccion.get(
                "liga",
                apuesta.get(
                    "liga",
                    "No registrada",
                ),
            )

            resultado_individual = str(
                seleccion.get(
                    "resultado_seleccion",
                    "no_registrado",
                )
            )

            print(f"\n[{numero}]")
            print(
                "Deporte:",
                deporte_seleccion,
            )
            print(
                "Liga:",
                liga_seleccion,
            )
            print(
                "Evento:",
                seleccion.get(
                    "evento",
                    "No registrado",
                ),
            )
            print(
                "Mercado:",
                seleccion.get(
                    "tipo_apuesta",
                    "No registrado",
                ),
            )
            print(
                "Selección:",
                seleccion.get(
                    "seleccion",
                    "No registrada",
                ),
            )

            cuota_individual = seleccion.get("cuota_texto_individual")

            tipo_individual = seleccion.get("tipo_cuota_individual")

            if cuota_individual is not None:
                if tipo_individual:
                    print(
                        "Cuota individual:",
                        cuota_individual,
                        f"({tipo_individual.capitalize()})",
                    )
                else:
                    print(
                        "Cuota individual:",
                        cuota_individual,
                    )

            print(
                "Resultado de selección:",
                resultado_individual.replace(
                    "_",
                    " ",
                ).capitalize(),
            )

    print("\n" + "-" * 50)

    cuota_ajustada = False
    cuota_oficial_registrada = False
    hay_push = False
    fuente_liquidacion = "Cuota original"

    if modalidad == "parlay":
        cuota_original = obtener_cuota_decimal(apuesta)

        cuota_liquidada = calcular_cuota_liquidada_parlay(apuesta)

        cuota_oficial_registrada = apuesta.get("cuota_liquidada") is not None

        hay_push = any(
            str(
                seleccion.get(
                    "resultado_seleccion",
                    "",
                )
            )
            .strip()
            .lower()
            == "push"
            for seleccion in selecciones
        )

        cuota_ajustada = (
            cuota_oficial_registrada or abs(cuota_liquidada - cuota_original) > 0.01
        )

        print(
            "Cuota original:",
            formatear_cuota_dual(cuota_original),
        )

        if hay_push:
            print(
                "Ajuste aplicado:",
                "selección Push eliminadade la cuota",
            )

        if cuota_oficial_registrada:
            print(
                "Cuota liquidada oficial:",
                formatear_cuota_dual(cuota_liquidada),
            )

        elif hay_push:
            print(
                "Cuota liquidada calculada:",
                formatear_cuota_dual(cuota_liquidada),
            )

        if resultado == "ganada" and cuota_ajustada:
            try:
                stake = float(
                    apuesta.get(
                        "stake",
                        0,
                    )
                )
            except (TypeError, ValueError):
                stake = 0

            ganancia_original = stake * (cuota_original - 1)

            print(
                "Ganancia potencial original (no aplicada):",
                formato_dinero(ganancia_original),
            )

    else:
        tipo_cuota = str(
            apuesta.get(
                "tipo_cuota",
                "No registrada",
            )
        )

        print(
            "Cuota:",
            apuesta.get(
                "cuota_texto",
                apuesta.get(
                    "cuota",
                    "No registrada",
                ),
            ),
            f"({tipo_cuota.capitalize()})",
        )

    try:
        stake = float(
            apuesta.get(
                "stake",
                0,
            )
        )
    except (TypeError, ValueError):
        stake = 0

    print(
        "Stake:",
        formato_monto(stake),
    )
    print(
        "Resultado:",
        resultado.capitalize(),
    )

    if retorno_total_real is not None:
        print(
            "Retorno total oficial:",
            formato_monto(retorno_total_real),
        )

    if resultado == "pendiente":
        print("Ganancia: Pendiente")
        fuente_liquidacion = "Pendiente"

    elif retorno_total_real is not None:
        print(
            "Ganancia neta oficial:",
            formato_dinero(ganancia),
        )
        fuente_liquidacion = "Retorno total oficial"

    elif cuota_oficial_registrada:
        print(
            "Ganancia liquidada oficial:",
            formato_dinero(ganancia),
        )
        fuente_liquidacion = "Cuota liquidada oficial"

    elif cuota_ajustada:
        print(
            "Ganancia liquidada calculada:",
            formato_dinero(ganancia),
        )
        fuente_liquidacion = "Cálculo automático por Push"

    else:
        print(
            "Ganancia:",
            formato_dinero(ganancia),
        )

        if modalidad == "parlay" and hay_push:
            fuente_liquidacion = "Cuota original: no fue posible recalcular el Push"

    print(
        "Fuente de liquidación:",
        fuente_liquidacion,
    )

    print("=" * 50)
