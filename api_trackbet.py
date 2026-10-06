from typing import Literal

from fastapi import FastAPI, HTTPException, Query

from configuracion_app import (
    NOMBRE_APP,
    VERSION_APP,
)
from servicios_apuestas import (
    actualizar_apuesta_parlay_por_id,
    actualizar_apuesta_straight_por_id,
    actualizar_resultado_straight_por_id,
    actualizar_selecciones_parlay_por_id,
    agregar_seleccion_parlay_por_id,
    buscar_apuestas_por_filtros,
    crear_apuesta_parlay,
    crear_apuesta_straight,
    eliminar_apuesta_por_id,
    listar_apuestas_pendientes,
    obtener_apuesta_por_id,
    eliminar_seleccion_parlay_por_id,
    reordenar_selecciones_parlay_por_id,
)
from servicios_reportes import obtener_resumen_financiero
from modelos_api import (
    ApuestaAPI,
    ApuestaEliminadaAPI,
    ApuestaParlayActualizarAPI,
    ApuestaParlayCrearAPI,
    ApuestaStraightActualizarAPI,
    ApuestaStraightCrearAPI,
    BankrollAPI,
    BankrollActualizarAPI,
    EstadisticasAPI,
    EstadoAPI,
    ListaApuestasAPI,
    ListaPendientesAPI,
    ResultadoApuestaActualizarAPI,
    SeleccionParlayCrearAPI,
    SeleccionesParlayActualizarAPI,
    ResumenFinancieroAPI,
    SeleccionEliminadaParlayAPI,
    OrdenSeleccionesParlayAPI,
    AnalisisCuotasAPI,
    AnalisisParlaysAPI,
    DiagnosticoAPI,
)
from servicios_configuracion import (
    actualizar_configuracion_bankroll,
    obtener_configuracion_bankroll,
)
from servicios_estadisticas import obtener_estadisticas
from servicios_analiticas import (
    obtener_analisis_cuotas,
    obtener_analisis_parlays,
)
from servicios_diagnostico import (
    obtener_diagnostico_sistema,
)
from errores_api import (
    registrar_manejadores_errores,
)

from configuracion_cors import (
    configurar_cors,
)

app = FastAPI(
    title=f"{NOMBRE_APP} API",
    version=VERSION_APP,
    description=(
        "API para consultar apuestas deportivas, pendientes y reportes financieros."
    ),
)

registrar_manejadores_errores(app)
configurar_cors(app)


@app.get(
    "/",
    response_model=EstadoAPI,
)
def obtener_estado_api():
    """Devuelve información básica de la API."""

    return {
        "aplicacion": NOMBRE_APP,
        "version": VERSION_APP,
        "estado": "API funcionando",
    }


@app.get(
    "/apuestas",
    response_model=ListaApuestasAPI,
)
def api_listar_apuestas(
    deporte: str | None = None,
    resultado: str | None = None,
    modalidad: str | None = None,
    casa: str | None = None,
    limite: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    desplazamiento: int = Query(
        default=0,
        ge=0,
    ),
    orden: Literal["asc", "desc"] = "desc",
):
    """Devuelve apuestas con filtros, paginación y ordenamiento."""

    filtros = {}

    if deporte:
        filtros["deporte"] = deporte

    if resultado:
        filtros["resultado"] = resultado

    if modalidad:
        filtros["modalidad"] = modalidad

    if casa:
        filtros["casa"] = casa

    apuestas = buscar_apuestas_por_filtros(filtros)

    apuestas_ordenadas = sorted(
        apuestas,
        key=lambda apuesta: int(apuesta.get("id", 0)),
        reverse=orden == "desc",
    )

    total = len(apuestas_ordenadas)

    apuestas_paginadas = apuestas_ordenadas[desplazamiento : desplazamiento + limite]

    return {
        "total": total,
        "cantidad": len(apuestas_paginadas),
        "limite": limite,
        "desplazamiento": desplazamiento,
        "orden": orden,
        "filtros": filtros,
        "apuestas": apuestas_paginadas,
    }


