

import logging
import os

from durus.file_storage import FileStorage
from durus.connection import Connection
from durus.persistent_dict import PersistentDict

from models import Client, Employee, Membership, Payment, BRANCHES

logging.getLogger("durus").setLevel(logging.WARNING)


class GymDB:
    """Base de datos orientada a objetos del gimnasio."""

    def __init__(self, db_path="data/gym.durus"):
        db_dir = os.path.dirname(db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)

        self.storage = FileStorage(db_path)
        self.connection = Connection(self.storage)
        self.root = self.connection.get_root()

        # --- Contenedores raiz: todo lo persistente cuelga de aqui ---
        for container in ("clients", "employees", "memberships"):
            if container not in self.root:
                self.root[container] = PersistentDict()

        # Contador de ids
        
        if "counters" not in self.root:
            self.root["counters"] = PersistentDict(
                {"client": 1, "employee": 1, "membership": 1}
            )

        self.connection.commit()

        self.clients = self.root["clients"]
        self.employees = self.root["employees"]
        self.memberships = self.root["memberships"]
        self.counters = self.root["counters"]

   
    # Transacciones 
    def commit(self):
        """Confirma todos los cambios pendientes."""
        self.connection.commit()

    def abort(self):
        """Revierte todos los cambios no confirmados."""
        self.connection.abort()

    def close(self):
       
        self.storage.close()

    def _next_id(self, kind):
        value = self.counters[kind]
        self.counters[kind] = value + 1
        return value

    # CREATE  
   
    def add_membership(self, name, monthly_price):
        membership = Membership(name=name, monthly_price=monthly_price)
        mid = self._next_id("membership")
        self.memberships[mid] = membership
        return mid, membership

    def add_client(self, name, lastname_p, lastname_m, phone, email,
                   branch, membership=None):
        # El constructor valida; si algo esta mal lanza ValueError y no
        # se agrega nada a la base.
        client = Client(
            name=name, lastname_p=lastname_p, lastname_m=lastname_m,
            phone=phone, email=email, branch=branch, membership=membership,
        )
        cid = self._next_id("client")
        self.clients[cid] = client
        return cid, client

    def add_employee(self, name, lastname_p, lastname_m, phone, email,
                     branch, position):
        employee = Employee(
            name=name, lastname_p=lastname_p, lastname_m=lastname_m,
            phone=phone, email=email, branch=branch, position=position,
        )
        eid = self._next_id("employee")
        self.employees[eid] = employee
        return eid, employee

    def add_payment(self, client, amount, reason, method):
        """Crea un pago y lo guarda DENTRO del cliente (composicion)."""
        payment = Payment(
            amount=amount, reason=reason, method=method, client=client,
        )
        client.add_payment(payment)
        return payment

    # READ  
    def get_client(self, client_id):
        return self.clients.get(client_id)

    def get_employee(self, employee_id):
        return self.employees.get(employee_id)

    def get_membership(self, membership_id):
        return self.memberships.get(membership_id)

    def all_clients(self):
        return list(self.clients.values())

    def all_employees(self):
        return list(self.employees.values())

    def all_people(self):
        """Clientes y empleados juntos: la base del polimorfismo."""
        return self.all_clients() + self.all_employees()

    def find_client_by_email(self, email):
        """Busca recorriendo los objetos (no hay indice por email)."""
        target = (email or "").strip().lower()
        for client in self.clients.values():
            if client.email == target:
                return client
        return None

    # UPDATE  
    def update_client_email(self, client, new_email):
        """La validacion vive en el setter del modelo, no aqui."""
        client.email = new_email
        return client

    def change_membership(self, client, membership):
        client.membership = membership
        return client

    # DELETE  
    def delete_client(self, client_id):
        """Da de baja un cliente.

        Efecto en cascada: los Payment solo eran alcanzables a traves de
        este cliente, asi que al quitarlo de la raiz dejan de pertenecer
        a la base de datos (COMPOSICION).

        En cambio su Membership NO se borra: es un objeto compartido del
        catalogo y sigue colgando de root['memberships'] (AGREGACION).
        """
        client = self.clients.get(client_id)
        if client is None:
            return None
        cascaded = len(client.payments)
        del self.clients[client_id]
        return {"client": client, "payments_cascaded": cascaded}

    def delete_employee(self, employee_id):
        employee = self.employees.get(employee_id)
        if employee is None:
            return None
        del self.employees[employee_id]
        return employee

    # NAVEGACION DEL GRAFO  
    def payments_of(self, client):
        """Consulta 1: todos los pagos de un cliente.

        SQL equivalente:
            SELECT amount, reason, date
            FROM Payment
            WHERE id_user = ?;
        """
        return list(client.payments)

    def membership_name_of(self, client):
        """Consulta 2: el tipo de membresia de un cliente.

        Navegacion: cliente -> membresia -> nombre (dos saltos).

        SQL equivalente (necesita DOS JOINs):
            SELECT m.membership
            FROM usergym u
            JOIN user_membership um ON u.id_user = um.id_user
            JOIN Membership      m  ON um.id_membership = m.id_membership
            WHERE u.id_user = ?;
        """
        return client.membership.name if client.membership else None

    def total_paid_by(self, client):
        """Consulta 3: total pagado por un cliente.

        SQL equivalente:
            SELECT SUM(amount) FROM Payment WHERE id_user = ?;
        """
        return client.total_paid()

    def clients_by_branch(self, branch):
        """Consulta 4: clientes de una sucursal.

        SQL equivalente:
            SELECT * FROM usergym
            WHERE role_gym = 'client' AND location = ?;
        """
        branch = (branch or "").strip().upper()
        if branch not in BRANCHES:
            raise ValueError(f"Sucursal invalida: '{branch}'.")
        return [c for c in self.clients.values() if c.branch == branch]

    def gym_revenue(self):
        """Consulta 5: ingreso total del gimnasio.

        Recorre el grafo completo: raiz -> clientes -> pagos.

        SQL equivalente:
            SELECT SUM(amount) FROM Payment;
        """
        return sum(c.total_paid() for c in self.clients.values())
