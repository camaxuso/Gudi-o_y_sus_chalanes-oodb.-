# Importaciones exclusivas de Durus
from durus.persistent import Persistent
from durus.persistent_list import PersistentList
from durus.persistent_dict import PersistentDict
from durus.file_storage import FileStorage
from durus.connection import Connection

#1. Definir Objetos
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
        # PersistentList
        self.historial_pagos = PersistentList()

    def registrar_pago(self, pago):
        self.historial_pagos.append(pago)

# 2. Conexion a la BD
almacenamiento = FileStorage('gimnasio.durus')
conexion = Connection(almacenamiento)
raiz = conexion.get_root() 

# PersistentDict
if 'usuarios' not in raiz:
    raiz['usuarios'] = PersistentDict()

# 3. Crear archivo y guardar
mi_tarjeta = Tarjeta(4152313456789123)
pago_mensualidad = Pago(500.00, mi_tarjeta)

cliente1 = Usuario('Ana', 'ana@email.com')
cliente1.registrar_pago(pago_mensualidad)

raiz['usuarios']['ana@email.com'] = cliente1

conexion.commit()

print("Guardado en Durus")