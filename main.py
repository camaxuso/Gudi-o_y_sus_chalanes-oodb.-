from durus.file_storage import FileStorage
from durus.connection import Connection
from durus.persistent_dict import PersistentDict # ¡Nueva línea!
from modelos import Cliente, Staff

# 1. Configurar la base de datos Durus
storage = FileStorage("gimnasio.durus")
connection = Connection(storage)
root = connection.get_root()

# Crear un diccionario persistente en lugar de uno nativo
if "usuarios_gym" not in root:
    root["usuarios_gym"] = PersistentDict() # ¡Cambio clave!
    connection.commit()

# 2. Prueba de Polimorfismo
print("--- 1. PRUEBA DE POLIMORFISMO ---")
cliente1 = Cliente("Monica", "Galindo", "monica@gmail.com", "Premium")
staff1 = Staff("Brandon", "Galindo", "brandon@gmail.com", "Administrador")

# Al llamar al mismo método, cada clase responde diferente:
print(cliente1.mostrar_informacion())
print(staff1.mostrar_informacion())

# 3. Prueba de Transacciones
print("\n--- 2. PRUEBA DE TRANSACCIONES ---")
try:
    # Transacción exitosa
    root["usuarios_gym"]["CLI-001"] = cliente1
    connection.commit() # Confirmamos el guardado
    print("Éxito: Cliente guardado y confirmado con commit().")

    # Transacción fallida
    print("Intentando guardar al Staff, pero simularemos un error de validación...")
    root["usuarios_gym"]["STF-001"] = staff1
    
    # Simulamos que algo salió mal antes de poder guardar (ej. se cayó la red o falló un dato)
    raise ValueError("¡Error de sistema! El rol operativo no es válido.")
    
    connection.commit() # Esta línea nunca se alcanza por el error

except Exception as e:
    print(f"Error detectado: {e}")
    connection.abort() # Revertimos cualquier cambio pendiente en la memoria
    print("Abort: Los cambios no guardados fueron revertidos correctamente.")

# 4. Verificar qué sobrevivió en la base de datos
print("\n--- 3. ESTADO DE LA BASE DE DATOS ---")
for key, usuario in root["usuarios_gym"].items():
    print(f"Guardado en DB -> ID {key}: {usuario.mostrar_informacion()}")