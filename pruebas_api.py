"""Pruebas automatizadas de la API de TrackBet."""

# pylint: disable=too-many-lines
# pylint: disable=missing-function-docstring


from copy import deepcopy


from fastapi.testclient import TestClient
from pydantic import ValidationError

from almacenamiento import (
    cargar_apuestas,
    cargar_config,
    guardar_apuestas,
    guardar_config,
)
from api_trackbet import app
from validaciones import normalizar_texto
from modelos_api import (
    ApuestaAPI,
    ApuestaStraightCrearAPI,
    EstadoAPI,
    ListaApuestasAPI,
    ResumenFinancieroAPI,
    ApuestaParlayCrearAPI,
    EstadisticasAPI,
    AnalisisCuotasAPI,
    AnalisisParlaysAPI,
    DiagnosticoAPI,
)
from auditoria_api import (
    detectar_colisiones_exactas,
    detectar_metodos_no_permitidos,
    detectar_rutas_sin_modelo,
    detectar_sombras_dinamicas,
    obtener_metodos_por_ruta,
)

cliente = TestClient(app)

resultados_pruebas = {
    "correctas": 0,
    "fallidas": 0,
}


def comprobar(nombre, condicion):
    """Registra el resultado de una prueba de la API."""

    if condicion:
        resultados_pruebas["correctas"] += 1
        print(f"[CORRECTO] {nombre}")
    else:
        resultados_pruebas["fallidas"] += 1
        print(f"[ERROR] {nombre}")


def probar_estado_api():
    respuesta = cliente.get("/")
    datos = respuesta.json()

    comprobar(
        "API estado responde 200",
        respuesta.status_code == 200,
    )

    comprobar(
        "API devuelve nombre de aplicación",
        datos.get("aplicacion") == "TrackBet",
    )

    comprobar(
        "API informa que está funcionando",
        datos.get("estado") == "API funcionando",
    )


def probar_listado_apuestas():
    respuesta = cliente.get("/apuestas")
    datos = respuesta.json()

    comprobar(
        "API listado de apuestas responde 200",
        respuesta.status_code == 200,
    )

    comprobar(
        "API total de apuestas es entero",
        isinstance(datos.get("total"), int),
    )

    comprobar(
        "API apuestas es una lista",
        isinstance(datos.get("apuestas"), list),
    )

    comprobar(
        "API cantidad coincide con la lista",
        datos.get("cantidad") == len(datos.get("apuestas", [])),
    )

    comprobar(
        "API total es mayor o igual que cantidad",
        datos.get("total", 0) >= datos.get("cantidad", 0),
    )

    return datos.get("apuestas", [])


def probar_filtros_apuestas():
    respuesta_deporte = cliente.get(
        "/apuestas",
        params={
            "deporte": "futbol",
        },
    )

    datos_deporte = respuesta_deporte.json()
    apuestas_deporte = datos_deporte.get(
        "apuestas",
        [],
    )

    comprobar(
        "API filtro por deporte responde 200",
        respuesta_deporte.status_code == 200,
    )

    comprobar(
        "API filtro por deporte devuelve lista",
        isinstance(apuestas_deporte, list),
    )

    comprobar(
        "API filtro por deporte coincide",
        all(
            "futbol" in normalizar_texto(apuesta.get("deporte", ""))
            for apuesta in apuestas_deporte
        ),
    )

    respuesta_resultado = cliente.get(
        "/apuestas",
        params={
            "resultado": "ganada",
        },
    )

    datos_resultado = respuesta_resultado.json()
    apuestas_resultado = datos_resultado.get(
        "apuestas",
        [],
    )

    comprobar(
        "API filtro por resultado responde 200",
        respuesta_resultado.status_code == 200,
    )

    comprobar(
        "API filtro por resultado coincide",
        all(
            normalizar_texto(apuesta.get("resultado", "")) == "ganada"
            for apuesta in apuestas_resultado
        ),
    )

    respuesta_combinada = cliente.get(
        "/apuestas",
        params={
            "deporte": "futbol",
            "resultado": "ganada",
        },
    )

    datos_combinados = respuesta_combinada.json()
    apuestas_combinadas = datos_combinados.get(
        "apuestas",
        [],
    )

    comprobar(
        "API filtros combinados responden 200",
        respuesta_combinada.status_code == 200,
    )

    comprobar(
        "API filtros combinados coinciden",
        all(
            "futbol" in normalizar_texto(apuesta.get("deporte", ""))
            and normalizar_texto(apuesta.get("resultado", "")) == "ganada"
            for apuesta in apuestas_combinadas
        ),
    )


def probar_apuestas_pendientes():
    respuesta = cliente.get("/apuestas/pendientes")
    datos = respuesta.json()

    comprobar(
        "API pendientes responde 200",
        respuesta.status_code == 200,
    )

    comprobar(
        "API pendientes devuelve lista",
        isinstance(datos.get("apuestas"), list),
    )

    comprobar(
        "API total pendientes coincide",
        datos.get("total") == len(datos.get("apuestas", [])),
    )

    resultados_validos = all(
        str(apuesta.get("resultado", "")).strip().lower() == "pendiente"
        for apuesta in datos.get("apuestas", [])
    )

    comprobar(
        "API solo devuelve apuestas pendientes",
        resultados_validos,
    )


def probar_apuesta_por_id(apuestas):
    if apuestas:
        id_apuesta = apuestas[0].get("id")

        respuesta = cliente.get(f"/apuestas/{id_apuesta}")

        datos = respuesta.json()

        comprobar(
            "API apuesta por ID responde 200",
            respuesta.status_code == 200,
        )

        comprobar(
            "API devuelve el ID solicitado",
            datos.get("id") == id_apuesta,
        )

    respuesta_inexistente = cliente.get("/apuestas/999999999")

    comprobar(
        "API apuesta inexistente responde 404",
        respuesta_inexistente.status_code == 404,
    )

    comprobar(
        "API apuesta inexistente devuelve mensaje",
        respuesta_inexistente.json().get("detail") == "Apuesta no encontrada.",
    )


def probar_resumen_financiero():
    respuesta = cliente.get("/reportes/resumen-financiero")

    datos = respuesta.json()

    comprobar(
        "API resumen financiero responde 200",
        respuesta.status_code == 200,
    )

    comprobar(
        "API resumen financiero devuelve objeto",
        isinstance(datos, dict),
    )

    comprobar(
        "API resumen contiene bankroll",
        "bankroll_inicial" in datos,
    )

    comprobar(
        "API resumen contiene ROI",
        "roi" in datos,
    )


def probar_paginacion_apuestas():
    respuesta = cliente.get(
        "/apuestas",
        params={
            "limite": 5,
            "desplazamiento": 0,
            "orden": "desc",
        },
    )

    datos = respuesta.json()
    apuestas = datos.get("apuestas", [])

    comprobar(
        "API paginación responde 200",
        respuesta.status_code == 200,
    )

    comprobar(
        "API paginación respeta límite",
        len(apuestas) <= 5,
    )

    comprobar(
        "API paginación informa cantidad",
        datos.get("cantidad") == len(apuestas),
    )

    comprobar(
        "API paginación informa límite",
        datos.get("limite") == 5,
    )

    comprobar(
        "API orden descendente aplicado",
        apuestas
        == sorted(
            apuestas,
            key=lambda apuesta: int(apuesta.get("id", 0)),
            reverse=True,
        ),
    )

    respuesta_segunda_pagina = cliente.get(
        "/apuestas",
        params={
            "limite": 5,
            "desplazamiento": 5,
        },
    )

    comprobar(
        "API segunda página responde 200",
        respuesta_segunda_pagina.status_code == 200,
    )

    respuesta_limite_invalido = cliente.get(
        "/apuestas",
        params={
            "limite": 0,
        },
    )

    comprobar(
        "API rechaza límite inválido",
        respuesta_limite_invalido.status_code == 422,
    )


def probar_modelos_respuesta():
    respuesta_estado = cliente.get("/")
    modelo_estado = EstadoAPI.model_validate(respuesta_estado.json())

    comprobar(
        "Modelo API valida estado",
        modelo_estado.aplicacion == "TrackBet",
    )

    respuesta_apuestas = cliente.get(
        "/apuestas",
        params={
            "limite": 5,
        },
    )

    modelo_lista = ListaApuestasAPI.model_validate(respuesta_apuestas.json())

    comprobar(
        "Modelo API valida listado",
        modelo_lista.cantidad == len(modelo_lista.apuestas),
    )

    if modelo_lista.apuestas:
        apuesta = ApuestaAPI.model_validate(modelo_lista.apuestas[0])

        comprobar(
            "Modelo API valida apuesta",
            isinstance(apuesta.id, int),
        )

    respuesta_resumen = cliente.get("/reportes/resumen-financiero")

    modelo_resumen = ResumenFinancieroAPI.model_validate(respuesta_resumen.json())

    comprobar(
        "Modelo API valida resumen financiero",
        isinstance(modelo_resumen.roi, float),
    )


