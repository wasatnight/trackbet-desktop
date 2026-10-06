from almacenamiento import (
    cargar_apuestas,
    guardar_apuestas,
)
from parlays import calcular_resultado_general_parlay
from validaciones import normalizar_texto
from datetime import datetime

from calculos import convertir_cuota_a_decimal
from copy import deepcopy

RESULTADOS_VALIDOS = {
    "ganada",
    "perdida",
    "push",
    "pendiente",
}


def normalizar_resultado(resultado):
    """Normaliza el resultado de una apuesta."""

    return str(resultado).strip().lower()


def listar_apuestas():
    """Devuelve todas las apuestas registradas."""

    return cargar_apuestas()


def obtener_apuesta_por_id(id_apuesta):
    """Busca una apuesta por ID."""

    apuestas = cargar_apuestas()

    try:
        id_buscado = int(id_apuesta)
    except (TypeError, ValueError):
        return None

    for apuesta in apuestas:
        if apuesta.get("id") == id_buscado:
            return apuesta

    return None


def obtener_siguiente_id(apuestas):
    """Calcula el siguiente ID disponible."""

    ids_existentes = [
        apuesta.get("id", 0)
        for apuesta in apuestas
        if isinstance(
            apuesta.get("id", 0),
            int,
        )
    ]

    return max(ids_existentes, default=0) + 1


def formatear_cuota_texto_entrada(
    tipo_cuota,
    cuota,
):
    """Convierte la cuota recibida en su texto original."""

    tipo_normalizado = str(tipo_cuota).strip().lower()

    valor = float(cuota)

    if tipo_normalizado == "americana":
        if valor.is_integer():
            return f"{int(valor):+d}"

        return f"{valor:+g}"

    return f"{valor:g}"


def construir_apuesta_straight(
    datos,
    id_apuesta,
    fecha=None,
):
    """Construye una apuesta straight sin guardarla."""

    if hasattr(datos, "model_dump"):
        datos = datos.model_dump()

    if fecha is None:
        fecha = datetime.now().strftime("%d/%m/%Y")

    tipo_cuota = str(datos["tipo_cuota"]).strip().lower()

    cuota_texto = formatear_cuota_texto_entrada(
        tipo_cuota,
        datos["cuota"],
    )

    cuota_decimal = convertir_cuota_a_decimal(
        tipo_cuota,
        cuota_texto,
    )

    deporte = str(datos["deporte"]).strip()

    liga = str(datos["liga"]).strip()

    seleccion_straight = {
        "deporte": deporte,
        "liga": liga,
        "evento": str(datos["evento"]).strip(),
        "tipo_apuesta": str(datos["mercado"]).strip(),
        "seleccion": str(datos["seleccion"]).strip(),
    }

    return {
        "fecha": fecha,
        "casa": str(datos["casa"]).strip(),
        "deporte": deporte,
        "liga": liga,
        "momento_apuesta": str(
            datos.get(
                "momento_apuesta",
                "prepartido",
            )
        )
        .strip()
        .lower(),
        "modalidad": "straight",
        "selecciones": [seleccion_straight],
        "tipo_cuota": tipo_cuota,
        "cuota_texto": cuota_texto,
        "cuota": cuota_decimal,
        "stake": float(datos["stake"]),
        "resultado": "pendiente",
        "id": int(id_apuesta),
    }


