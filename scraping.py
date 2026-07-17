
import logging
import requests
from bs4 import BeautifulSoup

from utilidades import ErrorScrapingError

logger = logging.getLogger("apuestas_mundial")

URL_RESULTADOS = "https://en.wikipedia.org/wiki/2026_FIFA_World_Cup"


def _descargar_html():
    """Descarga el HTML crudo de la página de resultados. Lanza excepción si falla."""
    headers = {
        "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"),
        "Accept-Language": "es-ES,es;q=0.9",
    }
    respuesta = requests.get(URL_RESULTADOS, headers=headers, timeout=15)
    respuesta.raise_for_status()
    return respuesta.text


def _parsear_marcador(texto):
    texto = texto.split("(")[0].strip()
    separador = "–" if "–" in texto else "-" if "-" in texto else None
    if separador is None:
        return None
    partes = texto.split(separador)
    try:
        return int(partes[0]), int(partes[1])
    except (ValueError, IndexError):
        return None


def _extraer_partidos(html):
    soup = BeautifulSoup(html, "html.parser")
    finalizados, pendientes = {}, {}

    cajas = soup.find_all("div", class_="footballbox")
    for caja in cajas:
        local_tag = caja.find("th", class_="fhome")
        visitante_tag = caja.find("th", class_="faway")
        marcador_tag = caja.find("th", class_="fscore")

        if not (local_tag and visitante_tag and marcador_tag):
            continue

        local = local_tag.get_text(strip=True)
        visitante = visitante_tag.get_text(strip=True)
        texto_marcador = marcador_tag.get_text(strip=True)
        clave = f"{local} vs {visitante}"

        marcador = _parsear_marcador(texto_marcador)

        if marcador is not None:
            marcador_local, marcador_visitante = marcador
            ganador = local if marcador_local > marcador_visitante else (
                visitante if marcador_visitante > marcador_local else "Empate")
            finalizados[clave] = {
                "local": local, "marcador_local": marcador_local,
                "visitante": visitante, "marcador_visitante": marcador_visitante,
                "ganador": ganador,
            }
        else:
            # No se pudo leer un marcador numérico -> partido aún no jugado.
            # El texto (ej. "19 July") se guarda como referencia de fecha.
            pendientes[clave] = {
                "local": local, "visitante": visitante, "fecha": texto_marcador,
            }

    return finalizados, pendientes


def _obtener_partidos():
    try:
        html = _descargar_html()
    except requests.exceptions.RequestException as e:
        logger.error(f"Web Scraping falló al conectar: {e}")
        raise ErrorScrapingError(
            "No se pudo conectar con la fuente de resultados (revisa tu conexión "
            f"a internet). Detalle técnico: {e}"
        )

    try:
        finalizados, pendientes = _extraer_partidos(html)
    except Exception as e:
        logger.error(f"Error al procesar el HTML de resultados: {e}")
        raise ErrorScrapingError(f"Error al interpretar la página de resultados: {e}")

    if not finalizados and not pendientes:
        logger.warning("El scraping no encontró partidos (posible cambio de "
                        "estructura en la página fuente).")
        raise ErrorScrapingError(
            "No se encontraron partidos en la página fuente. Es posible que "
            "la estructura de la página haya cambiado."
        )

    return finalizados, pendientes


def obtener_partidos_pendientes():
    _, pendientes = _obtener_partidos()
    if not pendientes:
        raise ErrorScrapingError(
            "No hay partidos pendientes por jugar en este momento — "
            "el torneo ya terminó o todos los partidos ya tienen resultado."
        )
    logger.info(f"{len(pendientes)} partido(s) pendiente(s) obtenidos para apostar.")
    return pendientes


def obtener_resultados_finalizados():
    finalizados, _ = _obtener_partidos()
    if not finalizados:
        raise ErrorScrapingError("No hay resultados finalizados disponibles todavía.")
    logger.info(f"{len(finalizados)} resultado(s) finalizado(s) obtenidos para validar apuestas.")
    return finalizados
