"""
utilidades.py
Configuración de logging y excepciones personalizadas del sistema.
"""

import logging
import os
import re

# ---------- Excepciones personalizadas ----------

class MontoInvalidoError(Exception):
    """Se lanza cuando un monto es negativo, cero o no numérico."""
    pass


class UsuarioNoRegistradoError(Exception):
    """Se lanza cuando se busca un usuario que no existe."""
    pass


class CredencialesInvalidasError(Exception):
    """Se lanza cuando el correo o la contraseña no coinciden."""
    pass


class ArchivoNoEncontradoError(Exception):
    """Se lanza cuando un archivo de datos esperado no existe."""
    pass


class DatosVaciosError(Exception):
    """Se lanza cuando se intenta operar sobre una estructura vacía."""
    pass


class OperacionInvalidaError(Exception):
    """Se lanza cuando se solicita una operación no permitida en el contexto actual."""
    pass


class ErrorScrapingError(Exception):

    pass


# ---------- Logging ----------

def configurar_logging():
    os.makedirs("logs", exist_ok=True)
    logging.basicConfig(
        filename=os.path.join("logs", "app.log"),
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    return logging.getLogger("apuestas_mundial")


# ---------- Validaciones ----------

def validar_monto(monto):
    try:
        monto = float(monto)
    except (TypeError, ValueError):
        raise MontoInvalidoError("El monto debe ser un número.")
    if monto <= 0:
        raise MontoInvalidoError("El monto debe ser mayor a cero.")
    return monto


def validar_correo(correo):
    patron = r"^[\w\.\-]+@[\w\-]+\.[a-zA-Z]{2,}$" #Estos son algunos de los caracteres al validar
    if not correo or not re.match(patron, correo):
        raise OperacionInvalidaError("Correo electrónico inválido.")
    return correo


def validar_edad(edad):
    try:
        edad = int(edad)
    except (TypeError, ValueError):
        raise OperacionInvalidaError("La edad debe ser un número entero.")
    if edad < 18 or edad > 99:
        raise OperacionInvalidaError("Debe ser mayor de edad para registrarse.")
    return edad