@app.get(
    "/apuestas/pendientes",
    response_model=ListaPendientesAPI,
)
def api_listar_apuestas_pendientes():
    """Devuelve las apuestas pendientes."""

    apuestas = listar_apuestas_pendientes()

    return {
        "total": len(apuestas),
        "apuestas": apuestas,
    }


@app.get(
    "/apuestas/{id_apuesta}",
    response_model=ApuestaAPI,
)
def api_obtener_apuesta(id_apuesta: int):
    """Devuelve una apuesta específica por ID."""

    apuesta = obtener_apuesta_por_id(id_apuesta)

    if apuesta is None:
        raise HTTPException(
            status_code=404,
            detail="Apuesta no encontrada.",
        )

    return apuesta


@app.get(
    "/reportes/resumen-financiero",
    response_model=ResumenFinancieroAPI,
)
def api_obtener_resumen_financiero():
    """Devuelve el resumen financiero actual."""

    return obtener_resumen_financiero()


@app.get(
    "/estadisticas",
    response_model=EstadisticasAPI,
)
def api_obtener_estadisticas():
    """Devuelve las estadísticas completas."""

    return obtener_estadisticas()


@app.get(
    "/diagnostico",
    response_model=DiagnosticoAPI,
)
def api_obtener_diagnostico():
    """Devuelve el diagnóstico completo del sistema."""

    return obtener_diagnostico_sistema()


@app.get(
    "/analiticas/cuotas",
    response_model=AnalisisCuotasAPI,
)
def api_obtener_analisis_cuotas():
    """Devuelve el análisis por rangos de cuotas."""

    return obtener_analisis_cuotas()


@app.get(
    "/analiticas/parlays",
    response_model=AnalisisParlaysAPI,
)
def api_obtener_analisis_parlays():
    """Devuelve el análisis completo de parlays."""

    return obtener_analisis_parlays()


@app.get(
    "/configuracion/bankroll",
    response_model=BankrollAPI,
)
def api_obtener_bankroll():
    """Devuelve el bankroll inicial configurado."""

    return obtener_configuracion_bankroll()


@app.put(
    "/configuracion/bankroll",
    response_model=BankrollAPI,
)
def api_actualizar_bankroll(
    datos: BankrollActualizarAPI,
):
    """Actualiza el bankroll inicial."""

    respuesta = actualizar_configuracion_bankroll(datos.bankroll_inicial)

    if not respuesta["ok"]:
        raise HTTPException(
            status_code=400,
            detail=respuesta["mensaje"],
        )

    return respuesta["configuracion"]


@app.post(
    "/apuestas",
    response_model=ApuestaAPI,
    status_code=201,
)
def api_crear_apuesta_straight(
    datos: ApuestaStraightCrearAPI,
):
    """Registra una nueva apuesta straight."""

    return crear_apuesta_straight(datos)


@app.patch(
    "/apuestas/{id_apuesta}/resultado",
    response_model=ApuestaAPI,
)
def api_actualizar_resultado_straight(
    id_apuesta: int,
    datos: ResultadoApuestaActualizarAPI,
):
    """Cierra una apuesta straight pendiente."""

    respuesta = actualizar_resultado_straight_por_id(
        id_apuesta,
        datos.resultado,
    )

    if respuesta["ok"]:
        return respuesta["apuesta"]

    codigo = respuesta["codigo"]

    if codigo == "no_encontrada":
        raise HTTPException(
            status_code=404,
            detail=respuesta["mensaje"],
        )

    if codigo in {
        "apuesta_resuelta",
        "modalidad_no_permitida",
    }:
        raise HTTPException(
            status_code=409,
            detail=respuesta["mensaje"],
        )

    raise HTTPException(
        status_code=400,
        detail=respuesta["mensaje"],
    )


