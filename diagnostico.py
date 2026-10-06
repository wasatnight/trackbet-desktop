from datetime import datetime
from pathlib import Path
from base_datos import (
    formatear_tamano_archivo,
    obtener_ruta_base_datos,
    obtener_tamano_base_datos,
    validar_tablas_principales,
)
from configuracion_app import (
    NOMBRE_APP,
    VERSION_APP,
    NOMBRE_BASE_DATOS,
    CARPETA_RESPALDOS,
)

from almacenamiento import (
    cargar_apuestas,
    cargar_config,
    obtener_modo_almacenamiento,
)
from calculos import (
    calcular_ganancia_apuesta,
    formato_dinero,
    formato_monto,
)


def contar_selecciones(apuestas):
    """Cuenta el total de selecciones registradas."""

    return sum(len(apuesta.get("selecciones", [])) for apuesta in apuestas)


def calcular_metricas_diagnostico(
    apuestas,
    bankroll_inicial,
):
    """Calcula métricas generales para el diagnóstico."""

    try:
        bankroll_inicial = float(bankroll_inicial)
    except (TypeError, ValueError):
        bankroll_inicial = 0.0

    ganancia_neta = 0
    apuestas_pendientes = 0
    stake_pendiente = 0

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

        try:
            stake = float(
                apuesta.get(
                    "stake",
                    0,
                )
            )
        except (TypeError, ValueError):
            stake = 0

        if resultado == "pendiente":
            apuestas_pendientes += 1
            stake_pendiente += stake

        ganancia_neta += calcular_ganancia_apuesta(apuesta)

    bankroll_actual = bankroll_inicial + ganancia_neta

    return {
        "ganancia_neta": ganancia_neta,
        "bankroll_actual": bankroll_actual,
        "apuestas_pendientes": apuestas_pendientes,
        "stake_pendiente": stake_pendiente,
    }


def validar_integridad_apuestas(apuestas):
    """Detecta posibles problemas en las apuestas registradas."""

    problemas = []

    resultados_validos = {
        "ganada",
        "perdida",
        "push",
        "pendiente",
    }

    for apuesta in apuestas:
        apuesta_id = apuesta.get(
            "id",
            "sin_id",
        )

        if "id" not in apuesta:
            problemas.append("Apuesta sin ID detectada.")

        try:
            stake = float(
                apuesta.get(
                    "stake",
                    0,
                )
            )
        except (TypeError, ValueError):
            stake = 0

        if stake <= 0:
            problemas.append(f"Apuesta ID {apuesta_id}: stake inválido.")

        resultado = (
            str(
                apuesta.get(
                    "resultado",
                    "",
                )
            )
            .strip()
            .lower()
        )

        if resultado not in resultados_validos:
            problemas.append(f"Apuesta ID {apuesta_id}: resultado inválido.")

        if resultado == "pendiente" and apuesta.get("retorno_total_real") is not None:
            problemas.append(f"Apuesta ID {apuesta_id}: pendiente con retorno oficial.")

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

        selecciones = apuesta.get(
            "selecciones",
            [],
        )

        if modalidad == "parlay" and len(selecciones) < 2:
            problemas.append(
                f"Apuesta ID {apuesta_id}: parlay con menos de 2 selecciones."
            )

        for numero, seleccion in enumerate(
            selecciones,
            start=1,
        ):
            if not seleccion.get("evento"):
                problemas.append(
                    f"Apuesta ID {apuesta_id}, selección {numero}: evento vacío."
                )

            if not seleccion.get("tipo_apuesta"):
                problemas.append(
                    f"Apuesta ID {apuesta_id}, selección {numero}: mercado vacío."
                )

            if not seleccion.get("seleccion"):
                problemas.append(
                    f"Apuesta ID {apuesta_id}, selección {numero}: selección vacía."
                )

    return problemas


def obtener_ultimo_respaldo():
    """Obtiene el respaldo más reciente si existe."""

    carpeta_respaldos = Path(CARPETA_RESPALDOS)

    if not carpeta_respaldos.exists():
        return None

    respaldos = list(carpeta_respaldos.glob("apuestas_*.json"))

    if not respaldos:
        return None

    ultimo_respaldo = max(
        respaldos,
        key=lambda ruta: ruta.stat().st_mtime,
    )

    return ultimo_respaldo


def verificar_base_datos_sqlite():
    """Verifica si existe la base de datos SQLite."""

    ruta_bd = Path(NOMBRE_BASE_DATOS)

    return ruta_bd.exists()


def obtener_resumen_diagnostico():
    """Genera un resumen del estado actual del sistema."""

    apuestas = cargar_apuestas()
    config = cargar_config()

    bankroll_inicial = config.get(
        "bankroll_inicial",
        0,
    )
    problemas_integridad = validar_integridad_apuestas(apuestas)

    ultimo_respaldo = obtener_ultimo_respaldo()

    metricas = calcular_metricas_diagnostico(
        apuestas,
        bankroll_inicial,
    )
    estado_tablas = validar_tablas_principales()
    tamano_base_datos = obtener_tamano_base_datos()
    base_sqlite_disponible = verificar_base_datos_sqlite()

    estado_general_correcto = (
        base_sqlite_disponible
        and estado_tablas["valida"]
        and len(problemas_integridad) == 0
        and tamano_base_datos > 0
    )

    return {
        "nombre_app": NOMBRE_APP,
        "version_app": VERSION_APP,
        "estado_general": (
            "Correcto" if estado_general_correcto else "Requiere revisión"
        ),
        "almacenamiento": obtener_modo_almacenamiento(),
        "base_datos": NOMBRE_BASE_DATOS,
        "ruta_base_datos": obtener_ruta_base_datos(),
        "tamano_base_datos": tamano_base_datos,
        "tamano_base_datos_formateado": formatear_tamano_archivo(tamano_base_datos),
        "tablas_validas": estado_tablas["valida"],
        "tablas_faltantes": estado_tablas["tablas_faltantes"],
        "base_datos_sqlite": base_sqlite_disponible,
        "apuestas_registradas": len(apuestas),
        "selecciones_registradas": contar_selecciones(apuestas),
        "bankroll_inicial": bankroll_inicial,
        "ganancia_neta": metricas["ganancia_neta"],
        "bankroll_actual": metricas["bankroll_actual"],
        "apuestas_pendientes": metricas["apuestas_pendientes"],
        "stake_pendiente": metricas["stake_pendiente"],
        "ultimo_respaldo": ultimo_respaldo,
        "problemas_integridad": problemas_integridad,
    }


