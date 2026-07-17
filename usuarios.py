import json
import os
import hashlib
import logging

from utilidades import (
    UsuarioNoRegistradoError,
    CredencialesInvalidasError,
    OperacionInvalidaError,
    validar_correo,
    validar_edad,
)

logger = logging.getLogger("apuestas_mundial")

RUTA_USUARIOS = os.path.join("datos", "usuarios.json")


class Usuario:
    def __init__(self, nombre, apellido, correo, edad, password_hash, saldo=0.0):
        self.nombre = nombre
        self.apellido = apellido
        self.correo = correo
        self.edad = edad
        self.password_hash = password_hash
        self.saldo = saldo

    def to_dict(self):
        return {
            "nombre": self.nombre,
            "apellido": self.apellido,
            "correo": self.correo,
            "edad": self.edad,
            "password_hash": self.password_hash,
            "saldo": self.saldo,
        }

    @staticmethod
    def from_dict(d):
        return Usuario(
            d["nombre"], d["apellido"], d["correo"], d["edad"],
            d["password_hash"], d.get("saldo", 0.0)
        )

    def __str__(self):
        return f"{self.nombre} {self.apellido} ({self.correo}) - Saldo: ${self.saldo:.2f}"


def _hash_password(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


class GestorUsuarios:
    def __init__(self):
        self.usuarios = {}  # diccionario: correo -> Usuario
        self.cargar_usuarios()

    # ---------- Persistencia ----------

    def cargar_usuarios(self):
        os.makedirs("datos", exist_ok=True)
        if not os.path.exists(RUTA_USUARIOS):
            self.usuarios = {}
            return
        try:
            with open(RUTA_USUARIOS, "r", encoding="utf-8") as f:
                datos = json.load(f)
            self.usuarios = {correo: Usuario.from_dict(u) for correo, u in datos.items()}
        except (json.JSONDecodeError, OSError) as e:
            logger.error(f"Error al cargar usuarios: {e}")
            self.usuarios = {}

    def guardar_usuarios(self):
        os.makedirs("datos", exist_ok=True)
        datos = {correo: u.to_dict() for correo, u in self.usuarios.items()}
        with open(RUTA_USUARIOS, "w", encoding="utf-8") as f:
            json.dump(datos, f, indent=4, ensure_ascii=False)

    # ---------- Registro / Login ----------

    def registrar_usuario(self, nombre, apellido, correo, edad, password):
        correo = validar_correo(correo)
        edad = validar_edad(edad)
        if correo in self.usuarios:
            raise OperacionInvalidaError("Ya existe un usuario registrado con ese correo.")
        if not password or len(password) < 4:
            raise OperacionInvalidaError("La contraseña debe tener al menos 4 caracteres.")

        nuevo_usuario = Usuario(nombre, apellido, correo, edad, _hash_password(password))
        self.usuarios[correo] = nuevo_usuario
        self.guardar_usuarios()
        logger.info(f"Usuario registrado: {correo}")
        return nuevo_usuario

    def iniciar_sesion(self, correo, password):
        usuario = self.usuarios.get(correo)
        if usuario is None:
            logger.warning(f"Intento de login con correo no registrado: {correo}")
            raise UsuarioNoRegistradoError("No existe un usuario con ese correo.")
        if usuario.password_hash != _hash_password(password):
            logger.warning(f"Contraseña incorrecta para: {correo}")
            raise CredencialesInvalidasError("Contraseña incorrecta.")
        logger.info(f"Inicio de sesión exitoso: {correo}")
        return usuario

    def obtener_usuario(self, correo):
        usuario = self.usuarios.get(correo)
        if usuario is None:
            raise UsuarioNoRegistradoError(f"Usuario no encontrado: {correo}")
        return usuario

    def listar_usuarios(self):
        return list(self.usuarios.values())
