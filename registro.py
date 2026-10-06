from datetime import datetime

from almacenamiento import (
    cargar_apuestas,
    guardar_apuestas,
)
from calculos import (
    convertir_cuota_a_decimal,
    formatear_cuota_dual,
)
from menus import (
    seleccionar_casa,
    seleccionar_deporte,
    seleccionar_mercado,
    seleccionar_modalidad,
    seleccionar_momento_apuesta,
    seleccionar_resultado,
    seleccionar_resultado_seleccion,
    seleccionar_tipo_cuota,
)
from parlays import calcular_resultado_general_parlay
from validaciones import pedir_cuota, pedir_numero


def registrar_apuesta():
    """Solicita los datos de una apuesta y la guarda."""

    fecha = datetime.now().strftime("%d/%m/%Y")

    casa = seleccionar_casa()
    momento_apuesta = seleccionar_momento_apuesta()
    modalidad = seleccionar_modalidad()

    selecciones = []

    if modalidad == "straight":
        deporte = seleccionar_deporte()
        liga = input("Liga: ").strip()
    else:
        deporte = "Mixto"
        liga = "Mixta"

    if modalidad == "parlay":
        while True:

            print(f"\n===== SELECCIÓN {len(selecciones) + 1} " "DEL PARLAY =====")

            deporte_seleccion = seleccionar_deporte()
            liga_seleccion = input("Liga de esta selección: ").strip()

            evento = input("Evento: ").strip()
            tipo_apuesta, seleccion_automatica = seleccionar_mercado()

            if seleccion_automatica is not None:
                seleccion = seleccion_automatica
                print("Selección:", seleccion)
            else:
                seleccion = input("Selección: ").strip()

            print("\nCuota individual de esta selección:")
            tipo_cuota_individual = seleccionar_tipo_cuota()

            cuota_texto_individual, _ = pedir_cuota(tipo_cuota_individual)

            cuota_individual_decimal = convertir_cuota_a_decimal(
                tipo_cuota_individual,
                cuota_texto_individual,
            )

            resultado_seleccion = seleccionar_resultado_seleccion()

            seleccion_parlay = {
                "deporte": deporte_seleccion,
                "liga": liga_seleccion,
                "evento": evento,
                "tipo_apuesta": tipo_apuesta,
                "seleccion": seleccion,
                "tipo_cuota_individual": tipo_cuota_individual,
                "cuota_texto_individual": cuota_texto_individual,
                "cuota_individual": cuota_individual_decimal,
                "resultado_seleccion": resultado_seleccion,
            }

            print("\n===== CONFIRMAR SELECCIÓN =====")
            print("Deporte:", deporte_seleccion)
            print("Liga:", liga_seleccion)
            print("Evento:", evento)
            print("Mercado:", tipo_apuesta)
            print("Selección:", seleccion)
            print(
                "Cuota:",
                formatear_cuota_dual(cuota_individual_decimal),
            )
            print(
                "Resultado:",
                resultado_seleccion.capitalize(),
            )

            print("\n1. Guardar esta selección")
            print("2. Volver a capturarla")
            print("3. Cancelar el registro completo")

            confirmacion = input("Elige una opción: ").strip()

            if confirmacion == "2":
                print("\nVuelve a capturar esta selección.")
                continue

            if confirmacion == "3":
                print("\nRegistro del parlay cancelado.")
                return

            if confirmacion != "1":
                print("\nOpción no válida. Vuelve a capturarla.")
                continue

            selecciones.append(seleccion_parlay)

            while True:
                print("\n¿Qué deseas hacer ahora?")
                print("1. Agregar otra selección al parlay")
                print("2. Deshacer la última selección")
                print("3. Finalizar el registro del parlay")
                print("4. Cancelar el registro completo")

                accion = input("Elige una opción: ").strip()

                if accion == "1":
                    break

                elif accion == "2":
                    seleccion_eliminada = selecciones.pop()

                    print(
                        "\nSelección eliminada:",
                        seleccion_eliminada["seleccion"],
                    )
                    print("Vuelve a capturar la selección.")
                    break

                elif accion == "3":
                    if len(selecciones) < 2:
                        print("\nUn parlay debe tener al menos 2 selecciones. ")
                        continue

                    break

                elif accion == "4":
                    print("\nRegistro del parlay cancelado.")
                    return

                else:
                    print("\nOpción no válida. Intenta de nuevo.")
            if accion == "3":
                break

        deportes_parlay = {seleccion["deporte"] for seleccion in selecciones}

        ligas_parlay = {seleccion["liga"] for seleccion in selecciones}

        if len(deportes_parlay) == 1:
            deporte = next(iter(deportes_parlay))
        else:
            deporte = "Mixto"

        if len(ligas_parlay) == 1:
            liga = next(iter(ligas_parlay))
        else:
            liga = "Mixta"

    else:
        evento = input("Evento: ").strip()
        tipo_apuesta, seleccion_automatica = seleccionar_mercado()

        if seleccion_automatica is not None:
            seleccion = seleccion_automatica
            print("Selección:", seleccion)
        else:
            seleccion = input("Selección: ").strip()

        selecciones.append(
            {
                "deporte": deporte,
                "liga": liga,
                "evento": evento,
                "tipo_apuesta": tipo_apuesta,
                "seleccion": seleccion,
            }
        )

    if modalidad == "parlay":
        cuota_teorica = 1

        for seleccion_parlay in selecciones:
            cuota_teorica *= seleccion_parlay["cuota_individual"]

        print("\n===== CUOTA TOTAL DEL PARLAY =====")
        print(
            "Cuota combinada teórica:",
            formatear_cuota_dual(cuota_teorica),
        )
        print("Ingresa la cuota combinada final que te ofrece la casa de apuestas.")

    else:
        print("\n===== CUOTA DE LA APUESTA =====")

    tipo_cuota = seleccionar_tipo_cuota()
    cuota_texto, cuota = pedir_cuota(tipo_cuota)
    stake = pedir_numero("Cantidad apostada: ")

    if modalidad == "parlay":
        resultado = calcular_resultado_general_parlay(selecciones)

        print(
            "\nResultado general calculado:",
            resultado.capitalize(),
        )

    else:
        resultado = seleccionar_resultado()

    apuesta = {
        "fecha": fecha,
        "casa": casa,
        "deporte": deporte,
        "liga": liga,
        "momento_apuesta": momento_apuesta,
        "modalidad": modalidad,
        "selecciones": selecciones,
        "tipo_cuota": tipo_cuota,
        "cuota_texto": cuota_texto,
        "cuota": cuota,
        "stake": stake,
        "resultado": resultado,
    }

    apuestas = cargar_apuestas()

    ids_existentes = [
        apuesta_guardada.get("id", 0)
        for apuesta_guardada in apuestas
        if isinstance(apuesta_guardada.get("id", 0), int)
    ]

    nuevo_id = max(ids_existentes, default=0) + 1
    apuesta["id"] = nuevo_id

    apuestas.append(apuesta)
    guardar_apuestas(apuestas)

    print("\nApuesta registrada correctamente.")
    print("ID:", nuevo_id)
    print("Fecha:", fecha)
    print("Casa:", casa)
    print("Deporte:", deporte)
    print("Liga:", liga)
    print(
        "Momento:",
        momento_apuesta.replace("_", " ").capitalize(),
    )
    print("Modalidad:", modalidad.capitalize())

    if modalidad == "straight":
        seleccion_guardada = selecciones[0]

        print("\nAPUESTA")
        print("-" * 50)
        print("Evento:", seleccion_guardada["evento"])
        print("Mercado:", seleccion_guardada["tipo_apuesta"])
        print("Selección:", seleccion_guardada["seleccion"])

    else:
        print("\nSELECCIONES")
        print("-" * 50)

        for numero, seleccion_guardada in enumerate(
            selecciones,
            start=1,
        ):
            tipo_individual = seleccion_guardada["tipo_cuota_individual"]

            print(f"\n[{numero}]")
            print(
                "Deporte:",
                seleccion_guardada["deporte"],
            )
            print(
                "Liga:",
                seleccion_guardada["liga"],
            )
            print("Evento:", seleccion_guardada["evento"])
            print(
                "Mercado:",
                seleccion_guardada["tipo_apuesta"],
            )
            print(
                "Selección:",
                seleccion_guardada["seleccion"],
            )
            print(
                "Cuota individual:",
                seleccion_guardada["cuota_texto_individual"],
                f"({tipo_individual.capitalize()})",
            )
            resultado_individual = seleccion_guardada.get(
                "resultado_seleccion",
                "pendiente",
            )

            print(
                "Resultado de selección:",
                resultado_individual.capitalize(),
            )

    print("\n" + "-" * 50)
    print("Tipo de cuota:", tipo_cuota.capitalize())
    print("Cuota:", cuota_texto)
    print(f"Stake: ${stake:.2f}")
    print("Resultado:", resultado.capitalize())