def construir_apuesta_parlay(
    datos,
    id_apuesta,
    fecha=None,
):
    """Construye una apuesta parlay sin guardarla."""

    if hasattr(datos, "model_dump"):
        datos = datos.model_dump()

    if fecha is None:
        fecha = datetime.now().strftime("%d/%m/%Y")

    selecciones = []

    for datos_seleccion in datos["selecciones"]:
        tipo_cuota_individual = str(datos_seleccion["tipo_cuota"]).strip().lower()

        cuota_texto_individual = formatear_cuota_texto_entrada(
            tipo_cuota_individual,
            datos_seleccion["cuota"],
        )

        cuota_individual_decimal = convertir_cuota_a_decimal(
            tipo_cuota_individual,
            cuota_texto_individual,
        )

        seleccion_parlay = {
            "deporte": str(datos_seleccion["deporte"]).strip(),
            "liga": str(datos_seleccion["liga"]).strip(),
            "evento": str(datos_seleccion["evento"]).strip(),
            "tipo_apuesta": str(datos_seleccion["mercado"]).strip(),
            "seleccion": str(datos_seleccion["seleccion"]).strip(),
            "tipo_cuota_individual": (tipo_cuota_individual),
            "cuota_texto_individual": (cuota_texto_individual),
            "cuota_individual": (cuota_individual_decimal),
            "resultado_seleccion": str(
                datos_seleccion.get(
                    "resultado_seleccion",
                    "pendiente",
                )
            )
            .strip()
            .lower(),
        }

        selecciones.append(seleccion_parlay)

    deportes = {seleccion["deporte"] for seleccion in selecciones}

    ligas = {seleccion["liga"] for seleccion in selecciones}

    if len(deportes) == 1:
        deporte = next(iter(deportes))
    else:
        deporte = "Mixto"

    if len(ligas) == 1:
        liga = next(iter(ligas))
    else:
        liga = "Mixta"

    tipo_cuota = str(datos["tipo_cuota"]).strip().lower()

    cuota_texto = formatear_cuota_texto_entrada(
        tipo_cuota,
        datos["cuota"],
    )

    cuota_decimal = convertir_cuota_a_decimal(
        tipo_cuota,
        cuota_texto,
    )

    resultado = calcular_resultado_general_parlay(selecciones)

    return {
        "fecha": fecha,
        "casa": str(datos["casa"]).strip(),
        "deporte": deporte,
        "liga": liga,
        "momento_apuesta": str(
            datos.get(
                "momento_apuesta",
                "prepartido",
            )
        )
        .strip()
        .lower(),
        "modalidad": "parlay",
        "selecciones": selecciones,
        "tipo_cuota": tipo_cuota,
        "cuota_texto": cuota_texto,
        "cuota": cuota_decimal,
        "stake": float(datos["stake"]),
        "resultado": resultado,
        "id": int(id_apuesta),
    }


def crear_apuesta_straight(datos):
    """Construye y guarda una apuesta straight validada."""

    apuestas = cargar_apuestas()

    nuevo_id = obtener_siguiente_id(apuestas)

    apuesta = construir_apuesta_straight(
        datos,
        id_apuesta=nuevo_id,
    )

    apuestas.append(apuesta)
    guardar_apuestas(apuestas)

    return apuesta


def crear_apuesta_parlay(datos):
    """Construye y guarda una apuesta parlay validada."""

    apuestas = cargar_apuestas()

    nuevo_id = obtener_siguiente_id(apuestas)

    apuesta = construir_apuesta_parlay(
        datos,
        id_apuesta=nuevo_id,
    )

    apuestas.append(apuesta)
    guardar_apuestas(apuestas)

    return apuesta


def actualizar_resultado_straight_por_id(
    id_apuesta,
    resultado,
):
    """Actualiza el resultado de una apuesta straight pendiente."""

    try:
        id_buscado = int(id_apuesta)
    except (TypeError, ValueError):
        return {
            "ok": False,
            "codigo": "id_invalido",
            "mensaje": "ID no válido.",
            "apuesta": None,
        }

    resultado_normalizado = normalizar_resultado(resultado)

    resultados_cierre = {
        "ganada",
        "perdida",
        "push",
    }

    if resultado_normalizado not in resultados_cierre:
        return {
            "ok": False,
            "codigo": "resultado_invalido",
            "mensaje": "Resultado no válido.",
            "apuesta": None,
        }

    apuestas = cargar_apuestas()

    for apuesta in apuestas:
        if apuesta.get("id") != id_buscado:
            continue

        modalidad = (
            str(
                apuesta.get(
                    "modalidad",
                    "straight",
                )
            )
            .strip()
            .lower()
        )

        if modalidad != "straight":
            return {
                "ok": False,
                "codigo": "modalidad_no_permitida",
                "mensaje": ("Este endpoint solo permite cerrar " "apuestas straight."),
                "apuesta": apuesta,
            }

        resultado_actual = normalizar_resultado(
            apuesta.get(
                "resultado",
                "pendiente",
            )
        )

        if resultado_actual != "pendiente":
            return {
                "ok": False,
                "codigo": "apuesta_resuelta",
                "mensaje": "La apuesta ya fue resuelta.",
                "apuesta": apuesta,
            }

        apuesta["resultado"] = resultado_normalizado

        guardar_apuestas(apuestas)

        return {
            "ok": True,
            "codigo": "actualizada",
            "mensaje": "Resultado actualizado correctamente.",
            "apuesta": apuesta,
        }

    return {
        "ok": False,
        "codigo": "no_encontrada",
        "mensaje": "Apuesta no encontrada.",
        "apuesta": None,
    }


