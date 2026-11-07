"""
    pip install -r requirements.txt
    python3 main.py

La demo reinicia la base de datos al iniciar para que siempre sea
reproducible.
"""

import os
import shutil

from durus.persistent import Persistent
from durus.persistent_list import PersistentList

from models import Client, Employee, Payment
from repository import GymDB

DB_DIR = "data"
DB_PATH = os.path.join(DB_DIR, "gym.durus")



def section(number, title):
    print()
    print("=" * 70)
    print(f"  {number}. {title}")
    print("=" * 70)


def step(text):
    print(f"\n-> {text}")


def ok(text):
    print(f"   [OK] {text}")


def fail(text):
    print(f"   [RECHAZADO] {text}")


# Preparacion

def reset_database():
    """Borra la base para que la demo sea reproducible."""
    shutil.rmtree(DB_DIR, ignore_errors=True)


def seed():
    """Carga los datos iniciales y los confirma en disco."""
    db = GymDB(DB_PATH)

    # Catalogo de membresias (objetos COMPARTIDOS -> agregacion)
    _, economica = db.add_membership("economica", 350.00)
    _, plus = db.add_membership("plus", 650.00)

    # Clientes
    _, ana = db.add_client(
        "Ana", "Lozano", "Beltran", "6641234501",
        "ana@gym.com", "OTAY", membership=plus,
    )
    _, luis = db.add_client(
        "Luis", "Salas", "Moreno", "6641234502",
        "luis@gym.com", "OTAY", membership=economica,
    )
    _, karla = db.add_client(
        "Karla", "Figueroa", "Ochoa", "6643234501",
        "karla@gym.com", "PLAYAS", membership=plus,
    )

    # Empleados
    db.add_employee(
        "Oscar", "Villalobos", "Ramos", "6642234501",
        "oscar@gym.com", "FUNDADORES", position="Entrenador",
    )

    # Pagos (viven DENTRO del cliente -> composicion)
    db.add_payment(ana, 650.00, "Mensualidad octubre", "Credit")
    db.add_payment(ana, 650.00, "Mensualidad noviembre", "Debit")
    db.add_payment(luis, 350.00, "Mensualidad noviembre", "Cash")
    db.add_payment(karla, 650.00, "Mensualidad noviembre", "Credit")

    db.commit()
    db.close()



#CLASES PERSISTENTES

def s1_persistent_classes(db):
    section(1, "CLASES PERSISTENTES")
    print("   Person, Client, Employee, Membership y Payment heredan de")
    print("   durus.persistent.Persistent, por eso se guardan en disco.")

    step("La base se cerro y se volvio a abrir. Lo que hay en disco:")
    for cid, client in db.clients.items():
        print(f"   id={cid}  {client.description()}")
    for eid, employee in db.employees.items():
        print(f"   id={eid}  {employee.description()}")

    step("Jerarquia de clases de un objeto recuperado del disco:")
    ana = db.get_client(1)
    cadena = " -> ".join(c.__name__ for c in type(ana).__mro__[:-1])
    print(f"   type(ana)                   = {type(ana).__name__}")
    print(f"   isinstance(ana, Client)     = {isinstance(ana, Client)}")
    print(f"   isinstance(ana, Persistent) = {isinstance(ana, Persistent)}")
    print(f"   Cadena de herencia          = {cadena}")
    ok("Los objetos conservan su clase real al recuperarse del disco.")



# ENCAPSULAMIENTO Y ABSTRACCION

