from almacenamiento import (
    cargar_apuestas,
    cargar_config,
)
from logica_estadisticas import calcular_estadisticas


def obtener_estadisticas():
    """Devuelve las estadísticas actuales de la aplicación."""

    apuestas = cargar_apuestas()
    config = cargar_config()

    bankroll_inicial = config.get(
        "bankroll_inicial",
        0,
    )

    return calcular_estadisticas(
        apuestas,
        bankroll_inicial,
    )
