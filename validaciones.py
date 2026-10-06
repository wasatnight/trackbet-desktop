import unicodedata


def pedir_numero(mensaje):
    """Solicita un número válido al usuario."""

    while True:
        valor = input(mensaje).strip().replace(",", ".")

        try:
            return float(valor)
        except ValueError:
            print("Error: ingresa un número válido.")


def pedir_cuota(tipo_cuota):
    """Solicita y valida una cuota decimal o americana."""

    while True:
        cuota_texto = input("Cuota: ").strip().replace(" ", "")
        cuota_limpia = cuota_texto.replace("+", "").replace(",", ".")

        try:
            cuota = float(cuota_limpia)
        except ValueError:
            print("Error: ingresa una cuota válida. Ejemplo: 1.90, -110 o +120.")
            continue

        if tipo_cuota == "decimal" and cuota <= 1:
            print("Error: una cuota decimal debe ser mayor a 1.00.")
            continue

        if tipo_cuota == "americana" and cuota == 0:
            print("Error: una cuota americana no puede ser 0.")
            continue

        if tipo_cuota == "americana" and cuota > 0 and not cuota_texto.startswith("+"):
            cuota_texto = "+" + cuota_texto

        return cuota_texto, cuota


def normalizar_texto(texto):
    """Normaliza mayúsculas, acentos, guiones bajos y espacios."""

    texto = str(texto).strip().casefold().replace("_", " ")

    texto = unicodedata.normalize(
        "NFD",
        texto,
    )

    texto = "".join(
        caracter for caracter in texto if unicodedata.category(caracter) != "Mn"
    )

    texto = " ".join(texto.split())

    equivalencias = {
        "soccer": "futbol",
    }

    return equivalencias.get(
        texto,
        texto,
    )
