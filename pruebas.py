"""Pruebas automatizadas de la lógica interna de TrackBet."""

# pylint: disable=too-many-lines
# pylint: disable=missing-function-docstring


from math import isclose
from pathlib import Path

from servicios_apuestas import (
    buscar_apuestas_por_filtros,
    cerrar_apuesta_por_id,
    construir_apuesta_straight,
    construir_apuesta_parlay,
    eliminar_apuesta_por_id,
    formatear_cuota_texto_entrada,
    listar_apuestas,
    listar_apuestas_pendientes,
    normalizar_resultado,
    obtener_apuesta_por_id,
    obtener_siguiente_id,
    actualizar_selecciones_parlay_por_id,
    actualizar_apuesta_parlay_por_id,
    agregar_seleccion_parlay_por_id,
    eliminar_seleccion_parlay_por_id,
    reordenar_selecciones_parlay_por_id,
)
from exportaciones_reportes import (
    exportar_todos_los_reportes,
    obtener_reportes_exportados,
)

from base_datos import (
    formatear_tamano_archivo,
    obtener_ruta_base_datos,
    obtener_tamano_base_datos,
    validar_tablas_principales,
)
from configuracion_app import (
    NOMBRE_APP,
    DESCRIPCION_APP,
    IDIOMA_APP,
    VERSION_APP,
    MODO_ALMACENAMIENTO,
    NOMBRE_BASE_DATOS,
)
from vistas_rapidas import (
    calcular_resumen_vista,
    filtrar_apuestas_por_resultado,
)
from pendientes import filtrar_apuestas_pendientes
from logica_reportes import calcular_resumen_financiero
from resumen_financiero import generar_texto_resumen_financiero
from almacenamiento import obtener_modo_almacenamiento

from bankroll import validar_bankroll_inicial
from busquedas import (
    filtrar_apuestas,
    filtrar_apuestas_desde_servicio,
)
from diagnostico import (
    calcular_metricas_diagnostico,
    contar_selecciones,
    generar_texto_diagnostico,
    obtener_resumen_diagnostico,
    validar_integridad_apuestas,
)
from calculos import (
    calcular_cuota_liquidada_parlay,
    calcular_ganancia_apuesta,
)
from liquidaciones import (
    calcular_retorno_esperado,
    eliminar_liquidacion_oficial,
)
from parlays import calcular_resultado_general_parlay
from validaciones import normalizar_texto
from servicios_reportes import obtener_resumen_financiero
from servicios_configuracion import (
    convertir_bankroll,
    obtener_configuracion_bankroll,
)
from logica_estadisticas import calcular_estadisticas
from servicios_estadisticas import obtener_estadisticas
from logica_analiticas import (
    calcular_analisis_cuotas,
    calcular_analisis_parlays,
    clasificar_muestra,
    clasificar_parlay_por_deportes,
    clasificar_parlay_por_eventos,
    obtener_cuota_individual_decimal,
    obtener_rango_cuota,
)
from servicios_analiticas import (
    obtener_analisis_cuotas,
    obtener_analisis_parlays,
)
from servicios_diagnostico import (
    obtener_diagnostico_sistema,
)
from errores_api import (
    construir_respuesta_error,
    obtener_codigo_error_http,
    obtener_mensaje_error,
)

from configuracion_cors import (
    ENCABEZADOS_CORS,
    METODOS_CORS,
    obtener_origenes_cors,
)

CONTADOR_PRUEBAS = {
    "correctas": 0,
    "fallidas": 0,
}


def comprobar(
    nombre,
    valor_obtenido,
    valor_esperado,
    tolerancia=0.01,
):
    """Comprueba un resultado numérico y muestra el resultado."""

    if isclose(
        valor_obtenido,
        valor_esperado,
        abs_tol=tolerancia,
    ):
        print(f"[CORRECTO] {nombre}: " f"{valor_obtenido:.2f}")
        CONTADOR_PRUEBAS["correctas"] += 1
    else:
        print(f"[ERROR] {nombre}")
        print(f"        Esperado: {valor_esperado:.2f}")
        print(f"        Obtenido: {valor_obtenido:.2f}")
        CONTADOR_PRUEBAS["fallidas"] += 1


def comprobar_texto(
    nombre,
    valor_obtenido,
    valor_esperado,
):
    """Comprueba que dos textos sean iguales."""

    if valor_obtenido == valor_esperado:
        print(f"[CORRECTO] {nombre}: " f"{valor_obtenido}")
        CONTADOR_PRUEBAS["correctas"] += 1

    else:
        print(f"[ERROR] {nombre}")
        print(f"        Esperado: {valor_esperado}")
        print(f"        Obtenido: {valor_obtenido}")
        CONTADOR_PRUEBAS["fallidas"] += 1


def probar_straight_ganada():
    apuesta = {
        "modalidad": "straight",
        "cuota": 2.50,
        "stake": 100,
        "resultado": "ganada",
    }

    ganancia = calcular_ganancia_apuesta(apuesta)

    comprobar(
        "Straight ganada",
        ganancia,
        150,
    )


def probar_straight_perdida():
    apuesta = {
        "modalidad": "straight",
        "cuota": 2.50,
        "stake": 100,
        "resultado": "perdida",
    }

    ganancia = calcular_ganancia_apuesta(apuesta)

    comprobar(
        "Straight perdida",
        ganancia,
        -100,
    )


def probar_straight_push():
    apuesta = {
        "modalidad": "straight",
        "cuota": 2.50,
        "stake": 100,
        "resultado": "push",
    }

    ganancia = calcular_ganancia_apuesta(apuesta)

    comprobar(
        "Straight Push",
        ganancia,
        0,
    )


def probar_apuesta_pendiente():
    apuesta = {
        "modalidad": "straight",
        "cuota": 2.50,
        "stake": 100,
        "resultado": "pendiente",
    }

    ganancia = calcular_ganancia_apuesta(apuesta)

    comprobar(
        "Apuesta pendiente",
        ganancia,
        0,
    )


def probar_parlay_ganado():
    apuesta = {
        "modalidad": "parlay",
        "cuota": 4.00,
        "stake": 100,
        "resultado": "ganada",
        "selecciones": [
            {
                "cuota_individual": 2.00,
                "resultado_seleccion": "ganada",
            },
            {
                "cuota_individual": 2.00,
                "resultado_seleccion": "ganada",
            },
        ],
    }

    ganancia = calcular_ganancia_apuesta(apuesta)

    comprobar(
        "Parlay ganado sin Push",
        ganancia,
        300,
    )


def probar_parlay_perdido():
    apuesta = {
        "modalidad": "parlay",
        "cuota": 4.00,
        "stake": 100,
        "resultado": "perdida",
        "selecciones": [
            {
                "cuota_individual": 2.00,
                "resultado_seleccion": "ganada",
            },
            {
                "cuota_individual": 2.00,
                "resultado_seleccion": "perdida",
            },
        ],
    }

    ganancia = calcular_ganancia_apuesta(apuesta)

    comprobar(
        "Parlay perdido",
        ganancia,
        -100,
    )


def probar_parlay_con_push():
    apuesta = {
        "modalidad": "parlay",
        "cuota": 6.00,
        "stake": 100,
        "resultado": "ganada",
        "selecciones": [
            {
                "cuota_individual": 2.00,
                "resultado_seleccion": "ganada",
            },
            {
                "cuota_individual": 3.00,
                "resultado_seleccion": "push",
            },
        ],
    }

    cuota_liquidada = calcular_cuota_liquidada_parlay(apuesta)

    ganancia = calcular_ganancia_apuesta(apuesta)

    comprobar(
        "Cuota liquidada de parlay con Push",
        cuota_liquidada,
        2.00,
    )

    comprobar(
        "Ganancia de parlay con Push",
        ganancia,
        100,
    )