def eliminar_apuesta_por_id(id_apuesta):
    """Elimina una apuesta por ID."""

    try:
        id_buscado = int(id_apuesta)
    except (TypeError, ValueError):
        return {
            "ok": False,
            "codigo": "id_invalido",
            "mensaje": "ID no válido.",
            "apuesta": None,
        }

    apuestas = cargar_apuestas()

    for indice, apuesta in enumerate(apuestas):
        if apuesta.get("id") != id_buscado:
            continue

        apuesta_eliminada = apuestas.pop(indice)

        guardar_apuestas(apuestas)

        return {
            "ok": True,
            "codigo": "eliminada",
            "mensaje": "Apuesta eliminada correctamente.",
            "apuesta": apuesta_eliminada,
        }

    return {
        "ok": False,
        "codigo": "no_encontrada",
        "mensaje": "Apuesta no encontrada.",
        "apuesta": None,
    }


def actualizar_apuesta_straight_por_id(
    id_apuesta,
    cambios,
):
    """Actualiza parcialmente una apuesta straight."""

    try:
        id_buscado = int(id_apuesta)
    except (TypeError, ValueError):
        return {
            "ok": False,
            "codigo": "id_invalido",
            "mensaje": "ID no válido.",
            "apuesta": None,
        }

    if hasattr(cambios, "model_dump"):
        cambios = cambios.model_dump(exclude_unset=True)
    else:
        cambios = dict(cambios)

    if not cambios:
        return {
            "ok": False,
            "codigo": "sin_cambios",
            "mensaje": "No se enviaron campos para actualizar.",
            "apuesta": None,
        }

    apuestas = cargar_apuestas()

    for apuesta in apuestas:
        if apuesta.get("id") != id_buscado:
            continue

        modalidad = (
            str(
                apuesta.get(
                    "modalidad",
                    "straight",
                )
            )
            .strip()
            .lower()
        )

        if modalidad != "straight":
            return {
                "ok": False,
                "codigo": "modalidad_no_permitida",
                "mensaje": ("Este endpoint solo permite editar " "apuestas straight."),
                "apuesta": apuesta,
            }

        selecciones = apuesta.get(
            "selecciones",
            [],
        )

        if (
            not isinstance(selecciones, list)
            or not selecciones
            or not isinstance(selecciones[0], dict)
        ):
            return {
                "ok": False,
                "codigo": "estructura_invalida",
                "mensaje": ("La apuesta no tiene una selección " "straight válida."),
                "apuesta": apuesta,
            }

        seleccion_guardada = selecciones[0]

        if "casa" in cambios:
            apuesta["casa"] = str(cambios["casa"]).strip()

        if "deporte" in cambios:
            deporte = str(cambios["deporte"]).strip()

            apuesta["deporte"] = deporte
            seleccion_guardada["deporte"] = deporte

        if "liga" in cambios:
            liga = str(cambios["liga"]).strip()

            apuesta["liga"] = liga
            seleccion_guardada["liga"] = liga

        if "evento" in cambios:
            seleccion_guardada["evento"] = str(cambios["evento"]).strip()

        if "mercado" in cambios:
            seleccion_guardada["tipo_apuesta"] = str(cambios["mercado"]).strip()

        if "seleccion" in cambios:
            seleccion_guardada["seleccion"] = str(cambios["seleccion"]).strip()

        if "momento_apuesta" in cambios:
            apuesta["momento_apuesta"] = str(cambios["momento_apuesta"]).strip().lower()

        if "stake" in cambios:
            apuesta["stake"] = float(cambios["stake"])

        tipo_enviado = "tipo_cuota" in cambios
        cuota_enviada = "cuota" in cambios

        if tipo_enviado != cuota_enviada:
            return {
                "ok": False,
                "codigo": "cuota_incompleta",
                "mensaje": ("Debes enviar tipo_cuota " "y cuota juntos."),
                "apuesta": apuesta,
            }

        if tipo_enviado and cuota_enviada:
            tipo_cuota = str(cambios["tipo_cuota"]).strip().lower()

            cuota_texto = formatear_cuota_texto_entrada(
                tipo_cuota,
                cambios["cuota"],
            )

            cuota_decimal = convertir_cuota_a_decimal(
                tipo_cuota,
                cuota_texto,
            )

            apuesta["tipo_cuota"] = tipo_cuota
            apuesta["cuota_texto"] = cuota_texto
            apuesta["cuota"] = cuota_decimal

        guardar_apuestas(apuestas)

        return {
            "ok": True,
            "codigo": "actualizada",
            "mensaje": "Apuesta actualizada correctamente.",
            "apuesta": apuesta,
        }

    return {
        "ok": False,
        "codigo": "no_encontrada",
        "mensaje": "Apuesta no encontrada.",
        "apuesta": None,
    }


