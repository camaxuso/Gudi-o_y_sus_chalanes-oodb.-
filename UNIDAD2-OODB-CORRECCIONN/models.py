"""
Modelo de objetos del Gimnasio (Durus).


    usergym (role_gym)  ->  Person (abstracta) -> Client / Employee
    Payment             ->  Payment
    Membership          ->  Membership

"""

from datetime import datetime

from durus.persistent import Persistent
from durus.persistent_list import PersistentList


#
# Valores permitidos (equivalentes a los ENUM del esquema relacional)
#
BRANCHES = ("OTAY", "FUNDADORES", "PLAYAS")
PAYMENT_METHODS = ("Cash", "Debit", "Credit")


#
# clase persistente con encapsulamiento
#
class Person(Persistent):


    def __init__(self, name, lastname_p, lastname_m, phone, email, branch):
        # Se asigna a traves de los setters para que TODO pase por las
        # validaciones, incluso al construir el objeto.
        self.name = name
        self.lastname_p = lastname_p
        self.lastname_m = lastname_m
        self.phone = phone
        self.email = email
        self.branch = branch

    # name
    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        value = (value or "").strip()
        if not value:
            raise ValueError("El nombre no puede estar vacio.")
        self._name = value

    # apellidos
    @property
    def lastname_p(self):
        return self._lastname_p

    @lastname_p.setter
    def lastname_p(self, value):
        value = (value or "").strip()
        if not value:
            raise ValueError("El apellido paterno no puede estar vacio.")
        self._lastname_p = value

    @property
    def lastname_m(self):
        return self._lastname_m

    @lastname_m.setter
    def lastname_m(self, value):
        # El apellido materno si puede ir vacio (en el DDL es NULL-able).
        self._lastname_m = (value or "").strip()

    # phone
    @property
    def phone(self):
        return self._phone

    @phone.setter
    def phone(self, value):
        
        value = str(value or "").strip()
        if not (value.isdigit() and len(value) == 10):
            raise ValueError(
                f"Telefono invalido: '{value}'. Deben ser 10 digitos."
            )
        self._phone = value

    # email
    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, value):
        value = (value or "").strip().lower()
        # Validacion simple pero suficiente: un "@", algo antes, y un
        # dominio con punto despues.
        if value.count("@") != 1:
            raise ValueError(f"Email invalido: '{value}'. Falta '@'.")
        local, _, domain = value.partition("@")
        if not local or "." not in domain or domain.startswith(".") or domain.endswith("."):
            raise ValueError(f"Email invalido: '{value}'.")
        self._email = value

    # branch
    @property
    def branch(self):
        return self._branch

    @branch.setter
    def branch(self, value):
        value = (value or "").strip().upper()
        if value not in BRANCHES:
            raise ValueError(
                f"Sucursal invalida: '{value}'. Opciones: {', '.join(BRANCHES)}."
            )
        self._branch = value

    # ---------------- utilidades ----------------
    def full_name(self):
        parts = [self._name, self._lastname_p, self._lastname_m]
        return " ".join(p for p in parts if p)

    # ------------------------------------------------------------------
    # metodos polimorficos.

    def role(self):
        raise NotImplementedError("Subclase debe implementar role().")

    def description(self):
        raise NotImplementedError("Subclase debe implementar description().")



class Membership(Persistent):


    def __init__(self, name, monthly_price):
        self.name = name
        self.monthly_price = monthly_price

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        value = (value or "").strip()
        if not value:
            raise ValueError("El nombre de la membresia no puede estar vacio.")
        self._name = value

    @property
    def monthly_price(self):
        return self._monthly_price

    @monthly_price.setter
    def monthly_price(self, value):
        value = float(value)
        if value < 0:
            raise ValueError("El precio de la membresia no puede ser negativo.")
        self._monthly_price = value

    def __repr__(self):
        return f"<Membership {self._name} ${self._monthly_price:,.2f}>"



class Payment(Persistent):

    def __init__(self, amount, reason, method, client, date=None):
        self.amount = amount
        self.reason = reason
        self.method = method
        # referencia directa al objeto
        self._client = client
        self._date = date or datetime.now()

    @property
    def amount(self):
        return self._amount

    @amount.setter
    def amount(self, value):
        value = float(value)
        if value <= 0:
            raise ValueError(f"El monto debe ser mayor a 0 (recibido: {value}).")
        self._amount = value

    @property
    def reason(self):
        return self._reason

    @reason.setter
    def reason(self, value):
        self._reason = (value or "").strip()

    @property
    def method(self):
        return self._method

    @method.setter
    def method(self, value):
        value = (value or "").strip()
        if value not in PAYMENT_METHODS:
            raise ValueError(
                f"Metodo de pago invalido: '{value}'. "
                f"Opciones: {', '.join(PAYMENT_METHODS)}."
            )
        self._method = value

    @property
    def client(self):
        """Solo lectura: un pago no cambia de dueno."""
        return self._client

    @property
    def date(self):
        return self._date

    def __repr__(self):
        return (
            f"<Payment ${self._amount:,.2f} {self._method} "
            f"{self._date:%Y-%m-%d} '{self._reason}'>"
        )


# subclases de Person

class Client(Person):
    """Socio del gimnasio. Era usergym con role_gym = 'client'."""

    def __init__(self, name, lastname_p, lastname_m, phone, email, branch,
                 membership=None):
        super().__init__(name, lastname_p, lastname_m, phone, email, branch)

        # referencia a un objeto compartido del catalogo
        self._membership = membership

        self._payments = PersistentList()

    @property
    def membership(self):
        return self._membership

    @membership.setter
    def membership(self, value):
        if value is not None and not isinstance(value, Membership):
            raise ValueError("La membresia debe ser un objeto Membership.")
        self._membership = value

    @property
    def payments(self):
        """Lista de pagos del cliente (solo lectura desde fuera).

        Para agregar un pago se usa add_payment(), que valida.
        """
        return self._payments

    def add_payment(self, payment):
        if not isinstance(payment, Payment):
            raise ValueError("Solo se pueden agregar objetos Payment.")
        if payment.client is not self:
            raise ValueError("El pago pertenece a otro cliente.")
        self._payments.append(payment)

    def total_paid(self):
        """Suma de todos los pagos. Recorre el grafo de objetos."""
        return sum(p.amount for p in self._payments)

    # metodos polimorficos 
    def role(self):
        return "client"

    def monthly_fee(self):
        """Cuota mensual segun la membresia (0 si no tiene)."""
        return self._membership.monthly_price if self._membership else 0.0

    def description(self):
        m = self._membership.name if self._membership else "sin membresia"
        return (
            f"[Cliente] {self.full_name()} - {self.branch} - "
            f"membresia {m} (${self.monthly_fee():,.2f}/mes)"
        )


class Employee(Person):
    """Personal del gimnasio. Era usergym con role_gym = 'employee'."""

    def __init__(self, name, lastname_p, lastname_m, phone, email, branch,
                 position=""):
        super().__init__(name, lastname_p, lastname_m, phone, email, branch)
        self.position = position

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, value):
        value = (value or "").strip()
        if not value:
            raise ValueError("El puesto del empleado no puede estar vacio.")
        self._position = value

    # ---- metodos polimorficos sobrescritos ----
    def role(self):
        return "employee"

    def monthly_fee(self):
        """Un empleado no paga cuota."""
        return 0.0

    def description(self):
        return (
            f"[Empleado] {self.full_name()} - {self.branch} - "
            f"puesto: {self._position}"
        )

