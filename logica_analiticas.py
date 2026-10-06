from calculos import (
    calcular_ganancia_apuesta,
    obtener_cuota_decimal,
)

RANGOS_CUOTAS = [
    ("1.01 - 1.49", 1.01, 1.50),
    ("1.50 - 1.79", 1.50, 1.80),
    ("1.80 - 1.99", 1.80, 2.00),
    ("2.00 - 2.49", 2.00, 2.50),
    ("2.50 o más", 2.50, None),
]


def convertir_float(
    valor,
    valor_defecto=0.0,
):
    """Convierte un valor a float de manera segura."""

    try:
        return float(valor)
    except (TypeError, ValueError):
        return valor_defecto


def obtener_rango_cuota(cuota):
    """Devuelve el rango de una cuota decimal."""

    cuota_decimal = convertir_float(cuota)

    for nombre, minimo, maximo in RANGOS_CUOTAS:
        if cuota_decimal >= minimo and (maximo is None or cuota_decimal < maximo):
            return nombre

    return None


def clasificar_muestra(cantidad):
    """Clasifica el tamaño de una muestra histórica."""

    if cantidad < 10:
        return "Muy pequeña"

    if cantidad < 30:
        return "Limitada"

    if cantidad < 100:
        return "Moderada"

    return "Amplia"


def calcular_analisis_cuotas(apuestas):
    """Calcula el rendimiento histórico por rangos de cuotas."""

    rendimiento_rangos = {}

    for nombre, _, _ in RANGOS_CUOTAS:
        rendimiento_rangos[nombre] = {
            "resueltas": 0,
            "ganadas": 0,
            "perdidas": 0,
            "push": 0,
            "stake": 0.0,
            "ganancia": 0.0,
            "suma_cuotas": 0.0,
            "suma_probabilidades": 0.0,
        }

    apuestas_validas = 0

    for apuesta in apuestas:
        resultado = (
            str(
                apuesta.get(
                    "resultado",
                    "pendiente",
                )
            )
            .strip()
            .lower()
        )

        if resultado == "pendiente":
            continue

        cuota = convertir_float(obtener_cuota_decimal(apuesta))

        stake = convertir_float(
            apuesta.get(
                "stake",
                0,
            )
        )

        if cuota <= 1:
            continue

        nombre_rango = obtener_rango_cuota(cuota)

        if nombre_rango is None:
            continue

        datos = rendimiento_rangos[nombre_rango]

        ganancia = convertir_float(calcular_ganancia_apuesta(apuesta))

        datos["resueltas"] += 1
        datos["stake"] += stake
        datos["ganancia"] += ganancia

        if resultado == "ganada":
            datos["ganadas"] += 1
            datos["suma_cuotas"] += cuota
            datos["suma_probabilidades"] += (1 / cuota) * 100

        elif resultado == "perdida":
            datos["perdidas"] += 1
            datos["suma_cuotas"] += cuota
            datos["suma_probabilidades"] += (1 / cuota) * 100

        elif resultado == "push":
            datos["push"] += 1

        apuestas_validas += 1

    rangos = []

    for nombre, _, _ in RANGOS_CUOTAS:
        datos = rendimiento_rangos[nombre]

        if datos["resueltas"] == 0:
            continue

        decididas = datos["ganadas"] + datos["perdidas"]

        if decididas > 0:
            win_rate = (datos["ganadas"] / decididas) * 100

            cuota_promedio = datos["suma_cuotas"] / decididas

            probabilidad_implicita = datos["suma_probabilidades"] / decididas

            diferencia = win_rate - probabilidad_implicita

        else:
            win_rate = 0.0
            cuota_promedio = 0.0
            probabilidad_implicita = 0.0
            diferencia = 0.0

        if datos["stake"] > 0:
            roi = (datos["ganancia"] / datos["stake"]) * 100
        else:
            roi = 0.0

        alertas = []

        if decididas < 10:
            alertas.append(
                "Todavía hay muy pocas apuestas para interpretar este rango."
            )

        elif diferencia > 0 and roi > 0:
            alertas.append(
                "Históricamente has superado el punto de equilibrio en este rango."
            )

        elif diferencia < 0 or roi < 0:
            alertas.append(
                "Históricamente este rango no ha alcanzado el punto de equilibrio."
            )

        rangos.append(
            {
                "rango": nombre,
                "resueltas": datos["resueltas"],
                "decididas": decididas,
                "ganadas": datos["ganadas"],
                "perdidas": datos["perdidas"],
                "push": datos["push"],
                "stake": datos["stake"],
                "ganancia": datos["ganancia"],
                "cuota_promedio": cuota_promedio,
                "win_rate": win_rate,
                "probabilidad_implicita": (probabilidad_implicita),
                "diferencia_equilibrio": diferencia,
                "roi": roi,
                "muestra": clasificar_muestra(decididas),
                "alertas": alertas,
            }
        )

    return {
        "total_apuestas": len(apuestas),
        "apuestas_validas": apuestas_validas,
        "rangos": rangos,
        "nota": (
            "Estos resultados describen el historial "
            "y no garantizan resultados futuros."
        ),
    }


