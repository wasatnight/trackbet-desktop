from almacenamiento import (
    cargar_apuestas,
    cargar_config,
)
from almacenamiento_sqlite import (
    cargar_apuestas_sqlite,
    cargar_config_sqlite,
)


def verificar_sqlite():
    """Compara JSON contra SQLite sin modificar datos."""

    apuestas_json = cargar_apuestas()
    apuestas_sqlite = cargar_apuestas_sqlite()

    config_json = cargar_config()
    config_sqlite = cargar_config_sqlite()

    print("\n===== VERIFICACIÓN SQLITE =====")

    print("Apuestas en JSON:", len(apuestas_json))
    print("Apuestas en SQLite:", len(apuestas_sqlite))

    selecciones_json = sum(
        len(apuesta.get("selecciones", [])) for apuesta in apuestas_json
    )

    selecciones_sqlite = sum(
        len(apuesta.get("selecciones", [])) for apuesta in apuestas_sqlite
    )

    print("Selecciones en JSON:", selecciones_json)
    print("Selecciones en SQLite:", selecciones_sqlite)

    print("Config JSON:", config_json)
    print("Config SQLite:", config_sqlite)

    if len(apuestas_json) == len(apuestas_sqlite):
        print("\nCantidad de apuestas correcta.")
    else:
        print("\nDiferencia en cantidad de apuestas.")

    if selecciones_json == selecciones_sqlite:
        print("Cantidad de selecciones correcta.")
    else:
        print("Diferencia en cantidad de selecciones.")

    if config_json == config_sqlite:
        print("Configuración correcta.")
    else:
        print("Diferencia en configuración.")

    if apuestas_sqlite:
        ultima_apuesta = apuestas_sqlite[-1]

        print("\n===== ÚLTIMA APUESTA CARGADA DESDE SQLITE =====")
        print("ID:", ultima_apuesta.get("id"))
        print("Fecha:", ultima_apuesta.get("fecha"))
        print("Casa:", ultima_apuesta.get("casa"))
        print("Deporte:", ultima_apuesta.get("deporte"))
        print("Liga:", ultima_apuesta.get("liga"))
        print("Modalidad:", ultima_apuesta.get("modalidad"))
        print("Resultado:", ultima_apuesta.get("resultado"))
        print(
            "Selecciones:",
            len(ultima_apuesta.get("selecciones", [])),
        )


if __name__ == "__main__":
    verificar_sqlite()
