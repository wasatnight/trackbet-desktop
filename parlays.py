from menus import seleccionar_resultado_seleccion


def calcular_resultado_general_parlay(selecciones):
    """Calcula el resultado general según las selecciones del parlay."""

    resultados = [
        str(
            seleccion.get(
                "resultado_seleccion",
                "pendiente",
            )
        )
        .strip()
        .lower()
        for seleccion in selecciones
    ]

    if not resultados:
        return "pendiente"

    # Una selección perdida hace perder todo el parlay.
    if "perdida" in resultados:
        return "perdida"

    # Si queda alguna selección pendiente,
    # el parlay todavía no está resuelto.
    if "pendiente" in resultados:
        return "pendiente"

    if "no_registrado" in resultados:
        return "pendiente"

    # Si todas las selecciones fueron Push.
    if all(resultado == "push" for resultado in resultados):
        return "push"

    # Ganadas y Push permiten que el parlay sea ganador.
    if all(resultado in ("ganada", "push") for resultado in resultados):
        return "ganada"

    return "pendiente"


def editar_resultados_parlay(apuesta):
    """Permite actualizar el resultado de cada selección del parlay."""

    if apuesta.get("modalidad") != "parlay":
        print("\nEsta apuesta no es un parlay.")
        return

    selecciones = apuesta.get("selecciones", [])

    if not selecciones:
        print("\nEste parlay no tiene selecciones registradas.")
        return

    while True:
        print("\n===== RESULTADOS DEL PARLAY =====")

        for numero, seleccion in enumerate(
            selecciones,
            start=1,
        ):
            resultado_actual = seleccion.get(
                "resultado_seleccion",
                "pendiente",
            )

            print(
                f"{numero}. "
                f"{seleccion.get('evento', 'No registrado')} | "
                f"{seleccion.get('seleccion', 'No registrada')} | "
                f"{resultado_actual.capitalize()}"
            )

        print("0. Terminar edición")

        try:
            numero_seleccion = int(
                input("Selecciona la pierna que quieres actualizar: ")
            )
        except ValueError:
            print("Debes ingresar un número válido.")
            continue

        if numero_seleccion == 0:
            break

        if not 1 <= numero_seleccion <= len(selecciones):
            print("Selección no válida.")
            continue

        seleccion_elegida = selecciones[numero_seleccion - 1]

        print(
            "\nActualizando:",
            seleccion_elegida.get(
                "evento",
                "No registrado",
            ),
        )

        nuevo_resultado = seleccionar_resultado_seleccion()

        seleccion_elegida["resultado_seleccion"] = nuevo_resultado

        resultado_general = calcular_resultado_general_parlay(selecciones)

        apuesta["resultado"] = resultado_general

        print(
            "Resultado de la selección actualizado:",
            nuevo_resultado.capitalize(),
        )
        print(
            "Resultado general del parlay:",
            resultado_general.capitalize(),
        )