def s2_encapsulation(db):
    section(2, "ENCAPSULAMIENTO Y ABSTRACCION")
    print("   Los atributos son privados (_email, _phone...) y solo se")
    print("   modifican por properties que validan. Un objeto nunca queda")
    print("   en estado invalido.")

    ana = db.get_client(1)

    step("Intentos de guardar datos invalidos:")
    intentos = [
        ("email sin @",        lambda: setattr(ana, "email", "anagym.com")),
        ("telefono de 5 digitos", lambda: setattr(ana, "phone", "66412")),
        ("sucursal inexistente",  lambda: setattr(ana, "branch", "TIJUANA")),
        ("pago en negativo",      lambda: Payment(-100, "x", "Cash", ana)),
        ("metodo de pago raro",   lambda: Payment(100, "x", "Bitcoin", ana)),
        ("nombre vacio",          lambda: setattr(ana, "name", "   ")),
    ]
    for etiqueta, accion in intentos:
        try:
            accion()
            print(f"   [ERROR] se acepto: {etiqueta}")
        except ValueError as e:
            fail(f"{etiqueta}: {e}")

    step("El objeto quedo intacto tras los intentos fallidos:")
    print(f"   email={ana.email}  phone={ana.phone}  branch={ana.branch}")

    step("Un cambio valido si pasa:")
    db.update_client_email(ana, "ANA.LOZANO@GYM.COM")
    ok(f"email normalizado a minusculas: {ana.email}")

    db.abort()  # se descarta el cambio solo pra demonstracion



# HERENCIA Y POLIMORFISMO

def s3_inheritance(db):
    section(3, "HERENCIA Y POLIMORFISMO")
    print("   En el modelo relacional el tipo era una columna:")
    print("       role_gym ENUM('client','employee')")
    print("   Aqui es una jerarquia real: Person -> Client / Employee.")

    step("Mismo bucle, mismas llamadas, comportamiento distinto:")
    for person in db.all_people():
        # description() y monthly_fee() estan sobrescritos en cada
        # subclase: esto es polimorfismo.
        print(f"   {person.role():9s} | cuota ${person.monthly_fee():7,.2f} | "
              f"{person.description()}")

    step("Llamar el metodo abstracto en la superclase es un error:")
    try:
        from models import Person
        Person.description(db.get_client(1))
    except NotImplementedError as e:
        fail(f"Person.description(): {e}")



#OBJETOS COMPLEJOS

def s4_complex_objects(db):
    section(4, "OBJETOS COMPLEJOS")
    print("   No hay claves foraneas: hay referencias DIRECTAS a objetos.")

    ana = db.get_client(1)

    step("COMPOSICION  Client <>-- Payment  (PersistentList dentro del cliente)")
    print(f"   type(ana.payments) = {type(ana.payments).__name__}")
    for p in ana.payments:
        print(f"   {p}")
    print(f"   Relacional: SELECT * FROM Payment WHERE id_user = 1;")
    print(f"   Objetos:    ana.payments")

    step("AGREGACION   Client <>-- Membership  (objeto compartido)")
    luis = db.get_client(2)
    karla = db.get_client(3)
    print(f"   ana.membership   -> {ana.membership}")
    print(f"   karla.membership -> {karla.membership}")
    print(f"   Es el MISMO objeto en memoria: "
          f"{ana.membership is karla.membership}")
    print(f"   luis tiene otra:  {luis.membership}")
    ok("Dos clientes comparten una sola instancia de Membership.")

    step("Navegacion inversa: del pago a su cliente")
    primer_pago = ana.payments[0]
    print(f"   primer_pago.client.full_name() = {primer_pago.client.full_name()}")
    print(f"   Es el mismo objeto Ana: {primer_pago.client is ana}")



# PERSISTENCIA POR ALCANZABILIDAD

def s5_reachability(db):
    section(5, "PERSISTENCIA POR ALCANZABILIDAD")
    print("   Solo se guarda lo que cuelga de connection.get_root().")

    step("Recorrido del grafo desde la raiz:")
    print("   raiz")
    for container in ("clients", "employees", "memberships", "counters"):
        print(f"    |-- '{container}'  ({type(db.root[container]).__name__})")

    print()
    print("   raiz -> 'clients'")
    for cid, client in db.clients.items():
        print(f"    |-- [{cid}] {client.full_name()}")
        print(f"    |     |-- _membership --> {client.membership.name}  (compartida)")
        print(f"    |     |-- _payments ({len(client.payments)} pagos)")
        for p in client.payments:
            print(f"    |           |-- ${p.amount:,.2f} {p.reason}")

    step("Punto clave:")
    print("   Los Payment NO tienen contenedor propio en la raiz.")
    print("   Se alcanzan SOLO a traves de su cliente. Por eso, al borrar")
    print("   el cliente, dejan de ser alcanzables (cascada automatica).")



