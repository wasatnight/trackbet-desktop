"""Funciones de cálculo y formato financiero de TrackBet."""


def formato_dinero(cantidad):
    """Formatea ganancias y pérdidas usando signo positivo o negativo."""

    if cantidad > 0:
        return f"+${cantidad:.2f}"

    if cantidad < 0:
        return f"-${abs(cantidad):.2f}"

    return "$0.00"


def formato_monto(cantidad):
    """Formatea cantidades normales de dinero sin agregar signo positivo."""

    return f"${cantidad:.2f}"


def convertir_cuota_a_decimal(tipo_cuota, cuota_texto):
    """Convierte una cuota decimal o americana a decimal."""

    tipo_cuota = str(tipo_cuota).strip().lower()

    try:
        valor = float(str(cuota_texto).strip().replace("+", ""))
    except (TypeError, ValueError):
        return 0

    if tipo_cuota == "decimal":
        if valor > 1:
            return valor

        return 0

    if tipo_cuota == "americana":
        if valor > 0:
            return 1 + (valor / 100)

        if valor < 0:
            return 1 + (100 / abs(valor))

    return 0


def obtener_cuota_decimal(apuesta):
    """Obtiene la cuota decimal general de una apuesta."""

    tipo_cuota = str(apuesta.get("tipo_cuota", "decimal")).strip().lower()

    try:
        cuota_guardada = float(apuesta.get("cuota", 0))
    except (TypeError, ValueError):
        cuota_guardada = 0

    if tipo_cuota != "americana":
        if cuota_guardada > 1:
            return cuota_guardada

        return 0

    cuota_texto = str(apuesta.get("cuota_texto", "")).strip()

    try:
        cuota_americana = float(cuota_texto.replace("+", ""))
    except (TypeError, ValueError):
        cuota_americana = 0

    if abs(cuota_americana) >= 100:
        return convertir_cuota_a_decimal(
            "americana",
            cuota_americana,
        )

    # Algunas apuestas nuevas ya guardan
    # la conversión decimal en "cuota".
    if cuota_guardada > 1:
        return cuota_guardada

    return 0


def convertir_decimal_a_americana(cuota_decimal):
    """Convierte una cuota decimal a su equivalente americano."""

    try:
        cuota_decimal = float(cuota_decimal)
    except (TypeError, ValueError):
        return None

    if cuota_decimal <= 1:
        return None

    if cuota_decimal >= 2:
        cuota_americana = (cuota_decimal - 1) * 100

        return f"+{round(cuota_americana)}"

    cuota_americana = -100 / (cuota_decimal - 1)

    return str(round(cuota_americana))


def formatear_cuota_dual(cuota_decimal, decimales=2):
    """Muestra una cuota en formato decimal y americano."""

    try:
        cuota_decimal = float(cuota_decimal)
    except (TypeError, ValueError):
        return "Cuota no válida"

    if cuota_decimal <= 1:
        return "Cuota no válida"

    cuota_americana = convertir_decimal_a_americana(cuota_decimal)

    return f"{cuota_decimal:.{decimales}f} decimal / " f"{cuota_americana} americana"


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

    try:
        cuota_guardada = float(seleccion.get("cuota_individual", 0))
    except (TypeError, ValueError):
        cuota_guardada = 0

    if tipo_cuota != "americana":
        if cuota_guardada > 1:
            return cuota_guardada

        return 0

    cuota_texto = str(
        seleccion.get(
            "cuota_texto_individual",
            "",
        )
    ).strip()

    try:
        cuota_americana = float(cuota_texto.replace("+", ""))
    except (TypeError, ValueError):
        cuota_americana = 0

    if abs(cuota_americana) >= 100:
        return convertir_cuota_a_decimal(
            "americana",
            cuota_americana,
        )

    # Las selecciones nuevas ya guardan
    # su conversión decimal.
    if cuota_guardada > 1:
        return cuota_guardada

    return 0


def calcular_cuota_liquidada_parlay(apuesta):
    """
    Calcula la cuota efectiva de un parlay
    cuando una o más selecciones terminan en push.
    """

    # Permite guardar manualmente la cuota final
    # aplicada por la casa de apuestas.
    try:
        cuota_manual = float(apuesta.get("cuota_liquidada", 0))
    except (TypeError, ValueError):
        cuota_manual = 0

    if cuota_manual > 1:
        return cuota_manual

    cuota_original = obtener_cuota_decimal(apuesta)
    selecciones = apuesta.get("selecciones", [])

    if not selecciones:
        return cuota_original

    resultados = [
        str(
            seleccion.get(
                "resultado_seleccion",
                "no_registrado",
            )
        )
        .strip()
        .lower()
        for seleccion in selecciones
    ]

    # Sin push se conserva la cuota original.
    if "push" not in resultados:
        return cuota_original

    # No se recalcula mientras existan
    # selecciones pendientes o sin resultado.
    if any(resultado not in ("ganada", "push") for resultado in resultados):
        return cuota_original

    cuota_liquidada = 1.0
    cantidad_ganadas = 0

    for seleccion in selecciones:
        resultado = (
            str(
                seleccion.get(
                    "resultado_seleccion",
                    "no_registrado",
                )
            )
            .strip()
            .lower()
        )

        # Una selección push se elimina
        # del cálculo de la cuota.
        if resultado == "push":
            continue

        cuota_individual = obtener_cuota_individual_decimal(seleccion)

        # Si falta una cuota individual,
        # conservamos la cuota original.
        if cuota_individual <= 1:
            return cuota_original

        cuota_liquidada *= cuota_individual
        cantidad_ganadas += 1

    # Si todas las selecciones fueron push,
    # se devuelve el stake completo.
    if cantidad_ganadas == 0:
        return 1.0

    return cuota_liquidada


def calcular_ganancia_apuesta(apuesta):
    """Calcula la ganancia o pérdida neta de una apuesta."""

    try:
        stake = float(apuesta.get("stake", 0))
    except (TypeError, ValueError):
        return 0

    resultado = str(apuesta.get("resultado", "pendiente")).strip().lower()

    if resultado == "pendiente":
        return 0

    # El retorno realmente pagado por la casa
    # tiene prioridad sobre cualquier cálculo de cuotas.
    retorno_total_real = apuesta.get("retorno_total_real")

    if retorno_total_real is not None:
        try:
            retorno_total_real = float(retorno_total_real)
        except (TypeError, ValueError):
            retorno_total_real = None

        if retorno_total_real is not None:
            return retorno_total_real - stake

    if resultado == "perdida":
        return -stake

    if resultado == "push":
        return 0

    if resultado != "ganada":
        return 0

    modalidad = str(apuesta.get("modalidad", "straight")).strip().lower()

    if modalidad == "parlay":
        cuota_decimal = calcular_cuota_liquidada_parlay(apuesta)
    else:
        cuota_decimal = obtener_cuota_decimal(apuesta)

    if cuota_decimal <= 1:
        return 0

    return stake * (cuota_decimal - 1)