def probar_parlay_todo_push():
    apuesta = {
        "modalidad": "parlay",
        "cuota": 4.00,
        "stake": 100,
        "resultado": "push",
        "selecciones": [
            {
                "cuota_individual": 2.00,
                "resultado_seleccion": "push",
            },
            {
                "cuota_individual": 2.00,
                "resultado_seleccion": "push",
            },
        ],
    }

    cuota_liquidada = calcular_cuota_liquidada_parlay(apuesta)

    ganancia = calcular_ganancia_apuesta(apuesta)

    comprobar(
        "Cuota de parlay con todo Push",
        cuota_liquidada,
        1.00,
    )

    comprobar(
        "Ganancia de parlay con todo Push",
        ganancia,
        0,
    )


def probar_cuota_liquidada_oficial():
    apuesta = {
        "modalidad": "parlay",
        "cuota": 6.00,
        "cuota_liquidada": 2.50,
        "stake": 100,
        "resultado": "ganada",
        "selecciones": [
            {
                "cuota_individual": 2.00,
                "resultado_seleccion": "ganada",
            },
            {
                "cuota_individual": 3.00,
                "resultado_seleccion": "push",
            },
        ],
    }

    cuota_liquidada = calcular_cuota_liquidada_parlay(apuesta)

    ganancia = calcular_ganancia_apuesta(apuesta)

    comprobar(
        "Cuota liquidada oficial",
        cuota_liquidada,
        2.50,
    )

    comprobar(
        "Ganancia con cuota oficial",
        ganancia,
        150,
    )


def probar_retorno_total_real():
    apuesta = {
        "modalidad": "parlay",
        "cuota": 9.02,
        "cuota_liquidada": 9.02,
        "stake": 300,
        "resultado": "ganada",
        "retorno_total_real": 700,
        "selecciones": [],
    }

    ganancia = calcular_ganancia_apuesta(apuesta)

    comprobar(
        "Retorno total real con prioridad",
        ganancia,
        400,
    )


def probar_normalizacion_texto():
    comprobar_texto(
        "Normalizar Fútbol",
        normalizar_texto("Fútbol"),
        "futbol",
    )

    comprobar_texto(
        "Normalizar Béisbol",
        normalizar_texto("BÉISBOL"),
        "beisbol",
    )

    comprobar_texto(
        "Normalizar México",
        normalizar_texto("  México  "),
        "mexico",
    )

    comprobar_texto(
        "Normalizar guiones bajos",
        normalizar_texto("en_vivo"),
        "en vivo",
    )

    comprobar_texto(
        "Normalizar Soccer",
        normalizar_texto("soccer"),
        "futbol",
    )


def probar_resultado_general_parlay():
    comprobar_texto(
        "Parlay general ganado",
        calcular_resultado_general_parlay(
            [
                {"resultado_seleccion": "ganada"},
                {"resultado_seleccion": "ganada"},
            ]
        ),
        "ganada",
    )

    comprobar_texto(
        "Parlay general ganado con Push",
        calcular_resultado_general_parlay(
            [
                {"resultado_seleccion": "ganada"},
                {"resultado_seleccion": "push"},
            ]
        ),
        "ganada",
    )

    comprobar_texto(
        "Parlay general perdido",
        calcular_resultado_general_parlay(
            [
                {"resultado_seleccion": "ganada"},
                {"resultado_seleccion": "perdida"},
            ]
        ),
        "perdida",
    )

    comprobar_texto(
        "Parlay general pendiente",
        calcular_resultado_general_parlay(
            [
                {"resultado_seleccion": "ganada"},
                {"resultado_seleccion": "pendiente"},
            ]
        ),
        "pendiente",
    )

    comprobar_texto(
        "Parlay general todo Push",
        calcular_resultado_general_parlay(
            [
                {"resultado_seleccion": "push"},
                {"resultado_seleccion": "push"},
            ]
        ),
        "push",
    )


def probar_liquidaciones():
    apuesta_ganada = {
        "modalidad": "parlay",
        "cuota": 4.00,
        "stake": 100,
        "resultado": "ganada",
        "selecciones": [
            {
                "cuota_individual": 2.00,
                "resultado_seleccion": "ganada",
            },
            {
                "cuota_individual": 2.00,
                "resultado_seleccion": "ganada",
            },
        ],
    }

    comprobar(
        "Retorno esperado parlay ganado",
        calcular_retorno_esperado(
            apuesta_ganada,
            "ganada",
            100,
        ),
        400,
    )

    comprobar(
        "Retorno esperado parlay perdido",
        calcular_retorno_esperado(
            apuesta_ganada,
            "perdida",
            100,
        ),
        0,
    )

    comprobar(
        "Retorno esperado parlay Push",
        calcular_retorno_esperado(
            apuesta_ganada,
            "push",
            100,
        ),
        100,
    )

    apuesta_con_liquidacion = {
        "cuota_liquidada": 2.50,
        "tipo_cuota_liquidada": "decimal",
        "cuota_liquidada_texto": "2.50",
        "retorno_total_real": 250,
    }

    eliminar_liquidacion_oficial(apuesta_con_liquidacion)

    comprobar_texto(
        "Eliminar cuota liquidada",
        str("cuota_liquidada" in apuesta_con_liquidacion),
        "False",
    )

    comprobar_texto(
        "Eliminar retorno total real",
        str("retorno_total_real" in apuesta_con_liquidacion),
        "False",
    )


def probar_busquedas():
    apuestas = [
        {
            "deporte": "Fútbol",
            "casa": "Stake MX",
            "liga": "FIFA CUP",
            "resultado": "ganada",
            "modalidad": "parlay",
            "momento_apuesta": "prepartido",
            "selecciones": [
                {
                    "tipo_apuesta": "Moneyline",
                    "evento": "México vs Ecuador",
                },
                {
                    "tipo_apuesta": "Over/Under",
                    "evento": "México vs Ecuador",
                },
            ],
        },
        {
            "deporte": "Béisbol",
            "casa": "Playdoit",
            "liga": "MLB",
            "resultado": "perdida",
            "modalidad": "straight",
            "momento_apuesta": "en_vivo",
            "selecciones": [
                {
                    "tipo_apuesta": "Handicap / Spread",
                    "evento": ("Minnesota Twins vs " "Houston Astros"),
                }
            ],
        },
    ]

    comprobar_texto(
        "Buscar deporte sin acento",
        str(
            len(
                filtrar_apuestas(
                    apuestas,
                    "1",
                    "futbol",
                )
            )
        ),
        "1",
    )

    comprobar_texto(
        "Buscar evento sin acento",
        str(
            len(
                filtrar_apuestas(
                    apuestas,
                    "7",
                    "mexico",
                )
            )
        ),
        "1",
    )

    comprobar_texto(
        "Buscar mercado parcial",
        str(
            len(
                filtrar_apuestas(
                    apuestas,
                    "6",
                    "over",
                )
            )
        ),
        "1",
    )

    comprobar_texto(
        "Buscar momento con espacio",
        str(
            len(
                filtrar_apuestas(
                    apuestas,
                    "8",
                    "en vivo",
                )
            )
        ),
        "1",
    )

    comprobar_texto(
        "Buscar casa parcial",
        str(
            len(
                filtrar_apuestas(
                    apuestas,
                    "2",
                    "stake",
                )
            )
        ),
        "1",
    )

    comprobar_texto(
        "Buscar deporte usando Soccer",
        str(
            len(
                filtrar_apuestas(
                    apuestas,
                    "1",
                    "soccer",
                )
            )
        ),
        "1",
    )