def modelo_straight_rechazado(datos):
    """Indica si Pydantic rechaza los datos recibidos."""

    try:
        ApuestaStraightCrearAPI.model_validate(datos)
        return False

    except ValidationError:
        return True


def probar_modelo_creacion_straight():
    datos_validos = {
        "casa": " Caliente ",
        "deporte": "Fútbol",
        "liga": "Liga MX",
        "evento": "América vs Pumas",
        "mercado": "Moneyline",
        "seleccion": "América",
        "momento_apuesta": "prepartido",
        "tipo_cuota": "decimal",
        "cuota": 1.90,
        "stake": 100,
    }

    modelo = ApuestaStraightCrearAPI.model_validate(datos_validos)

    comprobar(
        "Modelo creación straight válido",
        modelo.casa == "Caliente",
    )

    comprobar(
        "Modelo creación asigna modalidad straight",
        modelo.modalidad == "straight" and modelo.resultado == "pendiente",
    )

    datos_stake_invalido = dict(datos_validos)
    datos_stake_invalido["stake"] = 0

    comprobar(
        "Modelo creación rechaza stake inválido",
        modelo_straight_rechazado(datos_stake_invalido),
    )

    datos_decimal_invalida = dict(datos_validos)
    datos_decimal_invalida["cuota"] = 1.00

    comprobar(
        "Modelo creación rechaza cuota decimal inválida",
        modelo_straight_rechazado(datos_decimal_invalida),
    )

    datos_americana_invalida = dict(datos_validos)
    datos_americana_invalida["tipo_cuota"] = "americana"
    datos_americana_invalida["cuota"] = 50

    comprobar(
        "Modelo creación rechaza cuota americana inválida",
        modelo_straight_rechazado(datos_americana_invalida),
    )

    datos_con_campo_extra = dict(datos_validos)
    datos_con_campo_extra["campo_inventado"] = "valor"

    comprobar(
        "Modelo creación rechaza campos extra",
        modelo_straight_rechazado(datos_con_campo_extra),
    )


def probar_creacion_apuesta_straight_api():
    apuestas_originales = cargar_apuestas()

    total_original = len(apuestas_originales)

    ids_originales = {apuesta.get("id") for apuesta in apuestas_originales}

    datos_validos = {
        "casa": "Caliente",
        "deporte": "Fútbol",
        "liga": "Liga MX",
        "evento": "América vs Pumas",
        "mercado": "Moneyline",
        "seleccion": "América",
        "momento_apuesta": "prepartido",
        "tipo_cuota": "americana",
        "cuota": 120,
        "stake": 100,
    }

    try:
        respuesta = cliente.post(
            "/apuestas",
            json=datos_validos,
        )

        apuesta_creada = respuesta.json()

        comprobar(
            "API crear straight responde 201",
            respuesta.status_code == 201,
        )

        comprobar(
            "API crear straight asigna nuevo ID",
            isinstance(
                apuesta_creada.get("id"),
                int,
            )
            and apuesta_creada.get("id") not in ids_originales,
        )

        comprobar(
            "API crear straight fija modalidad",
            apuesta_creada.get("modalidad") == "straight",
        )

        comprobar(
            "API crear straight inicia pendiente",
            apuesta_creada.get("resultado") == "pendiente",
        )

        comprobar(
            "API crear straight conserva cuota americana",
            apuesta_creada.get("cuota_texto") == "+120",
        )

        comprobar(
            "API crear straight convierte cuota decimal",
            apuesta_creada.get("cuota") == 2.2,
        )

        listado = cliente.get(
            "/apuestas",
            params={
                "limite": 100,
            },
        ).json()

        comprobar(
            "API crear straight aumenta el total",
            listado.get("total") == total_original + 1,
        )

        datos_invalidos = dict(datos_validos)
        datos_invalidos["stake"] = 0

        respuesta_invalida = cliente.post(
            "/apuestas",
            json=datos_invalidos,
        )

        comprobar(
            "API crear straight rechaza stake inválido",
            respuesta_invalida.status_code == 422,
        )

    finally:
        guardar_apuestas(apuestas_originales)

    apuestas_restauradas = cargar_apuestas()

    comprobar(
        "API pruebas restauran apuestas originales",
        len(apuestas_restauradas) == total_original,
    )


def probar_actualizacion_resultado_straight_api():
    apuestas_originales = cargar_apuestas()
    total_original = len(apuestas_originales)

    datos_apuesta = {
        "casa": "Caliente",
        "deporte": "Fútbol",
        "liga": "Liga MX",
        "evento": "América vs Pumas",
        "mercado": "Moneyline",
        "seleccion": "América",
        "momento_apuesta": "prepartido",
        "tipo_cuota": "decimal",
        "cuota": 1.90,
        "stake": 100,
    }

    try:
        respuesta_creacion = cliente.post(
            "/apuestas",
            json=datos_apuesta,
        )

        comprobar(
            "API resultado crea apuesta temporal",
            respuesta_creacion.status_code == 201,
        )

        apuesta_creada = respuesta_creacion.json()
        id_apuesta = apuesta_creada.get("id")

        respuesta_actualizacion = cliente.patch(
            f"/apuestas/{id_apuesta}/resultado",
            json={
                "resultado": "ganada",
            },
        )

        apuesta_actualizada = respuesta_actualizacion.json()

        comprobar(
            "API actualizar resultado responde 200",
            respuesta_actualizacion.status_code == 200,
        )

        comprobar(
            "API actualizar resultado cambia a ganada",
            apuesta_actualizada.get("resultado") == "ganada",
        )

        respuesta_consulta = cliente.get(f"/apuestas/{id_apuesta}")

        comprobar(
            "API resultado actualizado queda guardado",
            respuesta_consulta.json().get("resultado") == "ganada",
        )

        respuesta_segundo_cierre = cliente.patch(
            f"/apuestas/{id_apuesta}/resultado",
            json={
                "resultado": "perdida",
            },
        )

        comprobar(
            "API impide cerrar apuesta resuelta",
            respuesta_segundo_cierre.status_code == 409,
        )

        respuesta_invalida = cliente.patch(
            f"/apuestas/{id_apuesta}/resultado",
            json={
                "resultado": "resultado_raro",
            },
        )

        comprobar(
            "API rechaza resultado inválido",
            respuesta_invalida.status_code == 422,
        )

        respuesta_inexistente = cliente.patch(
            "/apuestas/999999999/resultado",
            json={
                "resultado": "ganada",
            },
        )

        comprobar(
            "API resultado apuesta inexistente responde 404",
            respuesta_inexistente.status_code == 404,
        )

    finally:
        guardar_apuestas(apuestas_originales)

    apuestas_restauradas = cargar_apuestas()

    comprobar(
        "API resultado restaura apuestas originales",
        len(apuestas_restauradas) == total_original,
    )


def probar_eliminacion_apuesta_api():
    apuestas_originales = cargar_apuestas()

    total_original = len(apuestas_originales)

    ids_originales = [apuesta.get("id") for apuesta in apuestas_originales]

    datos_apuesta = {
        "casa": "Caliente",
        "deporte": "Fútbol",
        "liga": "Liga MX",
        "evento": "América vs Pumas",
        "mercado": "Moneyline",
        "seleccion": "América",
        "momento_apuesta": "prepartido",
        "tipo_cuota": "decimal",
        "cuota": 1.90,
        "stake": 100,
    }

    try:
        respuesta_creacion = cliente.post(
            "/apuestas",
            json=datos_apuesta,
        )

        comprobar(
            "API eliminar crea apuesta temporal",
            respuesta_creacion.status_code == 201,
        )

        apuesta_creada = respuesta_creacion.json()
        id_apuesta = apuesta_creada.get("id")

        respuesta_eliminacion = cliente.delete(f"/apuestas/{id_apuesta}")

        datos_eliminacion = respuesta_eliminacion.json()

        comprobar(
            "API eliminar apuesta responde 200",
            respuesta_eliminacion.status_code == 200,
        )

        comprobar(
            "API eliminar devuelve ID eliminado",
            datos_eliminacion.get("id_eliminado") == id_apuesta,
        )

        comprobar(
            "API eliminar devuelve apuesta eliminada",
            datos_eliminacion.get(
                "apuesta",
                {},
            ).get("id")
            == id_apuesta,
        )

        listado = cliente.get(
            "/apuestas",
            params={
                "limite": 100,
            },
        ).json()

        comprobar(
            "API eliminar restaura total previo",
            listado.get("total") == total_original,
        )

        respuesta_consulta = cliente.get(f"/apuestas/{id_apuesta}")

        comprobar(
            "API apuesta eliminada deja de existir",
            respuesta_consulta.status_code == 404,
        )

        respuesta_segunda_eliminacion = cliente.delete(f"/apuestas/{id_apuesta}")

        comprobar(
            "API impide eliminar dos veces",
            respuesta_segunda_eliminacion.status_code == 404,
        )

        respuesta_id_invalido = cliente.delete("/apuestas/id_invalido")

        comprobar(
            "API eliminar rechaza ID inválido",
            respuesta_id_invalido.status_code == 422,
        )

    finally:
        guardar_apuestas(apuestas_originales)

    apuestas_restauradas = cargar_apuestas()

    ids_restaurados = [apuesta.get("id") for apuesta in apuestas_restauradas]

    comprobar(
        "API eliminar restaura cantidad original",
        len(apuestas_restauradas) == total_original,
    )

    comprobar(
        "API eliminar restaura IDs originales",
        ids_restaurados == ids_originales,
    )


