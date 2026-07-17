"""
pagos.py
Gestión de depósitos, retiros y métodos de pago disponibles.
Estructura de datos principal: lista de transacciones (historial_pagos)
"""

import logging
from datetime import datetime

from utilidades import validar_monto, OperacionInvalidaError

logger = logging.getLogger("apuestas_mundial")

METODOS_PAGO = ["Tarjeta de Crédito", "Tarjeta de Débito", "PayPal", "Yappy", "Transferencia Bancaria"]


class GestorPagos:
    def __init__(self):
        self.historial_pagos = []  # lista de dicts: {correo, tipo, monto, metodo, fecha}

    def _registrar_transaccion(self, correo, tipo, monto, metodo):
        transaccion = {
            "correo": correo,
            "tipo": tipo,
            "monto": monto,
            "metodo": metodo,
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        self.historial_pagos.append(transaccion)
        return transaccion

    def depositar(self, usuario, monto, metodo):
        monto = validar_monto(monto)
        if metodo not in METODOS_PAGO:
            raise OperacionInvalidaError(f"Método de pago inválido. Opciones: {METODOS_PAGO}")

        usuario.saldo += monto
        self._registrar_transaccion(usuario.correo, "Depósito", monto, metodo)
        logger.info(f"Depósito de ${monto:.2f} ({metodo}) para {usuario.correo}. Nuevo saldo: ${usuario.saldo:.2f}")
        return usuario.saldo

    def retirar(self, usuario, monto, metodo):
        monto = validar_monto(monto)
        if metodo not in METODOS_PAGO:
            raise OperacionInvalidaError(f"Método de pago inválido. Opciones: {METODOS_PAGO}")
        if monto > usuario.saldo:
            raise OperacionInvalidaError("Saldo insuficiente para realizar el retiro.")

        usuario.saldo -= monto
        self._registrar_transaccion(usuario.correo, "Retiro", monto, metodo)
        logger.info(f"Retiro de ${monto:.2f} ({metodo}) para {usuario.correo}. Nuevo saldo: ${usuario.saldo:.2f}")
        return usuario.saldo

    def historial_por_usuario(self, correo):
        return [t for t in self.historial_pagos if t["correo"] == correo]
