from math import isclose

from almacenamiento import cargar_apuestas
from almacenamiento_sqlite import cargar_apuestas_sqlite
from calculos import calcular_ganancia_apuesta, formato_dinero, formato_monto


def crear_resumen(apuestas):
    """Crea un resumen financiero de una lista de apuestas."""

    total_stake = 0
    total_ganancia = 0
    total_selecciones = 0
    pendientes = 0

    for apuesta in apuestas:
        try:
            stake = float(apuesta.get("stake", 0))
        except (TypeError, ValueError):
            stake = 0

        resultado = str(apuesta.get("resultado", "pendiente")).strip().lower()

        if resultado == "pendiente":
            pendientes += 1

        total_stake += stake
        total_ganancia += calcular_ganancia_apuesta(apuesta)
        total_selecciones += len(apuesta.get("selecciones", []))

    return {
        "apuestas": len(apuestas),
        "selecciones": total_selecciones,
        "stake": total_stake,
        "ganancia": total_ganancia,
        "pendientes": pendientes,
    }


def mostrar_resumen(nombre, resumen):
    """Muestra un resumen financiero."""

    print(f"\n===== RESUMEN {nombre} =====")
    print("Apuestas:", resumen["apuestas"])
    print("Selecciones:", resumen["selecciones"])
    print("Stake total:", formato_monto(resumen["stake"]))
    print("Ganancia neta:", formato_dinero(resumen["ganancia"]))
    print("Apuestas pendientes:", resumen["pendientes"])


def comparar_resumenes(resumen_json, resumen_sqlite):
    """Compara los resúmenes de JSON y SQLite."""

    print("\n===== COMPARACIÓN =====")

    if resumen_json["apuestas"] == resumen_sqlite["apuestas"]:
        print("Cantidad de apuestas: correcta.")
    else:
        print("Cantidad de apuestas: diferente.")

    if resumen_json["selecciones"] == resumen_sqlite["selecciones"]:
        print("Cantidad de selecciones: correcta.")
    else:
        print("Cantidad de selecciones: diferente.")

    if isclose(
        resumen_json["stake"],
        resumen_sqlite["stake"],
        abs_tol=0.01,
    ):
        print("Stake total: correcto.")
    else:
        print("Stake total: diferente.")

    if isclose(
        resumen_json["ganancia"],
        resumen_sqlite["ganancia"],
        abs_tol=0.01,
    ):
        print("Ganancia neta: correcta.")
    else:
        print("Ganancia neta: diferente.")

    if resumen_json["pendientes"] == resumen_sqlite["pendientes"]:
        print("Apuestas pendientes: correcto.")
    else:
        print("Apuestas pendientes: diferente.")


def verificar_calculos_sqlite():
    """Compara cálculos entre JSON y SQLite."""

    apuestas_json = cargar_apuestas()
    apuestas_sqlite = cargar_apuestas_sqlite()

    resumen_json = crear_resumen(apuestas_json)
    resumen_sqlite = crear_resumen(apuestas_sqlite)

    mostrar_resumen("JSON", resumen_json)
    mostrar_resumen("SQLITE", resumen_sqlite)

    comparar_resumenes(
        resumen_json,
        resumen_sqlite,
    )


if __name__ == "__main__":
    verificar_calculos_sqlite()