# TRANSACCIONES

def s6_transactions(db):
    section(6, "TRANSACCIONES: commit() vs abort()")

    luis = db.get_client(2)
    inicial = len(luis.payments)
    print(f"   Luis tiene {inicial} pago(s) al inicio.")

    step("Operacion A: se agrega un pago y se hace COMMIT")
    db.add_payment(luis, 350.00, "Mensualidad diciembre", "Cash")
    db.commit()
    print(f"   Luis ahora tiene {len(luis.payments)} pago(s).")
    ok("Confirmado con commit().")

    step("Operacion B: se agrega otro pago y se hace ABORT")
    db.add_payment(luis, 9999.00, "Pago erroneo", "Credit")
    print(f"   Antes del abort, en memoria: {len(luis.payments)} pago(s).")
    db.abort()
    print(f"   Despues del abort:           {len(luis.payments)} pago(s).")
    fail("El pago de $9,999.00 nunca se guardo.")

    step("Verificacion en disco (se cierra y se reabre la base):")
    db.close()
    db2 = GymDB(DB_PATH)
    luis2 = db2.get_client(2)
    print(f"   Pagos de Luis en disco: {len(luis2.payments)}")
    for p in luis2.payments:
        print(f"     {p}")
    ok("Solo sobrevivio lo confirmado con commit().")
    return db2  # la conexion anterior quedo cerrada



# NAVEGACION DEL GRAFO

def s7_graph_navigation(db):
    section(7, "NAVEGACION DEL GRAFO (vs. SQL)")
    print("   Se recorren referencias con puntos, sin JOINs.")

    ana = db.get_client(1)

    step("Consulta 1: todos los pagos de un cliente")
    print("   Objetos: ana.payments")
    print("   SQL:     SELECT amount, reason FROM Payment WHERE id_user = 1;")
    for p in db.payments_of(ana):
        print(f"     ${p.amount:,.2f}  {p.reason}")

    step("Consulta 2: tipo de membresia de un cliente (2 saltos)")
    print("   Objetos: ana.membership.name")
    print("   SQL:     SELECT m.membership FROM usergym u")
    print("              JOIN user_membership um ON u.id_user = um.id_user")
    print("              JOIN Membership m ON um.id_membership = m.id_membership")
    print("            WHERE u.id_user = 1;   <-- DOS JOINs")
    print(f"     -> {db.membership_name_of(ana)}")

    step("Consulta 3: total pagado por un cliente")
    print("   Objetos: sum(p.amount for p in ana.payments)")
    print("   SQL:     SELECT SUM(amount) FROM Payment WHERE id_user = 1;")
    print(f"     -> ${db.total_paid_by(ana):,.2f}")

    step("Consulta 4: clientes de una sucursal")
    print("   SQL:     SELECT * FROM usergym WHERE location = 'OTAY';")
    for c in db.clients_by_branch("OTAY"):
        print(f"     {c.full_name()}")

    step("Consulta 5: ingreso total del gimnasio (raiz -> clientes -> pagos)")
    print("   SQL:     SELECT SUM(amount) FROM Payment;")
    print(f"     -> ${db.gym_revenue():,.2f}")



# CRUD FUNCIONAL

