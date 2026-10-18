from durus.persistent import Persistent

class UsuarioGym(Persistent):
    def __init__(self, nombre, apellidos, email):
        self.nombre = nombre
        self.apellidos = apellidos
        self.email = email

    # Este método es la base y debe ir aquí, en la superclase
    def mostrar_informacion(self):
        return f"Usuario genérico: {self.nombre} {self.apellidos}"

class Cliente(UsuarioGym):
    def __init__(self, nombre, apellidos, email, tipo_membresia):
        super().__init__(nombre, apellidos, email)
        self.tipo_membresia = tipo_membresia # Atributo exclusivo del cliente

    def mostrar_informacion(self):
        # Comportamiento polimórfico 1
        return f"CLIENTE: {self.nombre} | Membresía: {self.tipo_membresia}"

class Staff(UsuarioGym):
    def __init__(self, nombre, apellidos, email, rol_operativo):
        super().__init__(nombre, apellidos, email)
        self.rol_operativo = rol_operativo # Atributo exclusivo del empleado

    def mostrar_informacion(self):
        # Comportamiento polimórfico 2
        return f"STAFF: {self.nombre} | Área: {self.rol_operativo}"