def probar_bankroll():
    comprobar_texto(
        "Bankroll válido",
        str(validar_bankroll_inicial(1000)),
        "True",
    )

    comprobar_texto(
        "Bankroll cero inválido",
        str(validar_bankroll_inicial(0)),
        "False",
    )

    comprobar_texto(
        "Bankroll negativo inválido",
        str(validar_bankroll_inicial(-500)),
        "False",
    )

    comprobar_texto(
        "Bankroll texto inválido",
        str(validar_bankroll_inicial("abc")),
        "False",
    )


def probar_modo_almacenamiento():
    comprobar_texto(
        "Modo de almacenamiento válido",
        str(obtener_modo_almacenamiento() in ("JSON", "SQLite")),
        "True",
    )


def probar_diagnostico():
    apuestas = [
        {
            "selecciones": [
                {"seleccion": "A"},
                {"seleccion": "B"},
            ],
        },
        {
            "selecciones": [
                {"seleccion": "C"},
            ],
        },
    ]

    comprobar_texto(
        "Contar selecciones diagnóstico",
        str(contar_selecciones(apuestas)),
        "3",
    )


def probar_metricas_diagnostico():
    apuestas = [
        {
            "modalidad": "straight",
            "cuota": 2.00,
            "stake": 100,
            "resultado": "ganada",
        },
        {
            "modalidad": "straight",
            "cuota": 2.00,
            "stake": 50,
            "resultado": "perdida",
        },
        {
            "modalidad": "straight",
            "cuota": 2.00,
            "stake": 25,
            "resultado": "pendiente",
        },
    ]

    metricas = calcular_metricas_diagnostico(
        apuestas,
        1000,
    )

    comprobar(
        "Diagnóstico ganancia neta",
        metricas["ganancia_neta"],
        50,
    )

    comprobar(
        "Diagnóstico bankroll actual",
        metricas["bankroll_actual"],
        1050,
    )

    comprobar_texto(
        "Diagnóstico apuestas pendientes",
        str(metricas["apuestas_pendientes"]),
        "1",
    )

    comprobar(
        "Diagnóstico stake pendiente",
        metricas["stake_pendiente"],
        25,
    )


def probar_integridad_diagnostico():
    apuestas_correctas = [
        {
            "id": 1,
            "modalidad": "straight",
            "stake": 100,
            "resultado": "ganada",
            "selecciones": [
                {
                    "evento": "Equipo A vs Equipo B",
                    "tipo_apuesta": "Moneyline",
                    "seleccion": "Equipo A",
                }
            ],
        }
    ]

    comprobar_texto(
        "Integridad sin problemas",
        str(len(validar_integridad_apuestas(apuestas_correctas))),
        "0",
    )

    apuestas_con_problemas = [
        {
            "modalidad": "parlay",
            "stake": 0,
            "resultado": "pendiente",
            "retorno_total_real": 100,
            "selecciones": [
                {
                    "evento": "",
                    "tipo_apuesta": "",
                    "seleccion": "",
                }
            ],
        }
    ]

    problemas = validar_integridad_apuestas(apuestas_con_problemas)

    comprobar_texto(
        "Integridad detecta problemas",
        str(len(problemas) > 0),
        "True",
    )


def probar_resumen_financiero():
    apuestas = [
        {
            "modalidad": "straight",
            "cuota": 2.00,
            "stake": 100,
            "resultado": "ganada",
        },
        {
            "modalidad": "straight",
            "cuota": 2.00,
            "stake": 50,
            "resultado": "perdida",
        },
        {
            "modalidad": "straight",
            "cuota": 2.00,
            "stake": 25,
            "resultado": "pendiente",
        },
    ]

    resumen = calcular_resumen_financiero(
        apuestas,
        1000,
    )

    comprobar(
        "Resumen financiero ganancia neta",
        resumen["ganancia_neta"],
        50,
    )

    comprobar(
        "Resumen financiero bankroll actual",
        resumen["bankroll_actual"],
        1050,
    )

    comprobar(
        "Resumen financiero stake total",
        resumen["stake_total"],
        175,
    )

    comprobar(
        "Resumen financiero stake resuelto",
        resumen["stake_resuelto"],
        150,
    )

    comprobar(
        "Resumen financiero stake pendiente",
        resumen["stake_pendiente"],
        25,
    )

    comprobar_texto(
        "Resumen financiero apuestas pendientes",
        str(resumen["apuestas_pendientes"]),
        "1",
    )


def probar_apuestas_pendientes():
    apuestas = [
        {
            "id": 1,
            "resultado": "ganada",
        },
        {
            "id": 2,
            "resultado": "pendiente",
        },
        {
            "id": 3,
            "resultado": "perdida",
        },
        {
            "id": 4,
            "resultado": "pendiente",
        },
    ]

    pendientes = filtrar_apuestas_pendientes(apuestas)

    comprobar_texto(
        "Filtrar apuestas pendientes",
        str(len(pendientes)),
        "2",
    )


def probar_vistas_rapidas():
    apuestas = [
        {
            "id": 1,
            "resultado": "ganada",
        },
        {
            "id": 2,
            "resultado": "perdida",
        },
        {
            "id": 3,
            "resultado": "push",
        },
        {
            "id": 4,
            "resultado": "pendiente",
        },
        {
            "id": 5,
            "resultado": "ganada",
        },
    ]

    comprobar_texto(
        "Vista rápida ganadas",
        str(
            len(
                filtrar_apuestas_por_resultado(
                    apuestas,
                    "ganada",
                )
            )
        ),
        "2",
    )

    comprobar_texto(
        "Vista rápida perdidas",
        str(
            len(
                filtrar_apuestas_por_resultado(
                    apuestas,
                    "perdida",
                )
            )
        ),
        "1",
    )

    comprobar_texto(
        "Vista rápida push",
        str(
            len(
                filtrar_apuestas_por_resultado(
                    apuestas,
                    "push",
                )
            )
        ),
        "1",
    )

    comprobar_texto(
        "Vista rápida pendientes",
        str(
            len(
                filtrar_apuestas_por_resultado(
                    apuestas,
                    "pendiente",
                )
            )
        ),
        "1",
    )


def probar_resumen_vista_rapida():
    apuestas = [
        {
            "modalidad": "straight",
            "cuota": 2.00,
            "stake": 100,
            "resultado": "ganada",
        },
        {
            "modalidad": "straight",
            "cuota": 2.00,
            "stake": 50,
            "resultado": "perdida",
        },
    ]

    resumen = calcular_resumen_vista(apuestas)

    comprobar(
        "Vista rápida stake total",
        resumen["stake_total"],
        150,
    )

    comprobar(
        "Vista rápida ganancia neta",
        resumen["ganancia_neta"],
        50,
    )

    comprobar(
        "Vista rápida ROI",
        resumen["roi"],
        33.33,
        tolerancia=0.01,
    )


def probar_configuracion_app():
    diagnostico = obtener_diagnostico_sistema()

    comprobar_texto(
        "Diagnóstico contiene aplicación",
        diagnostico["nombre_app"],
        "TrackBet",
    )

    comprobar_texto(
        "Versión de aplicación configurada",
        str(bool(VERSION_APP)),
        "True",
    )

    comprobar_texto(
        "Modo de almacenamiento configurado",
        str(MODO_ALMACENAMIENTO in ("json", "sqlite")),
        "True",
    )

    comprobar_texto(
        "Descripción de aplicación configurada",
        DESCRIPCION_APP,
        "Registra tus apuestas deportivas y analiza tus resultados.",
    )


