from almacenamiento import cargar_apuestas
from presentacion import mostrar_detalle_apuesta
from validaciones import normalizar_texto
from servicios_apuestas import buscar_apuestas_por_filtros

CAMPOS_BUSQUEDA = {
    "1": "deporte",
    "2": "casa",
    "3": "liga",
    "4": "resultado",
    "5": "modalidad",
    "8": "momento_apuesta",
}


def filtrar_apuestas(
    apuestas,
    opcion_busqueda,
    valor_buscado,
):
    """Filtra apuestas sin pedir datos por teclado."""

    valor_buscado = normalizar_texto(valor_buscado)

    if not valor_buscado:
        return []

    resultados = []

    if opcion_busqueda in CAMPOS_BUSQUEDA:
        campo = CAMPOS_BUSQUEDA[opcion_busqueda]

        for apuesta in apuestas:
            valor_apuesta = apuesta.get(
                campo,
                "",
            )

            valor_apuesta = normalizar_texto(valor_apuesta)

            if valor_buscado in valor_apuesta:
                resultados.append(apuesta)

    elif opcion_busqueda == "6":
        for apuesta in apuestas:
            for seleccion in apuesta.get(
                "selecciones",
                [],
            ):
                mercado = normalizar_texto(
                    seleccion.get(
                        "tipo_apuesta",
                        "",
                    )
                )

                if valor_buscado in mercado:
                    resultados.append(apuesta)
                    break

    elif opcion_busqueda == "7":
        for apuesta in apuestas:
            for seleccion in apuesta.get(
                "selecciones",
                [],
            ):
                evento = normalizar_texto(
                    seleccion.get(
                        "evento",
                        "",
                    )
                )

                if valor_buscado in evento:
                    resultados.append(apuesta)
                    break

    return resultados


def filtrar_apuestas_desde_servicio(opcion_busqueda, valor_buscado):
    """Filtra apuestas usando la capa de servicios."""

    campo = CAMPOS_BUSQUEDA.get(opcion_busqueda)

    if not campo:
        return []

    return buscar_apuestas_por_filtros(
        {
            campo: valor_buscado,
        }
    )


def pedir_valor_busqueda(opcion_busqueda):
    """Solicita al usuario el valor que desea buscar."""

    if opcion_busqueda in CAMPOS_BUSQUEDA:
        campo = CAMPOS_BUSQUEDA[opcion_busqueda]

        if campo == "momento_apuesta":
            print("\nPuedes escribir:")
            print("- Prepartido")
            print("- En vivo")
            print("- No registrado")

        return input(f"Escribe el valor de {campo}: ")

    if opcion_busqueda == "6":
        return input("Escribe el mercado: ")

    if opcion_busqueda == "7":
        return input("Escribe el evento: ")

    return ""


def buscar_apuestas():
    """Busca apuestas por diferentes criterios."""

    apuestas = cargar_apuestas()

    if not apuestas:
        print("\nNo hay apuestas registradas.")
        return

    print("\n===== BUSCAR APUESTAS =====")
    print("1. Buscar por deporte")
    print("2. Buscar por casa de apuestas")
    print("3. Buscar por liga")
    print("4. Buscar por resultado")
    print("5. Buscar por modalidad")
    print("6. Buscar por mercado")
    print("7. Buscar por evento")
    print("8. Buscar por momento de la apuesta")
    print("9. Volver")

    opcion_busqueda = input("Elige una opción: ").strip()

    if opcion_busqueda == "9":
        return

    opciones_validas = set(CAMPOS_BUSQUEDA.keys()) | {"6", "7"}

    if opcion_busqueda not in opciones_validas:
        print("Opción no válida.")
        return

    valor_buscado = pedir_valor_busqueda(opcion_busqueda)

    resultados = filtrar_apuestas_desde_servicio(
        opcion_busqueda,
        valor_buscado,
    )

    if not resultados:
        print("\nNo se encontraron apuestas con ese criterio.")
        return

    print(f"\n===== RESULTADOS ENCONTRADOS: " f"{len(resultados)} =====")

    for apuesta in resultados:
        mostrar_detalle_apuesta(apuesta)