def buscar_apuestas_por_filtros(filtros):
    """Busca apuestas usando filtros no interactivos."""

    apuestas = cargar_apuestas()

    if not filtros:
        return apuestas

    resultados = []

    for apuesta in apuestas:
        coincide = True

        for campo, valor_buscado in filtros.items():
            valor_buscado_normalizado = normalizar_texto(valor_buscado)

            valor_apuesta_normalizado = normalizar_texto(
                apuesta.get(
                    campo,
                    "",
                )
            )

            if valor_buscado_normalizado not in valor_apuesta_normalizado:
                coincide = False
                break

        if coincide:
            resultados.append(apuesta)

    return resultados


def listar_apuestas_pendientes():
    """Devuelve las apuestas con resultado pendiente."""

    return buscar_apuestas_por_filtros(
        {
            "resultado": "pendiente",
        }
    )


def cerrar_apuesta_por_id(id_apuesta, resultado):
    """Cierra una apuesta pendiente por ID."""

    resultado_normalizado = normalizar_resultado(resultado)

    if resultado_normalizado not in RESULTADOS_VALIDOS:
        return {
            "ok": False,
            "mensaje": "Resultado no válido.",
            "apuesta": None,
        }

    apuestas = cargar_apuestas()

    try:
        id_buscado = int(id_apuesta)
    except (TypeError, ValueError):
        return {
            "ok": False,
            "mensaje": "ID no válido.",
            "apuesta": None,
        }

    for apuesta in apuestas:
        if apuesta.get("id") == id_buscado:
            resultado_actual = normalizar_resultado(
                apuesta.get(
                    "resultado",
                    "pendiente",
                )
            )

            if resultado_actual != "pendiente":
                return {
                    "ok": False,
                    "mensaje": "La apuesta no está pendiente.",
                    "apuesta": apuesta,
                }

            apuesta["resultado"] = resultado_normalizado

            if apuesta.get("modalidad") == "parlay":
                selecciones = apuesta.get("selecciones", [])

                if selecciones:
                    for seleccion in selecciones:
                        seleccion["resultado"] = resultado_normalizado

                    apuesta["resultado"] = calcular_resultado_general_parlay(
                        selecciones
                    )

            guardar_apuestas(apuestas)

            return {
                "ok": True,
                "mensaje": "Apuesta cerrada correctamente.",
                "apuesta": apuesta,
            }

    return {
        "ok": False,
        "mensaje": "Apuesta no encontrada.",
        "apuesta": None,
    }


