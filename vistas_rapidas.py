from almacenamiento import cargar_apuestas
from calculos import (
    calcular_ganancia_apuesta,
    formato_dinero,
    formato_monto,
)
from presentacion import mostrar_detalle_apuesta


def filtrar_apuestas_por_resultado(apuestas, resultado_buscado):
    """Filtra apuestas según su resultado general."""

    resultado_buscado = str(resultado_buscado).strip().lower()

    return [
        apuesta
        for apuesta in apuestas
        if str(
            apuesta.get(
                "resultado",
                "pendiente",
            )
        )
        .strip()
        .lower()
        == resultado_buscado
    ]


def calcular_resumen_vista(apuestas):
    """Calcula resumen financiero de una vista rápida."""

    stake_total = 0
    ganancia_neta = 0

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

        if resultado != "pendiente":
            ganancia_neta += calcular_ganancia_apuesta(apuesta)

    if stake_total > 0:
        roi = (ganancia_neta / stake_total) * 100
    else:
        roi = 0

    return {
        "stake_total": stake_total,
        "ganancia_neta": ganancia_neta,
        "roi": roi,
    }


def mostrar_apuestas_por_resultado(resultado_buscado, titulo):
    """Muestra apuestas filtradas por resultado."""

    apuestas = cargar_apuestas()

    resultados = filtrar_apuestas_por_resultado(
        apuestas,
        resultado_buscado,
    )

    if not resultados:
        print(f"\nNo hay apuestas con resultado: {titulo}.")
        return

    resumen = calcular_resumen_vista(resultados)

    print(f"\n===== {titulo.upper()} =====")
    print("Total:", len(resultados))
    print(
        "Stake total:",
        formato_monto(resumen["stake_total"]),
    )
    print(
        "Ganancia neta:",
        formato_dinero(resumen["ganancia_neta"]),
    )
    print(
        "ROI:",
        f"{resumen['roi']:.2f}%",
    )

    for apuesta in resultados:
        mostrar_detalle_apuesta(apuesta)


def mostrar_menu_vistas_rapidas():
    """Muestra el menú de vistas rápidas."""

    while True:
        print("\n===== VISTAS RÁPIDAS =====")
        print("1. Apuestas ganadas")
        print("2. Apuestas perdidas")
        print("3. Apuestas push")
        print("4. Apuestas pendientes")
        print("5. Volver")

        opcion = input("Elige una opción: ").strip()

        if opcion == "1":
            mostrar_apuestas_por_resultado(
                "ganada",
                "Apuestas ganadas",
            )

        elif opcion == "2":
            mostrar_apuestas_por_resultado(
                "perdida",
                "Apuestas perdidas",
            )

        elif opcion == "3":
            mostrar_apuestas_por_resultado(
                "push",
                "Apuestas push",
            )

        elif opcion == "4":
            mostrar_apuestas_por_resultado(
                "pendiente",
                "Apuestas pendientes",
            )

        elif opcion == "5":
            return

        else:
            print("Opción no válida.")
