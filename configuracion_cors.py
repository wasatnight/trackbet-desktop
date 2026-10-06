import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

ORIGENES_DESARROLLO = (
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:4173",
    "http://192.168.68.57:5173",
)


METODOS_CORS = [
    "GET",
    "POST",
    "PUT",
    "PATCH",
    "DELETE",
    "OPTIONS",
]


ENCABEZADOS_CORS = [
    "Accept",
    "Authorization",
    "Content-Type",
]


def obtener_origenes_cors():
    """Obtiene los orígenes autorizados para TrackBet."""

    valor_entorno = os.getenv(
        "TRACKBET_CORS_ORIGINS",
        "",
    )

    if valor_entorno.strip():
        origenes = [
            origen.strip().rstrip("/")
            for origen in valor_entorno.split(",")
            if origen.strip()
        ]
    else:
        origenes = list(ORIGENES_DESARROLLO)

    # Elimina duplicados sin alterar el orden.
    origenes = list(dict.fromkeys(origenes))

    if "*" in origenes:
        raise ValueError(
            "CORS no permite el origen '*' cuando las credenciales están activadas."
        )

    return origenes


def configurar_cors(
    app: FastAPI,
):
    """Configura CORS para React y futuros clientes."""

    app.add_middleware(
        CORSMiddleware,
        allow_origins=obtener_origenes_cors(),
        allow_credentials=True,
        allow_methods=METODOS_CORS,
        allow_headers=ENCABEZADOS_CORS,
        max_age=600,
    )
