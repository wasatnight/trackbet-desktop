from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import (
    HTTPException as StarletteHTTPException,
)

CODIGOS_ERROR_HTTP = {
    400: "solicitud_invalida",
    401: "no_autorizado",
    403: "acceso_denegado",
    404: "no_encontrado",
    405: "metodo_no_permitido",
    409: "conflicto",
    422: "validacion_fallida",
    429: "demasiadas_solicitudes",
    500: "error_interno",
}


MENSAJES_ERROR_HTTP = {
    400: "La solicitud no es válida.",
    401: "Debes autenticarte para continuar.",
    403: "No tienes permiso para realizar esta acción.",
    404: "El recurso solicitado no fue encontrado.",
    405: "El método HTTP no está permitido.",
    409: "La operación genera un conflicto.",
    422: "Los datos enviados no son válidos.",
    429: "Se realizaron demasiadas solicitudes.",
    500: "Ocurrió un error interno en el servidor.",
}


def obtener_codigo_error_http(
    status_code,
):
    """Devuelve un código legible para un estado HTTP."""

    try:
        codigo_http = int(status_code)
    except (TypeError, ValueError):
        return "error_desconocido"

    if codigo_http in CODIGOS_ERROR_HTTP:
        return CODIGOS_ERROR_HTTP[codigo_http]

    if 400 <= codigo_http < 500:
        return "error_cliente"

    if codigo_http >= 500:
        return "error_servidor"

    return "error_desconocido"


def obtener_mensaje_error(
    detalle,
    status_code,
):
    """Obtiene un mensaje legible a partir del detalle."""

    if isinstance(detalle, str):
        mensaje = detalle.strip()

        if mensaje:
            return mensaje

    if isinstance(detalle, dict):
        for clave in (
            "mensaje",
            "message",
            "detail",
        ):
            valor = detalle.get(clave)

            if isinstance(valor, str) and valor.strip():
                return valor.strip()

    try:
        codigo_http = int(status_code)
    except (TypeError, ValueError):
        codigo_http = 500

    return MENSAJES_ERROR_HTTP.get(
        codigo_http,
        "Ocurrió un error inesperado.",
    )


def construir_respuesta_error(
    codigo,
    mensaje,
    detalles=None,
    detalle_compatibilidad=None,
):
    """Construye la estructura estándar de un error."""

    respuesta = {
        "ok": False,
        "error": {
            "codigo": str(codigo),
            "mensaje": str(mensaje),
            "detalles": detalles,
        },
    }

    if detalle_compatibilidad is not None:
        respuesta["detail"] = detalle_compatibilidad

    return respuesta


def registrar_manejadores_errores(
    app: FastAPI,
):
    """Registra los manejadores globales de errores."""

    @app.exception_handler(StarletteHTTPException)
    async def manejar_error_http(
        _request: Request,
        excepcion: StarletteHTTPException,
    ):
        codigo = obtener_codigo_error_http(excepcion.status_code)

        mensaje = obtener_mensaje_error(
            excepcion.detail,
            excepcion.status_code,
        )

        detalles = None

        if not isinstance(
            excepcion.detail,
            str,
        ):
            detalles = jsonable_encoder(excepcion.detail)

        contenido = construir_respuesta_error(
            codigo=codigo,
            mensaje=mensaje,
            detalles=detalles,
            detalle_compatibilidad=(jsonable_encoder(excepcion.detail)),
        )

        return JSONResponse(
            status_code=excepcion.status_code,
            content=jsonable_encoder(contenido),
            headers=excepcion.headers,
        )

    @app.exception_handler(RequestValidationError)
    async def manejar_error_validacion(
        _request: Request,
        excepcion: RequestValidationError,
    ):
        errores = jsonable_encoder(excepcion.errors())

        contenido = construir_respuesta_error(
            codigo="validacion_fallida",
            mensaje=("Los datos enviados no son válidos."),
            detalles=errores,
            detalle_compatibilidad=errores,
        )

        return JSONResponse(
            status_code=422,
            content=jsonable_encoder(contenido),
        )
