from math import isclose

from almacenamiento import (
    cargar_apuestas,
    cargar_config,
)
from almacenamiento_sqlite import (
    cargar_apuestas_sqlite,
    cargar_config_sqlite,
    guardar_apuestas_sqlite,
    guardar_config_sqlite,
)
from calculos import (
    calcular_ganancia_apuesta,
    formato_dinero,
    formato_monto,
)


def crear_resumen(apuestas):
    """Crea un resumen financiero de las apuestas."""

    total_stake = 0
    total_ganancia = 0
    total_selecciones = 0

    for apuesta in apuestas:
        try:
            stake = float(apuesta.get("stake", 0))
        except (TypeError, ValueError):
            stake = 0

        total_stake += stake
        total_ganancia += calcular_ganancia_apuesta(apuesta)
        total_selecciones += len(apuesta.get("selecciones", []))

    return {
        "apuestas": len(apuestas),
        "selecciones": total_selecciones,
        "stake": total_stake,
        "ganancia": total_ganancia,
    }


def comparar_resumenes(resumen_json, resumen_sqlite):
    """Compara los datos guardados y leídos desde SQLite."""

    pruebas_correctas = 0
    pruebas_fallidas = 0

    comparaciones = [
        (
            "Cantidad de apuestas",
            resumen_json["apuestas"],
            resumen_sqlite["apuestas"],
        ),
        (
            "Cantidad de selecciones",
            resumen_json["selecciones"],
            resumen_sqlite["selecciones"],
        ),
    ]

    for nombre, esperado, obtenido in comparaciones:
        if esperado == obtenido:
            print(f"[CORRECTO] {nombre}: {obtenido}")
            pruebas_correctas += 1
        else:
            print(f"[ERROR] {nombre}")
            print("Esperado:", esperado)
            print("Obtenido:", obtenido)
            pruebas_fallidas += 1

    comparaciones_numericas = [
        (
            "Stake total",
            resumen_json["stake"],
            resumen_sqlite["stake"],
        ),
        (
            "Ganancia neta",
            resumen_json["ganancia"],
            resumen_sqlite["ganancia"],
        ),
    ]

    for nombre, esperado, obtenido in comparaciones_numericas:
        if isclose(esperado, obtenido, abs_tol=0.01):
            print(
                f"[CORRECTO] {nombre}:",
                (
                    formato_monto(obtenido)
                    if nombre == "Stake total"
                    else formato_dinero(obtenido)
                ),
            )
            pruebas_correctas += 1
        else:
            print(f"[ERROR] {nombre}")
            print("Esperado:", esperado)
            print("Obtenido:", obtenido)
            pruebas_fallidas += 1

    return pruebas_correctas, pruebas_fallidas


def probar_guardado_sqlite():
    """Prueba guardar datos en SQLite y leerlos nuevamente."""

    apuestas_json = cargar_apuestas()
    config_json = cargar_config()

    guardar_apuestas_sqlite(apuestas_json)
    guardar_config_sqlite(config_json)

    apuestas_sqlite = cargar_apuestas_sqlite()
    config_sqlite = cargar_config_sqlite()

    resumen_json = crear_resumen(apuestas_json)
    resumen_sqlite = crear_resumen(apuestas_sqlite)

    print("\n===== PRUEBA DE GUARDADO SQLITE =====")
    print("Apuestas JSON:", resumen_json["apuestas"])
    print("Apuestas SQLite:", resumen_sqlite["apuestas"])
    print("Selecciones JSON:", resumen_json["selecciones"])
    print("Selecciones SQLite:", resumen_sqlite["selecciones"])

    pruebas_correctas, pruebas_fallidas = comparar_resumenes(
        resumen_json,
        resumen_sqlite,
    )

    if config_json == config_sqlite:
        print("[CORRECTO] Configuración SQLite")
        pruebas_correctas += 1
    else:
        print("[ERROR] Configuración SQLite")
        print("JSON:", config_json)
        print("SQLite:", config_sqlite)
        pruebas_fallidas += 1

    print("\n" + "=" * 45)
    print("Pruebas correctas:", pruebas_correctas)
    print("Pruebas fallidas:", pruebas_fallidas)
    print("=" * 45)

    if pruebas_fallidas == 0:
        print("\nGuardado y lectura SQLite correctos.")
    else:
        print("\nHay diferencias entre JSON y SQLite.")
        raise SystemExit(1)


if __name__ == "__main__":
    probar_guardado_sqlite()