@app.post(
    "/apuestas/parlay",
    response_model=ApuestaAPI,
    status_code=201,
)
def api_crear_apuesta_parlay(
    datos: ApuestaParlayCrearAPI,
):
    """Registra una nueva apuesta parlay."""

    return crear_apuesta_parlay(datos)


@app.patch(
    "/apuestas/{id_apuesta}/selecciones",
    response_model=ApuestaAPI,
)
def api_actualizar_selecciones_parlay(
    id_apuesta: int,
    datos: SeleccionesParlayActualizarAPI,
):
    """Actualiza los resultados individuales de un parlay."""

    respuesta = actualizar_selecciones_parlay_por_id(
        id_apuesta,
        datos,
    )

    if respuesta["ok"]:
        return respuesta["apuesta"]

    codigo = respuesta["codigo"]

    if codigo == "no_encontrada":
        raise HTTPException(
            status_code=404,
            detail=respuesta["mensaje"],
        )

    if codigo in {
        "modalidad_no_permitida",
        "estructura_invalida",
    }:
        raise HTTPException(
            status_code=409,
            detail=respuesta["mensaje"],
        )

    if codigo in {
        "seleccion_fuera_rango",
        "numero_invalido",
        "numero_repetido",
        "resultado_invalido",
        "sin_cambios",
    }:
        raise HTTPException(
            status_code=422,
            detail=respuesta["mensaje"],
        )

    raise HTTPException(
        status_code=400,
        detail=respuesta["mensaje"],
    )


@app.patch(
    "/apuestas/{id_apuesta}/parlay",
    response_model=ApuestaAPI,
)
def api_actualizar_apuesta_parlay(
    id_apuesta: int,
    cambios: ApuestaParlayActualizarAPI,
):
    """Actualiza parcialmente una apuesta parlay."""

    respuesta = actualizar_apuesta_parlay_por_id(
        id_apuesta,
        cambios,
    )

    if respuesta["ok"]:
        return respuesta["apuesta"]

    codigo = respuesta["codigo"]

    if codigo == "no_encontrada":
        raise HTTPException(
            status_code=404,
            detail=respuesta["mensaje"],
        )

    if codigo in {
        "modalidad_no_permitida",
        "estructura_invalida",
    }:
        raise HTTPException(
            status_code=409,
            detail=respuesta["mensaje"],
        )

    if codigo in {
        "sin_cambios",
        "cuota_incompleta",
        "cuota_individual_incompleta",
        "numero_repetido",
        "seleccion_fuera_rango",
    }:
        raise HTTPException(
            status_code=422,
            detail=respuesta["mensaje"],
        )

    raise HTTPException(
        status_code=400,
        detail=respuesta["mensaje"],
    )


@app.delete(
    "/apuestas/{id_apuesta}",
    response_model=ApuestaEliminadaAPI,
)
def api_eliminar_apuesta(id_apuesta: int):
    """Elimina una apuesta registrada."""

    respuesta = eliminar_apuesta_por_id(id_apuesta)

    if respuesta["ok"]:
        apuesta_eliminada = respuesta["apuesta"]

        return {
            "mensaje": respuesta["mensaje"],
            "id_eliminado": apuesta_eliminada["id"],
            "apuesta": apuesta_eliminada,
        }

    if respuesta["codigo"] == "no_encontrada":
        raise HTTPException(
            status_code=404,
            detail=respuesta["mensaje"],
        )

    raise HTTPException(
        status_code=400,
        detail=respuesta["mensaje"],
    )


