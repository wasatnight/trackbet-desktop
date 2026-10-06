from almacenamiento_sqlite import cargar_apuestas_sqlite
from presentacion import mostrar_detalle_apuesta


def mostrar_historial_sqlite():
    """Muestra el historial cargado desde SQLite."""

    apuestas = cargar_apuestas_sqlite()

    if not apuestas:
        print("\nNo hay apuestas registradas en SQLite.")
        return

    print("\n===== HISTORIAL DESDE SQLITE =====")

    for apuesta in apuestas:
        mostrar_detalle_apuesta(apuesta)


if __name__ == "__main__":
    mostrar_historial_sqlite()
