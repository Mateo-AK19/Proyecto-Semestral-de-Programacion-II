"""
Proyecto semestral de programacion II
Integrantes: Mateo Lopez y Emmanuel Espinoza
"""

import os
import logging
from datetime import datetime

from utilidades import validar_monto, OperacionInvalidaError, DatosVaciosError

logger = logging.getLogger("apuestas_mundial")

RUTA_GANADORES = os.path.join("datos", "ganadores.txt")


class Apuesta:
    def __init__(self, correo, partido, equipo_apostado, monto, cuota):
        self.correo = correo
        self.partido = partido
        self.equipo_apostado = equipo_apostado
        self.monto = monto
        self.cuota = cuota
        self.estado = "Pendiente"   # Pendiente | Ganada | Perdida
        self.ganancia = 0.0
        self.fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def __str__(self):
        return (f"[{self.fecha}] {self.correo} apostó ${self.monto:.2f} a {self.equipo_apostado} "
                f"({self.partido}) - Estado: {self.estado}")


class GestorApuestas:
    def __init__(self):
        self.historial_apuestas = []      # lista de objetos Apuesta
        self.equipos_registrados = set()  # conjunto de equipos únicos

    def realizar_apuesta(self, usuario, partido, equipo_apostado, monto, cuota):
        monto = validar_monto(monto)
        try:
            cuota = float(cuota)
            if cuota <= 1:
                raise ValueError
        except ValueError:
            raise OperacionInvalidaError("La cuota debe ser un número mayor a 1.0.")

        if monto > usuario.saldo:
            raise OperacionInvalidaError("Saldo insuficiente para realizar la apuesta.")

        usuario.saldo -= monto  # se reserva el monto apostado
        nueva_apuesta = Apuesta(usuario.correo, partido, equipo_apostado, monto, cuota)
        self.historial_apuestas.append(nueva_apuesta)
        self.equipos_registrados.add(equipo_apostado)

        logger.info(f"Apuesta registrada: {usuario.correo} -> {equipo_apostado} "
                    f"(${monto:.2f} @ {cuota}) en {partido}")
        return nueva_apuesta

    def validar_resultados(self, resultados_mundial, gestor_usuarios):
        """
        Compara cada apuesta pendiente contra resultados_mundial (dict de scraping.py)
        y actualiza estado/ganancia. Acredita saldo a los ganadores.
        """
        if not self.historial_apuestas:
            raise DatosVaciosError("No hay apuestas registradas para validar.")

        ganadores = []
        for apuesta in self.historial_apuestas:
            if apuesta.estado != "Pendiente":
                continue
            resultado = resultados_mundial.get(apuesta.partido)
            if resultado is None:
                continue  # aún no hay resultado disponible para ese partido

            if resultado["ganador"] == apuesta.equipo_apostado:
                apuesta.estado = "Ganada"
                apuesta.ganancia = round(apuesta.monto * apuesta.cuota, 2)
                try:
                    usuario = gestor_usuarios.obtener_usuario(apuesta.correo)
                    usuario.saldo += apuesta.ganancia
                except Exception as e:
                    logger.error(f"No se pudo acreditar ganancia a {apuesta.correo}: {e}")
                ganadores.append(apuesta)
                logger.info(f"Apuesta ganada: {apuesta.correo} gana ${apuesta.ganancia:.2f}")
            else:
                apuesta.estado = "Perdida"
                apuesta.ganancia = -apuesta.monto
                logger.info(f"Apuesta perdida: {apuesta.correo} pierde ${apuesta.monto:.2f}")

        if ganadores:
            gestor_usuarios.guardar_usuarios()
            self.guardar_ganadores(ganadores)
        return ganadores

    def guardar_ganadores(self, ganadores):
        os.makedirs("datos", exist_ok=True)
        with open(RUTA_GANADORES, "a", encoding="utf-8") as f:
            for apuesta in ganadores:
                f.write(f"{apuesta.fecha} | {apuesta.correo} | {apuesta.equipo_apostado} | "
                        f"Ganancia: ${apuesta.ganancia:.2f}\n")
        logger.info(f"{len(ganadores)} ganador(es) guardados en {RUTA_GANADORES}")

    def historial_por_usuario(self, correo):
        return [a for a in self.historial_apuestas if a.correo == correo]

    def calcular_balance_general(self):
        """Retorna (total_apostado, total_ganado, total_perdido)."""
        total_apostado = sum(a.monto for a in self.historial_apuestas)
        total_ganado = sum(a.ganancia for a in self.historial_apuestas if a.estado == "Ganada")
        total_perdido = sum(a.monto for a in self.historial_apuestas if a.estado == "Perdida")
        return total_apostado, total_ganado, total_perdido
