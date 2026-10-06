from api_trackbet import app
from auditoria_modelos_api import (
    generar_resumen_auditoria_modelos,
)


def mostrar_lista(
    titulo,
    elementos,
):
    """Muestra una lista de hallazgos."""

    print(f"\n{titulo}: {len(elementos)}")

    for elemento in elementos:
        print("-", elemento)


def mostrar_revision_modelos():
    """Muestra la auditoría de modelos de la API."""

    resumen = generar_resumen_auditoria_modelos(app)

    print("\n===== AUDITORÍA DE MODELOS API =====")

    print(
        "Modelos de entrada revisados:",
        resumen["modelos_entrada_revisados"],
    )

    print(
        "Modelos de respuesta revisados:",
        resumen["modelos_respuesta_revisados"],
    )

    mostrar_lista(
        "Entradas sin extra='forbid'",
        resumen["entradas_sin_extra_forbid"],
    )

    mostrar_lista(
        "Salidas con extra='allow'",
        resumen["salidas_con_extra_allow"],
    )

    mostrar_lista(
        "Campos Any en entradas",
        resumen["campos_any_en_entradas"],
    )

    mostrar_lista(
        "Campos internos en respuestas",
        resumen["campos_internos_en_salidas"],
    )

    mostrar_lista(
        "Validación de NaN/infinito pendiente",
        resumen["validacion_no_finitos_pendiente"],
    )

    print(
        "\nErrores encontrados:",
        resumen["errores_encontrados"],
    )

    print(
        "Recomendaciones:",
        resumen["recomendaciones_encontradas"],
    )

    print(
        "\nEstado de contratos:",
        ("Correcto" if resumen["estado_correcto"] else "Requiere revisión"),
    )


if __name__ == "__main__":
    mostrar_revision_modelos()
