from almacenamiento import cargar_apuestas
from logica_analiticas import (
    calcular_analisis_cuotas,
    calcular_analisis_parlays,
)


def obtener_analisis_cuotas():
    """Devuelve el análisis actual por rangos de cuotas."""

    apuestas = cargar_apuestas()

    return calcular_analisis_cuotas(apuestas)


def obtener_analisis_parlays():
    """Devuelve el análisis actual de los parlays."""

    apuestas = cargar_apuestas()

    return calcular_analisis_parlays(apuestas)
