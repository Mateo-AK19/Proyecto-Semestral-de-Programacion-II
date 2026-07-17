"""
main.py
Sistema de Apuestas Deportivas del Mundial de Fútbol
Proyecto Final - Programación II - UTP - Grupo 1S3221

Punto de entrada: menú interactivo por consola que integra todos los módulos.
"""

import logging

from utilidades import (
    configurar_logging,
    UsuarioNoRegistradoError,
    CredencialesInvalidasError,
    MontoInvalidoError,
    OperacionInvalidaError,
    DatosVaciosError,
    ErrorScrapingError,
)
from usuarios import GestorUsuarios
from pagos import GestorPagos, METODOS_PAGO
from apuestas import GestorApuestas
from scraping import obtener_partidos_pendientes, obtener_resultados_finalizados
from reportes import generar_todos_los_reportes

logger = configurar_logging()

gestor_usuarios = GestorUsuarios()
gestor_pagos = GestorPagos()
gestor_apuestas = GestorApuestas()
usuario_actual = None          # sesión activa
partidos_pendientes_cache = {}  # partidos SIN resultado, para apostar (sin spoilers)
resultados_finalizados_cache = {}  # partidos CON resultado, solo para validar apuestas


def mostrar_menu():
    print("\n" + "=" * 45)
    print(" SISTEMA DE APUESTAS MUNDIAL FIFA")
    print("=" * 45)
    if usuario_actual:
        print(f" Sesión: {usuario_actual.correo}  |  Saldo: ${usuario_actual.saldo:.2f}")
    print("1. Registrar Usuario")
    print("2. Iniciar Sesión")
    print("3. Ver Partidos Disponibles para Apostar")
    print("4. Realizar Apuesta")
    print("5. Métodos de Pago (Depósito/Retiro)")
    print("6. Consultar Resultados Finalizados y Validar Apuestas")
    print("7. Reportes")
    print("8. Cerrar Sesión")
    print("9. Salir")


def opcion_registrar():
    print("\n--- Registro de Usuario ---")
    try:
        nombre = input("Nombre: ").strip()
        apellido = input("Apellido: ").strip()
        correo = input("Correo electrónico: ").strip()
        edad = input("Edad: ").strip()
        password = input("Contraseña: ").strip()
        gestor_usuarios.registrar_usuario(nombre, apellido, correo, edad, password)
        print("✔ Usuario registrado exitosamente.")
    except OperacionInvalidaError as e:
        print(f"✘ Error: {e}")


def opcion_login():
    global usuario_actual
    print("\n--- Iniciar Sesión ---")
    correo = input("Correo electrónico: ").strip()
    password = input("Contraseña: ").strip()
    try:
        usuario_actual = gestor_usuarios.iniciar_sesion(correo, password)
        print(f"✔ Bienvenido, {usuario_actual.nombre}.")
    except (UsuarioNoRegistradoError, CredencialesInvalidasError) as e:
        print(f"✘ Error: {e}")


def opcion_partidos_pendientes():
    """Muestra SOLO partidos sin resultado todavía — la única fuente válida para apostar."""
    global partidos_pendientes_cache
    print("\n--- Partidos disponibles para apostar (sin resultado aún) ---")
    try:
        partidos_pendientes_cache = obtener_partidos_pendientes()
    except ErrorScrapingError as e:
        print(f"✘ No se pudieron obtener partidos: {e}")
        return
    for partido, datos in partidos_pendientes_cache.items():
        print(f"  {partido}  —  {datos['ronda']}  ({datos['fecha']})")


def opcion_apostar():
    global partidos_pendientes_cache
    if usuario_actual is None:
        print("✘ Debes iniciar sesión primero.")
        return
    if not partidos_pendientes_cache:
        print("Primero consulta los partidos disponibles para apostar (opción 3).")
        return

    print("\n--- Realizar Apuesta ---")
    print("Partidos disponibles (sin resultado conocido):")
    partidos = list(partidos_pendientes_cache.keys())
    for i, p in enumerate(partidos, 1):
        print(f"  {i}. {p}")
    try:
        idx = int(input("Selecciona el número de partido: ")) - 1
        partido = partidos[idx]
        datos = partidos_pendientes_cache[partido]
        equipo = input(f"¿A qué equipo apuestas ({datos['local']} / "
                        f"{datos['visitante']})?: ").strip()
        monto = input("Monto a apostar: $").strip()
        cuota = input("Cuota (ej. 2.5): ").strip()
        apuesta = gestor_apuestas.realizar_apuesta(usuario_actual, partido, equipo, monto, cuota)
        print(f"✔ Apuesta registrada: {apuesta}")
        print("  (Se validará más adelante, cuando el partido tenga resultado — opción 6)")
    except (MontoInvalidoError, OperacionInvalidaError) as e:
        print(f"✘ Error: {e}")
    except (ValueError, IndexError):
        print("✘ Selección de partido inválida.")


