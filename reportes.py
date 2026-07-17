"""
reportes.py
Exportación de datos del sistema a archivos Excel usando Pandas y OpenPyXL.
Genera: usuarios.xlsx, apuestas.xlsx, pagos.xlsx, ganancias.xlsx
"""

import os
import logging
import pandas as pd

from utilidades import DatosVaciosError

logger = logging.getLogger("apuestas_mundial")
CARPETA_DATOS = "datos"


def _asegurar_carpeta():
    os.makedirs(CARPETA_DATOS, exist_ok=True)


def generar_reporte_usuarios(gestor_usuarios):
    _asegurar_carpeta()
    usuarios = gestor_usuarios.listar_usuarios()
    if not usuarios:
        raise DatosVaciosError("No hay usuarios registrados para exportar.")

    filas = [{"Nombre": u.nombre, "Apellido": u.apellido, "Correo": u.correo,
              "Edad": u.edad, "Saldo": u.saldo} for u in usuarios]
    ruta = os.path.join(CARPETA_DATOS, "usuarios.xlsx")
    pd.DataFrame(filas).to_excel(ruta, index=False, engine="openpyxl")
    logger.info(f"Reporte de usuarios generado: {ruta}")
    return ruta


def generar_reporte_apuestas(gestor_apuestas):
    _asegurar_carpeta()
    if not gestor_apuestas.historial_apuestas:
        raise DatosVaciosError("No hay apuestas registradas para exportar.")

    filas = [{"Fecha": a.fecha, "Correo": a.correo, "Partido": a.partido,
              "Equipo Apostado": a.equipo_apostado, "Monto": a.monto,
              "Cuota": a.cuota, "Estado": a.estado, "Ganancia": a.ganancia}
             for a in gestor_apuestas.historial_apuestas]
    ruta = os.path.join(CARPETA_DATOS, "apuestas.xlsx")
    pd.DataFrame(filas).to_excel(ruta, index=False, engine="openpyxl")
    logger.info(f"Reporte de apuestas generado: {ruta}")
    return ruta


def generar_reporte_pagos(gestor_pagos):
    _asegurar_carpeta()
    if not gestor_pagos.historial_pagos:
        raise DatosVaciosError("No hay pagos registrados para exportar.")

    ruta = os.path.join(CARPETA_DATOS, "pagos.xlsx")
    pd.DataFrame(gestor_pagos.historial_pagos).to_excel(ruta, index=False, engine="openpyxl")
    logger.info(f"Reporte de pagos generado: {ruta}")
    return ruta


def generar_reporte_ganancias(gestor_apuestas):
    _asegurar_carpeta()
    if not gestor_apuestas.historial_apuestas:
        raise DatosVaciosError("No hay apuestas registradas para calcular ganancias.")

    total_apostado, total_ganado, total_perdido = gestor_apuestas.calcular_balance_general()
    filas = [{
        "Total Apostado": total_apostado,
        "Total Ganado": total_ganado,
        "Total Perdido": total_perdido,
        "Balance Neto": total_ganado - total_perdido,
    }]
    ruta = os.path.join(CARPETA_DATOS, "ganancias.xlsx")
    pd.DataFrame(filas).to_excel(ruta, index=False, engine="openpyxl")
    logger.info(f"Reporte de ganancias generado: {ruta}")
    return ruta


def generar_todos_los_reportes(gestor_usuarios, gestor_apuestas, gestor_pagos):
    """Genera todos los reportes disponibles, omitiendo los que no tengan datos."""
    generados = []
    for nombre, funcion, args in [
        ("usuarios", generar_reporte_usuarios, (gestor_usuarios,)),
        ("apuestas", generar_reporte_apuestas, (gestor_apuestas,)),
        ("pagos", generar_reporte_pagos, (gestor_pagos,)),
        ("ganancias", generar_reporte_ganancias, (gestor_apuestas,)),
    ]:
        try:
            ruta = funcion(*args)
            generados.append(ruta)
        except DatosVaciosError as e:
            logger.warning(f"Reporte de {nombre} omitido: {e}")
    return generados
