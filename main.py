from durus.file_storage import FileStorage
from durus.connection import Connection
from durus.persistent_dict import PersistentDict

from modelos import UserCardMembresia, UserCardAccesoTaquilla

# -------------------------------------------------------------
# 1. Configuración del Almacenamiento y Conexión en Durus
# -------------------------------------------------------------
storage = FileStorage("gimnasio.durus")
connection = Connection(storage)
root = connection.get_root()

# Uso de PersistentDict para almacenar Clases Persistentes
if "user_card" not in root:
    root["user_card"] = PersistentDict()
    connection.commit()

# -------------------------------------------------------------
# 2. Demostración de Abstracción y Encapsulamiento
# -------------------------------------------------------------
print("--- 1. DEMOSTRACIÓN DE ABSTRACCIÓN Y ENCAPSULAMIENTO ---")

# Instanciamos los objetos sin necesidad de ejecutar sentencias SQL de tabla pivote (INSERT INTO user_card...)
card_gym = UserCardMembresia(id_user=101, id_card=5001, nivel_acceso="VIP Premium")
card_locker = UserCardAccesoTaquilla(id_user=102, id_card=5002, numero_casillero=45)

# Ocultamos la complejidad interna llamando directamente al método de la abstracción:
print(card_gym.mostrar_informacion())
print(card_locker.mostrar_informacion())

# -------------------------------------------------------------
# 3. Demostración de Persistencia y Manejo de Transacciones
# -------------------------------------------------------------
print("\n--- 2. DEMOSTRACIÓN DE TRANSACCIONES CON CLASES PERSISTENTES ---")
try:
    # Transacción Exitosa:
    # Durus rastrea de forma automática que card_gym es una 'Clase Persistente' (hereda de Persistent)
    root["user_card"]["UC-101"] = card_gym
    connection.commit()  # Los cambios se guardan permanentemente en la base de datos
    print("Éxito: Registro de UserCard (VIP Premium) guardado correctamente con commit().")

    # Transacción Fallida (Prueba de Rollback/Abort):
    print("\nIntentando registrar tarjeta de casillero, simulando error de validación...")
    root["user_card"]["UC-102"] = card_locker

    # Simulamos una falla del sistema antes del commit
    raise ValueError("¡Error de red! No se pudo validar la asignación del casillero.")

    connection.commit()  # Esta línea no se ejecuta debido a la excepción
except Exception as error:
    print(f"Excepción capturada: {error}")
    connection.abort()  # Se cancela la transacción y se descartan los datos pendientes en memoria
    print("Abort: Transacción cancelada. El estado de la base de datos no fue alterado.")

# -------------------------------------------------------------
# 4. Estado Final de la Base de Datos Persistente
# -------------------------------------------------------------
print("\n--- 3. VERIFICACIÓN DE DATOS PERSISTENTES EN LA DB ---")
for key, obj_card in root["user_card"].items():
    print(f"Clave en DB [{key}] -> {obj_card.mostrar_informacion()}")