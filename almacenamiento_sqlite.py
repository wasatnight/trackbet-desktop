import json

from base_datos import conectar_bd


def convertir_a_float(valor, valor_defecto=0):
    """Convierte un valor a float de forma segura."""

    try:
        return float(valor)
    except (TypeError, ValueError):
        return valor_defecto


def cargar_apuestas_sqlite():
    """Carga las apuestas desde SQLite con formato compatible con TrackBet."""

    apuestas = []

    with conectar_bd() as conexion:
        filas_apuestas = conexion.execute("""
            SELECT *
            FROM apuestas
            ORDER BY id
            """).fetchall()

        for fila in filas_apuestas:
            apuesta = {
                "id": fila["id"],
                "fecha": fila["fecha"],
                "casa": fila["casa"],
                "deporte": fila["deporte"],
                "liga": fila["liga"],
                "momento_apuesta": fila["momento_apuesta"],
                "modalidad": fila["modalidad"],
                "tipo_cuota": fila["tipo_cuota"],
                "cuota_texto": fila["cuota_texto"],
                "cuota": fila["cuota"],
                "stake": fila["stake"],
                "resultado": fila["resultado"],
                "selecciones": [],
            }

            if fila["cuota_liquidada"] is not None:
                apuesta["cuota_liquidada"] = fila["cuota_liquidada"]

            if fila["tipo_cuota_liquidada"] is not None:
                apuesta["tipo_cuota_liquidada"] = fila["tipo_cuota_liquidada"]

            if fila["cuota_liquidada_texto"] is not None:
                apuesta["cuota_liquidada_texto"] = fila["cuota_liquidada_texto"]

            if fila["retorno_total_real"] is not None:
                apuesta["retorno_total_real"] = fila["retorno_total_real"]

            filas_selecciones = conexion.execute(
                """
                SELECT *
                FROM selecciones
                WHERE apuesta_id = ?
                ORDER BY numero
                """,
                (fila["id"],),
            ).fetchall()

            for seleccion_fila in filas_selecciones:
                seleccion = {
                    "deporte": seleccion_fila["deporte"],
                    "liga": seleccion_fila["liga"],
                    "evento": seleccion_fila["evento"],
                    "tipo_apuesta": seleccion_fila["tipo_apuesta"],
                    "seleccion": seleccion_fila["seleccion"],
                }

                if seleccion_fila["tipo_cuota_individual"] is not None:
                    seleccion["tipo_cuota_individual"] = seleccion_fila[
                        "tipo_cuota_individual"
                    ]

                if seleccion_fila["cuota_texto_individual"] is not None:
                    seleccion["cuota_texto_individual"] = seleccion_fila[
                        "cuota_texto_individual"
                    ]

                if seleccion_fila["cuota_individual"] is not None:
                    seleccion["cuota_individual"] = seleccion_fila["cuota_individual"]

                if seleccion_fila["resultado_seleccion"] is not None:
                    seleccion["resultado_seleccion"] = seleccion_fila[
                        "resultado_seleccion"
                    ]

                apuesta["selecciones"].append(seleccion)

            apuestas.append(apuesta)

    return apuestas


def guardar_apuestas_sqlite(apuestas):
    """Guarda una lista completa de apuestas en SQLite."""

    with conectar_bd() as conexion:
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


def cargar_config_sqlite():
    """Carga la configuración desde SQLite."""

    config = {}

    with conectar_bd() as conexion:
        filas_config = conexion.execute("""
            SELECT clave, valor
            FROM configuracion
            """).fetchall()

        for fila in filas_config:
            try:
                config[fila["clave"]] = json.loads(fila["valor"])
            except json.JSONDecodeError:
                config[fila["clave"]] = fila["valor"]

    return config


def guardar_config_sqlite(config):
    """Guarda la configuración completa en SQLite."""

    with conectar_bd() as conexion:
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
