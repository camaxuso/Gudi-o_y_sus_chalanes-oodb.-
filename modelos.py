from durus.persistent import Persistent

# 1. CLASE PERSISTENTE Y ABSTRACCIÓN BASE
# Heredar de 'Persistent' convierte a la clase en una Clase Persistente dentro de Durus.
class UserCard(Persistent):
    def __init__(self, id_user: int, id_card: int, estado_activa: bool = True):
        # ENCAPSULAMIENTO: Los atributos internos del objeto se asignan en la inicialización
        # y quedan encapsulados dentro de cada instancia.
        if not isinstance(id_user, int) or not isinstance(id_card, int):
            raise TypeError("id_user e id_card deben ser números enteros.")
            
        self._id_user = id_user
        self._id_card = id_card
        self._estado_activa = estado_activa

    # ABSTRACCIÓN Y ENCAPSULAMIENTO: Métodos de acceso (Getters) para interactuar 
    # con los datos de forma controlada sin manipular directo el estado si no se desea.
    def obtener_id_user(self):
        return self._id_user

    def obtener_id_card(self):
        return self._id_card

    def esta_activa(self):
        return self._estado_activa

    # ABSTRACCIÓN: El usuario interactúa con un método legible sin preocuparse 
    # de cómo se estructuran las llaves foráneas a nivel de tabla relacional.
    def mostrar_informacion(self):
        estado = "Activa" if self._estado_activa else "Inactiva"
        return f"Relación UserCard -> ID Usuario: {self._id_user} | ID Tarjeta: {self._id_card} | Estado: {estado}"


# 2. HERENCIA Y POLIMORFISMO MANTENIENDO PERSISTENCIA
class UserCardMembresia(UserCard):
    def __init__(self, id_user: int, id_card: int, nivel_acceso: str, estado_activa: bool = True):
        super().__init__(id_user, id_card, estado_activa)
        self._nivel_acceso = nivel_acceso  # Atributo exclusivo encapsulado

    # Sobrescribimos el método (Polimorfismo) manteniendo la abstracción
    def mostrar_informacion(self):
        estado = "Activa" if self._estado_activa else "Inactiva"
        return f"MEMBRESÍA GIMNASIO -> ID User: {self._id_user} | ID Card: {self._id_card} | Acceso: {self._nivel_acceso} | Estado: {estado}"


class UserCardAccesoTaquilla(UserCard):
    def __init__(self, id_user: int, id_card: int, numero_casillero: int, estado_activa: bool = True):
        super().__init__(id_user, id_card, estado_activa)
        self._numero_casillero = numero_casillero  # Atributo exclusivo encapsulado

    def mostrar_informacion(self):
        estado = "Activa" if self._estado_activa else "Inactiva"
        return f"TARJETA TAQUILLA -> ID User: {self._id_user} | ID Card: {self._id_card} | Casillero #: {self._numero_casillero} | Estado: {estado}"