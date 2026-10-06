import sqlite3
from pathlib import Path

from configuracion_app import NOMBRE_BASE_DATOS

CARPETA_PROYECTO = Path(__file__).resolve().parent
RUTA_BASE_DATOS = CARPETA_PROYECTO / NOMBRE_BASE_DATOS


def obtener_ruta_base_datos():
    """Devuelve la ruta absoluta de la base de datos."""

    return str(RUTA_BASE_DATOS)


def obtener_tamano_base_datos():
    """Devuelve el tamaño de la base de datos en bytes."""

    if not RUTA_BASE_DATOS.exists():
        return 0

    return RUTA_BASE_DATOS.stat().st_size


def formatear_tamano_archivo(tamano_bytes):
    """Convierte bytes a un formato legible."""

    if tamano_bytes < 1024:
        return f"{tamano_bytes} B"

    if tamano_bytes < 1024 * 1024:
        return f"{tamano_bytes / 1024:.2f} KB"

    return f"{tamano_bytes / (1024 * 1024):.2f} MB"


def obtener_tablas_existentes():
    """Devuelve una lista con las tablas existentes en SQLite."""

    with conectar_bd() as conexion:
        filas = conexion.execute("""
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
            ORDER BY name
            """).fetchall()

    return [fila["name"] for fila in filas]


def validar_tablas_principales():
    """Valida que existan las tablas principales de la app."""

    tablas_existentes = set(obtener_tablas_existentes())

    tablas_requeridas = {
        "apuestas",
        "selecciones",
        "configuracion",
    }

    tablas_faltantes = sorted(tablas_requeridas - tablas_existentes)

    return {
        "valida": len(tablas_faltantes) == 0,
        "tablas_existentes": sorted(tablas_existentes),
        "tablas_faltantes": tablas_faltantes,
    }


def conectar_bd():
    """Crea una conexión con la base de datos SQLite."""

    conexion = sqlite3.connect(RUTA_BASE_DATOS)
    conexion.row_factory = sqlite3.Row
    conexion.execute("PRAGMA foreign_keys = ON")

    return conexion


def crear_tablas():
    """Crea las tablas principales de TrackBet si no existen."""

    with conectar_bd() as conexion:
        conexion.execute("""
            CREATE TABLE IF NOT EXISTS apuestas (
                id INTEGER PRIMARY KEY,
                fecha TEXT NOT NULL,
                casa TEXT NOT NULL,
                deporte TEXT NOT NULL,
                liga TEXT NOT NULL,
                momento_apuesta TEXT NOT NULL,
                modalidad TEXT NOT NULL,
                tipo_cuota TEXT NOT NULL,
                cuota_texto TEXT NOT NULL,
                cuota REAL NOT NULL,
                stake REAL NOT NULL,
                resultado TEXT NOT NULL,
                cuota_liquidada REAL,
                tipo_cuota_liquidada TEXT,
                cuota_liquidada_texto TEXT,
                retorno_total_real REAL
            )
            """)

        conexion.execute("""
            CREATE TABLE IF NOT EXISTS selecciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                apuesta_id INTEGER NOT NULL,
                numero INTEGER NOT NULL,
                deporte TEXT,
                liga TEXT,
                evento TEXT NOT NULL,
                tipo_apuesta TEXT NOT NULL,
                seleccion TEXT NOT NULL,
                tipo_cuota_individual TEXT,
                cuota_texto_individual TEXT,
                cuota_individual REAL,
                resultado_seleccion TEXT,
                FOREIGN KEY (apuesta_id)
                    REFERENCES apuestas (id)
                    ON DELETE CASCADE
            )
            """)

        conexion.execute("""
            CREATE TABLE IF NOT EXISTS configuracion (
                clave TEXT PRIMARY KEY,
                valor TEXT NOT NULL
            )
            """)

    print("Base de datos y tablas creadas correctamente.")


def probar_conexion():
    """Prueba que SQLite funcione correctamente."""

    with conectar_bd() as conexion:
        resultado = conexion.execute("SELECT sqlite_version()").fetchone()

    print(
        "Conexión SQLite correcta. Versión:",
        resultado[0],
    )


if __name__ == "__main__":
    probar_conexion()
    crear_tablas()