comprobar_texto(
    "Idioma de aplicación configurado",
    IDIOMA_APP,
    "Español",
)


def probar_ruta_base_datos():
    ruta = Path(obtener_ruta_base_datos())

    comprobar_texto(
        "Ruta de base de datos absoluta",
        str(ruta.is_absolute()),
        "True",
    )

    comprobar_texto(
        "Ruta de base de datos correcta",
        ruta.name,
        NOMBRE_BASE_DATOS,
    )


def probar_tablas_principales_sqlite():
    estado = validar_tablas_principales()

    comprobar_texto(
        "Tablas SQLite principales válidas",
        str(estado["valida"]),
        "True",
    )

    comprobar_texto(
        "Tabla apuestas existente",
        str("apuestas" in estado["tablas_existentes"]),
        "True",
    )

    comprobar_texto(
        "Tabla selecciones existente",
        str("selecciones" in estado["tablas_existentes"]),
        "True",
    )

    comprobar_texto(
        "Tabla configuracion existente",
        str("configuracion" in estado["tablas_existentes"]),
        "True",
    )


def probar_tamano_base_datos():
    tamano = obtener_tamano_base_datos()

    comprobar_texto(
        "Tamaño de base de datos positivo",
        str(tamano > 0),
        "True",
    )

    comprobar_texto(
        "Formato tamaño bytes",
        formatear_tamano_archivo(500),
        "500 B",
    )

    comprobar_texto(
        "Formato tamaño KB",
        formatear_tamano_archivo(2048),
        "2.00 KB",
    )

    comprobar_texto(
        "Formato tamaño MB",
        formatear_tamano_archivo(2 * 1024 * 1024),
        "2.00 MB",
    )


def probar_estado_general_diagnostico():
    resumen = obtener_resumen_diagnostico()

    comprobar_texto(
        "Diagnóstico estado general",
        resumen["estado_general"],
        "Correcto",
    )


def probar_texto_diagnostico():
    texto_diagnostico = generar_texto_diagnostico()

    comprobar_texto(
        "Texto diagnóstico contiene aplicación",
        str("Aplicación: TrackBet" in texto_diagnostico),
        "True",
    )

    comprobar_texto(
        "Texto diagnóstico contiene estado general",
        str("Estado general: Correcto" in texto_diagnostico),
        "True",
    )

    comprobar_texto(
        "Texto diagnóstico contiene base de datos",
        str(f"Base de datos: {NOMBRE_BASE_DATOS}" in texto_diagnostico),
        "True",
    )


def probar_texto_resumen_financiero():
    texto = generar_texto_resumen_financiero()

    comprobar_texto(
        "Texto resumen contiene título",
        str("RESUMEN FINANCIERO" in texto),
        "True",
    )

    comprobar_texto(
        "Texto resumen contiene bankroll",
        str("Bankroll inicial" in texto),
        "True",
    )

    comprobar_texto(
        "Texto resumen contiene ROI",
        str("ROI:" in texto),
        "True",
    )


def probar_exportacion_todos_reportes():
    comprobar_texto(
        "Exportar todos los reportes disponible",
        str(callable(exportar_todos_los_reportes)),
        "True",
    )


def probar_reportes_exportados():
    reportes = obtener_reportes_exportados()

    comprobar_texto(
        "Lista de reportes exportados disponible",
        str(isinstance(reportes, list)),
        "True",
    )


def probar_servicios_apuestas():
    apuestas = listar_apuestas()

    comprobar_texto(
        "Servicio listar apuestas devuelve lista",
        str(isinstance(apuestas, list)),
        "True",
    )

    comprobar_texto(
        "Servicio normalizar resultado",
        normalizar_resultado(" Ganada "),
        "ganada",
    )

    if apuestas:
        primera_apuesta = apuestas[0]
        id_apuesta = primera_apuesta.get("id")

        apuesta_encontrada = obtener_apuesta_por_id(id_apuesta)

        comprobar_texto(
            "Servicio obtener apuesta por ID",
            str(apuesta_encontrada is not None),
            "True",
        )

    apuesta_inexistente = obtener_apuesta_por_id("id_invalido")

    comprobar_texto(
        "Servicio apuesta ID inválido",
        str(apuesta_inexistente is None),
        "True",
    )


def probar_servicio_cierre_apuestas():
    respuesta_id_invalido = cerrar_apuesta_por_id(
        "id_invalido",
        "ganada",
    )

    comprobar_texto(
        "Servicio cerrar apuesta ID inválido",
        str(respuesta_id_invalido["ok"]),
        "False",
    )

    respuesta_resultado_invalido = cerrar_apuesta_por_id(
        1,
        "resultado_raro",
    )

    comprobar_texto(
        "Servicio cerrar apuesta resultado inválido",
        str(respuesta_resultado_invalido["ok"]),
        "False",
    )


def probar_servicio_busqueda_apuestas():
    todas = buscar_apuestas_por_filtros({})

    comprobar_texto(
        "Servicio búsqueda sin filtros devuelve lista",
        str(isinstance(todas, list)),
        "True",
    )

    apuestas_futbol = buscar_apuestas_por_filtros(
        {
            "deporte": "futbol",
        }
    )

    comprobar_texto(
        "Servicio búsqueda por deporte devuelve lista",
        str(isinstance(apuestas_futbol, list)),
        "True",
    )

    apuestas_ganadas = buscar_apuestas_por_filtros(
        {
            "resultado": "ganada",
        }
    )

    comprobar_texto(
        "Servicio búsqueda por resultado devuelve lista",
        str(isinstance(apuestas_ganadas, list)),
        "True",
    )

    apuestas_inexistentes = buscar_apuestas_por_filtros(
        {
            "deporte": "deporte_que_no_existe",
        }
    )

    comprobar_texto(
        "Servicio búsqueda sin coincidencias",
        str(len(apuestas_inexistentes)),
        "0",
    )


def probar_busqueda_con_servicio():
    resultados = filtrar_apuestas_desde_servicio(
        "1",
        "futbol",
    )

    comprobar_texto(
        "Búsqueda consola usando servicio devuelve lista",
        str(isinstance(resultados, list)),
        "True",
    )

    resultados_invalidos = filtrar_apuestas_desde_servicio(
        "opcion_invalida",
        "futbol",
    )

    comprobar_texto(
        "Búsqueda consola servicio opción inválida",
        str(resultados_invalidos),
        "[]",
    )


def probar_servicio_apuestas_pendientes():
    pendientes = listar_apuestas_pendientes()

    comprobar_texto(
        "Servicio listar pendientes devuelve lista",
        str(isinstance(pendientes, list)),
        "True",
    )

    for apuesta in pendientes:
        comprobar_texto(
            "Servicio pendiente tiene resultado pendiente",
            normalizar_resultado(
                apuesta.get(
                    "resultado",
                    "pendiente",
                )
            ),
            "pendiente",
        )


def probar_servicio_resumen_financiero():
    resumen = obtener_resumen_financiero()

    comprobar_texto(
        "Servicio resumen financiero devuelve dict",
        str(isinstance(resumen, dict)),
        "True",
    )

    comprobar_texto(
        "Servicio resumen contiene bankroll",
        str("bankroll_inicial" in resumen),
        "True",
    )

    comprobar_texto(
        "Servicio resumen contiene ROI",
        str("roi" in resumen),
        "True",
    )


