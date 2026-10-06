from typing import (
    Any,
    get_args,
    get_origin,
)

from pydantic import BaseModel

from auditoria_api import obtener_rutas_publicas
from modelos_api import (
    ApuestaParlayActualizarAPI,
    ApuestaParlayCrearAPI,
    ApuestaStraightActualizarAPI,
    ApuestaStraightCrearAPI,
    BankrollActualizarAPI,
    OrdenSeleccionesParlayAPI,
    ResultadoApuestaActualizarAPI,
    ResultadoSeleccionParlayAPI,
    SeleccionParlayActualizarAPI,
    SeleccionParlayCrearAPI,
    SeleccionesParlayActualizarAPI,
)

MODELOS_ENTRADA = (
    ApuestaStraightCrearAPI,
    ApuestaStraightActualizarAPI,
    ApuestaParlayCrearAPI,
    ApuestaParlayActualizarAPI,
    SeleccionParlayCrearAPI,
    SeleccionParlayActualizarAPI,
    ResultadoApuestaActualizarAPI,
    ResultadoSeleccionParlayAPI,
    SeleccionesParlayActualizarAPI,
    OrdenSeleccionesParlayAPI,
    BankrollActualizarAPI,
)


CAMPOS_NUMERICOS_SENSIBLES = {
    "cuota",
    "stake",
    "bankroll_inicial",
}


CAMPOS_INTERNOS_PROHIBIDOS = {
    "ruta_base_datos",
    "base_datos",
    "ultimo_respaldo",
    "ruta_archivo",
    "contrasena",
    "password",
    "token",
}


def es_modelo_pydantic(tipo):
    """Indica si un objeto es una clase Pydantic."""

    return isinstance(tipo, type) and issubclass(tipo, BaseModel)


def contiene_tipo_any(anotacion):
    """Detecta el uso de Any dentro de una anotación."""

    if anotacion is Any:
        return True

    return any(
        contiene_tipo_any(argumento)
        for argumento in get_args(anotacion)
        if argumento is not Ellipsis
    )


def extraer_modelos_desde_tipo(
    tipo,
    modelos=None,
):
    """Obtiene modelos Pydantic anidados desde un tipo."""

    if modelos is None:
        modelos = set()

    if tipo is None:
        return modelos

    if es_modelo_pydantic(tipo):
        if tipo in modelos:
            return modelos

        modelos.add(tipo)

        for campo in tipo.model_fields.values():
            extraer_modelos_desde_tipo(
                campo.annotation,
                modelos,
            )

        return modelos

    origen = get_origin(tipo)

    if origen is not None:
        for argumento in get_args(tipo):
            if argumento is Ellipsis:
                continue

            extraer_modelos_desde_tipo(
                argumento,
                modelos,
            )

    return modelos


def obtener_modelos_respuesta(app):
    """Obtiene todos los modelos usados en respuestas."""

    modelos = set()

    for ruta in obtener_rutas_publicas(app):
        extraer_modelos_desde_tipo(
            ruta.response_model,
            modelos,
        )

    return modelos


def detectar_entradas_sin_extra_forbid():
    """Detecta modelos de entrada que aceptan campos extra."""

    problemas = []

    for modelo in MODELOS_ENTRADA:
        configuracion_extra = modelo.model_config.get(
            "extra",
            "ignore",
        )

        if configuracion_extra != "forbid":
            problemas.append(
                {
                    "modelo": modelo.__name__,
                    "configuracion_extra": (configuracion_extra),
                }
            )

    return problemas


def detectar_salidas_con_extra_allow(app):
    """Detecta respuestas que conservan campos inesperados."""

    problemas = []

    for modelo in obtener_modelos_respuesta(app):
        configuracion_extra = modelo.model_config.get(
            "extra",
            "ignore",
        )

        if configuracion_extra == "allow":
            problemas.append(
                {
                    "modelo": modelo.__name__,
                    "configuracion_extra": "allow",
                }
            )

    return sorted(
        problemas,
        key=lambda elemento: elemento["modelo"],
    )


def detectar_any_en_entradas():
    """Detecta campos de entrada sin tipo concreto."""

    problemas = []

    for modelo in MODELOS_ENTRADA:
        for nombre, campo in modelo.model_fields.items():
            if contiene_tipo_any(campo.annotation):
                problemas.append(
                    {
                        "modelo": modelo.__name__,
                        "campo": nombre,
                        "anotacion": str(campo.annotation),
                    }
                )

    return problemas


def detectar_campos_internos_salida(app):
    """Detecta información interna en modelos públicos."""

    problemas = []

    for modelo in obtener_modelos_respuesta(app):
        campos = set(modelo.model_fields.keys())

        campos_detectados = sorted(campos & CAMPOS_INTERNOS_PROHIBIDOS)

        if campos_detectados:
            problemas.append(
                {
                    "modelo": modelo.__name__,
                    "campos": campos_detectados,
                }
            )

    return sorted(
        problemas,
        key=lambda elemento: elemento["modelo"],
    )


def detectar_validacion_no_finitos_pendiente():
    """Detecta modelos monetarios que aún aceptan infinito o NaN."""

    recomendaciones = []

    for modelo in MODELOS_ENTRADA:
        campos_numericos = sorted(
            set(modelo.model_fields.keys()) & CAMPOS_NUMERICOS_SENSIBLES
        )

        if not campos_numericos:
            continue

        permite_no_finitos = modelo.model_config.get(
            "allow_inf_nan",
            True,
        )

        if permite_no_finitos is not False:
            recomendaciones.append(
                {
                    "modelo": modelo.__name__,
                    "campos": campos_numericos,
                }
            )

    return recomendaciones


def generar_resumen_auditoria_modelos(app):
    """Genera la auditoría completa de contratos Pydantic."""

    entradas_permisivas = detectar_entradas_sin_extra_forbid()

    salidas_permisivas = detectar_salidas_con_extra_allow(app)

    campos_any = detectar_any_en_entradas()

    campos_internos = detectar_campos_internos_salida(app)

    no_finitos_pendientes = detectar_validacion_no_finitos_pendiente()

    errores = (
        len(entradas_permisivas)
        + len(salidas_permisivas)
        + len(campos_any)
        + len(campos_internos)
    )

    return {
        "modelos_entrada_revisados": len(MODELOS_ENTRADA),
        "modelos_respuesta_revisados": len(obtener_modelos_respuesta(app)),
        "entradas_sin_extra_forbid": (entradas_permisivas),
        "salidas_con_extra_allow": (salidas_permisivas),
        "campos_any_en_entradas": campos_any,
        "campos_internos_en_salidas": (campos_internos),
        "validacion_no_finitos_pendiente": (no_finitos_pendientes),
        "errores_encontrados": errores,
        "recomendaciones_encontradas": len(no_finitos_pendientes),
        "estado_correcto": errores == 0,
    }