def obtener_cuota_individual_decimal(seleccion):
    """Obtiene la cuota decimal de una selección del parlay."""

    tipo_cuota = (
        str(
            seleccion.get(
                "tipo_cuota_individual",
                "decimal",
            )
        )
        .strip()
        .lower()
    )

    cuota_guardada = convertir_float(
        seleccion.get(
            "cuota_individual",
            0,
        )
    )

    # Las selecciones nuevas ya almacenan la cuota decimal.
    if 1 < cuota_guardada < 100:
        return cuota_guardada

    if tipo_cuota != "americana":
        if cuota_guardada > 1:
            return cuota_guardada

        return 0.0

    cuota_texto = str(
        seleccion.get(
            "cuota_texto_individual",
            cuota_guardada,
        )
    ).strip()

    cuota_texto = cuota_texto.replace(
        "+",
        "",
    )

    cuota_americana = convertir_float(cuota_texto)

    if cuota_americana >= 100:
        return 1 + (cuota_americana / 100)

    if cuota_americana <= -100:
        return 1 + (100 / abs(cuota_americana))

    return 0.0


def clasificar_parlay_por_deportes(apuesta):
    """Clasifica un parlay por cantidad de deportes."""

    deportes = set()

    for seleccion in apuesta.get(
        "selecciones",
        [],
    ):
        deporte = seleccion.get(
            "deporte",
            apuesta.get(
                "deporte",
                "no_registrado",
            ),
        )

        deporte = str(deporte).strip().lower()

        if deporte not in {
            "",
            "no_registrado",
            "no registrado",
            "mixto",
        }:
            deportes.add(deporte)

    deporte_general = (
        str(
            apuesta.get(
                "deporte",
                "",
            )
        )
        .strip()
        .lower()
    )

    if deporte_general == "mixto" or len(deportes) > 1:
        return "Multideporte"

    if len(deportes) == 1:
        return "Un solo deporte"

    return "No clasificado"


def clasificar_parlay_por_eventos(apuesta):
    """Clasifica un parlay según sus eventos."""

    eventos = set()

    for seleccion in apuesta.get(
        "selecciones",
        [],
    ):
        evento = (
            str(
                seleccion.get(
                    "evento",
                    "",
                )
            )
            .strip()
            .lower()
        )

        if evento:
            eventos.add(evento)

    if len(eventos) == 1:
        return "Mismo evento"

    if len(eventos) > 1:
        return "Eventos diferentes"

    return "No clasificado"


def agregar_parlay_a_resumen(
    resumen,
    categoria,
    apuesta,
):
    """Agrega un parlay a una categoría de análisis."""

    if categoria not in resumen:
        resumen[categoria] = {
            "registrados": 0,
            "resueltos": 0,
            "pendientes": 0,
            "ganadas": 0,
            "perdidas": 0,
            "push": 0,
            "stake": 0.0,
            "ganancia": 0.0,
        }

    datos = resumen[categoria]
    datos["registrados"] += 1

    resultado = (
        str(
            apuesta.get(
                "resultado",
                "pendiente",
            )
        )
        .strip()
        .lower()
    )

    if resultado == "pendiente":
        datos["pendientes"] += 1
        return

    if resultado not in {
        "ganada",
        "perdida",
        "push",
    }:
        datos["pendientes"] += 1
        return

    stake = convertir_float(
        apuesta.get(
            "stake",
            0,
        )
    )

    ganancia = convertir_float(calcular_ganancia_apuesta(apuesta))

    datos["resueltos"] += 1
    datos["stake"] += stake
    datos["ganancia"] += ganancia

    if resultado == "ganada":
        datos["ganadas"] += 1

    elif resultado == "perdida":
        datos["perdidas"] += 1

    elif resultado == "push":
        datos["push"] += 1


def completar_resumen_parlays(resumen):
    """Calcula ROI, win rate y tamaño de muestra."""

    resumen_completo = {}

    for categoria, datos in resumen.items():
        decididas = datos["ganadas"] + datos["perdidas"]

        if decididas > 0:
            win_rate = (datos["ganadas"] / decididas) * 100
        else:
            win_rate = 0.0

        if datos["stake"] > 0:
            roi = (datos["ganancia"] / datos["stake"]) * 100
        else:
            roi = 0.0

        resumen_completo[categoria] = {
            **datos,
            "decididas": decididas,
            "win_rate": win_rate,
            "roi": roi,
            "muestra": clasificar_muestra(decididas),
        }

    return resumen_completo