def probar_edicion_apuesta_straight_api():
    apuestas_originales = cargar_apuestas()

    total_original = len(apuestas_originales)

    ids_originales = [apuesta.get("id") for apuesta in apuestas_originales]

    datos_apuesta = {
        "casa": "Caliente",
        "deporte": "Fútbol",
        "liga": "Liga MX",
        "evento": "América vs Pumas",
        "mercado": "Moneyline",
        "seleccion": "América",
        "momento_apuesta": "prepartido",
        "tipo_cuota": "decimal",
        "cuota": 1.90,
        "stake": 100,
    }

    try:
        respuesta_creacion = cliente.post(
            "/apuestas",
            json=datos_apuesta,
        )

        comprobar(
            "API editar crea apuesta temporal",
            respuesta_creacion.status_code == 201,
        )

        apuesta_creada = respuesta_creacion.json()
        id_apuesta = apuesta_creada.get("id")

        cambios = {
            "casa": "Novibet",
            "evento": "América vs Cruz Azul",
            "mercado": "Over/Under",
            "seleccion": "Over 2.5",
            "tipo_cuota": "americana",
            "cuota": -110,
            "stake": 150,
        }

        respuesta_edicion = cliente.patch(
            f"/apuestas/{id_apuesta}",
            json=cambios,
        )

        apuesta_editada = respuesta_edicion.json()

        comprobar(
            "API editar straight responde 200",
            respuesta_edicion.status_code == 200,
        )

        comprobar(
            "API editar cambia casa",
            apuesta_editada.get("casa") == "Novibet",
        )

        seleccion_editada = apuesta_editada.get(
            "selecciones",
            [{}],
        )[0]

        comprobar(
            "API editar cambia selección interna",
            seleccion_editada.get("evento") == "América vs Cruz Azul"
            and seleccion_editada.get("tipo_apuesta") == "Over/Under"
            and seleccion_editada.get("seleccion") == "Over 2.5",
        )

        comprobar(
            "API editar cambia stake",
            apuesta_editada.get("stake") == 150.0,
        )

        comprobar(
            "API editar conserva resultado",
            apuesta_editada.get("resultado") == "pendiente",
        )

        comprobar(
            "API editar conserva cuota americana",
            apuesta_editada.get("cuota_texto") == "-110",
        )

        comprobar(
            "API editar convierte cuota decimal",
            abs(apuesta_editada.get("cuota", 0) - 1.9090909090909092) < 0.000001,
        )

        respuesta_consulta = cliente.get(f"/apuestas/{id_apuesta}")

        comprobar(
            "API edición queda guardada",
            respuesta_consulta.json().get("casa") == "Novibet",
        )

        respuesta_vacia = cliente.patch(
            f"/apuestas/{id_apuesta}",
            json={},
        )

        comprobar(
            "API editar rechaza cuerpo vacío",
            respuesta_vacia.status_code == 422,
        )

        respuesta_cuota_incompleta = cliente.patch(
            f"/apuestas/{id_apuesta}",
            json={
                "cuota": 2.10,
            },
        )

        comprobar(
            "API editar rechaza cuota incompleta",
            respuesta_cuota_incompleta.status_code == 422,
        )

        respuesta_inexistente = cliente.patch(
            "/apuestas/999999999",
            json={
                "casa": "Otra casa",
            },
        )

        comprobar(
            "API editar apuesta inexistente responde 404",
            respuesta_inexistente.status_code == 404,
        )

    finally:
        guardar_apuestas(apuestas_originales)

    apuestas_restauradas = cargar_apuestas()

    ids_restaurados = [apuesta.get("id") for apuesta in apuestas_restauradas]

    comprobar(
        "API editar restaura apuestas originales",
        len(apuestas_restauradas) == total_original
        and ids_restaurados == ids_originales,
    )


def probar_configuracion_bankroll_api():
    config_original = cargar_config()

    try:
        respuesta_consulta = cliente.get("/configuracion/bankroll")

        comprobar(
            "API consultar bankroll responde 200",
            respuesta_consulta.status_code == 200,
        )

        comprobar(
            "API consultar bankroll devuelve valor",
            isinstance(
                respuesta_consulta.json().get("bankroll_inicial"),
                float,
            ),
        )

        respuesta_actualizacion = cliente.put(
            "/configuracion/bankroll",
            json={
                "bankroll_inicial": 5000,
            },
        )

        comprobar(
            "API actualizar bankroll responde 200",
            respuesta_actualizacion.status_code == 200,
        )

        comprobar(
            "API actualizar bankroll guarda valor",
            respuesta_actualizacion.json().get("bankroll_inicial") == 5000.0,
        )

        respuesta_confirmacion = cliente.get("/configuracion/bankroll")

        comprobar(
            "API bankroll actualizado queda persistido",
            respuesta_confirmacion.json().get("bankroll_inicial") == 5000.0,
        )

        respuesta_negativa = cliente.put(
            "/configuracion/bankroll",
            json={
                "bankroll_inicial": -100,
            },
        )

        comprobar(
            "API rechaza bankroll negativo",
            respuesta_negativa.status_code == 422,
        )

        respuesta_extra = cliente.put(
            "/configuracion/bankroll",
            json={
                "bankroll_inicial": 5000,
                "campo_inventado": True,
            },
        )

        comprobar(
            "API bankroll rechaza campos extra",
            respuesta_extra.status_code == 422,
        )

    finally:
        guardar_config(config_original)

    config_restaurada = cargar_config()

    comprobar(
        "API bankroll restaura configuración original",
        config_restaurada == config_original,
    )


def modelo_parlay_rechazado(datos):
    """Indica si Pydantic rechaza los datos del parlay."""

    try:
        ApuestaParlayCrearAPI.model_validate(datos)
        return False

    except ValidationError:
        return True


def probar_modelo_creacion_parlay():
    datos_validos = {
        "casa": " Caliente ",
        "momento_apuesta": "prepartido",
        "tipo_cuota": "decimal",
        "cuota": 3.30,
        "stake": 100,
        "selecciones": [
            {
                "deporte": "Fútbol",
                "liga": "Liga MX",
                "evento": "América vs Pumas",
                "mercado": "Moneyline",
                "seleccion": "América",
                "tipo_cuota": "decimal",
                "cuota": 1.80,
            },
            {
                "deporte": "Béisbol",
                "liga": "MLB",
                "evento": "Yankees vs Red Sox",
                "mercado": "Moneyline",
                "seleccion": "Yankees",
                "tipo_cuota": "americana",
                "cuota": -110,
            },
        ],
    }

    modelo = ApuestaParlayCrearAPI.model_validate(datos_validos)

    comprobar(
        "Modelo creación parlay válido",
        modelo.casa == "Caliente" and len(modelo.selecciones) == 2,
    )

    comprobar(
        "Modelo parlay asigna modalidad y pendiente",
        modelo.modalidad == "parlay" and modelo.resultado == "pendiente",
    )

    comprobar(
        "Modelo parlay inicia selecciones pendientes",
        all(
            seleccion.resultado_seleccion == "pendiente"
            for seleccion in modelo.selecciones
        ),
    )

    datos_una_seleccion = deepcopy(datos_validos)
    datos_una_seleccion["selecciones"] = datos_una_seleccion["selecciones"][:1]

    comprobar(
        "Modelo parlay exige mínimo dos selecciones",
        modelo_parlay_rechazado(datos_una_seleccion),
    )

    datos_cuota_final_invalida = deepcopy(datos_validos)
    datos_cuota_final_invalida["cuota"] = 1.0

    comprobar(
        "Modelo parlay rechaza cuota final inválida",
        modelo_parlay_rechazado(datos_cuota_final_invalida),
    )

    datos_individual_decimal = deepcopy(datos_validos)
    datos_individual_decimal["selecciones"][0]["cuota"] = 1.0

    comprobar(
        "Modelo parlay rechaza cuota individual decimal",
        modelo_parlay_rechazado(datos_individual_decimal),
    )

    datos_individual_americana = deepcopy(datos_validos)
    datos_individual_americana["selecciones"][1]["cuota"] = 50

    comprobar(
        "Modelo parlay rechaza cuota individual americana",
        modelo_parlay_rechazado(datos_individual_americana),
    )

    datos_campo_extra = deepcopy(datos_validos)
    datos_campo_extra["campo_inventado"] = "valor"

    comprobar(
        "Modelo parlay rechaza campos extra",
        modelo_parlay_rechazado(datos_campo_extra),
    )


