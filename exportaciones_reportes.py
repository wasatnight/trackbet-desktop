from pathlib import Path

from diagnostico import exportar_diagnostico_txt
from resumen_financiero import exportar_resumen_financiero_txt


def exportar_todos_los_reportes():
    """Exporta todos los reportes disponibles."""

    print("\n===== EXPORTAR TODOS LOS REPORTES =====")

    exportar_diagnostico_txt()
    exportar_resumen_financiero_txt()

    print("\nTodos los reportes fueron exportados correctamente.")


def obtener_reportes_exportados():
    """Devuelve una lista de reportes TXT exportados."""

    carpeta = Path("reportes")

    if not carpeta.exists():
        return []

    reportes = sorted(
        carpeta.glob("*.txt"),
        key=lambda archivo: archivo.stat().st_mtime,
        reverse=True,
    )

    return reportes


def mostrar_reportes_exportados():
    """Muestra los reportes exportados disponibles."""

    reportes = obtener_reportes_exportados()

    if not reportes:
        print("\nNo hay reportes exportados todavía.")
        return

    print("\n===== REPORTES EXPORTADOS =====")

    for indice, reporte in enumerate(reportes, start=1):
        tamano_kb = reporte.stat().st_size / 1024

        print(f"{indice}. {reporte.name} " f"({tamano_kb:.2f} KB)")
    print("=" * 40)