def mostrar_diagnostico():
    """Muestra el diagnóstico general del sistema."""

    resumen = obtener_resumen_diagnostico()

    print("\n===== DIAGNÓSTICO DEL SISTEMA =====")
    print("Aplicación:", resumen["nombre_app"])
    print("Versión:", resumen["version_app"])
    print("Estado general:", resumen["estado_general"])
    print("Base de datos:", resumen["base_datos"])
    print("Ruta de base de datos:", resumen["ruta_base_datos"])
    print(
        "Tamaño de base de datos:",
        resumen["tamano_base_datos_formateado"],
    )
    print(
        "Tablas principales:",
        "Correctas" if resumen["tablas_validas"] else "Incompletas",
    )

    if resumen["tablas_faltantes"]:
        print(
            "Tablas faltantes:",
            ", ".join(resumen["tablas_faltantes"]),
        )
    print(
        "Almacenamiento activo:",
        resumen["almacenamiento"],
    )
    print(
        "Apuestas registradas:",
        resumen["apuestas_registradas"],
    )
    print(
        "Selecciones registradas:",
        resumen["selecciones_registradas"],
    )
    print(
        "Bankroll inicial:",
        formato_monto(resumen["bankroll_inicial"]),
    )
    print(
        "Ganancia neta total:",
        formato_dinero(resumen["ganancia_neta"]),
    )
    print(
        "Bankroll actual estimado:",
        formato_monto(resumen["bankroll_actual"]),
    )
    print(
        "Apuestas pendientes:",
        resumen["apuestas_pendientes"],
    )
    print(
        "Stake pendiente:",
        formato_monto(resumen["stake_pendiente"]),
    )
    print(
        "Base de datos SQLite:",
        ("Disponible" if resumen["base_datos_sqlite"] else "No encontrada"),
    )

    if resumen["ultimo_respaldo"] is None:
        print("Último respaldo: No encontrado")
    else:
        print(
            "Último respaldo:",
            resumen["ultimo_respaldo"],
        )

    problemas = resumen["problemas_integridad"]

    print(
        "Problemas de integridad:",
        len(problemas),
    )

    if problemas:
        print("\n===== ALERTAS DE INTEGRIDAD =====")

        for problema in problemas:
            print("-", problema)


def generar_texto_diagnostico():
    """Genera el diagnóstico del sistema en formato de texto."""

    resumen = obtener_resumen_diagnostico()

    lineas = [
        "===== DIAGNÓSTICO DEL SISTEMA =====",
        f"Aplicación: {resumen['nombre_app']}",
        f"Versión: {resumen['version_app']}",
        f"Estado general: {resumen['estado_general']}",
        f"Base de datos: {resumen['base_datos']}",
        f"Ruta de base de datos: {resumen['ruta_base_datos']}",
        f"Tamaño de base de datos: {resumen['tamano_base_datos_formateado']}",
        "Tablas principales: "
        + ("Correctas" if resumen["tablas_validas"] else "Incompletas"),
        f"Almacenamiento activo: {resumen['almacenamiento']}",
        f"Apuestas registradas: {resumen['apuestas_registradas']}",
        f"Selecciones registradas: {resumen['selecciones_registradas']}",
        f"Bankroll inicial: ${resumen['bankroll_inicial']:.2f}",
        f"Ganancia neta total: ${resumen['ganancia_neta']:.2f}",
        f"Bankroll actual estimado: ${resumen['bankroll_actual']:.2f}",
        f"Apuestas pendientes: {resumen['apuestas_pendientes']}",
        f"Stake pendiente: ${resumen['stake_pendiente']:.2f}",
        "Base de datos SQLite: "
        + ("Disponible" if resumen["base_datos_sqlite"] else "No disponible"),
        f"Último respaldo: {resumen['ultimo_respaldo']}",
        f"Problemas de integridad: {len(resumen['problemas_integridad'])}",
    ]

    if resumen["tablas_faltantes"]:
        lineas.append("Tablas faltantes: " + ", ".join(resumen["tablas_faltantes"]))

    if resumen["problemas_integridad"]:
        lineas.append("")
        lineas.append("Detalle de problemas:")

        for problema in resumen["problemas_integridad"]:
            lineas.append(f"- {problema}")

    return "\n".join(lineas)


def exportar_diagnostico_txt():
    """Exporta el diagnóstico del sistema a un archivo TXT."""

    carpeta = Path("reportes")
    carpeta.mkdir(exist_ok=True)

    fecha = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    ruta_archivo = carpeta / f"diagnostico_trackbet_{fecha}.txt"

    texto = generar_texto_diagnostico()

    with open(ruta_archivo, "w", encoding="utf-8") as archivo:
        archivo.write(texto)

    print("\nDiagnóstico exportado correctamente.")
    print("Archivo:", ruta_archivo)
