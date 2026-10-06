"""Herramientas para auditar las rutas y contratos de la API de TrackBet."""

from fastapi import FastAPI
from fastapi.routing import APIRoute

METODOS_PUBLICOS_PERMITIDOS = {
    "GET",
    "POST",
    "PUT",
    "PATCH",
    "DELETE",
}


def obtener_rutas_publicas(
    app: FastAPI,
):
    """Devuelve únicamente las rutas creadas por la aplicación."""

    return [ruta for ruta in app.routes if isinstance(ruta, APIRoute)]


def obtener_nombre_modelo(
    modelo,
):
    """Devuelve un nombre legible para un modelo de respuesta."""

    if modelo is None:
        return None

    nombre = getattr(
        modelo,
        "__name__",
        None,
    )

    if nombre:
        return nombre

    return str(modelo)


def obtener_inventario_rutas(
    app: FastAPI,
):
    """Genera un inventario de las rutas de la API."""

    inventario = []

    for ruta in obtener_rutas_publicas(app):
        metodos = sorted(
            metodo
            for metodo in ruta.methods
            if metodo
            not in {
                "HEAD",
                "OPTIONS",
            }
        )

        inventario.append(
            {
                "ruta": ruta.path,
                "metodos": metodos,
                "nombre": ruta.name,
                "modelo_respuesta": (obtener_nombre_modelo(ruta.response_model)),
            }
        )

    return inventario


def obtener_metodos_por_ruta(
    app: FastAPI,
):
    """Agrupa todos los métodos disponibles por ruta."""

    metodos_por_ruta = {}

    for elemento in obtener_inventario_rutas(app):
        ruta = elemento["ruta"]

        if ruta not in metodos_por_ruta:
            metodos_por_ruta[ruta] = set()

        metodos_por_ruta[ruta].update(elemento["metodos"])

    return metodos_por_ruta


def detectar_colisiones_exactas(
    app: FastAPI,
):
    """Detecta métodos y rutas registrados más de una vez."""

    encontrados = {}
    colisiones = []

    for ruta in obtener_rutas_publicas(app):
        for metodo in ruta.methods:
            if metodo in {
                "HEAD",
                "OPTIONS",
            }:
                continue

            clave = (
                metodo,
                ruta.path,
            )

            if clave in encontrados:
                colisiones.append(
                    {
                        "metodo": metodo,
                        "ruta": ruta.path,
                        "primera_funcion": encontrados[clave],
                        "segunda_funcion": ruta.name,
                    }
                )
            else:
                encontrados[clave] = ruta.name

    return colisiones


def es_segmento_dinamico(
    segmento,
):
    """Indica si un segmento representa un parámetro de ruta."""

    return segmento.startswith("{") and segmento.endswith("}")


def ruta_dinamica_captura_estatica(
    ruta_dinamica,
    ruta_estatica,
):
    """Detecta si una ruta dinámica podría ocultar una estática."""

    segmentos_dinamicos = [
        segmento for segmento in ruta_dinamica.strip("/").split("/") if segmento
    ]

    segmentos_estaticos = [
        segmento for segmento in ruta_estatica.strip("/").split("/") if segmento
    ]

    if len(segmentos_dinamicos) != len(segmentos_estaticos):
        return False

    captura_segmento_estatico = False

    for dinamico, estatico in zip(
        segmentos_dinamicos,
        segmentos_estaticos,
    ):
        if es_segmento_dinamico(dinamico):
            if not es_segmento_dinamico(estatico):
                captura_segmento_estatico = True

            continue

        if dinamico != estatico:
            return False

    return captura_segmento_estatico


def detectar_sombras_dinamicas(
    app: FastAPI,
):
    """Detecta rutas dinámicas colocadas antes de rutas estáticas."""

    rutas = obtener_rutas_publicas(app)
    problemas = []

    for indice, ruta_anterior in enumerate(rutas):
        metodos_anteriores = set(ruta_anterior.methods)

        for ruta_posterior in rutas[indice + 1 :]:
            metodos_comunes = metodos_anteriores & set(ruta_posterior.methods)

            metodos_comunes -= {
                "HEAD",
                "OPTIONS",
            }

            if not metodos_comunes:
                continue

            if ruta_dinamica_captura_estatica(
                ruta_anterior.path,
                ruta_posterior.path,
            ):
                problemas.append(
                    {
                        "ruta_dinamica": (ruta_anterior.path),
                        "ruta_estatica": (ruta_posterior.path),
                        "metodos": sorted(metodos_comunes),
                    }
                )

    return problemas


def detectar_rutas_sin_modelo(
    app: FastAPI,
):
    """Detecta endpoints sin modelo de respuesta declarado."""

    return [
        {
            "ruta": ruta.path,
            "metodos": sorted(
                metodo
                for metodo in ruta.methods
                if metodo
                not in {
                    "HEAD",
                    "OPTIONS",
                }
            ),
            "nombre": ruta.name,
        }
        for ruta in obtener_rutas_publicas(app)
        if ruta.response_model is None
    ]


def detectar_metodos_no_permitidos(
    app: FastAPI,
):
    """Detecta métodos que no forman parte del diseño público."""

    problemas = []

    for ruta in obtener_rutas_publicas(app):
        for metodo in ruta.methods:
            if metodo in {
                "HEAD",
                "OPTIONS",
            }:
                continue

            if metodo not in METODOS_PUBLICOS_PERMITIDOS:
                problemas.append(
                    {
                        "ruta": ruta.path,
                        "metodo": metodo,
                    }
                )

    return problemas


def generar_resumen_auditoria(
    app: FastAPI,
):
    """Genera el resumen completo de rutas de la API."""

    inventario = obtener_inventario_rutas(app)

    colisiones = detectar_colisiones_exactas(app)

    sombras = detectar_sombras_dinamicas(app)

    sin_modelo = detectar_rutas_sin_modelo(app)

    metodos_invalidos = detectar_metodos_no_permitidos(app)

    return {
        "rutas_registradas": len(inventario),
        "inventario": inventario,
        "colisiones_exactas": colisiones,
        "sombras_dinamicas": sombras,
        "rutas_sin_modelo": sin_modelo,
        "metodos_no_permitidos": (metodos_invalidos),
        "estado_correcto": (
            not colisiones and not sombras and not sin_modelo and not metodos_invalidos
        ),
    }
