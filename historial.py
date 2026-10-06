from almacenamiento import cargar_apuestas
from presentacion import mostrar_detalle_apuesta


def mostrar_historial():
    """Muestra todas las apuestas registradas."""

    apuestas = cargar_apuestas()

    if not apuestas:
        print("\nNo hay apuestas registradas.")
        return

    print("\n===== HISTORIAL =====")

    for apuesta in apuestas:
        mostrar_detalle_apuesta(apuesta)