def probar_construccion_apuesta_straight():
    comprobar(
        "Servicio siguiente ID vacío",
        obtener_siguiente_id([]),
        1,
    )

    comprobar(
        "Servicio siguiente ID disponible",
        obtener_siguiente_id(
            [
                {"id": 2},
                {"id": 5},
                {"id": "9"},
            ]
        ),
        6,
    )

    datos = {
        "casa": " Caliente ",
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

    apuesta = construir_apuesta_straight(
        datos,
        id_apuesta=25,
        fecha="21/07/2026",
    )

    comprobar(
        "Construcción straight asigna ID",
        apuesta["id"],
        25,
    )

    comprobar_texto(
        "Construcción straight fija modalidad",
        apuesta["modalidad"],
        "straight",
    )

    comprobar_texto(
        "Construcción straight inicia pendiente",
        apuesta["resultado"],
        "pendiente",
    )

    comprobar_texto(
        "Construcción straight guarda mercado",
        apuesta["selecciones"][0]["tipo_apuesta"],
        "Moneyline",
    )

    comprobar_texto(
        "Construcción cuota americana conserva signo",
        apuesta["cuota_texto"],
        "+120",
    )

    comprobar(
        "Construcción cuota americana convierte decimal",
        apuesta["cuota"],
        2.2,
    )

    comprobar(
        "Construcción straight guarda stake",
        apuesta["stake"],
        100.0,
    )

    comprobar_texto(
        "Formato cuota americana negativa",
        formatear_cuota_texto_entrada(
            "americana",
            -110,
        ),
        "-110",
    )


def probar_servicio_eliminar_apuesta():
    respuesta_id_invalido = eliminar_apuesta_por_id("id_invalido")

    comprobar_texto(
        "Servicio eliminar rechaza ID inválido",
        str(respuesta_id_invalido["ok"]),
        "False",
    )

    respuesta_inexistente = eliminar_apuesta_por_id(999999999)

    comprobar_texto(
        "Servicio eliminar detecta apuesta inexistente",
        str(respuesta_inexistente["ok"]),
        "False",
    )


def probar_servicios_configuracion():
    comprobar(
        "Configuración convierte bankroll válido",
        convertir_bankroll("1500"),
        1500.0,
    )

    comprobar_texto(
        "Configuración rechaza bankroll negativo",
        str(convertir_bankroll(-1) is None),
        "True",
    )

    comprobar_texto(
        "Configuración rechaza bankroll no numérico",
        str(convertir_bankroll("invalido") is None),
        "True",
    )

    configuracion = obtener_configuracion_bankroll()

    comprobar_texto(
        "Configuración bankroll devuelve diccionario",
        str(isinstance(configuracion, dict)),
        "True",
    )


def probar_construccion_apuesta_parlay():
    datos = {
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
                "resultado_seleccion": "pendiente",
            },
            {
                "deporte": "Béisbol",
                "liga": "MLB",
                "evento": "Yankees vs Red Sox",
                "mercado": "Moneyline",
                "seleccion": "Yankees",
                "tipo_cuota": "americana",
                "cuota": -110,
                "resultado_seleccion": "pendiente",
            },
        ],
    }

    apuesta = construir_apuesta_parlay(
        datos,
        id_apuesta=30,
        fecha="22/07/2026",
    )

    comprobar(
        "Construcción parlay asigna ID",
        apuesta["id"],
        30,
    )

    comprobar_texto(
        "Construcción parlay asigna fecha",
        apuesta["fecha"],
        "22/07/2026",
    )

    comprobar_texto(
        "Construcción parlay fija modalidad y pendiente",
        str(apuesta["modalidad"] == "parlay" and apuesta["resultado"] == "pendiente"),
        "True",
    )

    comprobar(
        "Construcción parlay guarda selecciones",
        len(apuesta["selecciones"]),
        2,
    )

    comprobar_texto(
        "Construcción parlay detecta mezcla",
        str(apuesta["deporte"] == "Mixto" and apuesta["liga"] == "Mixta"),
        "True",
    )

    comprobar_texto(
        "Construcción parlay guarda mercado",
        apuesta["selecciones"][0]["tipo_apuesta"],
        "Moneyline",
    )

    comprobar_texto(
        "Construcción cuota individual decimal",
        str(
            isclose(
                apuesta["selecciones"][0]["cuota_individual"],
                1.80,
            )
        ),
        "True",
    )

    comprobar_texto(
        "Construcción cuota individual americana conserva texto",
        apuesta["selecciones"][1]["cuota_texto_individual"],
        "-110",
    )

    comprobar_texto(
        "Construcción cuota individual americana convierte decimal",
        str(
            isclose(
                apuesta["selecciones"][1]["cuota_individual"],
                1.9090909090909092,
            )
        ),
        "True",
    )

    comprobar_texto(
        "Construcción parlay conserva cuota total",
        apuesta["cuota_texto"],
        "3.3",
    )

    comprobar_texto(
        "Construcción parlay convierte cuota total",
        str(
            isclose(
                apuesta["cuota"],
                3.30,
            )
        ),
        "True",
    )

    comprobar(
        "Construcción parlay guarda stake",
        apuesta["stake"],
        100.0,
    )


def probar_servicio_actualizacion_parlay():
    respuesta_id_invalido = actualizar_selecciones_parlay_por_id(
        "id_invalido",
        {
            "selecciones": [
                {
                    "numero": 1,
                    "resultado": "ganada",
                }
            ]
        },
    )

    comprobar_texto(
        "Servicio parlay rechaza ID inválido",
        str(respuesta_id_invalido["ok"]),
        "False",
    )

    respuesta_inexistente = actualizar_selecciones_parlay_por_id(
        999999999,
        {
            "selecciones": [
                {
                    "numero": 1,
                    "resultado": "ganada",
                }
            ]
        },
    )

    comprobar_texto(
        "Servicio parlay detecta apuesta inexistente",
        str(respuesta_inexistente["ok"]),
        "False",
    )


def probar_servicio_edicion_parlay():
    respuesta_id_invalido = actualizar_apuesta_parlay_por_id(
        "id_invalido",
        {
            "casa": "Novibet",
        },
    )

    comprobar_texto(
        "Servicio editar parlay rechaza ID inválido",
        str(respuesta_id_invalido["ok"]),
        "False",
    )

    respuesta_inexistente = actualizar_apuesta_parlay_por_id(
        999999999,
        {
            "casa": "Novibet",
        },
    )

    comprobar_texto(
        "Servicio editar parlay detecta inexistente",
        str(respuesta_inexistente["ok"]),
        "False",
    )


def probar_servicio_agregar_seleccion_parlay():
    respuesta_id_invalido = agregar_seleccion_parlay_por_id(
        "id_invalido",
        {},
    )

    comprobar_texto(
        "Servicio agregar selección rechaza ID inválido",
        str(respuesta_id_invalido["ok"]),
        "False",
    )

    respuesta_inexistente = agregar_seleccion_parlay_por_id(
        999999999,
        {},
    )

    comprobar_texto(
        "Servicio agregar selección detecta inexistente",
        str(respuesta_inexistente["ok"]),
        "False",
    )


def probar_servicio_eliminar_seleccion_parlay():
    respuesta_id_invalido = eliminar_seleccion_parlay_por_id(
        "id_invalido",
        1,
    )

    comprobar_texto(
        "Servicio eliminar selección rechaza ID inválido",
        str(respuesta_id_invalido["ok"]),
        "False",
    )

    respuesta_inexistente = eliminar_seleccion_parlay_por_id(
        999999999,
        1,
    )

    comprobar_texto(
        "Servicio eliminar selección detecta inexistente",
        str(respuesta_inexistente["ok"]),
        "False",
    )