def probar_creacion_apuesta_parlay_api():
    apuestas_originales = cargar_apuestas()

    total_original = len(apuestas_originales)

    ids_originales = [apuesta.get("id") for apuesta in apuestas_originales]

    datos_parlay = {
        "casa": "Caliente",
        "momento_apuesta": "prepartido",
        "tipo_cuota": "decimal",
        "cuota": 3.30,
        "stake": 100,
        "selecciones": [
            {
                "deporte": "Fútbol",
                "liga": "Liga MX",
                "evento": "América vs Pumas",
                "mercado": "Moneyline",
                "seleccion": "América",
                "tipo_cuota": "decimal",
                "cuota": 1.80,
            },
            {
                "deporte": "Béisbol",
                "liga": "MLB",
                "evento": "Yankees vs Red Sox",
                "mercado": "Moneyline",
                "seleccion": "Yankees",
                "tipo_cuota": "americana",
                "cuota": -110,
            },
        ],
    }

    try:
        respuesta = cliente.post(
            "/apuestas/parlay",
            json=datos_parlay,
        )

        apuesta_creada = respuesta.json()
        id_apuesta = apuesta_creada.get("id")

        comprobar(
            "API crear parlay responde 201",
            respuesta.status_code == 201,
        )

        comprobar(
            "API crear parlay asigna nuevo ID",
            isinstance(id_apuesta, int) and id_apuesta not in ids_originales,
        )

        comprobar(
            "API crear parlay fija modalidad y pendiente",
            apuesta_creada.get("modalidad") == "parlay"
            and apuesta_creada.get("resultado") == "pendiente",
        )

        selecciones = apuesta_creada.get(
            "selecciones",
            [],
        )

        comprobar(
            "API crear parlay guarda selecciones",
            len(selecciones) == 2,
        )

        comprobar(
            "API crear parlay detecta mezcla",
            apuesta_creada.get("deporte") == "Mixto"
            and apuesta_creada.get("liga") == "Mixta",
        )

        comprobar(
            "API parlay conserva cuota americana individual",
            selecciones[1].get("cuota_texto_individual") == "-110",
        )

        comprobar(
            "API parlay convierte cuota individual",
            abs(
                selecciones[1].get(
                    "cuota_individual",
                    0,
                )
                - 1.9090909090909092
            )
            < 0.000001,
        )

        listado = cliente.get(
            "/apuestas",
            params={
                "limite": 100,
            },
        ).json()

        comprobar(
            "API crear parlay aumenta el total",
            listado.get("total") == total_original + 1,
        )

        respuesta_consulta = cliente.get(f"/apuestas/{id_apuesta}")

        comprobar(
            "API parlay creado queda guardado",
            respuesta_consulta.status_code == 200
            and respuesta_consulta.json().get("modalidad") == "parlay",
        )

        datos_una_seleccion = {
            **datos_parlay,
            "selecciones": datos_parlay["selecciones"][:1],
        }

        respuesta_una_seleccion = cliente.post(
            "/apuestas/parlay",
            json=datos_una_seleccion,
        )

        comprobar(
            "API parlay rechaza una sola selección",
            respuesta_una_seleccion.status_code == 422,
        )

        datos_cuota_invalida = {
            **datos_parlay,
            "selecciones": [
                dict(seleccion) for seleccion in datos_parlay["selecciones"]
            ],
        }

        datos_cuota_invalida["selecciones"][0]["cuota"] = 1.0

        respuesta_cuota_invalida = cliente.post(
            "/apuestas/parlay",
            json=datos_cuota_invalida,
        )

        comprobar(
            "API parlay rechaza cuota individual inválida",
            respuesta_cuota_invalida.status_code == 422,
        )

    finally:
        guardar_apuestas(apuestas_originales)

    apuestas_restauradas = cargar_apuestas()

    ids_restaurados = [apuesta.get("id") for apuesta in apuestas_restauradas]

    comprobar(
        "API parlay restaura apuestas originales",
        len(apuestas_restauradas) == total_original
        and ids_restaurados == ids_originales,
    )


def probar_actualizacion_selecciones_parlay_api():
    apuestas_originales = cargar_apuestas()

    total_original = len(apuestas_originales)

    datos_parlay = {
        "casa": "Caliente",
        "momento_apuesta": "prepartido",
        "tipo_cuota": "decimal",
        "cuota": 3.30,
        "stake": 100,
        "selecciones": [
            {
                "deporte": "Fútbol",
                "liga": "Liga MX",
                "evento": "América vs Pumas",
                "mercado": "Moneyline",
                "seleccion": "América",
                "tipo_cuota": "decimal",
                "cuota": 1.80,
            },
            {
                "deporte": "Béisbol",
                "liga": "MLB",
                "evento": "Yankees vs Red Sox",
                "mercado": "Moneyline",
                "seleccion": "Yankees",
                "tipo_cuota": "americana",
                "cuota": -110,
            },
        ],
    }

    datos_straight = {
        "casa": "Caliente",
        "deporte": "Fútbol",
        "liga": "Liga MX",
        "evento": "América vs Pumas",
        "mercado": "Moneyline",
        "seleccion": "América",
        "momento_apuesta": "prepartido",
        "tipo_cuota": "decimal",
        "cuota": 1.90,
        "stake": 100,
    }

    try:
        respuesta_creacion = cliente.post(
            "/apuestas/parlay",
            json=datos_parlay,
        )

        comprobar(
            "API selecciones crea parlay temporal",
            respuesta_creacion.status_code == 201,
        )

        parlay = respuesta_creacion.json()
        id_parlay = parlay.get("id")

        respuesta_parcial = cliente.patch(
            f"/apuestas/{id_parlay}/selecciones",
            json={
                "selecciones": [
                    {
                        "numero": 1,
                        "resultado": "ganada",
                    }
                ]
            },
        )

        parlay_parcial = respuesta_parcial.json()

        comprobar(
            "API actualizar selección responde 200",
            respuesta_parcial.status_code == 200,
        )

        comprobar(
            "API actualiza selección indicada",
            parlay_parcial.get(
                "selecciones",
                [{}],
            )[
                0
            ].get("resultado_seleccion")
            == "ganada",
        )

        comprobar(
            "API conserva otras selecciones pendientes",
            parlay_parcial.get(
                "selecciones",
                [{}, {}],
            )[
                1
            ].get("resultado_seleccion")
            == "pendiente",
        )

        comprobar(
            "API parlay parcial continúa pendiente",
            parlay_parcial.get("resultado") == "pendiente",
        )

        respuesta_ganada = cliente.patch(
            f"/apuestas/{id_parlay}/selecciones",
            json={
                "selecciones": [
                    {
                        "numero": 2,
                        "resultado": "push",
                    }
                ]
            },
        )

        comprobar(
            "API parlay ganada con ganada y push",
            respuesta_ganada.status_code == 200
            and respuesta_ganada.json().get("resultado") == "ganada",
        )

        respuesta_push = cliente.patch(
            f"/apuestas/{id_parlay}/selecciones",
            json={
                "selecciones": [
                    {
                        "numero": 1,
                        "resultado": "push",
                    }
                ]
            },
        )

        comprobar(
            "API parlay todas push resulta push",
            respuesta_push.json().get("resultado") == "push",
        )

        respuesta_perdida = cliente.patch(
            f"/apuestas/{id_parlay}/selecciones",
            json={
                "selecciones": [
                    {
                        "numero": 1,
                        "resultado": "perdida",
                    }
                ]
            },
        )

        comprobar(
            "API selección perdida determina parlay perdido",
            respuesta_perdida.json().get("resultado") == "perdida",
        )

        respuesta_fuera_rango = cliente.patch(
            f"/apuestas/{id_parlay}/selecciones",
            json={
                "selecciones": [
                    {
                        "numero": 99,
                        "resultado": "ganada",
                    }
                ]
            },
        )

        comprobar(
            "API rechaza selección fuera de rango",
            respuesta_fuera_rango.status_code == 422,
        )

        respuesta_repetida = cliente.patch(
            f"/apuestas/{id_parlay}/selecciones",
            json={
                "selecciones": [
                    {
                        "numero": 1,
                        "resultado": "ganada",
                    },
                    {
                        "numero": 1,
                        "resultado": "push",
                    },
                ]
            },
        )

        comprobar(
            "API rechaza número de selección repetido",
            respuesta_repetida.status_code == 422,
        )

        respuesta_resultado_invalido = cliente.patch(
            f"/apuestas/{id_parlay}/selecciones",
            json={
                "selecciones": [
                    {
                        "numero": 1,
                        "resultado": "resultado_raro",
                    }
                ]
            },
        )

        comprobar(
            "API rechaza resultado de selección inválido",
            respuesta_resultado_invalido.status_code == 422,
        )

        respuesta_straight = cliente.post(
            "/apuestas",
            json=datos_straight,
        )

        id_straight = respuesta_straight.json().get("id")

        respuesta_modalidad = cliente.patch(
            f"/apuestas/{id_straight}/selecciones",
            json={
                "selecciones": [
                    {
                        "numero": 1,
                        "resultado": "ganada",
                    }
                ]
            },
        )

        comprobar(
            "API impide actualizar selecciones de straight",
            respuesta_modalidad.status_code == 409,
        )

        respuesta_inexistente = cliente.patch(
            "/apuestas/999999999/selecciones",
            json={
                "selecciones": [
                    {
                        "numero": 1,
                        "resultado": "ganada",
                    }
                ]
            },
        )

        comprobar(
            "API selecciones apuesta inexistente responde 404",
            respuesta_inexistente.status_code == 404,
        )

    finally:
        guardar_apuestas(apuestas_originales)

    apuestas_restauradas = cargar_apuestas()

    comprobar(
        "API selecciones restaura apuestas originales",
        len(apuestas_restauradas) == total_original,
    )


