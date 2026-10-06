from api_trackbet import app
from auditoria_api import (
    generar_resumen_auditoria,
)


def mostrar_resultados():
    """Muestra el inventario y los problemas de la API."""

    resumen = generar_resumen_auditoria(app)

    print("\n===== AUDITORÍA DE LA API =====")

    print(
        "Rutas registradas:",
        resumen["rutas_registradas"],
    )

    print("\n===== INVENTARIO =====")

    for elemento in resumen["inventario"]:
        metodos = ", ".join(elemento["metodos"])

        modelo = elemento["modelo_respuesta"] or "Sin modelo"

        print(f"{metodos:<12} " f"{elemento['ruta']:<55} " f"→ {modelo}")

    print(
        "\nColisiones exactas:",
        len(resumen["colisiones_exactas"]),
    )

    print(
        "Sombras dinámicas:",
        len(resumen["sombras_dinamicas"]),
    )

    print(
        "Rutas sin modelo:",
        len(resumen["rutas_sin_modelo"]),
    )

    print(
        "Métodos no permitidos:",
        len(resumen["metodos_no_permitidos"]),
    )

    print(
        "\nEstado general:",
        ("Correcto" if resumen["estado_correcto"] else "Requiere revisión"),
    )

    if resumen["colisiones_exactas"]:
        print("\nDetalle de colisiones:")

        for problema in resumen["colisiones_exactas"]:
            print("-", problema)

    if resumen["sombras_dinamicas"]:
        print("\nDetalle de sombras dinámicas:")

        for problema in resumen["sombras_dinamicas"]:
            print("-", problema)

    if resumen["rutas_sin_modelo"]:
        print("\nRutas sin modelo:")

        for problema in resumen["rutas_sin_modelo"]:
            print("-", problema)


if __name__ == "__main__":
    mostrar_resultados()
