from durus.file_storage import FileStorage
from durus.connection import Connection
from durus.persistent import Persistent
from durus.persistent_list import PersistentList

# 1. Reconstruir Las clases
class Tarjeta(Persistent):
    def __init__(self, num_tarjeta):
        self.num_tarjeta = num_tarjeta

class Pago(Persistent):
    def __init__(self, monto, tarjeta):
        self.monto = monto
        self.tarjeta = tarjeta 

class Usuario(Persistent):
    def __init__(self, nombre, correo):
        self.nombre = nombre
        self.correo = correo
        self.historial_pagos = PersistentList()

# 2. Conexion a la base de datos
almacenamiento = FileStorage('gimnasio.durus')
conexion = Connection(almacenamiento)
raiz = conexion.get_root()

# 3. Seleccionamos al cliente
cliente = raiz['usuarios']['ana@email.com']

# 4. Comprobacion
print("--- DATOS RECUPERADOS EXITOSAMENTE ---")
print(f"Nombre: {cliente.nombre} | Correo: {cliente.correo}")

for pago in cliente.historial_pagos:
    print(f"- Realizó un pago de: ${pago.monto}")
    print(f"  Con la tarjeta terminada en: {str(pago.tarjeta.num_tarjeta)[-4:]}")