def probar_edicion_apuesta_parlay_api():
    apuestas_originales = cargar_apuestas()

    total_original = len(apuestas_originales)

    ids_originales = [apuesta.get("id") for apuesta in apuestas_originales]

    datos_parlay = {
        "casa": "Caliente",
        "momento_apuesta": "prepartido",
        "tipo_cuota": "decimal",
        "cuota": 3.30,
        "stake": 100,
        "selecciones": [
            {
                "deporte": "Fútbol",
                "liga": "Liga MX",
                "evento": "América vs Pumas",
                "mercado": "Moneyline",
                "seleccion": "América",
                "tipo_cuota": "decimal",
                "cuota": 1.80,
            },
            {
                "deporte": "Béisbol",
                "liga": "MLB",
                "evento": "Yankees vs Red Sox",
                "mercado": "Moneyline",
                "seleccion": "Yankees",
                "tipo_cuota": "americana",
                "cuota": -110,
            },
        ],
    }

    datos_straight = {
        "casa": "Caliente",
        "deporte": "Fútbol",
        "liga": "Liga MX",
        "evento": "América vs Pumas",
        "mercado": "Moneyline",
        "seleccion": "América",
        "momento_apuesta": "prepartido",
        "tipo_cuota": "decimal",
        "cuota": 1.90,
        "stake": 100,
    }

    try:
        respuesta_creacion = cliente.post(
            "/apuestas/parlay",
            json=datos_parlay,
        )

        comprobar(
            "API editar parlay crea temporal",
            respuesta_creacion.status_code == 201,
        )

        parlay = respuesta_creacion.json()
        id_parlay = parlay.get("id")

        cambios = {
            "casa": "Novibet",
            "momento_apuesta": "en_vivo",
            "tipo_cuota": "americana",
            "cuota": 250,
            "stake": 200,
            "selecciones": [
                {
                    "numero": 1,
                    "evento": "América vs Cruz Azul",
                    "mercado": "Over/Under",
                    "seleccion": "Over 2.5",
                    "tipo_cuota": "americana",
                    "cuota": -105,
                },
                {
                    "numero": 2,
                    "deporte": "Fútbol",
                    "liga": "Liga MX",
                },
            ],
        }

        respuesta_edicion = cliente.patch(
            f"/apuestas/{id_parlay}/parlay",
            json=cambios,
        )

        parlay_editado = respuesta_edicion.json()

        comprobar(
            "API editar parlay responde 200",
            respuesta_edicion.status_code == 200,
        )

        comprobar(
            "API editar parlay cambia datos generales",
            parlay_editado.get("casa") == "Novibet"
            and parlay_editado.get("momento_apuesta") == "en_vivo"
            and parlay_editado.get("stake") == 200.0,
        )

        comprobar(
            "API editar parlay cambia cuota final",
            parlay_editado.get("cuota_texto") == "+250"
            and abs(parlay_editado.get("cuota", 0) - 3.5) < 0.000001,
        )

        selecciones = parlay_editado.get(
            "selecciones",
            [],
        )

        comprobar(
            "API editar parlay cambia selección",
            selecciones[0].get("evento") == "América vs Cruz Azul"
            and selecciones[0].get("tipo_apuesta") == "Over/Under"
            and selecciones[0].get("seleccion") == "Over 2.5",
        )

        comprobar(
            "API editar parlay cambia cuota individual",
            selecciones[0].get("cuota_texto_individual") == "-105"
            and abs(
                selecciones[0].get(
                    "cuota_individual",
                    0,
                )
                - 1.9523809523809523
            )
            < 0.000001,
        )

        comprobar(
            "API editar parlay recalcula deporte y liga",
            parlay_editado.get("deporte") == "Fútbol"
            and parlay_editado.get("liga") == "Liga MX",
        )

        comprobar(
            "API editar parlay conserva resultados",
            parlay_editado.get("resultado") == "pendiente"
            and all(
                seleccion.get("resultado_seleccion") == "pendiente"
                for seleccion in selecciones
            ),
        )

        respuesta_consulta = cliente.get(f"/apuestas/{id_parlay}")

        comprobar(
            "API edición parlay queda guardada",
            respuesta_consulta.status_code == 200
            and respuesta_consulta.json().get("casa") == "Novibet",
        )

        respuesta_vacia = cliente.patch(
            f"/apuestas/{id_parlay}/parlay",
            json={},
        )

        comprobar(
            "API editar parlay rechaza cuerpo vacío",
            respuesta_vacia.status_code == 422,
        )

        respuesta_cuota_incompleta = cliente.patch(
            f"/apuestas/{id_parlay}/parlay",
            json={
                "cuota": 4.0,
            },
        )

        comprobar(
            "API editar parlay rechaza cuota incompleta",
            respuesta_cuota_incompleta.status_code == 422,
        )

        respuesta_individual_incompleta = cliente.patch(
            f"/apuestas/{id_parlay}/parlay",
            json={
                "selecciones": [
                    {
                        "numero": 1,
                        "cuota": 2.0,
                    }
                ]
            },
        )

        comprobar(
            "API editar rechaza cuota individual incompleta",
            respuesta_individual_incompleta.status_code == 422,
        )

        respuesta_fuera_rango = cliente.patch(
            f"/apuestas/{id_parlay}/parlay",
            json={
                "selecciones": [
                    {
                        "numero": 99,
                        "evento": "Evento inexistente",
                    }
                ]
            },
        )

        comprobar(
            "API editar parlay rechaza número fuera de rango",
            respuesta_fuera_rango.status_code == 422,
        )

        respuesta_straight = cliente.post(
            "/apuestas",
            json=datos_straight,
        )

        id_straight = respuesta_straight.json().get("id")

        respuesta_modalidad = cliente.patch(
            f"/apuestas/{id_straight}/parlay",
            json={
                "casa": "Novibet",
            },
        )

        comprobar(
            "API impide editar straight como parlay",
            respuesta_modalidad.status_code == 409,
        )

        respuesta_inexistente = cliente.patch(
            "/apuestas/999999999/parlay",
            json={
                "casa": "Novibet",
            },
        )

        comprobar(
            "API editar parlay inexistente responde 404",
            respuesta_inexistente.status_code == 404,
        )

    finally:
        guardar_apuestas(apuestas_originales)

    apuestas_restauradas = cargar_apuestas()

    ids_restaurados = [apuesta.get("id") for apuesta in apuestas_restauradas]

    comprobar(
        "API editar parlay restaura originales",
        len(apuestas_restauradas) == total_original
        and ids_restaurados == ids_originales,
    )


