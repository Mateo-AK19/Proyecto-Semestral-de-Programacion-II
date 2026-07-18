# Manual de Usuario

## Sistema de Apuestas Deportivas del Mundial de Fútbol 2026

Universidad Tecnológica de Panamá — Programación II — Grupo 1S3221

---

## 1. ¿Qué es este sistema?

Es una aplicación de consola que te permite registrarte, depositar saldo, apostar sobre partidos **reales** del Mundial 2026 (obtenidos en vivo desde Wikipedia mediante Web Scraping), y cobrar tus ganancias automáticamente cuando el partido real termine.

**Importante:** el sistema solo te deja apostar sobre partidos que **todavía no se han jugado** — nunca vas a ver el resultado antes de apostar.

---

## 2. Instalación

### 2.1 Requisitos previos
- Tener **Python 3.12 o superior** instalado. Verifica con:
  ```bash
  python --version
  ```

### 2.2 Instalar las dependencias
Desde la carpeta del proyecto, ejecuta:
```bash
pip install -r requirements.txt
```
Esto instala: `pandas`, `openpyxl`, `requests` y `beautifulsoup4`.

### 2.3 Ejecutar el sistema
```bash
python main.py
```

---

## 3. El menú principal

Al iniciar, verás:

```
=============================================
 SISTEMA DE APUESTAS MUNDIAL FIFA
=============================================
1. Registrar Usuario
2. Iniciar Sesión
3. Ver Partidos Disponibles para Apostar
4. Realizar Apuesta
5. Métodos de Pago (Depósito/Retiro)
6. Consultar Resultados Finalizados y Validar Apuestas
7. Reportes
8. Cerrar Sesión
9. Salir
Selecciona una opción:
```

Escribes el número de la opción que quieras y presionas Enter. El menú vuelve a aparecer automáticamente después de cada acción.

---

## 4. Guía paso a paso

### Paso 1 — Registrar Usuario (opción 1)
Te va a pedir:
- Nombre
- Apellido
- Correo electrónico (debe tener formato válido, ej. `correo@dominio.com`)
- Edad (debes ser mayor de 18 años)
- Contraseña (mínimo 4 caracteres)

Tu contraseña **nunca se guarda en texto plano** — el sistema la protege con un hash criptográfico (SHA-256).

### Paso 2 — Iniciar Sesión (opción 2)
Ingresa el correo y contraseña que registraste. Si es correcto, verás tu correo y saldo en la parte superior del menú.

### Paso 3 — Ver Partidos Disponibles para Apostar (opción 3)
El sistema se conecta a Wikipedia en tiempo real y te muestra **únicamente** los partidos del Mundial 2026 que aún no se han jugado, por ejemplo:

```
--- Partidos disponibles para apostar (sin resultado aún) ---
  France vs England  —  Match for third place  (19 July)
  Spain vs Argentina  —  Final  (19 July)
```

No vas a ver marcador ni ganador — todavía no existen.

### Paso 4 — Depositar saldo (opción 5)
Antes de apostar necesitas saldo. Elige "1" para depositar, ingresa el monto, y elige un método de pago:
1. Tarjeta de Crédito
2. Tarjeta de Débito
3. PayPal
4. Yappy
5. Transferencia Bancaria

### Paso 5 — Realizar Apuesta (opción 4)
1. Elige el número del partido (de la lista que obtuviste en el paso 3).
2. Escribe a qué equipo apuestas.
3. Ingresa el monto.
4. Ingresa la cuota (multiplicador de tu ganancia si aciertas, ej. `2.5`).

Tu saldo se descuenta de inmediato. La apuesta queda en estado **"Pendiente"** hasta que el partido real se juegue.

### Paso 6 — Consultar Resultados Finalizados y Validar Apuestas (opción 6)
Aquí el sistema busca partidos que **ya tienen marcador** y revisa automáticamente si alguna de tus apuestas pendientes ya se puede resolver. Si ganaste, tu saldo se acredita automáticamente y aparece en el archivo `datos/ganadores.txt`.

Puedes correr esta opción cuando quieras — por ejemplo, un día después de que se jugó el partido que apostaste.

### Paso 7 — Retirar saldo (opción 5, retiro)
Igual que el depósito, pero seleccionando "2" (Retirar). No puedes retirar más de lo que tienes disponible.

### Paso 8 — Reportes (opción 7)
Genera automáticamente 4 archivos Excel dentro de la carpeta `datos/`:
- `usuarios.xlsx` — lista de usuarios registrados y su saldo
- `apuestas.xlsx` — historial completo de apuestas
- `pagos.xlsx` — historial de depósitos y retiros
- `ganancias.xlsx` — resumen de totales apostados, ganados y perdidos

### Paso 9 — Cerrar Sesión / Salir (opciones 8 y 9)
Cierra tu sesión actual, o termina el programa.

---

## 5. Preguntas frecuentes

**¿Por qué solo veo 1 o 2 partidos disponibles para apostar?**
Porque el Mundial 2026 ya casi termina — el sistema solo muestra partidos reales que de verdad faltan por jugarse. Esto es intencional: así nunca apuestas sabiendo el resultado.

**Aposté a un partido, ¿cuándo sé si gané?**
Cuando el partido real se juegue, corre la opción 6 en cualquier momento posterior. El sistema revisa Wikipedia de nuevo y valida tu apuesta automáticamente.

**Me sale "No se pudieron obtener partidos" o "No se pudieron obtener resultados", ¿qué hago?**
Revisa tu conexión a internet. Si el problema persiste, es posible que la página fuente (Wikipedia) esté temporalmente inaccesible o haya cambiado de estructura — el sistema no muestra datos falsos en ese caso, solo te avisa del error.

**¿Dónde se guarda mi información?**
En la carpeta `datos/` (se crea automáticamente): `usuarios.json`, los reportes `.xlsx`, y `ganadores.txt`. El registro de auditoría (logs) se guarda en `logs/app.log`.

**¿Puedo cerrar el programa y volver a entrar después?**
Sí. Tu usuario y saldo quedan guardados en `datos/usuarios.json` y se recargan automáticamente la próxima vez que ejecutes `python main.py`.
