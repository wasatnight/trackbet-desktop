# @author:Wasatnight(Ivan Solano)
# Idea de TrackBet para el publico latinoamericano, una aplicacion de consola, despues pagina web HTML y Apps de celular, para registrar apuestas deportivas, ver historial y estadisticas.

from base_datos import crear_tablas
from configuracion_app import NOMBRE_APP
from reportes_rapidos import mostrar_menu_reportes_rapidos
from pendientes import cerrar_apuesta_pendiente
from almacenamiento import asignar_ids_faltantes
from menus import mostrar_menu

from registro import registrar_apuesta
from historial import mostrar_historial
from busquedas import buscar_apuestas
from edicion import editar_apuesta
from eliminacion import eliminar_apuesta
from bankroll import configurar_bankroll
from respaldar_sqlite_a_json import respaldar_sqlite_a_json

from reportes import exportar_apuestas_csv
from estadisticas import mostrar_estadisticas
from analiticas import mostrar_menu_analiticas


# Funcion que muestra el menu principal y da opciones para registrar las apuestas, ver el historial y las estadisticas o salir del programa.
def app():
    while True:
        mostrar_menu()
        opcion = input("Elige una opción: ").strip()

        if opcion == "1":
            registrar_apuesta()

        elif opcion == "2":
            mostrar_historial()

        elif opcion == "3":
            mostrar_estadisticas()

        elif opcion == "4":
            configurar_bankroll()

        elif opcion == "5":
            exportar_apuestas_csv()

        elif opcion == "6":
            buscar_apuestas()

        elif opcion == "7":
            editar_apuesta()

        elif opcion == "8":
            eliminar_apuesta()

        elif opcion == "9":
            mostrar_menu_analiticas()

        elif opcion == "10":
            respaldar_sqlite_a_json()

        elif opcion == "11":
            cerrar_apuesta_pendiente()

        elif opcion == "12":
            mostrar_menu_reportes_rapidos()

        elif opcion == "13":
            print(f"Gracias por usar {NOMBRE_APP}.")
            break


if __name__ == "__main__":
    crear_tablas()
    asignar_ids_faltantes()
    app()