def probar_agregar_seleccion_parlay_api():
    apuestas_originales = cargar_apuestas()

    total_original = len(apuestas_originales)

    datos_parlay = {
        "casa": "Caliente",
        "momento_apuesta": "prepartido",
        "tipo_cuota": "decimal",
        "cuota": 3.30,
        "stake": 100,
        "selecciones": [
            {
                "deporte": "Fútbol",
                "liga": "Liga MX",
                "evento": "América vs Pumas",
                "mercado": "Moneyline",
                "seleccion": "América",
                "tipo_cuota": "decimal",
                "cuota": 1.80,
            },
            {
                "deporte": "Béisbol",
                "liga": "MLB",
                "evento": "Yankees vs Red Sox",
                "mercado": "Moneyline",
                "seleccion": "Yankees",
                "tipo_cuota": "americana",
                "cuota": -110,
            },
        ],
    }

    datos_straight = {
        "casa": "Caliente",
        "deporte": "Fútbol",
        "liga": "Liga MX",
        "evento": "América vs Pumas",
        "mercado": "Moneyline",
        "seleccion": "América",
        "momento_apuesta": "prepartido",
        "tipo_cuota": "decimal",
        "cuota": 1.90,
        "stake": 100,
    }

    nueva_seleccion = {
        "deporte": "Hockey",
        "liga": "NHL",
        "evento": "Oilers vs Flames",
        "mercado": "Moneyline",
        "seleccion": "Oilers",
        "tipo_cuota": "americana",
        "cuota": 120,
    }

    try:
        respuesta_creacion = cliente.post(
            "/apuestas/parlay",
            json=datos_parlay,
        )

        comprobar(
            "API agregar selección crea parlay temporal",
            respuesta_creacion.status_code == 201,
        )

        parlay = respuesta_creacion.json()
        id_parlay = parlay.get("id")

        respuesta_agregar = cliente.post(
            f"/apuestas/{id_parlay}/selecciones",
            json=nueva_seleccion,
        )

        parlay_actualizado = respuesta_agregar.json()

        comprobar(
            "API agregar selección responde 201",
            respuesta_agregar.status_code == 201,
        )

        selecciones = parlay_actualizado.get(
            "selecciones",
            [],
        )

        comprobar(
            "API agregar selección aumenta cantidad",
            len(selecciones) == 3,
        )

        seleccion_agregada = selecciones[-1]

        comprobar(
            "API agregar selección guarda datos",
            seleccion_agregada.get("deporte") == "Hockey"
            and seleccion_agregada.get("liga") == "NHL"
            and seleccion_agregada.get("tipo_apuesta") == "Moneyline",
        )

        comprobar(
            "API agregar selección conserva cuota americana",
            seleccion_agregada.get("cuota_texto_individual") == "+120",
        )

        comprobar(
            "API agregar selección convierte cuota decimal",
            abs(
                seleccion_agregada.get(
                    "cuota_individual",
                    0,
                )
                - 2.2
            )
            < 0.000001,
        )

        comprobar(
            "API agregar selección inicia pendiente",
            seleccion_agregada.get("resultado_seleccion") == "pendiente"
            and parlay_actualizado.get("resultado") == "pendiente",
        )

        respuesta_consulta = cliente.get(f"/apuestas/{id_parlay}")

        comprobar(
            "API selección agregada queda guardada",
            len(
                respuesta_consulta.json().get(
                    "selecciones",
                    [],
                )
            )
            == 3,
        )

        respuesta_straight = cliente.post(
            "/apuestas",
            json=datos_straight,
        )

        id_straight = respuesta_straight.json().get("id")

        respuesta_modalidad = cliente.post(
            f"/apuestas/{id_straight}/selecciones",
            json=nueva_seleccion,
        )

        comprobar(
            "API impide agregar selección a straight",
            respuesta_modalidad.status_code == 409,
        )

        respuesta_inexistente = cliente.post(
            "/apuestas/999999999/selecciones",
            json=nueva_seleccion,
        )

        comprobar(
            "API agregar selección inexistente responde 404",
            respuesta_inexistente.status_code == 404,
        )

        seleccion_invalida = dict(nueva_seleccion)
        seleccion_invalida["cuota"] = 50

        respuesta_invalida = cliente.post(
            f"/apuestas/{id_parlay}/selecciones",
            json=seleccion_invalida,
        )

        comprobar(
            "API agregar selección rechaza cuota inválida",
            respuesta_invalida.status_code == 422,
        )

    finally:
        guardar_apuestas(apuestas_originales)

    apuestas_restauradas = cargar_apuestas()

    comprobar(
        "API agregar selección restaura originales",
        len(apuestas_restauradas) == total_original,
    )


def probar_eliminar_seleccion_parlay_api():
    apuestas_originales = cargar_apuestas()

    total_original = len(apuestas_originales)

    ids_originales = [apuesta.get("id") for apuesta in apuestas_originales]

    datos_parlay = {
        "casa": "Caliente",
        "momento_apuesta": "prepartido",
        "tipo_cuota": "decimal",
        "cuota": 5.20,
        "stake": 100,
        "selecciones": [
            {
                "deporte": "Fútbol",
                "liga": "Liga MX",
                "evento": "América vs Pumas",
                "mercado": "Moneyline",
                "seleccion": "América",
                "tipo_cuota": "decimal",
                "cuota": 1.80,
            },
            {
                "deporte": "Béisbol",
                "liga": "MLB",
                "evento": "Yankees vs Red Sox",
                "mercado": "Moneyline",
                "seleccion": "Yankees",
                "tipo_cuota": "americana",
                "cuota": -110,
            },
            {
                "deporte": "Fútbol",
                "liga": "Liga MX",
                "evento": "Tigres vs Monterrey",
                "mercado": "Over/Under",
                "seleccion": "Over 2.5",
                "tipo_cuota": "decimal",
                "cuota": 1.70,
            },
        ],
    }

    datos_straight = {
        "casa": "Caliente",
        "deporte": "Fútbol",
        "liga": "Liga MX",
        "evento": "América vs Pumas",
        "mercado": "Moneyline",
        "seleccion": "América",
        "momento_apuesta": "prepartido",
        "tipo_cuota": "decimal",
        "cuota": 1.90,
        "stake": 100,
    }

    try:
        respuesta_creacion = cliente.post(
            "/apuestas/parlay",
            json=datos_parlay,
        )

        comprobar(
            "API eliminar selección crea parlay temporal",
            respuesta_creacion.status_code == 201,
        )

        parlay = respuesta_creacion.json()
        id_parlay = parlay.get("id")

        respuesta_eliminacion = cliente.delete(f"/apuestas/{id_parlay}/selecciones/2")

        datos_eliminacion = respuesta_eliminacion.json()

        comprobar(
            "API eliminar selección responde 200",
            respuesta_eliminacion.status_code == 200,
        )

        comprobar(
            "API eliminar selección devuelve número",
            datos_eliminacion.get("numero_eliminado") == 2,
        )

        comprobar(
            "API eliminar devuelve selección correcta",
            datos_eliminacion.get(
                "seleccion_eliminada",
                {},
            ).get("evento")
            == "Yankees vs Red Sox",
        )

        parlay_actualizado = datos_eliminacion.get(
            "apuesta",
            {},
        )

        selecciones = parlay_actualizado.get(
            "selecciones",
            [],
        )

        comprobar(
            "API eliminar selección reduce cantidad",
            len(selecciones) == 2,
        )

        comprobar(
            "API eliminar selección conserva orden",
            selecciones[0].get("evento") == "América vs Pumas"
            and selecciones[1].get("evento") == "Tigres vs Monterrey",
        )

        comprobar(
            "API eliminar recalcula deporte y liga",
            parlay_actualizado.get("deporte") == "Fútbol"
            and parlay_actualizado.get("liga") == "Liga MX",
        )

        respuesta_consulta = cliente.get(f"/apuestas/{id_parlay}")

        comprobar(
            "API eliminación de selección queda guardada",
            len(
                respuesta_consulta.json().get(
                    "selecciones",
                    [],
                )
            )
            == 2,
        )

        respuesta_minimo = cliente.delete(f"/apuestas/{id_parlay}/selecciones/1")

        comprobar(
            "API impide dejar menos de dos selecciones",
            respuesta_minimo.status_code == 409,
        )

        respuesta_fuera_rango = cliente.delete(f"/apuestas/{id_parlay}/selecciones/99")

        comprobar(
            "API eliminar rechaza número fuera de rango",
            respuesta_fuera_rango.status_code == 422,
        )

        respuesta_straight = cliente.post(
            "/apuestas",
            json=datos_straight,
        )

        id_straight = respuesta_straight.json().get("id")

        respuesta_modalidad = cliente.delete(f"/apuestas/{id_straight}/selecciones/1")

        comprobar(
            "API impide eliminar selección de straight",
            respuesta_modalidad.status_code == 409,
        )

        respuesta_inexistente = cliente.delete("/apuestas/999999999/selecciones/1")

        comprobar(
            "API eliminar selección inexistente responde 404",
            respuesta_inexistente.status_code == 404,
        )

        respuesta_id_invalido = cliente.delete("/apuestas/id_invalido/selecciones/1")

        comprobar(
            "API eliminar selección rechaza ID inválido",
            respuesta_id_invalido.status_code == 422,
        )

    finally:
        guardar_apuestas(apuestas_originales)

    apuestas_restauradas = cargar_apuestas()

    ids_restaurados = [apuesta.get("id") for apuesta in apuestas_restauradas]

    comprobar(
        "API eliminar selección restaura originales",
        len(apuestas_restauradas) == total_original
        and ids_restaurados == ids_originales,
    )