def actualizar_selecciones_parlay_por_id(
    id_apuesta,
    actualizaciones,
):
    """Actualiza selecciones y recalcula el resultado del parlay."""

    try:
        id_buscado = int(id_apuesta)
    except (TypeError, ValueError):
        return {
            "ok": False,
            "codigo": "id_invalido",
            "mensaje": "ID no válido.",
            "apuesta": None,
        }

    if hasattr(actualizaciones, "model_dump"):
        datos = actualizaciones.model_dump()
    else:
        datos = dict(actualizaciones)

    cambios = datos.get(
        "selecciones",
        [],
    )

    if not cambios:
        return {
            "ok": False,
            "codigo": "sin_cambios",
            "mensaje": ("Debes enviar al menos una " "selección para actualizar."),
            "apuesta": None,
        }

    apuestas = cargar_apuestas()

    for apuesta in apuestas:
        if apuesta.get("id") != id_buscado:
            continue

        modalidad = (
            str(
                apuesta.get(
                    "modalidad",
                    "straight",
                )
            )
            .strip()
            .lower()
        )

        if modalidad != "parlay":
            return {
                "ok": False,
                "codigo": "modalidad_no_permitida",
                "mensaje": ("Este endpoint solo permite " "actualizar parlays."),
                "apuesta": apuesta,
            }

        selecciones = apuesta.get(
            "selecciones",
            [],
        )

        if not isinstance(selecciones, list) or not selecciones:
            return {
                "ok": False,
                "codigo": "estructura_invalida",
                "mensaje": ("El parlay no contiene " "selecciones válidas."),
                "apuesta": apuesta,
            }

        cambios_validados = []
        numeros_recibidos = set()

        for cambio in cambios:
            try:
                numero = int(cambio["numero"])
            except (
                KeyError,
                TypeError,
                ValueError,
            ):
                return {
                    "ok": False,
                    "codigo": "numero_invalido",
                    "mensaje": ("El número de selección " "no es válido."),
                    "apuesta": apuesta,
                }

            if numero in numeros_recibidos:
                return {
                    "ok": False,
                    "codigo": "numero_repetido",
                    "mensaje": ("No puedes repetir el número " "de una selección."),
                    "apuesta": apuesta,
                }

            numeros_recibidos.add(numero)

            if numero < 1 or numero > len(selecciones):
                return {
                    "ok": False,
                    "codigo": "seleccion_fuera_rango",
                    "mensaje": (f"La selección {numero} " "no existe en este parlay."),
                    "apuesta": apuesta,
                }

            resultado = normalizar_resultado(
                cambio.get(
                    "resultado",
                    "",
                )
            )

            if resultado not in RESULTADOS_VALIDOS:
                return {
                    "ok": False,
                    "codigo": "resultado_invalido",
                    "mensaje": ("El resultado de la selección " "no es válido."),
                    "apuesta": apuesta,
                }

            cambios_validados.append(
                (
                    numero,
                    resultado,
                )
            )

        for numero, resultado in cambios_validados:
            selecciones[numero - 1]["resultado_seleccion"] = resultado

        apuesta["resultado"] = calcular_resultado_general_parlay(selecciones)

        guardar_apuestas(apuestas)

        return {
            "ok": True,
            "codigo": "actualizada",
            "mensaje": ("Selecciones del parlay " "actualizadas correctamente."),
            "apuesta": apuesta,
        }

    return {
        "ok": False,
        "codigo": "no_encontrada",
        "mensaje": "Apuesta no encontrada.",
        "apuesta": None,
    }


