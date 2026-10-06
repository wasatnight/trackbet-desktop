import json

from almacenamiento import (
    cargar_apuestas,
    cargar_config,
)
from base_datos import (
    conectar_bd,
    crear_tablas,
)


def convertir_a_float(valor, valor_defecto=0):
    """Convierte un valor a float de forma segura."""

    try:
        return float(valor)
    except (TypeError, ValueError):
        return valor_defecto


def migrar_apuestas(conexion, apuestas):
    """Migra las apuestas y sus selecciones a SQLite."""

    conexion.execute("DELETE FROM selecciones")
    conexion.execute("DELETE FROM apuestas")

    for indice, apuesta in enumerate(
        apuestas,
        start=1,
    ):
        apuesta_id = apuesta.get(
            "id",
            indice,
        )

        conexion.execute(
            """
            INSERT INTO apuestas (
                id,
                fecha,
                casa,
                deporte,
                liga,
                momento_apuesta,
                modalidad,
                tipo_cuota,
                cuota_texto,
                cuota,
                stake,
                resultado,
                cuota_liquidada,
                tipo_cuota_liquidada,
                cuota_liquidada_texto,
                retorno_total_real
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                apuesta_id,
                apuesta.get("fecha", "No registrada"),
                apuesta.get("casa", "No registrada"),
                apuesta.get("deporte", "No registrado"),
                apuesta.get("liga", "No registrada"),
                apuesta.get(
                    "momento_apuesta",
                    "no_registrado",
                ),
                apuesta.get("modalidad", "straight"),
                apuesta.get("tipo_cuota", "decimal"),
                str(
                    apuesta.get(
                        "cuota_texto",
                        apuesta.get("cuota", "0"),
                    )
                ),
                convertir_a_float(apuesta.get("cuota", 0)),
                convertir_a_float(apuesta.get("stake", 0)),
                apuesta.get("resultado", "pendiente"),
                (
                    convertir_a_float(apuesta.get("cuota_liquidada"))
                    if apuesta.get("cuota_liquidada") is not None
                    else None
                ),
                apuesta.get("tipo_cuota_liquidada"),
                apuesta.get("cuota_liquidada_texto"),
                (
                    convertir_a_float(apuesta.get("retorno_total_real"))
                    if apuesta.get("retorno_total_real") is not None
                    else None
                ),
            ),
        )

        for numero, seleccion in enumerate(
            apuesta.get("selecciones", []),
            start=1,
        ):
            conexion.execute(
                """
                INSERT INTO selecciones (
                    apuesta_id,
                    numero,
                    deporte,
                    liga,
                    evento,
                    tipo_apuesta,
                    seleccion,
                    tipo_cuota_individual,
                    cuota_texto_individual,
                    cuota_individual,
                    resultado_seleccion
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    apuesta_id,
                    numero,
                    seleccion.get(
                        "deporte",
                        apuesta.get(
                            "deporte",
                            "No registrado",
                        ),
                    ),
                    seleccion.get(
                        "liga",
                        apuesta.get(
                            "liga",
                            "No registrada",
                        ),
                    ),
                    seleccion.get(
                        "evento",
                        "No registrado",
                    ),
                    seleccion.get(
                        "tipo_apuesta",
                        "No registrado",
                    ),
                    seleccion.get(
                        "seleccion",
                        "No registrada",
                    ),
                    seleccion.get("tipo_cuota_individual"),
                    seleccion.get("cuota_texto_individual"),
                    (
                        convertir_a_float(seleccion.get("cuota_individual"))
                        if seleccion.get("cuota_individual") is not None
                        else None
                    ),
                    seleccion.get(
                        "resultado_seleccion",
                        "no_registrado",
                    ),
                ),
            )


def migrar_configuracion(conexion, config):
    """Migra la configuración a SQLite."""

    conexion.execute("DELETE FROM configuracion")

    for clave, valor in config.items():
        conexion.execute(
            """
            INSERT INTO configuracion (
                clave,
                valor
            )
            VALUES (?, ?)
            """,
            (
                clave,
                json.dumps(
                    valor,
                    ensure_ascii=False,
                ),
            ),
        )


def contar_registros(conexion):
    """Muestra cuántos registros quedaron en SQLite."""

    total_apuestas = conexion.execute("SELECT COUNT(*) FROM apuestas").fetchone()[0]

    total_selecciones = conexion.execute("SELECT COUNT(*) FROM selecciones").fetchone()[
        0
    ]

    total_config = conexion.execute("SELECT COUNT(*) FROM configuracion").fetchone()[0]

    print("\n===== MIGRACIÓN COMPLETADA =====")
    print("Apuestas migradas:", total_apuestas)
    print("Selecciones migradas:", total_selecciones)
    print("Configuraciones migradas:", total_config)


def migrar_json_a_sqlite():
    """Migra apuestas.json y config.json hacia TrackBet."""

    crear_tablas()

    apuestas = cargar_apuestas()
    config = cargar_config()

    with conectar_bd() as conexion:
        migrar_apuestas(
            conexion,
            apuestas,
        )
        migrar_configuracion(
            conexion,
            config,
        )
        contar_registros(conexion)


if __name__ == "__main__":
    migrar_json_a_sqlite()