def probar_reordenar_selecciones_parlay_api():
    apuestas_originales = cargar_apuestas()

    total_original = len(apuestas_originales)

    datos_parlay = {
        "casa": "Caliente",
        "momento_apuesta": "prepartido",
        "tipo_cuota": "decimal",
        "cuota": 5.20,
        "stake": 100,
        "selecciones": [
            {
                "deporte": "Fútbol",
                "liga": "Liga MX",
                "evento": "Evento número uno",
                "mercado": "Moneyline",
                "seleccion": "Selección uno",
                "tipo_cuota": "decimal",
                "cuota": 1.80,
            },
            {
                "deporte": "Béisbol",
                "liga": "MLB",
                "evento": "Evento número dos",
                "mercado": "Moneyline",
                "seleccion": "Selección dos",
                "tipo_cuota": "americana",
                "cuota": -110,
            },
            {
                "deporte": "Hockey",
                "liga": "NHL",
                "evento": "Evento número tres",
                "mercado": "Moneyline",
                "seleccion": "Selección tres",
                "tipo_cuota": "decimal",
                "cuota": 1.70,
            },
        ],
    }

    datos_straight = {
        "casa": "Caliente",
        "deporte": "Fútbol",
        "liga": "Liga MX",
        "evento": "América vs Pumas",
        "mercado": "Moneyline",
        "seleccion": "América",
        "momento_apuesta": "prepartido",
        "tipo_cuota": "decimal",
        "cuota": 1.90,
        "stake": 100,
    }

    try:
        respuesta_creacion = cliente.post(
            "/apuestas/parlay",
            json=datos_parlay,
        )

        comprobar(
            "API reordenar crea parlay temporal",
            respuesta_creacion.status_code == 201,
        )

        id_parlay = respuesta_creacion.json().get("id")

        respuesta_orden = cliente.patch(
            f"/apuestas/{id_parlay}/selecciones/orden",
            json={
                "orden": [3, 1, 2],
            },
        )

        parlay_reordenado = respuesta_orden.json()

        comprobar(
            "API reordenar selecciones responde 200",
            respuesta_orden.status_code == 200,
        )

        selecciones = parlay_reordenado.get(
            "selecciones",
            [],
        )

        eventos = [seleccion.get("evento") for seleccion in selecciones]

        comprobar(
            "API aplica el nuevo orden",
            eventos
            == [
                "Evento número tres",
                "Evento número uno",
                "Evento número dos",
            ],
        )

        comprobar(
            "API reordenar conserva cantidad",
            len(selecciones) == 3,
        )

        respuesta_consulta = cliente.get(f"/apuestas/{id_parlay}")

        eventos_guardados = [
            seleccion.get("evento")
            for seleccion in (
                respuesta_consulta.json().get(
                    "selecciones",
                    [],
                )
            )
        ]

        comprobar(
            "API nuevo orden queda guardado",
            eventos_guardados == eventos,
        )

        respuesta_incompleta = cliente.patch(
            f"/apuestas/{id_parlay}/selecciones/orden",
            json={
                "orden": [1, 2],
            },
        )

        comprobar(
            "API rechaza orden incompleto",
            respuesta_incompleta.status_code == 422,
        )

        respuesta_repetida = cliente.patch(
            f"/apuestas/{id_parlay}/selecciones/orden",
            json={
                "orden": [1, 1, 2],
            },
        )

        comprobar(
            "API rechaza orden repetido",
            respuesta_repetida.status_code == 422,
        )

        respuesta_fuera_rango = cliente.patch(
            f"/apuestas/{id_parlay}/selecciones/orden",
            json={
                "orden": [1, 2, 4],
            },
        )

        comprobar(
            "API rechaza orden fuera de rango",
            respuesta_fuera_rango.status_code == 422,
        )

        respuesta_straight = cliente.post(
            "/apuestas",
            json=datos_straight,
        )

        id_straight = respuesta_straight.json().get("id")

        respuesta_modalidad = cliente.patch(
            f"/apuestas/{id_straight}/selecciones/orden",
            json={
                "orden": [1, 2],
            },
        )

        comprobar(
            "API impide reordenar una straight",
            respuesta_modalidad.status_code == 409,
        )

        respuesta_inexistente = cliente.patch(
            "/apuestas/999999999/selecciones/orden",
            json={
                "orden": [1, 2],
            },
        )

        comprobar(
            "API reordenar parlay inexistente responde 404",
            respuesta_inexistente.status_code == 404,
        )

    finally:
        guardar_apuestas(apuestas_originales)

    apuestas_restauradas = cargar_apuestas()

    comprobar(
        "API reordenar restaura apuestas originales",
        len(apuestas_restauradas) == total_original,
    )


def probar_estadisticas_api():
    respuesta = cliente.get("/estadisticas")

    datos = respuesta.json()

    comprobar(
        "API estadísticas responde 200",
        respuesta.status_code == 200,
    )

    modelo = EstadisticasAPI.model_validate(datos)

    comprobar(
        "API modelo valida estadísticas",
        isinstance(
            modelo.roi,
            float,
        ),
    )

    comprobar(
        "API estadísticas contiene resultados",
        isinstance(
            datos.get("ganadas"),
            int,
        )
        and isinstance(
            datos.get("perdidas"),
            int,
        ),
    )

    comprobar(
        "API estadísticas contiene métricas",
        isinstance(
            datos.get("win_rate"),
            float,
        )
        and isinstance(
            datos.get("roi"),
            float,
        ),
    )

    comprobar(
        "API estadísticas contiene rendimientos",
        isinstance(
            datos.get("rendimiento_deportes"),
            dict,
        )
        and isinstance(
            datos.get("rendimiento_mercados"),
            dict,
        ),
    )

    comprobar(
        "API estadísticas contiene momentos",
        isinstance(
            datos.get("rendimiento_momentos"),
            dict,
        ),
    )

    comprobar(
        "API estadísticas contiene stakes recomendados",
        isinstance(
            datos.get("stakes_recomendados"),
            dict,
        ),
    )

    comprobar(
        "API estadísticas contiene alertas",
        isinstance(
            datos.get("alertas"),
            list,
        ),
    )


def probar_analisis_cuotas_api():
    respuesta = cliente.get("/analiticas/cuotas")

    datos = respuesta.json()

    comprobar(
        "API analíticas cuotas responde 200",
        respuesta.status_code == 200,
    )

    modelo = AnalisisCuotasAPI.model_validate(datos)

    comprobar(
        "API modelo valida analíticas de cuotas",
        isinstance(
            modelo.apuestas_validas,
            int,
        ),
    )

    comprobar(
        "API analíticas contiene total",
        isinstance(
            datos.get("total_apuestas"),
            int,
        ),
    )

    comprobar(
        "API analíticas contiene apuestas válidas",
        isinstance(
            datos.get("apuestas_validas"),
            int,
        ),
    )

    comprobar(
        "API analíticas devuelve rangos",
        isinstance(
            datos.get("rangos"),
            list,
        ),
    )

    comprobar(
        "API analíticas devuelve nota",
        isinstance(
            datos.get("nota"),
            str,
        ),
    )


def probar_analisis_parlays_api():
    respuesta = cliente.get("/analiticas/parlays")

    datos = respuesta.json()

    comprobar(
        "API analíticas parlays responde 200",
        respuesta.status_code == 200,
    )

    modelo = AnalisisParlaysAPI.model_validate(datos)

    comprobar(
        "API modelo valida analíticas parlays",
        isinstance(
            modelo.parlays_registrados,
            int,
        ),
    )

    comprobar(
        "API analíticas parlays contiene totales",
        isinstance(
            datos.get("parlays_resueltos"),
            int,
        )
        and isinstance(
            datos.get("parlays_pendientes"),
            int,
        ),
    )

    comprobar(
        "API analíticas parlays contiene categorías",
        isinstance(
            datos.get("rendimiento_piernas"),
            dict,
        )
        and isinstance(
            datos.get("rendimiento_eventos"),
            dict,
        ),
    )

    comprobar(
        "API analíticas parlays contiene resultados",
        isinstance(
            datos.get("resultados_selecciones"),
            dict,
        ),
    )

    comprobar(
        "API analíticas parlays contiene cuotas",
        isinstance(
            datos.get("comparaciones_cuotas"),
            list,
        ),
    )

    comprobar(
        "API analíticas parlays contiene nota",
        isinstance(
            datos.get("nota"),
            str,
        ),
    )


