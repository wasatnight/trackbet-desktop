from datetime import datetime
from pathlib import Path

from calculos import (
    formato_dinero,
    formato_monto,
)
from servicios_reportes import obtener_resumen_financiero


def mostrar_resumen_financiero():
    """Muestra el resumen financiero general."""

    resumen = obtener_resumen_financiero()

    print("\n===== RESUMEN FINANCIERO =====")
    print(
        "Bankroll inicial:",
        formato_monto(resumen["bankroll_inicial"]),
    )
    print(
        "Ganancia neta:",
        formato_dinero(resumen["ganancia_neta"]),
    )
    print(
        "Bankroll actual estimado:",
        formato_monto(resumen["bankroll_actual"]),
    )
    print(
        "Stake total:",
        formato_monto(resumen["stake_total"]),
    )
    print(
        "Stake resuelto:",
        formato_monto(resumen["stake_resuelto"]),
    )
    print(
        "Stake pendiente:",
        formato_monto(resumen["stake_pendiente"]),
    )
    print(
        "ROI:",
        f"{resumen['roi']:.2f}%",
    )
    print(
        "Apuestas totales:",
        resumen["apuestas_totales"],
    )
    print(
        "Apuestas resueltas:",
        resumen["apuestas_resueltas"],
    )
    print(
        "Apuestas pendientes:",
        resumen["apuestas_pendientes"],
    )


def generar_texto_resumen_financiero():
    """Genera el resumen financiero en formato de texto."""

    resumen = obtener_resumen_financiero()

    lineas = [
        "===== RESUMEN FINANCIERO =====",
        f"Bankroll inicial: {formato_monto(resumen['bankroll_inicial'])}",
        f"Ganancia neta: {formato_dinero(resumen['ganancia_neta'])}",
        f"Bankroll actual estimado: {formato_monto(resumen['bankroll_actual'])}",
        f"Stake total: {formato_monto(resumen['stake_total'])}",
        f"Stake resuelto: {formato_monto(resumen['stake_resuelto'])}",
        f"Stake pendiente: {formato_monto(resumen['stake_pendiente'])}",
        f"ROI: {resumen['roi']:.2f}%",
        f"Apuestas totales: {resumen['apuestas_totales']}",
        f"Apuestas resueltas: {resumen['apuestas_resueltas']}",
        f"Apuestas pendientes: {resumen['apuestas_pendientes']}",
    ]

    return "\n".join(lineas)


def exportar_resumen_financiero_txt():
    """Exporta el resumen financiero a un archivo TXT."""

    carpeta = Path("reportes")
    carpeta.mkdir(exist_ok=True)

    fecha = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    ruta_archivo = carpeta / f"resumen_financiero_trackbet_{fecha}.txt"

    texto = generar_texto_resumen_financiero()

    with open(ruta_archivo, "w", encoding="utf-8") as archivo:
        archivo.write(texto)

    print("\nResumen financiero exportado correctamente.")
    print("Archivo:", ruta_archivo)