def actualizar_apuesta_parlay_por_id(
    id_apuesta,
    cambios,
):
    """Actualiza parcialmente una apuesta parlay."""

    try:
        id_buscado = int(id_apuesta)
    except (TypeError, ValueError):
        return {
            "ok": False,
            "codigo": "id_invalido",
            "mensaje": "ID no válido.",
            "apuesta": None,
        }

    if hasattr(cambios, "model_dump"):
        cambios = cambios.model_dump(exclude_unset=True)
    else:
        cambios = dict(cambios)

    if not cambios:
        return {
            "ok": False,
            "codigo": "sin_cambios",
            "mensaje": ("No se enviaron campos para actualizar."),
            "apuesta": None,
        }

    apuestas = cargar_apuestas()

    for indice, apuesta in enumerate(apuestas):
        if apuesta.get("id") != id_buscado:
            continue

        modalidad = (
            str(
                apuesta.get(
                    "modalidad",
                    "straight",
                )
            )
            .strip()
            .lower()
        )

        if modalidad != "parlay":
            return {
                "ok": False,
                "codigo": "modalidad_no_permitida",
                "mensaje": ("Este endpoint solo permite editar " "apuestas parlay."),
                "apuesta": apuesta,
            }

        selecciones_originales = apuesta.get(
            "selecciones",
            [],
        )

        if (
            not isinstance(
                selecciones_originales,
                list,
            )
            or len(selecciones_originales) < 2
        ):
            return {
                "ok": False,
                "codigo": "estructura_invalida",
                "mensaje": (
                    "El parlay no contiene una estructura " "de selecciones válida."
                ),
                "apuesta": apuesta,
            }

        apuesta_actualizada = deepcopy(apuesta)

        selecciones = apuesta_actualizada["selecciones"]

        if "casa" in cambios:
            apuesta_actualizada["casa"] = str(cambios["casa"]).strip()

        if "momento_apuesta" in cambios:
            apuesta_actualizada["momento_apuesta"] = (
                str(cambios["momento_apuesta"]).strip().lower()
            )

        if "stake" in cambios:
            apuesta_actualizada["stake"] = float(cambios["stake"])

        tipo_enviado = "tipo_cuota" in cambios
        cuota_enviada = "cuota" in cambios

        if tipo_enviado != cuota_enviada:
            return {
                "ok": False,
                "codigo": "cuota_incompleta",
                "mensaje": ("Debes enviar tipo_cuota " "y cuota juntos."),
                "apuesta": apuesta,
            }

        if tipo_enviado and cuota_enviada:
            tipo_cuota = str(cambios["tipo_cuota"]).strip().lower()

            cuota_texto = formatear_cuota_texto_entrada(
                tipo_cuota,
                cambios["cuota"],
            )

            cuota_decimal = convertir_cuota_a_decimal(
                tipo_cuota,
                cuota_texto,
            )

            apuesta_actualizada["tipo_cuota"] = tipo_cuota

            apuesta_actualizada["cuota_texto"] = cuota_texto

            apuesta_actualizada["cuota"] = cuota_decimal

        cambios_selecciones = cambios.get(
            "selecciones",
            [],
        )

        numeros_recibidos = set()

        for cambio in cambios_selecciones:
            numero = int(cambio["numero"])

            if numero in numeros_recibidos:
                return {
                    "ok": False,
                    "codigo": "numero_repetido",
                    "mensaje": ("No puedes repetir el número " "de una selección."),
                    "apuesta": apuesta,
                }

            numeros_recibidos.add(numero)

            if numero < 1 or numero > len(selecciones):
                return {
                    "ok": False,
                    "codigo": "seleccion_fuera_rango",
                    "mensaje": (f"La selección {numero} " "no existe en este parlay."),
                    "apuesta": apuesta,
                }

            seleccion_guardada = selecciones[numero - 1]

            if "deporte" in cambio:
                seleccion_guardada["deporte"] = str(cambio["deporte"]).strip()

            if "liga" in cambio:
                seleccion_guardada["liga"] = str(cambio["liga"]).strip()

            if "evento" in cambio:
                seleccion_guardada["evento"] = str(cambio["evento"]).strip()

            if "mercado" in cambio:
                seleccion_guardada["tipo_apuesta"] = str(cambio["mercado"]).strip()

            if "seleccion" in cambio:
                seleccion_guardada["seleccion"] = str(cambio["seleccion"]).strip()

            tipo_individual_enviado = "tipo_cuota" in cambio
            cuota_individual_enviada = "cuota" in cambio

            if tipo_individual_enviado != cuota_individual_enviada:
                return {
                    "ok": False,
                    "codigo": ("cuota_individual_incompleta"),
                    "mensaje": (
                        "Debes enviar tipo_cuota "
                        "y cuota juntos para modificar "
                        "una cuota individual."
                    ),
                    "apuesta": apuesta,
                }

            if tipo_individual_enviado and cuota_individual_enviada:
                tipo_individual = str(cambio["tipo_cuota"]).strip().lower()

                cuota_texto_individual = formatear_cuota_texto_entrada(
                    tipo_individual,
                    cambio["cuota"],
                )

                cuota_decimal_individual = convertir_cuota_a_decimal(
                    tipo_individual,
                    cuota_texto_individual,
                )

                seleccion_guardada["tipo_cuota_individual"] = tipo_individual

                seleccion_guardada["cuota_texto_individual"] = cuota_texto_individual

                seleccion_guardada["cuota_individual"] = cuota_decimal_individual

        deportes = {seleccion["deporte"] for seleccion in selecciones}

        ligas = {seleccion["liga"] for seleccion in selecciones}

        apuesta_actualizada["deporte"] = (
            next(iter(deportes)) if len(deportes) == 1 else "Mixto"
        )

        apuesta_actualizada["liga"] = next(iter(ligas)) if len(ligas) == 1 else "Mixta"

        apuesta_actualizada["resultado"] = calcular_resultado_general_parlay(
            selecciones
        )

        apuestas[indice] = apuesta_actualizada

        guardar_apuestas(apuestas)

        return {
            "ok": True,
            "codigo": "actualizada",
            "mensaje": ("Apuesta parlay actualizada " "correctamente."),
            "apuesta": apuesta_actualizada,
        }

    return {
        "ok": False,
        "codigo": "no_encontrada",
        "mensaje": "Apuesta no encontrada.",
        "apuesta": None,
    }


