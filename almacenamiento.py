from configuracion_app import MODO_ALMACENAMIENTO
import json

from almacenamiento_sqlite import (
    cargar_apuestas_sqlite,
    cargar_config_sqlite,
    guardar_apuestas_sqlite,
    guardar_config_sqlite,
)


def cargar_apuestas_json():
    """Carga las apuestas almacenadas en apuestas.json."""

    try:
        with open(
            "apuestas.json",
            "r",
            encoding="utf-8",
        ) as archivo:
            return json.load(archivo)

    except FileNotFoundError:
        return []

    except json.JSONDecodeError:
        print("Error: apuestas.json contiene información inválida.")
        return []


def guardar_apuestas_json(apuestas):
    """Guarda la lista de apuestas en apuestas.json."""

    with open(
        "apuestas.json",
        "w",
        encoding="utf-8",
    ) as archivo:
        json.dump(
            apuestas,
            archivo,
            indent=4,
            ensure_ascii=False,
        )


def cargar_config_json():
    """Carga la configuración desde config.json."""

    try:
        with open(
            "config.json",
            "r",
            encoding="utf-8",
        ) as archivo:
            return json.load(archivo)

    except FileNotFoundError:
        return {
            "bankroll_inicial": 0,
        }

    except json.JSONDecodeError:
        return {
            "bankroll_inicial": 0,
        }


def guardar_config_json(config):
    """Guarda la configuración en config.json."""

    with open(
        "config.json",
        "w",
        encoding="utf-8",
    ) as archivo:
        json.dump(
            config,
            archivo,
            indent=4,
            ensure_ascii=False,
        )


def cargar_apuestas():
    """Carga apuestas según el modo de almacenamiento activo."""

    if MODO_ALMACENAMIENTO == "sqlite":
        return cargar_apuestas_sqlite()

    return cargar_apuestas_json()


def guardar_apuestas(apuestas):
    """Guarda apuestas según el modo de almacenamiento activo."""

    if MODO_ALMACENAMIENTO == "sqlite":
        guardar_apuestas_sqlite(apuestas)
        return

    guardar_apuestas_json(apuestas)


def cargar_config():
    """Carga configuración según el modo de almacenamiento activo."""

    if MODO_ALMACENAMIENTO == "sqlite":
        config = cargar_config_sqlite()

        if not config:
            return {
                "bankroll_inicial": 0,
            }

        return config

    return cargar_config_json()


def guardar_config(config):
    """Guarda configuración según el modo de almacenamiento activo."""

    if MODO_ALMACENAMIENTO == "sqlite":
        guardar_config_sqlite(config)
        return

    guardar_config_json(config)


def asignar_ids_faltantes():
    """Asigna un ID único a las apuestas antiguas que no lo tengan."""

    apuestas = cargar_apuestas()
    cambio_realizado = False

    ids_existentes = [
        apuesta.get("id", 0)
        for apuesta in apuestas
        if isinstance(
            apuesta.get("id", 0),
            int,
        )
    ]

    siguiente_id = (
        max(
            ids_existentes,
            default=0,
        )
        + 1
    )

    for apuesta in apuestas:
        if "id" not in apuesta:
            apuesta["id"] = siguiente_id
            siguiente_id += 1
            cambio_realizado = True

    if cambio_realizado:
        guardar_apuestas(apuestas)


def obtener_modo_almacenamiento():
    """Devuelve el modo de almacenamiento actual."""

    if MODO_ALMACENAMIENTO == "sqlite":
        return "SQLite"

    if MODO_ALMACENAMIENTO == "json":
        return "JSON"

    return "Desconocido"
