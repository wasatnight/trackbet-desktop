from almacenamiento import (
    cargar_apuestas,
    guardar_apuestas,
)


def eliminar_apuesta():
    """Elimina una apuesta utilizando su ID."""

    apuestas = cargar_apuestas()

    if not apuestas:
        print("\nNo hay apuestas registradas.")
        return

    try:
        id_buscado = int(input("Ingresa el ID de la apuesta que quieres eliminar: "))
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

    momento = apuesta_encontrada.get(
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
        momento.replace("_", " ").capitalize(),
    )
    print(
        "Modalidad:",
        apuesta_encontrada["modalidad"].capitalize(),
    )
    print(
        "Resultado:",
        apuesta_encontrada.get("resultado", "pendiente").capitalize(),
    )

    confirmacion = (
        input("\n¿Seguro que quieres eliminar esta apuesta? (si/no): ").strip().lower()
    )

    if confirmacion in ("si", "sí", "s"):
        apuestas.remove(apuesta_encontrada)
        guardar_apuestas(apuestas)
        print("Apuesta eliminada correctamente.")
    else:
        print("Eliminación cancelada.")