def agregar_seleccion_parlay_por_id(
    id_apuesta,
    datos_seleccion,
):
    """Agrega una selección a un parlay existente."""

    try:
        id_buscado = int(id_apuesta)
    except (TypeError, ValueError):
        return {
            "ok": False,
            "codigo": "id_invalido",
            "mensaje": "ID no válido.",
            "apuesta": None,
        }

    if hasattr(datos_seleccion, "model_dump"):
        datos_seleccion = datos_seleccion.model_dump()
    else:
        datos_seleccion = dict(datos_seleccion)

    apuestas = cargar_apuestas()

    for apuesta in apuestas:
        if apuesta.get("id") != id_buscado:
            continue

        modalidad = (
            str(
                apuesta.get(
                    "modalidad",
                    "straight",
                )
            )
            .strip()
            .lower()
        )

        if modalidad != "parlay":
            return {
                "ok": False,
                "codigo": "modalidad_no_permitida",
                "mensaje": ("Solo puedes agregar selecciones " "a una apuesta parlay."),
                "apuesta": apuesta,
            }

        selecciones = apuesta.get(
            "selecciones",
            [],
        )

        if not isinstance(selecciones, list):
            return {
                "ok": False,
                "codigo": "estructura_invalida",
                "mensaje": (
                    "El parlay no contiene una " "estructura de selecciones válida."
                ),
                "apuesta": apuesta,
            }

        tipo_cuota = str(datos_seleccion["tipo_cuota"]).strip().lower()

        cuota_texto = formatear_cuota_texto_entrada(
            tipo_cuota,
            datos_seleccion["cuota"],
        )

        cuota_decimal = convertir_cuota_a_decimal(
            tipo_cuota,
            cuota_texto,
        )

        nueva_seleccion = {
            "deporte": str(datos_seleccion["deporte"]).strip(),
            "liga": str(datos_seleccion["liga"]).strip(),
            "evento": str(datos_seleccion["evento"]).strip(),
            "tipo_apuesta": str(datos_seleccion["mercado"]).strip(),
            "seleccion": str(datos_seleccion["seleccion"]).strip(),
            "tipo_cuota_individual": tipo_cuota,
            "cuota_texto_individual": cuota_texto,
            "cuota_individual": cuota_decimal,
            "resultado_seleccion": str(
                datos_seleccion.get(
                    "resultado_seleccion",
                    "pendiente",
                )
            )
            .strip()
            .lower(),
        }

        selecciones.append(nueva_seleccion)

        deportes = {seleccion["deporte"] for seleccion in selecciones}

        ligas = {seleccion["liga"] for seleccion in selecciones}

        apuesta["deporte"] = next(iter(deportes)) if len(deportes) == 1 else "Mixto"

        apuesta["liga"] = next(iter(ligas)) if len(ligas) == 1 else "Mixta"

        apuesta["resultado"] = calcular_resultado_general_parlay(selecciones)

        guardar_apuestas(apuestas)

        return {
            "ok": True,
            "codigo": "seleccion_agregada",
            "mensaje": ("Selección agregada correctamente."),
            "apuesta": apuesta,
        }

    return {
        "ok": False,
        "codigo": "no_encontrada",
        "mensaje": "Apuesta no encontrada.",
        "apuesta": None,
    }


def eliminar_seleccion_parlay_por_id(
    id_apuesta,
    numero,
):
    """Elimina una selección existente de un parlay."""

    try:
        id_buscado = int(id_apuesta)
    except (TypeError, ValueError):
        return {
            "ok": False,
            "codigo": "id_invalido",
            "mensaje": "ID no válido.",
            "apuesta": None,
            "seleccion_eliminada": None,
        }

    try:
        numero_buscado = int(numero)
    except (TypeError, ValueError):
        return {
            "ok": False,
            "codigo": "numero_invalido",
            "mensaje": "Número de selección no válido.",
            "apuesta": None,
            "seleccion_eliminada": None,
        }

    apuestas = cargar_apuestas()

    for apuesta in apuestas:
        if apuesta.get("id") != id_buscado:
            continue

        modalidad = (
            str(
                apuesta.get(
                    "modalidad",
                    "straight",
                )
            )
            .strip()
            .lower()
        )

        if modalidad != "parlay":
            return {
                "ok": False,
                "codigo": "modalidad_no_permitida",
                "mensaje": (
                    "Solo puedes eliminar selecciones " "de una apuesta parlay."
                ),
                "apuesta": apuesta,
                "seleccion_eliminada": None,
            }

        selecciones = apuesta.get(
            "selecciones",
            [],
        )

        if not isinstance(selecciones, list) or len(selecciones) < 2:
            return {
                "ok": False,
                "codigo": "estructura_invalida",
                "mensaje": (
                    "El parlay no contiene una estructura " "de selecciones válida."
                ),
                "apuesta": apuesta,
                "seleccion_eliminada": None,
            }

        if numero_buscado < 1 or numero_buscado > len(selecciones):
            return {
                "ok": False,
                "codigo": "seleccion_fuera_rango",
                "mensaje": (
                    f"La selección {numero_buscado} " "no existe en este parlay."
                ),
                "apuesta": apuesta,
                "seleccion_eliminada": None,
            }

        if len(selecciones) <= 2:
            return {
                "ok": False,
                "codigo": "minimo_selecciones",
                "mensaje": ("Un parlay debe conservar al menos " "dos selecciones."),
                "apuesta": apuesta,
                "seleccion_eliminada": None,
            }

        seleccion_eliminada = selecciones.pop(numero_buscado - 1)

        deportes = {
            str(
                seleccion.get(
                    "deporte",
                    "",
                )
            ).strip()
            for seleccion in selecciones
        }

        ligas = {
            str(
                seleccion.get(
                    "liga",
                    "",
                )
            ).strip()
            for seleccion in selecciones
        }

        deportes.discard("")
        ligas.discard("")

        apuesta["deporte"] = next(iter(deportes)) if len(deportes) == 1 else "Mixto"

        apuesta["liga"] = next(iter(ligas)) if len(ligas) == 1 else "Mixta"

        apuesta["resultado"] = calcular_resultado_general_parlay(selecciones)

        guardar_apuestas(apuestas)

        return {
            "ok": True,
            "codigo": "seleccion_eliminada",
            "mensaje": ("Selección eliminada correctamente."),
            "apuesta": apuesta,
            "seleccion_eliminada": seleccion_eliminada,
        }

    return {
        "ok": False,
        "codigo": "no_encontrada",
        "mensaje": "Apuesta no encontrada.",
        "apuesta": None,
        "seleccion_eliminada": None,
    }


