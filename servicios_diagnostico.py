from pathlib import Path

from diagnostico import obtener_resumen_diagnostico


def obtener_fecha_ultimo_respaldo(
    ultimo_respaldo,
):
    """Devuelve la fecha del respaldo sin exponer su ruta."""

    if ultimo_respaldo is None:
        return None

    try:
        ruta = Path(ultimo_respaldo)

        fecha_modificacion = ruta.stat().st_mtime

        from datetime import datetime

        return datetime.fromtimestamp(fecha_modificacion).isoformat(timespec="seconds")

    except (
        OSError,
        TypeError,
        ValueError,
    ):
        return None


def obtener_diagnostico_sistema():
    """Devuelve un diagnóstico seguro para la API."""

    resumen = obtener_resumen_diagnostico()

    problemas = resumen.get(
        "problemas_integridad",
        [],
    )

    ultimo_respaldo = resumen.get("ultimo_respaldo")

    return {
        "nombre_app": resumen.get(
            "nombre_app",
            "",
        ),
        "version_app": resumen.get(
            "version_app",
            "",
        ),
        "estado_general": resumen.get(
            "estado_general",
            "Requiere revisión",
        ),
        "almacenamiento": resumen.get(
            "almacenamiento",
            "",
        ),
        "tamano_base_datos": resumen.get(
            "tamano_base_datos",
            0,
        ),
        "tamano_base_datos_formateado": (
            resumen.get(
                "tamano_base_datos_formateado",
                "0 B",
            )
        ),
        "tablas_validas": resumen.get(
            "tablas_validas",
            False,
        ),
        "tablas_faltantes": resumen.get(
            "tablas_faltantes",
            [],
        ),
        "base_datos_sqlite": resumen.get(
            "base_datos_sqlite",
            False,
        ),
        "apuestas_registradas": resumen.get(
            "apuestas_registradas",
            0,
        ),
        "selecciones_registradas": resumen.get(
            "selecciones_registradas",
            0,
        ),
        "bankroll_inicial": resumen.get(
            "bankroll_inicial",
            0.0,
        ),
        "ganancia_neta": resumen.get(
            "ganancia_neta",
            0.0,
        ),
        "bankroll_actual": resumen.get(
            "bankroll_actual",
            0.0,
        ),
        "apuestas_pendientes": resumen.get(
            "apuestas_pendientes",
            0,
        ),
        "stake_pendiente": resumen.get(
            "stake_pendiente",
            0.0,
        ),
        "ultimo_respaldo_disponible": (ultimo_respaldo is not None),
        "ultimo_respaldo_fecha": (obtener_fecha_ultimo_respaldo(ultimo_respaldo)),
        "problemas_integridad": problemas,
        "cantidad_problemas_integridad": len(problemas),
    }
