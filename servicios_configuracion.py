from almacenamiento import (
    cargar_config,
    guardar_config,
)


def convertir_bankroll(valor):
    """Convierte y valida un bankroll."""

    try:
        bankroll = float(valor)
    except (TypeError, ValueError):
        return None

    if bankroll < 0:
        return None

    return bankroll


def obtener_configuracion_bankroll():
    """Devuelve la configuración actual del bankroll."""

    config = cargar_config()

    bankroll = convertir_bankroll(config.get("bankroll_inicial", 0))

    if bankroll is None:
        bankroll = 0.0

    return {
        "bankroll_inicial": bankroll,
    }


def actualizar_configuracion_bankroll(bankroll_inicial):
    """Actualiza el bankroll inicial."""

    bankroll = convertir_bankroll(bankroll_inicial)

    if bankroll is None:
        return {
            "ok": False,
            "mensaje": ("El bankroll debe ser un número " "mayor o igual que cero."),
            "configuracion": None,
        }

    config = cargar_config()
    config["bankroll_inicial"] = bankroll

    guardar_config(config)

    return {
        "ok": True,
        "mensaje": "Bankroll actualizado correctamente.",
        "configuracion": {
            "bankroll_inicial": bankroll,
        },
    }
