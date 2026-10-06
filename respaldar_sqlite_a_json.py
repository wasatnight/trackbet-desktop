from configuracion_app import CARPETA_RESPALDOS
import json
from datetime import datetime
from pathlib import Path

from almacenamiento_sqlite import (
    cargar_apuestas_sqlite,
    cargar_config_sqlite,
)


def crear_carpeta_respaldos():
    """Crea la carpeta de respaldos si no existe."""

    carpeta = Path(CARPETA_RESPALDOS)
    carpeta.mkdir(exist_ok=True)

    return carpeta


def generar_nombre_respaldo(nombre_base):
    """Genera un nombre de respaldo con fecha y hora."""

    fecha_hora = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    return f"{nombre_base}_{fecha_hora}.json"


def guardar_json(ruta, datos):
    """Guarda datos en un archivo JSON."""

    with open(
        ruta,
        "w",
        encoding="utf-8",
    ) as archivo:
        json.dump(
            datos,
            archivo,
            indent=4,
            ensure_ascii=False,
        )


def respaldar_sqlite_a_json():
    """Crea respaldos JSON desde la base de datos SQLite."""

    carpeta_respaldos = crear_carpeta_respaldos()

    apuestas = cargar_apuestas_sqlite()
    config = cargar_config_sqlite()

    ruta_apuestas = carpeta_respaldos / generar_nombre_respaldo("apuestas")

    ruta_config = carpeta_respaldos / generar_nombre_respaldo("config")

    guardar_json(
        ruta_apuestas,
        apuestas,
    )

    guardar_json(
        ruta_config,
        config,
    )

    print("\n===== RESPALDO COMPLETADO =====")
    print("Apuestas respaldadas:", len(apuestas))
    print("Archivo:", ruta_apuestas)
    print("Configuración respaldada:", ruta_config)


if __name__ == "__main__":
    respaldar_sqlite_a_json()
