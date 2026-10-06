from almacenamiento import (
    cargar_apuestas,
    guardar_apuestas,
)
from menus import (
    seleccionar_casa,
    seleccionar_deporte,
    seleccionar_momento_apuesta,
    seleccionar_resultado,
    seleccionar_tipo_cuota,
)
from validaciones import (
    pedir_cuota,
    pedir_numero,
)
from parlays import editar_resultados_parlay
from liquidaciones import gestionar_liquidacion_parlay


def editar_apuesta():
    apuestas = cargar_apuestas()

    if not apuestas:
        print("\nNo hay apuestas registradas.")
        return

    try:
        id_buscado = int(input("Ingresa el ID de la apuesta que quieres editar: "))
    except ValueError:
        print("ID no válido.")
        return

    apuesta_encontrada = None

    for apuesta in apuestas:
        if apuesta.get("id") == id_buscado:
            apuesta_encontrada = apuesta
            break

    if apuesta_encontrada is None:
        print("No existe una apuesta con ese ID.")
        return

    momento_actual = apuesta_encontrada.get(
        "momento_apuesta",
        "no_registrado",
    )

    print("\n===== APUESTA ENCONTRADA =====")
    print("ID:", apuesta_encontrada["id"])
    print("Fecha:", apuesta_encontrada["fecha"])
    print("Casa:", apuesta_encontrada["casa"])
    print("Deporte:", apuesta_encontrada["deporte"])
    print("Liga:", apuesta_encontrada["liga"])
    print(
        "Momento:",
        momento_actual.replace("_", " ").capitalize(),
    )
    print(
        "Cuota:",
        apuesta_encontrada.get(
            "cuota_texto",
            apuesta_encontrada["cuota"],
        ),
    )
    print(f"Stake: ${apuesta_encontrada['stake']:.2f}")
    print(
        "Resultado:",
        apuesta_encontrada["resultado"].capitalize(),
    )

    print("\n¿Qué deseas editar?")
    print("1.  Casa de apuestas")
    print("2.  Deporte")
    print("3.  Liga")
    print("4.  Momento de la apuesta")
    print("5.  Tipo de cuota y cuota")
    print("6.  Stake")
    print("7.  Resultado general")
    print("8.  Resultados de las selecciones del parlay")
    print("9.  Cuota liquidada oficial del parlay")
    print("10. Cancelar")

    opcion_edicion = input("Elige una opción: ").strip()

    if opcion_edicion == "1":
        apuesta_encontrada["casa"] = seleccionar_casa()

    elif opcion_edicion == "2":
        apuesta_encontrada["deporte"] = seleccionar_deporte()

    elif opcion_edicion == "3":
        nueva_liga = input("Nueva liga: ").strip()

        if nueva_liga:
            apuesta_encontrada["liga"] = nueva_liga

    elif opcion_edicion == "4":
        apuesta_encontrada["momento_apuesta"] = seleccionar_momento_apuesta()

    elif opcion_edicion == "5":
        modalidad_actual = apuesta_encontrada.get("modalidad", "straight")
        if modalidad_actual == "parlay":
            print("\n===== CUOTA TOTAL DEL PARLAY =====")
            print("Ingresa la cuota combinada final que te ofrece la casa de apuestas.")
        else:
            print("\n===== CUOTA DE LA APUESTA =====")

        tipo_cuota = seleccionar_tipo_cuota()
        cuota_texto, cuota = pedir_cuota(tipo_cuota)

        apuesta_encontrada["tipo_cuota"] = tipo_cuota
        apuesta_encontrada["cuota_texto"] = cuota_texto
        apuesta_encontrada["cuota"] = cuota

    elif opcion_edicion == "6":
        apuesta_encontrada["stake"] = pedir_numero("Nuevo stake: ")

    elif opcion_edicion == "7":
        if apuesta_encontrada.get("modalidad") == "parlay":
            print(
                "En un parlay, modifica los resultados "
                "individuales desde la opción 8."
            )
            return

        apuesta_encontrada["resultado"] = seleccionar_resultado()

    elif opcion_edicion == "8":
        if apuesta_encontrada.get("modalidad") != "parlay":
            print("Esta opción solamente está disponible " + "para apuestas parlay.")
            return

        editar_resultados_parlay(apuesta_encontrada)

    elif opcion_edicion == "9":
        cambios_realizados = gestionar_liquidacion_parlay(apuesta_encontrada)

        if not cambios_realizados:
            return

    elif opcion_edicion == "10":
        print("Edición cancelada.")
        return
    else:
        print("Opción no válida.")
        return

    guardar_apuestas(apuestas)
    print("Apuesta guardada correctamente")