def s8_crud(db):
    section(8, "CRUD FUNCIONAL (con cascada)")

    step("CREATE: alta de un cliente nuevo")
    plus = db.get_membership(2)
    cid, sergio = db.add_client(
        "Sergio", "Bautista", "Renteria", "6643234502",
        "sergio@gym.com", "PLAYAS", membership=plus,
    )
    db.add_payment(sergio, 650.00, "Inscripcion", "Debit")
    db.commit()
    ok(f"Alta id={cid}: {sergio.description()}")

    step("READ: busqueda por email (recorriendo objetos)")
    encontrado = db.find_client_by_email("sergio@gym.com")
    ok(f"Encontrado: {encontrado.full_name()} ({encontrado.branch})")

    step("UPDATE: cambio de membresia y de telefono")
    economica = db.get_membership(1)
    db.change_membership(sergio, economica)
    sergio.phone = "6649999999"
    db.commit()
    ok(f"Actualizado: {sergio.description()}")
    ok(f"Nuevo telefono: {sergio.phone}")

    step("DELETE: baja del cliente, con efecto en cascada")
    antes_pagos = len(sergio.payments)
    antes_membresias = len(db.memberships)
    resultado = db.delete_client(cid)
    db.commit()
    print(f"   Cliente dado de baja: {resultado['client'].full_name()}")
    print(f"   Pagos eliminados en cascada: {resultado['payments_cascaded']} "
          f"(COMPOSICION: no eran alcanzables sin el cliente)")
    print(f"   Membresias en el catalogo: {antes_membresias} -> "
          f"{len(db.memberships)}  (AGREGACION: sobrevive)")
    print(f"   Busqueda posterior por email: {db.find_client_by_email('sergio@gym.com')}")
    ok("La baja respeto composicion (cascada) y agregacion (sin cascada).")




def extra_note(db):
    section("NOTA TECNICA: colecciones nativas vs persistentes")
    print("   Durus NO detecta cambios dentro de una lista o dict NATIVO")
    print("   de Python guardado en un objeto persistente.")

    ana = db.get_client(1)

    # Se le cuelga a Ana una lista nativa y una persistente.
    ana.nativa = []
    ana.persistente = PersistentList()
    db.commit()

    step("Se agrega un elemento a cada una y se hace commit:")
    ana.nativa.append("rutina-A")        # mutacion NO detectada
    ana.persistente.append("rutina-B")   # mutacion SI detectada
    db.commit()
    print(f"   En memoria -> nativa={list(ana.nativa)}  "
          f"persistente={list(ana.persistente)}")

    step("Se cierra y se reabre la base para ver que sobrevivio:")
    db.close()
    db2 = GymDB(DB_PATH)
    ana2 = db2.get_client(1)
    print(f"   En disco   -> nativa={list(ana2.nativa)}  "
          f"persistente={list(ana2.persistente)}")
    fail("La lista nativa se perdio: Durus no vio el cambio.")
    ok("La PersistentList si se guardo.")

    step("Solucion alternativa: avisar manualmente con _p_note_change()")
    ana2.nativa.append("rutina-C")
    ana2._p_note_change()
    db2.commit()
    db2.close()

    db3 = GymDB(DB_PATH)
    ana3 = db3.get_client(1)
    print(f"   En disco   -> nativa={list(ana3.nativa)}")
    ok("Con _p_note_change() la lista nativa si persistio.")
    return db3


# ----------------------------------------------------------------------
def main():
    print("DEMO - BASE DE DATOS ORIENTADA A OBJETOS DEL GIMNASIO")
    print("Python + Durus")

    reset_database()
    seed()

    db = GymDB(DB_PATH)
    try:
        s1_persistent_classes(db)
        s2_encapsulation(db)
        s3_inheritance(db)
        s4_complex_objects(db)
        s5_reachability(db)
        db = s6_transactions(db)      # devuelve una conexion nueva
        s7_graph_navigation(db)
        s8_crud(db)
        db = extra_note(db)           # devuelve una conexion nueva
    finally:
        db.close()

    print()
    
    print(" fin. Base de datos en:", DB_PATH)
    


if __name__ == "__main__":
    main()
