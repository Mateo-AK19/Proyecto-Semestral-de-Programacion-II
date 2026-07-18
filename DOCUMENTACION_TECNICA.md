# Documentación Técnica

## Sistema de Apuestas Deportivas del Mundial de Fútbol 2026

Universidad Tecnológica de Panamá — Facultad de Ingeniería de Sistemas Computacionales
Licenciatura en Ciberseguridad — Programación II — Grupo 1S3221
Profesor: Jorge Cisneros

---

## 1. Resumen

Sistema de consola desarrollado en Python 3.12+ que gestiona usuarios, saldos, apuestas deportivas y reportes, integrando **datos reales del Mundial 2026 mediante Web Scraping** (Requests + BeautifulSoup) en lugar de datos simulados o estáticos.

## 2. Arquitectura

### 2.1 Estructura de archivos

```
proyecto_apuestas/
├── main.py          # Punto de entrada: menú interactivo, orquesta los demás módulos
├── usuarios.py       # Registro, login, persistencia de usuarios (JSON)
├── pagos.py          # Depósitos y retiros de saldo
├── apuestas.py        # Registro y validación de apuestas, ganadores
├── scraping.py         # Obtención de datos reales vía Web Scraping
├── reportes.py         # Exportación a Excel (Pandas/OpenPyXL)
├── utilidades.py        # Logging y excepciones personalizadas
├── requirements.txt      # Dependencias
├── datos/              # (se genera en tiempo de ejecución) JSON, .xlsx, ganadores.txt
└── logs/                # (se genera en tiempo de ejecución) app.log
```

### 2.2 Diagrama de dependencias

```
                    ┌─────────────┐
                    │ utilidades  │  (excepciones + logging)
                    └──────┬──────┘
                           │
        ┌──────────┬───────┼───────┬──────────┐
        │          │       │       │          │
  ┌─────▼────┐ ┌───▼───┐ ┌─▼─────┐ │    ┌─────▼─────┐
  │ usuarios │ │ pagos │ │apuestas│ │    │ scraping  │
  └─────┬────┘ └───┬───┘ └─┬─────┘ │    └─────┬─────┘
        │          │       │       │          │
        └──────────┴───────┴───┬───┴──────────┘
                                │
                          ┌─────▼─────┐
                          │  main.py  │  (orquestador)
                          └─────┬─────┘
                                │
                          ┌─────▼─────┐
                          │ reportes  │
                          └───────────┘
```

`reportes.py` no depende directamente de los otros módulos de negocio — recibe los "gestores" (`GestorUsuarios`, `GestorApuestas`, `GestorPagos`) como parámetros desde `main.py`.

## 3. Módulos

### 3.1 `utilidades.py`
Base del sistema. Define:
- **Excepciones personalizadas**: `MontoInvalidoError`, `UsuarioNoRegistradoError`, `CredencialesInvalidasError`, `ArchivoNoEncontradoError`, `DatosVaciosError`, `OperacionInvalidaError`, `ErrorScrapingError`.
- **`configurar_logging()`**: configura `logging` para escribir en `logs/app.log` con formato `fecha | nivel | mensaje`.
- **Validaciones reutilizables**: `validar_monto()`, `validar_correo()`, `validar_edad()`.

### 3.2 `usuarios.py`
- Clase `Usuario` (POO): nombre, apellido, correo, edad, `password_hash` (SHA-256, nunca texto plano), saldo.
- Clase `GestorUsuarios`: administra un **diccionario** `{correo: Usuario}` para búsqueda O(1).
  - Persistencia en `datos/usuarios.json` (serialización manual vía `to_dict()`/`from_dict()`).
  - `registrar_usuario()`, `iniciar_sesion()`.

### 3.3 `pagos.py`
- `METODOS_PAGO`: lista de métodos válidos (Tarjeta de Crédito, Débito, PayPal, Yappy, Transferencia Bancaria).
- Clase `GestorPagos`: administra una **lista** (`historial_pagos`) de transacciones (diccionarios con correo, tipo, monto, método, fecha).
  - `depositar()` / `retirar()`, con validación de saldo suficiente para retiros.

### 3.4 `apuestas.py`
- Clase `Apuesta` (POO): correo, partido, equipo apostado, monto, cuota, estado (`Pendiente`/`Ganada`/`Perdida`), ganancia, fecha.
- Clase `GestorApuestas`: administra una **lista** (`historial_apuestas`) y un **conjunto** (`equipos_registrados`, sin duplicados).
  - `realizar_apuesta()`: reserva el monto del saldo del usuario inmediatamente.
  - `validar_resultados()`: compara apuestas pendientes contra resultados reales, acredita ganancias (`monto * cuota`), marca perdidas.
  - `guardar_ganadores()`: escribe en `datos/ganadores.txt` (modo *append*, nunca sobrescribe el historial).

### 3.5 `scraping.py` — Módulo central del proyecto

**Fuente de datos**: `https://en.wikipedia.org/wiki/2026_FIFA_World_Cup` (Wikipedia, página principal del torneo).

**Técnica**: cada partido está envuelto en un `<div class="footballbox">`, con el nombre de cada equipo en `<th class="fhome">` / `<th class="faway">`, y el marcador (o la fecha, si el partido no se ha jugado) en `<th class="fscore">`.