def calcular_analisis_parlays(apuestas):
    """Calcula las analíticas completas de parlays."""

    parlays = [
        apuesta
        for apuesta in apuestas
        if str(
            apuesta.get(
                "modalidad",
                "",
            )
        )
        .strip()
        .lower()
        == "parlay"
    ]

    resumen_piernas = {}
    resumen_deportes = {}
    resumen_eventos = {}

    comparaciones_cuotas = []
    mercados_perdidos = {}
    deportes_perdidos = {}

    resultados_selecciones = {
        "ganadas": 0,
        "perdidas": 0,
        "push": 0,
        "pendientes": 0,
        "sin_resultado": 0,
    }

    for apuesta in parlays:
        selecciones = apuesta.get(
            "selecciones",
            [],
        )

        if not isinstance(
            selecciones,
            list,
        ):
            selecciones = []

        cantidad_selecciones = len(selecciones)

        if cantidad_selecciones == 1:
            categoria_piernas = "1 selección"
        else:
            categoria_piernas = f"{cantidad_selecciones} selecciones"

        agregar_parlay_a_resumen(
            resumen_piernas,
            categoria_piernas,
            apuesta,
        )

        tipo_deportes = clasificar_parlay_por_deportes(apuesta)

        agregar_parlay_a_resumen(
            resumen_deportes,
            tipo_deportes,
            apuesta,
        )

        tipo_eventos = clasificar_parlay_por_eventos(apuesta)

        agregar_parlay_a_resumen(
            resumen_eventos,
            tipo_eventos,
            apuesta,
        )

        for seleccion in selecciones:
            resultado_individual = (
                str(
                    seleccion.get(
                        "resultado_seleccion",
                        "no_registrado",
                    )
                )
                .strip()
                .lower()
            )

            if resultado_individual == "ganada":
                resultados_selecciones["ganadas"] += 1

            elif resultado_individual == "perdida":
                resultados_selecciones["perdidas"] += 1

                mercado = str(
                    seleccion.get(
                        "tipo_apuesta",
                        "No registrado",
                    )
                ).strip()

                deporte = str(
                    seleccion.get(
                        "deporte",
                        apuesta.get(
                            "deporte",
                            "No registrado",
                        ),
                    )
                ).strip()

                mercados_perdidos[mercado] = (
                    mercados_perdidos.get(
                        mercado,
                        0,
                    )
                    + 1
                )

                deportes_perdidos[deporte] = (
                    deportes_perdidos.get(
                        deporte,
                        0,
                    )
                    + 1
                )

            elif resultado_individual == "push":
                resultados_selecciones["push"] += 1

            elif resultado_individual == "pendiente":
                resultados_selecciones["pendientes"] += 1

            else:
                resultados_selecciones["sin_resultado"] += 1

        cuotas_individuales = [
            obtener_cuota_individual_decimal(seleccion) for seleccion in selecciones
        ]

        cuotas_validas = (
            bool(selecciones)
            and len(cuotas_individuales) == len(selecciones)
            and all(cuota > 1 for cuota in cuotas_individuales)
        )

        if cuotas_validas:
            cuota_producto = 1.0

            for cuota_individual in cuotas_individuales:
                cuota_producto *= cuota_individual

            cuota_ofrecida = convertir_float(obtener_cuota_decimal(apuesta))

            cuota_producto = round(
                cuota_producto,
                2,
            )

            cuota_ofrecida = round(
                cuota_ofrecida,
                2,
            )

            if cuota_ofrecida > 1:
                diferencia = ((cuota_ofrecida / cuota_producto) - 1) * 100

                comparaciones_cuotas.append(
                    {
                        "id": apuesta.get("id"),
                        "selecciones": (cantidad_selecciones),
                        "tipo_eventos": (tipo_eventos),
                        "cuota_producto": (cuota_producto),
                        "cuota_ofrecida": (cuota_ofrecida),
                        "diferencia": diferencia,
                    }
                )

    parlays_resueltos = sum(
        1
        for apuesta in parlays
        if str(
            apuesta.get(
                "resultado",
                "",
            )
        )
        .strip()
        .lower()
        in {
            "ganada",
            "perdida",
            "push",
        }
    )

    parlays_pendientes = len(parlays) - parlays_resueltos

    return {
        "total_apuestas": len(apuestas),
        "parlays_registrados": len(parlays),
        "parlays_resueltos": parlays_resueltos,
        "parlays_pendientes": parlays_pendientes,
        "rendimiento_piernas": (completar_resumen_parlays(resumen_piernas)),
        "rendimiento_deportes": (completar_resumen_parlays(resumen_deportes)),
        "rendimiento_eventos": (completar_resumen_parlays(resumen_eventos)),
        "resultados_selecciones": (resultados_selecciones),
        "mercados_perdidos": (mercados_perdidos),
        "deportes_perdidos": (deportes_perdidos),
        "comparaciones_cuotas": (comparaciones_cuotas),
        "nota": ("Una muestra pequeña no permite " "obtener conclusiones confiables."),
    }
