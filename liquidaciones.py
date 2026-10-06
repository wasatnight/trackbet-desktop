from calculos import (
    calcular_cuota_liquidada_parlay,
    convertir_cuota_a_decimal,
    formatear_cuota_dual,
    formato_dinero,
    formato_monto,
)
from menus import seleccionar_tipo_cuota
from validaciones import pedir_cuota, pedir_numero


def gestionar_liquidacion_parlay(apuesta):
    """Gestiona cuota liquidada oficial o retorno real de un parlay."""

    if apuesta.get("modalidad") != "parlay":
        print("Esta opción solamente está disponible para apuestas parlay.")
        return False

    print("\n===== LIQUIDACIÓN OFICIAL DEL PARLAY =====")
    print("1. Registrar cuota liquidada oficial")
    print("2. Registrar retorno total pagado")
    print("3. Eliminar liquidación oficial")
    print("4. Cancelar")

    opcion_liquidada = input("Elige una opción: ").strip()

    if opcion_liquidada == "1":
        tipo_cuota_liquidada = seleccionar_tipo_cuota()

        cuota_liquidada_texto, _ = pedir_cuota(tipo_cuota_liquidada)

        cuota_liquidada_decimal = convertir_cuota_a_decimal(
            tipo_cuota_liquidada,
            cuota_liquidada_texto,
        )

        if cuota_liquidada_decimal <= 1:
            print("La cuota liquidada no es válida.")
            return False

        apuesta["cuota_liquidada"] = cuota_liquidada_decimal
        apuesta["tipo_cuota_liquidada"] = tipo_cuota_liquidada
        apuesta["cuota_liquidada_texto"] = cuota_liquidada_texto

        print(
            "Cuota liquidada oficial guardada:",
            formatear_cuota_dual(cuota_liquidada_decimal),
        )

        return True

    if opcion_liquidada == "2":
        return registrar_retorno_total_oficial(apuesta)

    if opcion_liquidada == "3":
        eliminar_liquidacion_oficial(apuesta)
        return True

    if opcion_liquidada == "4":
        print("Operación cancelada.")
        return False

    print("Opción no válida.")
    return False


def registrar_retorno_total_oficial(apuesta):
    """Registra el retorno total pagado por la casa."""

    resultado_actual = (
        str(
            apuesta.get(
                "resultado",
                "pendiente",
            )
        )
        .strip()
        .lower()
    )

    if resultado_actual == "pendiente":
        print(
            "No puedes registrar un retorno oficial "
            "mientras la apuesta esté pendiente."
        )
        return False

    while True:
        retorno_total_real = pedir_numero(
            "Retorno total pagado por la casa (incluye el stake): "
        )

        if retorno_total_real < 0:
            print("El retorno total no puede ser negativo.")
            continue

        try:
            stake = float(
                apuesta.get(
                    "stake",
                    0,
                )
            )
        except (TypeError, ValueError):
            stake = 0

        retorno_esperado = calcular_retorno_esperado(
            apuesta,
            resultado_actual,
            stake,
        )

        if retorno_esperado is not None:
            diferencia = retorno_total_real - retorno_esperado

            if abs(diferencia) > 0.05:
                print("\n===== ADVERTENCIA DE LIQUIDACIÓN =====")
                print(
                    "Retorno esperado:",
                    formato_monto(retorno_esperado),
                )
                print(
                    "Retorno introducido:",
                    formato_monto(retorno_total_real),
                )
                print(
                    "Diferencia:",
                    formato_dinero(diferencia),
                )

                print("\n1. Guardar de todas formas")
                print("2. Volver a introducir el retorno")
                print("3. Cancelar")

                decision = input("Elige una opción: ").strip()

                if decision == "1":
                    break

                if decision == "2":
                    continue

                if decision == "3":
                    print("Operación cancelada.")
                    return False

                print("Opción no válida.")
                continue

        break

    apuesta["retorno_total_real"] = retorno_total_real

    ganancia_real = retorno_total_real - stake

    print(
        "Retorno total oficial guardado:",
        formato_monto(retorno_total_real),
    )

    print(
        "Ganancia neta oficial:",
        formato_dinero(ganancia_real),
    )

    return True


def calcular_retorno_esperado(
    apuesta,
    resultado_actual,
    stake,
):
    """Calcula el retorno esperado según el resultado del parlay."""

    if resultado_actual == "ganada":
        cuota_referencia = calcular_cuota_liquidada_parlay(apuesta)

        return stake * cuota_referencia

    if resultado_actual == "perdida":
        return 0

    if resultado_actual == "push":
        return stake

    return None


def eliminar_liquidacion_oficial(apuesta):
    """Elimina los datos oficiales de liquidación."""

    apuesta.pop(
        "cuota_liquidada",
        None,
    )

    apuesta.pop(
        "tipo_cuota_liquidada",
        None,
    )

    apuesta.pop(
        "cuota_liquidada_texto",
        None,
    )

    apuesta.pop(
        "retorno_total_real",
        None,
    )

    print("Liquidación oficial eliminada, Se utilizará el cálculo automático.")
