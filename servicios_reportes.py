from almacenamiento import (
    cargar_apuestas,
    cargar_config,
)
from logica_reportes import calcular_resumen_financiero


def obtener_resumen_financiero():
    """Devuelve el resumen financiero actual."""

    apuestas = cargar_apuestas()
    config = cargar_config()

    try:
        bankroll_inicial = float(
            config.get(
                "bankroll_inicial",
                0,
            )
        )
    except (TypeError, ValueError):
        bankroll_inicial = 0

    return calcular_resumen_financiero(
        apuestas,
        bankroll_inicial,
    )