def reordenar_selecciones_parlay_por_id(
    id_apuesta,
    datos_orden,
):
    """Reordena todas las selecciones de un parlay."""

    try:
        id_buscado = int(id_apuesta)
    except (TypeError, ValueError):
        return {
            "ok": False,
            "codigo": "id_invalido",
            "mensaje": "ID no válido.",
            "apuesta": None,
        }

    if hasattr(datos_orden, "model_dump"):
        datos_orden = datos_orden.model_dump()
    else:
        datos_orden = dict(datos_orden)

    orden = datos_orden.get(
        "orden",
        [],
    )

    if not orden:
        return {
            "ok": False,
            "codigo": "sin_orden",
            "mensaje": "No se recibió un nuevo orden.",
            "apuesta": None,
        }

    apuestas = cargar_apuestas()

    for apuesta in apuestas:
        if apuesta.get("id") != id_buscado:
            continue

        modalidad = (
            str(
                apuesta.get(
                    "modalidad",
                    "straight",
                )
            )
            .strip()
            .lower()
        )

        if modalidad != "parlay":
            return {
                "ok": False,
                "codigo": "modalidad_no_permitida",
                "mensaje": (
                    "Solo puedes reordenar selecciones " "de una apuesta parlay."
                ),
                "apuesta": apuesta,
            }

        selecciones = apuesta.get(
            "selecciones",
            [],
        )

        if not isinstance(selecciones, list) or len(selecciones) < 2:
            return {
                "ok": False,
                "codigo": "estructura_invalida",
                "mensaje": (
                    "El parlay no contiene una estructura " "de selecciones válida."
                ),
                "apuesta": apuesta,
            }

        try:
            orden_normalizado = [int(numero) for numero in orden]
        except (TypeError, ValueError):
            return {
                "ok": False,
                "codigo": "orden_invalido",
                "mensaje": ("El orden contiene números inválidos."),
                "apuesta": apuesta,
            }

        numeros_esperados = set(
            range(
                1,
                len(selecciones) + 1,
            )
        )

        numeros_recibidos = set(orden_normalizado)

        if (
            len(orden_normalizado) != len(selecciones)
            or numeros_recibidos != numeros_esperados
        ):
            return {
                "ok": False,
                "codigo": "orden_incompleto",
                "mensaje": (
                    "El nuevo orden debe incluir exactamente "
                    "una vez cada selección del parlay."
                ),
                "apuesta": apuesta,
            }

        selecciones_reordenadas = [
            selecciones[numero - 1] for numero in orden_normalizado
        ]

        apuesta["selecciones"] = selecciones_reordenadas

        apuesta["resultado"] = calcular_resultado_general_parlay(
            selecciones_reordenadas
        )

        guardar_apuestas(apuestas)

        return {
            "ok": True,
            "codigo": "reordenada",
            "mensaje": ("Selecciones reordenadas correctamente."),
            "apuesta": apuesta,
        }

    return {
        "ok": False,
        "codigo": "no_encontrada",
        "mensaje": "Apuesta no encontrada.",
        "apuesta": None,
    }
