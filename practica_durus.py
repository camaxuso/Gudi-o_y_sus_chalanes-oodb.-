from durus.file_storage import FileStorage
from durus.connection import Connection
from durus.persistent import Persistent
from durus.persistent_list import PersistentList

# 1. Clases
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

    def registrar_pago(self, pago):
        self.historial_pagos.append(pago)

# 2. Conexion a BD
almacenamiento = FileStorage('gimnasio.durus')
conexion = Connection(almacenamiento)
raiz = conexion.get_root()

# 3. Cliente
cliente = raiz['usuarios']['ana@email.com']


# Actualizar Datos
print(f"Nombre original: {cliente.nombre}")
print(f"Pagos originales: {len(cliente.historial_pagos)}")

# Modificar datos del cliente
cliente.nombre = "Ana María"

# Nuevo objeto (2 Mes)
nueva_tarjeta = Tarjeta(9876543210987654)
pago_segundo_mes = Pago(750.00, nueva_tarjeta) 

# Guardamos en Historial
cliente.registrar_pago(pago_segundo_mes)

# Se guarda
conexion.commit()

print("\n Se actualizo el nombre y se agrego segundo pago")