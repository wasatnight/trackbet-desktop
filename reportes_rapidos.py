from diagnostico import (
    exportar_diagnostico_txt,
    mostrar_diagnostico,
)
from exportaciones_reportes import (
    exportar_todos_los_reportes,
    mostrar_reportes_exportados,
)
from pendientes import mostrar_apuestas_pendientes
from resumen_financiero import (
    exportar_resumen_financiero_txt,
    mostrar_resumen_financiero,
)
from vistas_rapidas import mostrar_menu_vistas_rapidas


def mostrar_menu_reportes_rapidos():
    """Muestra el menú de reportes rápidos."""

    while True:
        print("\n===== REPORTES RÁPIDOS =====")
        print("1. Vistas por resultado")
        print("2. Ver apuestas pendientes")
        print("3. Resumen financiero")
        print("4. Diagnóstico del sistema")
        print("5. Exportar diagnóstico a TXT")
        print("6. Exportar resumen financiero a TXT")
        print("7. Exportar todos los reportes")
        print("8. Ver reportes exportados")
        print("9. Volver al menú principal")

        opcion = input("Elige una opción: ").strip()

        if opcion == "1":
            mostrar_menu_vistas_rapidas()

        elif opcion == "2":
            mostrar_apuestas_pendientes()

        elif opcion == "3":
            mostrar_resumen_financiero()

        elif opcion == "4":
            mostrar_diagnostico()

        elif opcion == "5":
            exportar_diagnostico_txt()

        elif opcion == "6":
            exportar_resumen_financiero_txt()

        elif opcion == "7":
            exportar_todos_los_reportes()

        elif opcion == "8":
            mostrar_reportes_exportados()

        elif opcion == "9":
            return

        else:
            print("Opción no válida.")