def opcion_validar_resultados():
    """Consulta partidos YA finalizados y valida cualquier apuesta pendiente contra ellos."""
    global resultados_finalizados_cache
    print("\n--- Consultando resultados finalizados (Web Scraping) ---")
    try:
        resultados_finalizados_cache = obtener_resultados_finalizados()
    except ErrorScrapingError as e:
        print(f"✘ No se pudieron obtener resultados: {e}")
        return

    for partido, datos in resultados_finalizados_cache.items():
        print(f"  {partido}: {datos['marcador_local']} - {datos['marcador_visitante']}"
              f"  (Ganador: {datos['ganador']})")

    try:
        ganadores = gestor_apuestas.validar_resultados(resultados_finalizados_cache, gestor_usuarios)
        if ganadores:
            print(f"\n✔ {len(ganadores)} apuesta(s) ganadora(s) validada(s) y acreditada(s):")
            for g in ganadores:
                print(f"   {g}")
        else:
            print("\nNo hay apuestas ganadoras nuevas para validar en este momento.")
    except DatosVaciosError:
        print("\n(No tienes apuestas registradas todavía.)")


def opcion_pagos():
    if usuario_actual is None:
        print("✘ Debes iniciar sesión primero.")
        return

    print("\n--- Métodos de Pago ---")
    print("1. Depositar")
    print("2. Retirar")
    for i, m in enumerate(METODOS_PAGO, 1):
        print(f"   {i}. {m}")
    try:
        tipo = input("Selecciona operación (1=Depositar, 2=Retirar): ").strip()
        monto = input("Monto: $").strip()
        idx_metodo = int(input("Selecciona método de pago (número): ")) - 1
        metodo = METODOS_PAGO[idx_metodo]

        if tipo == "1":
            nuevo_saldo = gestor_pagos.depositar(usuario_actual, monto, metodo)
            print(f"✔ Depósito exitoso. Nuevo saldo: ${nuevo_saldo:.2f}")
        elif tipo == "2":
            nuevo_saldo = gestor_pagos.retirar(usuario_actual, monto, metodo)
            print(f"✔ Retiro exitoso. Nuevo saldo: ${nuevo_saldo:.2f}")
        else:
            print("✘ Opción inválida.")
        gestor_usuarios.guardar_usuarios()
    except (MontoInvalidoError, OperacionInvalidaError) as e:
        print(f"✘ Error: {e}")
    except (ValueError, IndexError):
        print("✘ Selección de método inválida.")


def opcion_reportes():
    print("\n--- Generación de Reportes Excel ---")
    try:
        rutas = generar_todos_los_reportes(gestor_usuarios, gestor_apuestas, gestor_pagos)
        if rutas:
            print("✔ Reportes generados:")
            for r in rutas:
                print(f"   - {r}")
        else:
            print("No hay datos suficientes para generar reportes todavía.")
    except DatosVaciosError as e:
        print(f"✘ Error: {e}")


def opcion_cerrar_sesion():
    global usuario_actual
    if usuario_actual:
        logger.info(f"Cierre de sesión: {usuario_actual.correo}")
        print(f"Sesión de {usuario_actual.correo} cerrada.")
        usuario_actual = None
    else:
        print("No hay sesión activa.")


def main():
    logger.info("=== Inicio de la aplicación ===")
    while True:
        mostrar_menu()
        opcion = input("Selecciona una opción: ").strip()

        try:
            if opcion == "1":
                opcion_registrar()
            elif opcion == "2":
                opcion_login()
            elif opcion == "3":
                opcion_partidos_pendientes()
            elif opcion == "4":
                opcion_apostar()
            elif opcion == "5":
                opcion_pagos()
            elif opcion == "6":
                opcion_validar_resultados()
            elif opcion == "7":
                opcion_reportes()
            elif opcion == "8":
                opcion_cerrar_sesion()
            elif opcion == "9":
                print("Gracias por usar el sistema. ¡Hasta pronto!")
                logger.info("=== Fin de la aplicación ===")
                break
            else:
                print("✘ Opción no válida. Intenta de nuevo.")
        except Exception as e:
            # Red de seguridad: ningún error inesperado debe cerrar el programa
            logger.error(f"Error inesperado: {e}")
            print(f"✘ Ocurrió un error inesperado: {e}")


if __name__ == "__main__":
    main()
