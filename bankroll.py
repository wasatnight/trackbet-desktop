from almacenamiento import (
    cargar_config,
    guardar_config,
)
from calculos import formato_monto
from validaciones import pedir_numero


def validar_bankroll_inicial(bankroll_inicial):
    """Valida que el bankroll inicial sea mayor que cero."""

    try:
        bankroll_inicial = float(bankroll_inicial)
    except (TypeError, ValueError):
        return False

    return bankroll_inicial > 0


def guardar_bankroll_inicial(bankroll_inicial):
    """Guarda el bankroll inicial en la configuración."""

    config = cargar_config()
    config["bankroll_inicial"] = bankroll_inicial
    guardar_config(config)


def configurar_bankroll():
    """Solicita y guarda el bankroll inicial del usuario."""

    bankroll_inicial = pedir_numero("Ingresa tu bankroll inicial: ")

    if not validar_bankroll_inicial(bankroll_inicial):
        print("El bankroll debe ser mayor que cero.")
        return

    guardar_bankroll_inicial(bankroll_inicial)

    print(
        "Bankroll guardado correctamente:",
        formato_monto(bankroll_inicial),
    )