@app.patch(
    "/apuestas/{id_apuesta}",
    response_model=ApuestaAPI,
)
def api_actualizar_apuesta_straight(
    id_apuesta: int,
    cambios: ApuestaStraightActualizarAPI,
):
    """Actualiza parcialmente una apuesta straight."""

    respuesta = actualizar_apuesta_straight_por_id(
        id_apuesta,
        cambios,
    )

    if respuesta["ok"]:
        return respuesta["apuesta"]

    codigo = respuesta["codigo"]

    if codigo == "no_encontrada":
        raise HTTPException(
            status_code=404,
            detail=respuesta["mensaje"],
        )

    if codigo == "modalidad_no_permitida":
        raise HTTPException(
            status_code=409,
            detail=respuesta["mensaje"],
        )

    raise HTTPException(
        status_code=400,
        detail=respuesta["mensaje"],
    )


@app.post(
    "/apuestas/{id_apuesta}/selecciones",
    response_model=ApuestaAPI,
    status_code=201,
)
def api_agregar_seleccion_parlay(
    id_apuesta: int,
    datos: SeleccionParlayCrearAPI,
):
    """Agrega una selección a un parlay existente."""

    respuesta = agregar_seleccion_parlay_por_id(
        id_apuesta,
        datos,
    )

    if respuesta["ok"]:
        return respuesta["apuesta"]

    codigo = respuesta["codigo"]

    if codigo == "no_encontrada":
        raise HTTPException(
            status_code=404,
            detail=respuesta["mensaje"],
        )

    if codigo in {
        "modalidad_no_permitida",
        "estructura_invalida",
    }:
        raise HTTPException(
            status_code=409,
            detail=respuesta["mensaje"],
        )

    raise HTTPException(
        status_code=400,
        detail=respuesta["mensaje"],
    )


@app.delete(
    "/apuestas/{id_apuesta}/selecciones/{numero}",
    response_model=SeleccionEliminadaParlayAPI,
)
def api_eliminar_seleccion_parlay(
    id_apuesta: int,
    numero: int,
):
    """Elimina una selección de un parlay existente."""

    respuesta = eliminar_seleccion_parlay_por_id(
        id_apuesta,
        numero,
    )

    if respuesta["ok"]:
        return {
            "mensaje": respuesta["mensaje"],
            "numero_eliminado": numero,
            "seleccion_eliminada": (respuesta["seleccion_eliminada"]),
            "apuesta": respuesta["apuesta"],
        }

    codigo = respuesta["codigo"]

    if codigo == "no_encontrada":
        raise HTTPException(
            status_code=404,
            detail=respuesta["mensaje"],
        )

    if codigo in {
        "modalidad_no_permitida",
        "estructura_invalida",
        "minimo_selecciones",
    }:
        raise HTTPException(
            status_code=409,
            detail=respuesta["mensaje"],
        )

    if codigo in {
        "numero_invalido",
        "seleccion_fuera_rango",
    }:
        raise HTTPException(
            status_code=422,
            detail=respuesta["mensaje"],
        )

    raise HTTPException(
        status_code=400,
        detail=respuesta["mensaje"],
    )


@app.patch(
    "/apuestas/{id_apuesta}/selecciones/orden",
    response_model=ApuestaAPI,
)
def api_reordenar_selecciones_parlay(
    id_apuesta: int,
    datos: OrdenSeleccionesParlayAPI,
):
    """Reordena las selecciones de un parlay."""

    respuesta = reordenar_selecciones_parlay_por_id(
        id_apuesta,
        datos,
    )

    if respuesta["ok"]:
        return respuesta["apuesta"]

    codigo = respuesta["codigo"]

    if codigo == "no_encontrada":
        raise HTTPException(
            status_code=404,
            detail=respuesta["mensaje"],
        )

    if codigo in {
        "modalidad_no_permitida",
        "estructura_invalida",
    }:
        raise HTTPException(
            status_code=409,
            detail=respuesta["mensaje"],
        )

    if codigo in {
        "sin_orden",
        "orden_invalido",
        "orden_incompleto",
    }:
        raise HTTPException(
            status_code=422,
            detail=respuesta["mensaje"],
        )

    raise HTTPException(
        status_code=400,
        detail=respuesta["mensaje"],
    )
