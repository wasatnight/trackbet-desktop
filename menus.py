from configuracion_app import NOMBRE_APP
from almacenamiento import obtener_modo_almacenamiento


def mostrar_menu():
    print(f"\n===== {NOMBRE_APP.upper()} =====")
    print("Almacenamiento:", obtener_modo_almacenamiento())

    print("\n------------------------")
    print("1.  Registrar apuesta")
    print("2.  Ver historial")
    print("3.  Ver estadísticas")
    print("4.  Configurar bankroll")
    print("5.  Exportar apuestas a CSV")
    print("6.  Buscar apuestas")
    print("7.  Editar apuesta")
    print("8.  Eliminar apuesta")
    print("9.  Analíticas avanzadas")
    print("10. Respaldar SQLite a JSON")
    print("11. Cerrar apuesta pendiente")
    print("12. Reportes rápidos")
    print("13. Salir")


def seleccionar_casa():
    print("\nCasas de apuestas:")
    print("1. Caliente")
    print("2. Playdoit")
    print("3. Stake mx")
    print("4. Novibet")
    print("5. Codere")
    print("6. Draftea")
    print("7. Betvip")
    print("8. Otro")

    opcion = input("Elige tu casa de apuestas: ")
    if opcion == "1":
        return "Caliente"
    elif opcion == "2":
        return "playdoit"
    elif opcion == "3":
        return "Stake mx"
    elif opcion == "4":
        return "Novibet"

    elif opcion == "5":
        return "Codere"
    elif opcion == "6":
        return "Draftea"
    elif opcion == "7":
        return "Betvip"
    elif opcion == "8":
        return input("Escribe el nombre de tu casa de apuestas: ")
    else:
        return "Otro"


def seleccionar_deporte():
    print("\nDeportes:")
    print("1. Fútbol")
    print("2. Basquetbol")
    print("3. Béisbol")
    print("4. Hockey")
    print("5. Fútbol Americano")
    print("6. Tenis")
    print("7. Box")
    print("8. Otro")

    opcion = input("Elige un deporte:")

    if opcion == "1":
        return "Fútbol"
    elif opcion == "2":
        return "Basquetbol"
    elif opcion == "3":
        return "Béisbol"
    elif opcion == "4":
        return "Hockey"
    elif opcion == "5":
        return "Fútbol Americano"
    elif opcion == "6":
        return "Tenis"
    elif opcion == "7":
        return "Box"
    elif opcion == "8":
        return input("Escribe el deporte")
    else:
        return "Otro"


def seleccionar_mercado():
    """Selecciona el mercado y, cuando aplica, su selección automática."""

    while True:
        print("\nMercados de apuesta:")
        print("1. Moneyline")
        print("2. Over/Under")
        print("3. Handicap / Spread")
        print("4. Props")
        print("5. Ambos anotan")
        print("6. Doble oportunidad")
        print("7. Resultado exacto")
        print("8. Otro")

        opcion = input("Elige el mercado: ").strip()

        if opcion == "1":
            return "Moneyline", None

        elif opcion == "2":
            return "Over/Under", None

        elif opcion == "3":
            return "Handicap / Spread", None

        elif opcion == "4":
            return "Props", None

        elif opcion == "5":
            while True:
                print("\n===== AMBOS ANOTAN =====")
                print("1. Ambos anotan — Sí")
                print("2. Ambos anotan — No")
                print("3. Volver")

                opcion_ambos = input("Elige una opción: ").strip()

                if opcion_ambos == "1":
                    return "Ambos anotan", "Sí"

                elif opcion_ambos == "2":
                    return "Ambos anotan", "No"

                elif opcion_ambos == "3":
                    break

                else:
                    print("Opción no válida.")

        elif opcion == "6":
            return "Doble oportunidad", None

        elif opcion == "7":
            return "Resultado exacto", None

        elif opcion == "8":
            otro_mercado = input("Escribe el mercado: ").strip()

            if otro_mercado:
                return otro_mercado, None

            print("Debes escribir un mercado.")

        else:
            print("Opción no válida.")


def seleccionar_tipo_cuota():
    print("\nTipo de cuota")
    print("1. Decimal")
    print("2. Americana")

    opcion = input("Elige el tipo de cuota: ")

    if opcion == "1":
        return "decimal"
    elif opcion == "2":
        return "americana"
    else:
        return "decimal"


def seleccionar_resultado():
    """Permite seleccionar el estado o resultado de la apuesta."""

    while True:
        print("\n===== RESULTADO DE LA APUESTA =====")
        print("1. Pendiente")
        print("2. Ganada")
        print("3. Perdida")
        print("4. Push")

        opcion = input("Selecciona una opción: ").strip()

        if opcion == "1":
            return "pendiente"

        elif opcion == "2":
            return "ganada"

        elif opcion == "3":
            return "perdida"

        elif opcion == "4":
            return "push"

        else:
            print("Opción no válida. Intenta nuevamente.")


def seleccionar_modalidad():
    print("\nModalidad de apuesta:")
    print("1. Straight bet")
    print("2. Parlay")

    opcion = input("Elige la modalidad: ")

    if opcion == "1":
        return "straight"
    elif opcion == "2":
        return "parlay"
    else:
        return "straight"


def seleccionar_momento_apuesta():
    """Permite elegir si la apuesta es prepartido o en vivo."""

    while True:
        print("\n===== MOMENTO DE LA APUESTA =====")
        print("1. Prepartido")
        print("2. En vivo")

        opcion = input("Selecciona una opción: ").strip()

        if opcion == "1":
            return "prepartido"

        elif opcion == "2":
            return "en_vivo"

        else:
            print("Opción no válida. Intenta nuevamente.")


def seleccionar_resultado_seleccion():
    """Selecciona el resultado individual de una pierna del parlay."""

    while True:
        print("\nResultado de esta selección del parlay:")
        print("1. Pendiente")
        print("2. Ganada")
        print("3. Perdida")
        print("4. Push")

        opcion = input("Elige el resultado: ").strip()

        if opcion == "1":
            return "pendiente"

        elif opcion == "2":
            return "ganada"

        elif opcion == "3":
            return "perdida"

        elif opcion == "4":
            return "push"

        else:
            print("Opción no válida.")
