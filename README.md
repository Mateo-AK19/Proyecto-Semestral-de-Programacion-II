# Sistema de Apuestas Deportivas del Mundial de Fútbol

Proyecto Final — Programación II — UTP — Grupo 1S3221
Profesor: Jorge Cisneros

## Descripción

Aplicación de consola en Python que permite registrar usuarios, gestionar
depósitos/retiros, consultar resultados de fútbol mediante **Web Scraping**,
realizar apuestas y generar reportes en **Excel** (Pandas/OpenPyXL).

## Instalación

```bash
pip install -r requirements.txt
```

## Ejecución

```bash
python main.py
```

## Estructura del proyecto

| Archivo         | Responsabilidad                                                   |
|-----------------|---------------------------------------------------------------------|
| `main.py`       | Menú interactivo, integra todos los módulos                       |
| `usuarios.py`   | Registro/login (diccionario `correo -> Usuario`), hash de contraseñas |
| `pagos.py`      | Depósitos, retiros y métodos de pago (lista de transacciones)     |
| `apuestas.py`   | Registro y validación de apuestas, cálculo de ganancias, ganadores |
| `scraping.py`   | Obtención de resultados vía Requests + BeautifulSoup (con respaldo simulado si falla la conexión) |
| `reportes.py`   | Exportación a Excel (`usuarios.xlsx`, `apuestas.xlsx`, `pagos.xlsx`, `ganancias.xlsx`) |
| `utilidades.py` | Logging (`logs/app.log`) y excepciones personalizadas             |

Al ejecutarse, el sistema crea automáticamente las carpetas:
- `datos/` → usuarios.json, ganadores.txt, reportes .xlsx
- `logs/`  → app.log (auditoría: logins, apuestas, depósitos, retiros, errores)

## Flujo recomendado de uso

1. Registrar Usuario
2. Iniciar Sesión
3. Consultar Resultados (carga los partidos disponibles para apostar)
4. Realizar Apuesta
5. Métodos de Pago → Depositar saldo antes de apostar
6. Reportes → genera los archivos Excel

## Notas sobre el Web Scraping

El módulo `scraping.py` intenta extraer resultados reales desde Wikipedia
esultados del Mundial 2026 como referencia.

## Estructuras de datos utilizadas

- **Diccionarios**: usuarios registrados (`correo -> Usuario`), resultados de partidos
- **Listas**: historial de apuestas, historial de pagos
- **Conjuntos**: equipos únicos apostados (`equipos_registrados`)

## Próximos pasos sugeridos (no incluidos en esta entrega)

- Subir el repositorio a GitHub como "Proyecto Final Python"
- Preparar la presentación y documentación técnica/manual de usuario
- Opcional: reemplazar el menú de consola por `console-menu`, `textual` o Django