def probar_diagnostico_api():
    respuesta = cliente.get("/diagnostico")

    datos = respuesta.json()

    comprobar(
        "API diagnóstico responde 200",
        respuesta.status_code == 200,
    )

    modelo = DiagnosticoAPI.model_validate(datos)

    comprobar(
        "API modelo valida diagnóstico",
        modelo.estado_general
        in {
            "Correcto",
            "Requiere revisión",
        },
    )

    comprobar(
        "API diagnóstico contiene aplicación",
        isinstance(
            datos.get("nombre_app"),
            str,
        )
        and isinstance(
            datos.get("version_app"),
            str,
        ),
    )

    comprobar(
        "API diagnóstico no expone ruta de base de datos",
        "ruta_base_datos" not in datos and "base_datos" not in datos,
    )

    comprobar(
        "API diagnóstico no expone ruta de respaldo",
        "ultimo_respaldo" not in datos
        and isinstance(
            datos.get("ultimo_respaldo_disponible"),
            bool,
        ),
    )

    comprobar(
        "API diagnóstico contiene métricas",
        isinstance(
            datos.get("apuestas_registradas"),
            int,
        )
        and isinstance(
            datos.get("bankroll_actual"),
            float,
        ),
    )

    comprobar(
        "API diagnóstico contiene tablas",
        isinstance(
            datos.get("tablas_validas"),
            bool,
        )
        and isinstance(
            datos.get("tablas_faltantes"),
            list,
        ),
    )

    comprobar(
        "API diagnóstico contiene integridad",
        isinstance(
            datos.get("problemas_integridad"),
            list,
        )
        and datos.get("cantidad_problemas_integridad")
        == len(
            datos.get(
                "problemas_integridad",
                [],
            )
        ),
    )


def probar_errores_estandarizados_api():
    respuesta_no_encontrada = cliente.get("/apuestas/999999999")

    datos_no_encontrados = respuesta_no_encontrada.json()

    comprobar(
        "API error estándar conserva estado 404",
        respuesta_no_encontrada.status_code == 404,
    )

    comprobar(
        "API error estándar contiene estructura",
        datos_no_encontrados.get("ok") is False
        and isinstance(
            datos_no_encontrados.get("error"),
            dict,
        ),
    )

    comprobar(
        "API error estándar contiene código",
        datos_no_encontrados.get(
            "error",
            {},
        ).get("codigo")
        == "no_encontrado",
    )

    comprobar(
        "API error estándar contiene mensaje",
        isinstance(
            datos_no_encontrados.get(
                "error",
                {},
            ).get("mensaje"),
            str,
        )
        and bool(
            datos_no_encontrados.get(
                "error",
                {},
            ).get("mensaje")
        ),
    )

    comprobar(
        "API error mantiene detail compatible",
        "detail" in datos_no_encontrados,
    )

    respuesta_validacion = cliente.post(
        "/apuestas",
        json={
            "stake": 0,
        },
    )

    datos_validacion = respuesta_validacion.json()

    comprobar(
        "API validación estándar responde 422",
        respuesta_validacion.status_code == 422,
    )

    comprobar(
        "API validación estándar contiene código",
        datos_validacion.get(
            "error",
            {},
        ).get("codigo")
        == "validacion_fallida",
    )

    comprobar(
        "API validación estándar contiene detalles",
        isinstance(
            datos_validacion.get(
                "error",
                {},
            ).get("detalles"),
            list,
        ),
    )

    respuesta_metodo = cliente.post("/diagnostico")

    datos_metodo = respuesta_metodo.json()

    comprobar(
        "API error estándar maneja método no permitido",
        respuesta_metodo.status_code == 405
        and datos_metodo.get(
            "error",
            {},
        ).get("codigo")
        == "metodo_no_permitido",
    )


def probar_auditoria_rutas_api():
    rutas_esperadas = {
        "/": {
            "GET",
        },
        "/apuestas": {
            "GET",
            "POST",
        },
        "/apuestas/pendientes": {
            "GET",
        },
        "/apuestas/{id_apuesta}": {
            "GET",
            "PATCH",
            "DELETE",
        },
        "/apuestas/{id_apuesta}/resultado": {
            "PATCH",
        },
        "/apuestas/parlay": {
            "POST",
        },
        "/apuestas/{id_apuesta}/parlay": {
            "PATCH",
        },
        "/apuestas/{id_apuesta}/selecciones": {
            "POST",
            "PATCH",
        },
        "/apuestas/{id_apuesta}/selecciones/{numero}": {
            "DELETE",
        },
        "/apuestas/{id_apuesta}/selecciones/orden": {
            "PATCH",
        },
        "/reportes/resumen-financiero": {
            "GET",
        },
        "/estadisticas": {
            "GET",
        },
        "/analiticas/cuotas": {
            "GET",
        },
        "/analiticas/parlays": {
            "GET",
        },
        "/diagnostico": {
            "GET",
        },
        "/configuracion/bankroll": {
            "GET",
            "PUT",
        },
    }

    metodos_reales = obtener_metodos_por_ruta(app)

    comprobar(
        "Auditoría API inventario de rutas correcto",
        metodos_reales == rutas_esperadas,
    )

    comprobar(
        "Auditoría API sin colisiones exactas",
        not detectar_colisiones_exactas(app),
    )

    comprobar(
        "Auditoría API sin rutas dinámicas ocultando estáticas",
        not detectar_sombras_dinamicas(app),
    )

    comprobar(
        "Auditoría API todas las rutas tienen modelo",
        not detectar_rutas_sin_modelo(app),
    )

    comprobar(
        "Auditoría API utiliza métodos permitidos",
        not detectar_metodos_no_permitidos(app),
    )


def probar_cors_api():
    origen_permitido = "http://localhost:5173"

    respuesta_preflight = cliente.options(
        "/apuestas",
        headers={
            "Origin": origen_permitido,
            "Access-Control-Request-Method": ("GET"),
            "Access-Control-Request-Headers": ("content-type"),
        },
    )

    comprobar(
        "CORS preflight permitido responde 200",
        respuesta_preflight.status_code == 200,
    )

    comprobar(
        "CORS devuelve origen permitido",
        respuesta_preflight.headers.get("access-control-allow-origin")
        == origen_permitido,
    )

    comprobar(
        "CORS permite credenciales",
        respuesta_preflight.headers.get("access-control-allow-credentials") == "true",
    )

    metodos_permitidos = respuesta_preflight.headers.get(
        "access-control-allow-methods",
        "",
    )

    comprobar(
        "CORS informa métodos necesarios",
        all(
            metodo in metodos_permitidos
            for metodo in (
                "GET",
                "POST",
                "PUT",
                "PATCH",
                "DELETE",
            )
        ),
    )

    respuesta_normal = cliente.get(
        "/apuestas",
        headers={
            "Origin": origen_permitido,
        },
    )

    comprobar(
        "CORS agrega encabezado a respuesta normal",
        respuesta_normal.status_code == 200
        and respuesta_normal.headers.get("access-control-allow-origin")
        == origen_permitido,
    )

    origen_no_permitido = "https://sitio-no-permitido.example"

    respuesta_bloqueada = cliente.options(
        "/apuestas",
        headers={
            "Origin": origen_no_permitido,
            "Access-Control-Request-Method": ("GET"),
        },
    )

    comprobar(
        "CORS bloquea origen desconocido",
        respuesta_bloqueada.status_code == 400
        and respuesta_bloqueada.headers.get("access-control-allow-origin") is None,
    )


def ejecutar_pruebas_api():
    print("\n===== PRUEBAS DE TRACKBET API =====")

    probar_estado_api()

    apuestas = probar_listado_apuestas()

    probar_filtros_apuestas()
    probar_paginacion_apuestas()
    probar_modelos_respuesta()
    probar_modelo_creacion_straight()
    probar_creacion_apuesta_straight_api()
    probar_agregar_seleccion_parlay_api()
    probar_eliminar_seleccion_parlay_api()
    probar_reordenar_selecciones_parlay_api()
    probar_actualizacion_selecciones_parlay_api()
    probar_modelo_creacion_parlay()
    probar_creacion_apuesta_parlay_api()
    probar_actualizacion_resultado_straight_api()
    probar_edicion_apuesta_straight_api()
    probar_configuracion_bankroll_api()
    probar_eliminacion_apuesta_api()
    probar_apuestas_pendientes()
    probar_apuesta_por_id(apuestas)
    probar_resumen_financiero()
    probar_edicion_apuesta_parlay_api()
    probar_estadisticas_api()
    probar_analisis_cuotas_api()
    probar_analisis_parlays_api()
    probar_diagnostico_api()
    probar_errores_estandarizados_api()
    probar_auditoria_rutas_api()
    probar_cors_api()

    correctas = resultados_pruebas["correctas"]
    fallidas = resultados_pruebas["fallidas"]
    total = correctas + fallidas

    print("\n========================================")
    print("Total de pruebas API:", total)
    print("Pruebas correctas:", correctas)
    print("Pruebas fallidas:", fallidas)
    print("========================================")

    if fallidas == 0:
        print("\nTodas las pruebas de la API pasaron correctamente.")


if __name__ == "__main__":
    ejecutar_pruebas_api()