def probar_servicio_reordenar_selecciones_parlay():
    respuesta_id_invalido = reordenar_selecciones_parlay_por_id(
        "id_invalido",
        {
            "orden": [2, 1],
        },
    )

    comprobar_texto(
        "Servicio reordenar rechaza ID inválido",
        str(respuesta_id_invalido["ok"]),
        "False",
    )

    respuesta_inexistente = reordenar_selecciones_parlay_por_id(
        999999999,
        {
            "orden": [2, 1],
        },
    )

    comprobar_texto(
        "Servicio reordenar detecta inexistente",
        str(respuesta_inexistente["ok"]),
        "False",
    )


def probar_logica_estadisticas():
    apuestas = [
        {
            "id": 1,
            "deporte": "Fútbol",
            "liga": "Liga MX",
            "casa": "Caliente",
            "modalidad": "straight",
            "momento_apuesta": "prepartido",
            "cuota": 2.0,
            "stake": 100,
            "resultado": "ganada",
            "selecciones": [
                {
                    "evento": "América vs Pumas",
                    "tipo_apuesta": "Moneyline",
                    "seleccion": "América",
                }
            ],
        },
        {
            "id": 2,
            "deporte": "Mixto",
            "liga": "Mixta",
            "casa": "Caliente",
            "modalidad": "parlay",
            "momento_apuesta": "en_vivo",
            "cuota": 3.0,
            "stake": 50,
            "resultado": "perdida",
            "selecciones": [
                {
                    "evento": "Parlay de prueba",
                    "tipo_apuesta": "Moneyline",
                    "seleccion": "Combinada",
                }
            ],
        },
        {
            "id": 3,
            "deporte": "Béisbol",
            "liga": "MLB",
            "casa": "Novibet",
            "modalidad": "straight",
            "momento_apuesta": "prepartido",
            "cuota": 1.90,
            "stake": 25,
            "resultado": "pendiente",
            "selecciones": [
                {
                    "evento": "Yankees vs Red Sox",
                    "tipo_apuesta": "Moneyline",
                    "seleccion": "Yankees",
                }
            ],
        },
    ]

    estadisticas = calcular_estadisticas(
        apuestas,
        bankroll_inicial=1000,
    )

    comprobar(
        "Estadísticas total apostado",
        estadisticas["total_apostado"],
        150.0,
    )

    comprobar(
        "Estadísticas ganancia neta",
        estadisticas["ganancia_neta"],
        50.0,
    )

    comprobar_texto(
        "Estadísticas conteo de resultados",
        str(
            estadisticas["ganadas"] == 1
            and estadisticas["perdidas"] == 1
            and estadisticas["pendientes"] == 1
        ),
        "True",
    )

    comprobar(
        "Estadísticas stake pendiente",
        estadisticas["stake_pendiente"],
        25.0,
    )

    comprobar(
        "Estadísticas win rate",
        estadisticas["win_rate"],
        50.0,
    )

    comprobar_texto(
        "Estadísticas ROI",
        str(
            isclose(
                estadisticas["roi"],
                33.33333333333333,
            )
        ),
        "True",
    )

    comprobar(
        "Estadísticas bankroll actual",
        estadisticas["bankroll_actual"],
        1050.0,
    )

    comprobar_texto(
        "Estadísticas rendimiento por modalidad",
        str(
            estadisticas["rendimiento_modalidades"]["straight"] == 100.0
            and estadisticas["rendimiento_modalidades"]["parlay"] == -50.0
        ),
        "True",
    )

    comprobar_texto(
        "Estadísticas rendimiento por momento",
        str(
            estadisticas["rendimiento_momentos"]["prepartido"]["ganadas"] == 1
            and estadisticas["rendimiento_momentos"]["en_vivo"]["perdidas"] == 1
        ),
        "True",
    )

    comprobar_texto(
        "Estadísticas genera alertas",
        str(
            isinstance(
                estadisticas["alertas"],
                list,
            )
            and len(estadisticas["alertas"]) > 0
        ),
        "True",
    )


def probar_servicio_estadisticas():
    estadisticas = obtener_estadisticas()

    comprobar_texto(
        "Servicio estadísticas devuelve diccionario",
        str(
            isinstance(
                estadisticas,
                dict,
            )
        ),
        "True",
    )

    comprobar_texto(
        "Servicio estadísticas contiene ROI",
        str("roi" in estadisticas),
        "True",
    )

    comprobar_texto(
        "Servicio estadísticas contiene alertas",
        str(
            isinstance(
                estadisticas.get("alertas"),
                list,
            )
        ),
        "True",
    )

    comprobar_texto(
        "Servicio estadísticas contiene bankroll",
        str(
            isinstance(
                estadisticas.get("bankroll_actual"),
                float,
            )
        ),
        "True",
    )


def probar_logica_analisis_cuotas():
    comprobar_texto(
        "Analíticas detecta rango cuota baja",
        obtener_rango_cuota(1.49),
        "1.01 - 1.49",
    )

    comprobar_texto(
        "Analíticas detecta límite de rango",
        obtener_rango_cuota(1.50),
        "1.50 - 1.79",
    )

    comprobar_texto(
        "Analíticas detecta rango cuota alta",
        obtener_rango_cuota(2.50),
        "2.50 o más",
    )

    comprobar_texto(
        "Analíticas clasifica muestra pequeña",
        clasificar_muestra(9),
        "Muy pequeña",
    )

    comprobar_texto(
        "Analíticas clasifica muestra limitada",
        clasificar_muestra(10),
        "Limitada",
    )

    apuestas = [
        {
            "id": 1,
            "tipo_cuota": "decimal",
            "cuota": 2.0,
            "stake": 100,
            "resultado": "ganada",
        },
        {
            "id": 2,
            "tipo_cuota": "decimal",
            "cuota": 1.5,
            "stake": 50,
            "resultado": "perdida",
        },
        {
            "id": 3,
            "tipo_cuota": "decimal",
            "cuota": 1.9,
            "stake": 20,
            "resultado": "push",
        },
        {
            "id": 4,
            "tipo_cuota": "decimal",
            "cuota": 2.5,
            "stake": 25,
            "resultado": "pendiente",
        },
    ]

    analisis = calcular_analisis_cuotas(apuestas)

    rangos = {datos["rango"]: datos for datos in analisis["rangos"]}

    comprobar(
        "Analíticas ignora apuestas pendientes",
        analisis["apuestas_validas"],
        3,
    )

    rango_ganado = rangos.get("2.00 - 2.49")

    comprobar_texto(
        "Analíticas genera rango ganador",
        str(rango_ganado is not None),
        "True",
    )

    if rango_ganado is None:
        print(
            "Rangos generados:",
            list(rangos.keys()),
        )
        return

    comprobar_texto(
        "Analíticas calcula rango ganador",
        str(rango_ganado["ganadas"] == 1 and rango_ganado["win_rate"] == 100),
        "True",
    )

    comprobar_texto(
        "Analíticas calcula ROI ganador",
        str(
            isclose(
                rango_ganado["roi"],
                100.0,
            )
        ),
        "True",
    )

    rango_perdido = rangos["1.50 - 1.79"]

    comprobar_texto(
        "Analíticas calcula ROI perdido",
        str(
            isclose(
                rango_perdido["roi"],
                -100.0,
            )
        ),
        "True",
    )

    rango_push = rangos["1.80 - 1.99"]

    comprobar_texto(
        "Analíticas calcula rango push",
        str(
            rango_push["push"] == 1
            and rango_push["decididas"] == 0
            and rango_push["roi"] == 0
        ),
        "True",
    )


