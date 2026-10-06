import csv

from almacenamiento import cargar_apuestas
from calculos import (
    calcular_cuota_liquidada_parlay,
    calcular_ganancia_apuesta,
    formatear_cuota_dual,
    obtener_cuota_decimal,
)


def determinar_fuente_liquidacion(
    apuesta,
    modalidad,
    resultado,
    cuota_original,
    cuota_liquidada,
):
    """Indica qué dato se utilizó para calcular la ganancia."""

    if resultado == "pendiente":
        return "Pendiente"

    if apuesta.get("retorno_total_real") is not None:
        return "Retorno total oficial"

    if modalidad == "parlay":
        if apuesta.get("cuota_liquidada") is not None:
            return "Cuota liquidada oficial"

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
            for seleccion in apuesta.get(
                "selecciones",
                [],
            )
        )

        if hay_push:
            if abs(cuota_liquidada - cuota_original) > 0.01:
                return "Cálculo automático por Push"

            return "Cuota original: no fue posible " "recalcular el Push"

    return "Cuota original"


def formatear_cuota_csv(cuota):
    """Presenta una cuota para el reporte CSV."""

    try:
        cuota = float(cuota)
    except (TypeError, ValueError):
        return ""

    if cuota > 1:
        return formatear_cuota_dual(cuota)

    if cuota == 1:
        return "1.00 decimal / apuesta reembolsada"

    return ""


def exportar_apuestas_csv():
    """Exporta las apuestas y sus liquidaciones a un archivo CSV."""

    apuestas = cargar_apuestas()

    if not apuestas:
        print("No hay apuestas para exportar.")
        return

    with open(
        "reporte_apuestas.csv",
        "w",
        newline="",
        encoding="utf-8-sig",
    ) as archivo:

        columnas = [
            "id",
            "fecha",
            "casa",
            "deporte",
            "liga",
            "momento_apuesta",
            "modalidad",
            "selecciones",
            "tipo_cuota",
            "cuota",
            "cuota_original_decimal",
            "cuota_original_equivalente",
            "cuota_liquidada_decimal",
            "cuota_liquidada_equivalente",
            "fuente_liquidacion",
            "stake",
            "resultado",
            "retorno_total_oficial",
            "retorno_total_final",
            "ganancia",
        ]

        escritor = csv.DictWriter(
            archivo,
            fieldnames=columnas,
        )

        escritor.writeheader()

        for apuesta in apuestas:
            selecciones_texto = []

            for seleccion in apuesta.get(
                "selecciones",
                [],
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

                cuota_individual = seleccion.get(
                    "cuota_texto_individual",
                    "No registrada",
                )

                tipo_cuota_individual = seleccion.get(
                    "tipo_cuota_individual",
                    "No registrada",
                )

                resultado_individual = (
                    str(
                        seleccion.get(
                            "resultado_seleccion",
                            "no_registrado",
                        )
                    )
                    .replace("_", " ")
                    .capitalize()
                )

                texto = (
                    f"{deporte_seleccion} | "
                    f"{liga_seleccion} | "
                    f"{seleccion.get('evento', 'No registrado')} | "
                    f"{seleccion.get('tipo_apuesta', 'No registrado')} | "
                    f"{seleccion.get('seleccion', 'No registrada')} | "
                    f"Cuota individual: {cuota_individual} "
                    f"({tipo_cuota_individual.capitalize()}) | "
                    f"Resultado individual: {resultado_individual}"
                )

                selecciones_texto.append(texto)

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

            modalidad = (
                str(
                    apuesta.get(
                        "modalidad",
                        "no_registrada",
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

            try:
                stake = float(apuesta.get("stake", 0))
            except (TypeError, ValueError):
                stake = 0

            cuota_original = obtener_cuota_decimal(apuesta)

            if modalidad == "parlay":
                cuota_liquidada = calcular_cuota_liquidada_parlay(apuesta)
            else:
                cuota_liquidada = cuota_original

            ganancia = calcular_ganancia_apuesta(apuesta)

            fuente_liquidacion = determinar_fuente_liquidacion(
                apuesta,
                modalidad,
                resultado,
                cuota_original,
                cuota_liquidada,
            )

            retorno_total_real = apuesta.get("retorno_total_real")

            if retorno_total_real is not None:
                try:
                    retorno_total_oficial = round(
                        float(retorno_total_real),
                        2,
                    )
                except (TypeError, ValueError):
                    retorno_total_oficial = ""
            else:
                retorno_total_oficial = ""

            if resultado == "pendiente":
                ganancia_exportada = ""
                retorno_total_final = ""
            else:
                ganancia_exportada = round(
                    ganancia,
                    2,
                )

                retorno_total_final = round(
                    stake + ganancia,
                    2,
                )

            escritor.writerow(
                {
                    "id": apuesta.get(
                        "id",
                        "No registrado",
                    ),
                    "fecha": apuesta.get(
                        "fecha",
                        "No registrada",
                    ),
                    "casa": apuesta.get(
                        "casa",
                        "No registrada",
                    ),
                    "deporte": apuesta.get(
                        "deporte",
                        "No registrado",
                    ),
                    "liga": apuesta.get(
                        "liga",
                        "No registrada",
                    ),
                    "momento_apuesta": (momento.replace("_", " ").capitalize()),
                    "modalidad": modalidad.capitalize(),
                    "selecciones": " || ".join(selecciones_texto),
                    "tipo_cuota": apuesta.get(
                        "tipo_cuota",
                        "No registrada",
                    ).capitalize(),
                    "cuota": apuesta.get(
                        "cuota_texto",
                        apuesta.get(
                            "cuota",
                            "No registrada",
                        ),
                    ),
                    "cuota_original_decimal": (
                        round(cuota_original, 2) if cuota_original > 1 else ""
                    ),
                    "cuota_original_equivalente": (formatear_cuota_csv(cuota_original)),
                    "cuota_liquidada_decimal": (
                        round(cuota_liquidada, 2) if cuota_liquidada >= 1 else ""
                    ),
                    "cuota_liquidada_equivalente": (
                        formatear_cuota_csv(cuota_liquidada)
                    ),
                    "fuente_liquidacion": (fuente_liquidacion),
                    "stake": round(stake, 2),
                    "resultado": resultado.capitalize(),
                    "retorno_total_oficial": (retorno_total_oficial),
                    "retorno_total_final": (retorno_total_final),
                    "ganancia": ganancia_exportada,
                }
            )

    print("Reporte exportado correctamente como:reporte_apuestas.csv")