**Diseño clave — separación pendientes/finalizados:**

El sistema descarga la página **una sola vez** y clasifica cada partido según si su campo de marcador se puede interpretar como dos números (`X-Y`):

| Función pública | Contenido | Uso permitido |
|---|---|---|
| `obtener_partidos_pendientes()` | Partidos sin marcador numérico (el campo trae una fecha) | Única fuente válida para ofrecer partidos sobre los que apostar |
| `obtener_resultados_finalizados()` | Partidos con marcador numérico | Únicamente para validar apuestas ya realizadas |

Esta separación es una decisión de diseño deliberada: evita que el usuario pueda apostar sobre un partido cuyo resultado el sistema ya conoce, lo cual invalidaría el propósito de "apostar".

**Manejo de excepciones (sin datos simulados):**
```
_descargar_html()
  └─ requests.exceptions.RequestException  →  ErrorScrapingError (fallo de conexión)

_extraer_partidos()
  └─ Exception genérica                     →  ErrorScrapingError (fallo al interpretar HTML)

Si no se encuentra ningún partido                → ErrorScrapingError (estructura cambió / sin datos)
```
El sistema **nunca** sustituye un fallo de scraping con datos inventados; propaga un error explicativo hasta `main.py`, que lo captura y muestra al usuario sin cerrar el programa. Esto satisface el requerimiento de manejo de excepciones de conexión de forma honesta.

### 3.6 `reportes.py`
Convierte los datos en memoria a archivos `.xlsx` con **Pandas** (`pd.DataFrame`) y **OpenPyXL** como motor de escritura:
- `usuarios.xlsx`, `apuestas.xlsx`, `pagos.xlsx`, `ganancias.xlsx`.
- `generar_todos_los_reportes()` omite (sin fallar) los reportes cuyos datos aún estén vacíos, registrando una advertencia en el log.

### 3.7 `main.py`
Orquestador: bucle de menú (`while True`), delega cada opción a la función correspondiente de cada módulo. Contiene un `try/except Exception` general como última red de seguridad — ningún error no capturado específicamente cierra el programa.

## 4. Estructuras de datos utilizadas

| Estructura | Dónde | Propósito |
|---|---|---|
| Diccionario | `GestorUsuarios.usuarios` | Búsqueda de usuario por correo en O(1) |
| Diccionario | Resultados de `scraping.py` | Mapeo partido → datos del partido |
| Lista | `GestorApuestas.historial_apuestas` | Registro cronológico de apuestas |
| Lista | `GestorPagos.historial_pagos` | Registro cronológico de transacciones |
| Conjunto | `GestorApuestas.equipos_registrados` | Equipos únicos apostados, sin duplicados |

## 5. Seguridad

- Las contraseñas se almacenan como hash **SHA-256** (`hashlib`), nunca en texto plano.
- Las validaciones de entrada (monto, correo, edad) se centralizan en `utilidades.py` para evitar lógica duplicada e inconsistente.

## 6. Logging y auditoría

Todo evento relevante (registro, login, depósito, retiro, apuesta, resultado de scraping, errores) se registra en `logs/app.log` con marca de tiempo, mediante el logger `"apuestas_mundial"`, compartido por todos los módulos vía `logging.getLogger("apuestas_mundial")`.

## 7. Limitaciones conocidas

- **Dependencia de la estructura HTML de Wikipedia**: si Wikipedia cambia el nombre de las clases `footballbox`/`fhome`/`faway`/`fscore`, el scraping deja de funcionar hasta actualizar `scraping.py`. Esto está mitigado (no evitado) por el manejo de excepciones, que informa el fallo en vez de fallar silenciosamente.
- **Disponibilidad de partidos pendientes**: dado que el Mundial 2026 está por finalizar, el número de partidos disponibles para apostar en cualquier momento dado puede ser muy bajo (incluso 0 tras la final).
- **Persistencia simple**: `usuarios.json` no es una base de datos transaccional; en un entorno multiusuario concurrente real, esto no sería suficiente.

## 8. Posibles mejoras futuras

- Historial de apuestas visible directamente desde el menú (actualmente solo vía reporte Excel).
- Migrar la persistencia de usuarios a una base de datos (SQLite) en vez de JSON plano.
- Cachear resultados de scraping con expiración, para reducir peticiones repetidas a Wikipedia.
- Interfaz de menú con `console-menu`, `textual`, o una versión web con Django (sugerido en el enunciado original).

## 9. Requerimientos técnicos cubiertos

| Requerimiento del documento | Módulo(s) |
|---|---|
| Listas, diccionarios, conjuntos | `usuarios.py`, `apuestas.py`, `pagos.py`, `scraping.py` |
| Manejo de excepciones | `utilidades.py` (definición) + todos los módulos (uso) |
| Logging | `utilidades.py`, usado en todos los módulos |
| Web Scraping (Requests + BeautifulSoup) | `scraping.py` |
| Pandas + OpenPyXL | `reportes.py` |
| Programación orientada a objetos | Clases `Usuario`, `Apuesta`, `GestorUsuarios`, `GestorPagos`, `GestorApuestas` |
| Interfaz por menú | `main.py` |