def probar_servicio_analisis_cuotas():
    analisis = obtener_analisis_cuotas()

    comprobar_texto(
        "Servicio analíticas devuelve diccionario",
        str(isinstance(analisis, dict)),
        "True",
    )

    comprobar_texto(
        "Servicio analíticas contiene total",
        str(
            isinstance(
                analisis.get("total_apuestas"),
                int,
            )
        ),
        "True",
    )

    comprobar_texto(
        "Servicio analíticas contiene rangos",
        str(
            isinstance(
                analisis.get("rangos"),
                list,
            )
        ),
        "True",
    )

    comprobar_texto(
        "Servicio analíticas contiene nota",
        str(
            isinstance(
                analisis.get("nota"),
                str,
            )
        ),
        "True",
    )


def probar_logica_analisis_parlays():
    cuota_americana = obtener_cuota_individual_decimal(
        {
            "tipo_cuota_individual": ("americana"),
            "cuota_individual": -110,
            "cuota_texto_individual": ("-110"),
        }
    )

    comprobar_texto(
        "Analíticas parlay convierte cuota americana",
        str(
            isclose(
                cuota_americana,
                1.9090909090909092,
            )
        ),
        "True",
    )

    parlay_ganado = {
        "id": 1,
        "modalidad": "parlay",
        "resultado": "ganada",
        "deporte": "Fútbol",
        "liga": "Liga MX",
        "tipo_cuota": "decimal",
        "cuota": 3.20,
        "stake": 100,
        "selecciones": [
            {
                "deporte": "Fútbol",
                "liga": "Liga MX",
                "evento": "América vs Pumas",
                "tipo_apuesta": "Moneyline",
                "seleccion": "América",
                "tipo_cuota_individual": "decimal",
                "cuota_individual": 2.0,
                "resultado_seleccion": "ganada",
            },
            {
                "deporte": "Fútbol",
                "liga": "Liga MX",
                "evento": "Tigres vs Monterrey",
                "tipo_apuesta": "Over/Under",
                "seleccion": "Over 2.5",
                "tipo_cuota_individual": "decimal",
                "cuota_individual": 1.5,
                "resultado_seleccion": "push",
            },
        ],
    }

    parlay_perdido = {
        "id": 2,
        "modalidad": "parlay",
        "resultado": "perdida",
        "deporte": "Mixto",
        "liga": "Mixta",
        "tipo_cuota": "decimal",
        "cuota": 4.50,
        "stake": 50,
        "selecciones": [
            {
                "deporte": "Fútbol",
                "liga": "Liga MX",
                "evento": "Cruz Azul vs Toluca",
                "tipo_apuesta": "Moneyline",
                "seleccion": "Cruz Azul",
                "tipo_cuota_individual": "decimal",
                "cuota_individual": 1.8,
                "resultado_seleccion": "perdida",
            },
            {
                "deporte": "Béisbol",
                "liga": "MLB",
                "evento": "Yankees vs Red Sox",
                "tipo_apuesta": "Moneyline",
                "seleccion": "Yankees",
                "tipo_cuota_individual": "decimal",
                "cuota_individual": 2.0,
                "resultado_seleccion": "ganada",
            },
            {
                "deporte": "Hockey",
                "liga": "NHL",
                "evento": "Oilers vs Flames",
                "tipo_apuesta": "Total",
                "seleccion": "Over 5.5",
                "tipo_cuota_individual": "decimal",
                "cuota_individual": 1.5,
                "resultado_seleccion": "pendiente",
            },
        ],
    }

    parlay_pendiente = {
        "id": 3,
        "modalidad": "parlay",
        "resultado": "pendiente",
        "deporte": "Fútbol",
        "liga": "Liga MX",
        "tipo_cuota": "decimal",
        "cuota": 2.50,
        "stake": 25,
        "selecciones": [
            {
                "deporte": "Fútbol",
                "liga": "Liga MX",
                "evento": "América vs Pumas",
                "tipo_apuesta": "Moneyline",
                "seleccion": "América",
                "tipo_cuota_individual": "decimal",
                "cuota_individual": 1.6,
                "resultado_seleccion": "pendiente",
            },
            {
                "deporte": "Fútbol",
                "liga": "Liga MX",
                "evento": "América vs Pumas",
                "tipo_apuesta": "Over/Under",
                "seleccion": "Over 2.5",
                "tipo_cuota_individual": "decimal",
                "cuota_individual": 1.7,
                "resultado_seleccion": "pendiente",
            },
        ],
    }

    apuesta_straight = {
        "id": 4,
        "modalidad": "straight",
        "resultado": "ganada",
        "cuota": 2.0,
        "stake": 100,
        "selecciones": [],
    }

    comprobar_texto(
        "Analíticas clasifica parlay unideporte",
        clasificar_parlay_por_deportes(parlay_ganado),
        "Un solo deporte",
    )

    comprobar_texto(
        "Analíticas clasifica parlay multideporte",
        clasificar_parlay_por_deportes(parlay_perdido),
        "Multideporte",
    )

    comprobar_texto(
        "Analíticas clasifica eventos diferentes",
        clasificar_parlay_por_eventos(parlay_ganado),
        "Eventos diferentes",
    )

    comprobar_texto(
        "Analíticas clasifica mismo evento",
        clasificar_parlay_por_eventos(parlay_pendiente),
        "Mismo evento",
    )

    analisis = calcular_analisis_parlays(
        [
            parlay_ganado,
            parlay_perdido,
            parlay_pendiente,
            apuesta_straight,
        ]
    )

    comprobar(
        "Analíticas cuenta parlays registrados",
        analisis["parlays_registrados"],
        3,
    )

    comprobar_texto(
        "Analíticas cuenta parlays resueltos y pendientes",
        str(analisis["parlays_resueltos"] == 2 and analisis["parlays_pendientes"] == 1),
        "True",
    )

    resultados = analisis["resultados_selecciones"]

    comprobar_texto(
        "Analíticas cuenta resultados de selecciones",
        str(
            resultados["ganadas"] == 2
            and resultados["perdidas"] == 1
            and resultados["push"] == 1
            and resultados["pendientes"] == 3
            and resultados["sin_resultado"] == 0
        ),
        "True",
    )

    resumen_piernas = analisis["rendimiento_piernas"]

    comprobar_texto(
        "Analíticas agrupa por número de selecciones",
        str(
            resumen_piernas["2 selecciones"]["registrados"] == 2
            and resumen_piernas["3 selecciones"]["registrados"] == 1
        ),
        "True",
    )

    resumen_deportes = analisis["rendimiento_deportes"]

    comprobar_texto(
        "Analíticas agrupa por deportes",
        str(
            resumen_deportes["Un solo deporte"]["registrados"] == 2
            and resumen_deportes["Multideporte"]["registrados"] == 1
        ),
        "True",
    )

    comprobar_texto(
        "Analíticas detecta mercados perdidos",
        str(
            analisis["mercados_perdidos"].get("Moneyline") == 1
            and analisis["deportes_perdidos"].get("Fútbol") == 1
        ),
        "True",
    )

    comparaciones = analisis["comparaciones_cuotas"]

    comprobar_texto(
        "Analíticas compara cuotas de parlays",
        str(
            len(comparaciones) == 3
            and comparaciones[0]["id"] == 1
            and comparaciones[1]["id"] == 2
            and comparaciones[2]["id"] == 3
        ),
        "True",
    )


