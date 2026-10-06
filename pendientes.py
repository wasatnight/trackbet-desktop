from almacenamiento import (
    cargar_apuestas,
    guardar_apuestas,
)
from menus import seleccionar_resultado
from parlays import editar_resultados_parlay
from presentacion import mostrar_detalle_apuesta
from servicios_apuestas import (
    cerrar_apuesta_por_id,
    listar_apuestas_pendientes,
)


def filtrar_apuestas_pendientes(apuestas):
    """Devuelve solo las apuestas pendientes."""

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
        == "pendiente"
    ]


def mostrar_apuestas_pendientes():
    """Muestra las apuestas que siguen pendientes."""

    pendientes = listar_apuestas_pendientes()

    if not pendientes:
        print("\nNo hay apuestas pendientes.")
        return

    print("\n===== APUESTAS PENDIENTES =====")
    print("Total pendientes:", len(pendientes))

    for apuesta in pendientes:
        mostrar_detalle_apuesta(apuesta)


def cerrar_apuesta_pendiente():
    """Permite cerrar rápidamente una apuesta pendiente."""

    apuestas = cargar_apuestas()
    pendientes = filtrar_apuestas_pendientes(apuestas)

    if not pendientes:
        print("\nNo hay apuestas pendientes para cerrar.")
        return

    print("\n===== CERRAR APUESTA PENDIENTE =====")
    print("Apuestas pendientes encontradas:", len(pendientes))

    for apuesta in pendientes:
        print("\n" + "-" * 50)
        print("ID:", apuesta.get("id", "No registrado"))
        print("Fecha:", apuesta.get("fecha", "No registrada"))
        print("Casa:", apuesta.get("casa", "No registrada"))
        print("Deporte:", apuesta.get("deporte", "No registrado"))
        print("Liga:", apuesta.get("liga", "No registrada"))
        print("Modalidad:", apuesta.get("modalidad", "No registrada").capitalize())
        print("Stake:", apuesta.get("stake", 0))

        selecciones = apuesta.get("selecciones", [])

        if selecciones:
            primera_seleccion = selecciones[0]
            print(
                "Evento:",
                primera_seleccion.get(
                    "evento",
                    "No registrado",
                ),
            )
            print(
                "Selección:",
                primera_seleccion.get(
                    "seleccion",
                    "No registrada",
                ),
            )

    try:
        id_buscado = int(
            input("\nIngresa el ID de la apuesta pendiente que quieres cerrar: ")
        )
    except ValueError:
        print("ID no válido.")
        return

    apuesta_encontrada = None

    for apuesta in pendientes:
        if apuesta.get("id") == id_buscado:
            apuesta_encontrada = apuesta
            break

    if apuesta_encontrada is None:
        print("No existe una apuesta pendiente con ese ID.")
        return

    print("\n===== APUESTA SELECCIONADA =====")
    mostrar_detalle_apuesta(apuesta_encontrada)

    confirmacion = input("\n¿Deseas cerrar esta apuesta? (si/no): ").strip().lower()

    if confirmacion not in ("si", "sí", "s"):
        print("Operación cancelada.")
        return

    modalidad = (
        str(
            apuesta_encontrada.get(
                "modalidad",
                "straight",
            )
        )
        .strip()
        .lower()
    )

    if modalidad == "parlay":
        print("\nEsta apuesta es un parlay. Actualiza los resultados individuales.")

        editar_resultados_parlay(apuesta_encontrada)
        guardar_apuestas(apuestas)

        print("Apuesta pendiente actualizada correctamente.")
        return

    nuevo_resultado = seleccionar_resultado()

    respuesta = cerrar_apuesta_por_id(
        apuesta_encontrada["id"],
        nuevo_resultado,
    )

    print(respuesta["mensaje"])