def probar_servicio_analisis_parlays():
    analisis = obtener_analisis_parlays()

    comprobar_texto(
        "Servicio analíticas parlays devuelve diccionario",
        str(isinstance(analisis, dict)),
        "True",
    )

    comprobar_texto(
        "Servicio analíticas parlays contiene total",
        str(
            isinstance(
                analisis.get("parlays_registrados"),
                int,
            )
        ),
        "True",
    )

    comprobar_texto(
        "Servicio analíticas parlays contiene rendimientos",
        str(
            isinstance(
                analisis.get("rendimiento_piernas"),
                dict,
            )
        ),
        "True",
    )

    comprobar_texto(
        "Servicio analíticas parlays contiene comparaciones",
        str(
            isinstance(
                analisis.get("comparaciones_cuotas"),
                list,
            )
        ),
        "True",
    )


def probar_servicio_diagnostico():
    diagnostico = obtener_diagnostico_sistema()

    comprobar_texto(
        "Servicio diagnóstico devuelve diccionario",
        str(isinstance(diagnostico, dict)),
        "True",
    )

    comprobar_texto(
        "Servicio diagnóstico contiene estado",
        str(
            diagnostico.get("estado_general")
            in {
                "Correcto",
                "Requiere revisión",
            }
        ),
        "True",
    )

    comprobar_texto(
        "Servicio diagnóstico contiene base SQLite",
        str(
            isinstance(
                diagnostico.get("base_datos_sqlite"),
                bool,
            )
        ),
        "True",
    )

    comprobar_texto(
        "Servicio diagnóstico contiene conteos",
        str(
            isinstance(
                diagnostico.get("apuestas_registradas"),
                int,
            )
            and isinstance(
                diagnostico.get("selecciones_registradas"),
                int,
            )
        ),
        "True",
    )

    comprobar_texto(
        "Servicio diagnóstico contiene integridad",
        str(
            isinstance(
                diagnostico.get("problemas_integridad"),
                list,
            )
            and isinstance(
                diagnostico.get("cantidad_problemas_integridad"),
                int,
            )
        ),
        "True",
    )

    comprobar_texto(
        "Servicio diagnóstico no expone rutas internas",
        str(
            "ruta_base_datos" not in diagnostico
            and "ultimo_respaldo" not in diagnostico
        ),
        "True",
    )

    comprobar_texto(
        "Servicio diagnóstico informa respaldo seguro",
        str(
            isinstance(
                diagnostico.get("ultimo_respaldo_disponible"),
                bool,
            )
        ),
        "True",
    )


def probar_utilidades_errores_api():
    comprobar_texto(
        "Errores API asigna código 400",
        obtener_codigo_error_http(400),
        "solicitud_invalida",
    )

    comprobar_texto(
        "Errores API asigna código 404",
        obtener_codigo_error_http(404),
        "no_encontrado",
    )

    comprobar_texto(
        "Errores API asigna código 409",
        obtener_codigo_error_http(409),
        "conflicto",
    )

    comprobar_texto(
        "Errores API asigna código 422",
        obtener_codigo_error_http(422),
        "validacion_fallida",
    )

    comprobar_texto(
        "Errores API conserva mensaje recibido",
        obtener_mensaje_error(
            "Apuesta no encontrada.",
            404,
        ),
        "Apuesta no encontrada.",
    )

    respuesta = construir_respuesta_error(
        codigo="no_encontrado",
        mensaje="Apuesta no encontrada.",
    )

    comprobar_texto(
        "Errores API construye respuesta estándar",
        str(
            respuesta["ok"] is False
            and respuesta["error"]["codigo"] == "no_encontrado"
            and respuesta["error"]["mensaje"] == "Apuesta no encontrada."
        ),
        "True",
    )


def probar_configuracion_cors():
    origenes = obtener_origenes_cors()

    comprobar_texto(
        "CORS permite frontend React local",
        str(
            "http://localhost:5173" in origenes and "http://127.0.0.1:5173" in origenes
        ),
        "True",
    )

    comprobar_texto(
        "CORS permite métodos necesarios",
        str(
            set(METODOS_CORS)
            == {
                "GET",
                "POST",
                "PUT",
                "PATCH",
                "DELETE",
                "OPTIONS",
            }
        ),
        "True",
    )

    comprobar_texto(
        "CORS permite encabezados necesarios",
        str(
            {
                "Accept",
                "Authorization",
                "Content-Type",
            }.issubset(set(ENCABEZADOS_CORS))
        ),
        "True",
    )


def ejecutar_pruebas():
    print(f"\n===== PRUEBAS DE {NOMBRE_APP.upper()} =====")

    probar_straight_ganada()
    probar_straight_perdida()
    probar_straight_push()
    probar_apuesta_pendiente()
    probar_parlay_ganado()
    probar_parlay_perdido()
    probar_parlay_con_push()
    probar_parlay_todo_push()
    probar_cuota_liquidada_oficial()
    probar_retorno_total_real()
    probar_normalizacion_texto()
    probar_resultado_general_parlay()
    probar_liquidaciones()
    probar_busquedas()
    probar_bankroll()
    probar_modo_almacenamiento()
    probar_diagnostico()
    probar_metricas_diagnostico()
    probar_integridad_diagnostico()
    probar_resumen_financiero()
    probar_apuestas_pendientes()
    probar_vistas_rapidas()
    probar_resumen_vista_rapida()
    probar_configuracion_app()
    probar_ruta_base_datos()
    probar_tablas_principales_sqlite()
    probar_tamano_base_datos()
    probar_estado_general_diagnostico()
    probar_texto_diagnostico()
    probar_texto_resumen_financiero()
    probar_exportacion_todos_reportes()
    probar_reportes_exportados()
    probar_servicios_apuestas()
    probar_servicio_cierre_apuestas()
    probar_servicio_busqueda_apuestas()
    probar_busqueda_con_servicio()
    probar_servicio_apuestas_pendientes()
    probar_servicio_resumen_financiero()
    probar_construccion_apuesta_straight()
    probar_construccion_apuesta_parlay()
    probar_servicio_eliminar_apuesta()
    probar_servicios_configuracion()
    probar_servicio_actualizacion_parlay()
    probar_servicio_edicion_parlay()
    probar_servicio_agregar_seleccion_parlay()
    probar_servicio_eliminar_seleccion_parlay()
    probar_servicio_reordenar_selecciones_parlay()
    probar_logica_estadisticas()
    probar_servicio_estadisticas()
    probar_logica_analisis_cuotas()
    probar_logica_analisis_parlays()
    probar_servicio_analisis_cuotas()
    probar_servicio_analisis_parlays()
    probar_servicio_diagnostico()
    probar_utilidades_errores_api()
    probar_configuracion_cors()

    total = CONTADOR_PRUEBAS["correctas"] + CONTADOR_PRUEBAS["fallidas"]

    print("\n" + "=" * 45)
    print("Total de pruebas:", total)
    print(
        "Pruebas correctas:",
        CONTADOR_PRUEBAS["correctas"],
    )
    print(
        "Pruebas fallidas:",
        CONTADOR_PRUEBAS["fallidas"],
    )
    print("=" * 45)

    if CONTADOR_PRUEBAS["fallidas"] == 0:
        print("\nTodas las pruebas pasaron correctamente.")
    else:
        print("\nHay cálculos que necesitan revisión.")
        raise SystemExit(1)


if __name__ == "__main__":
    ejecutar_pruebas()
