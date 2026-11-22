"""
FASE 4 - COMPONENTE PRACTICO DE PROGRAMACION
Sistema Integral de Gestion de Clientes, Servicios y Reservas
Empresa: Software FJ

Requisitos implementados:
- Programacion orientada a objetos: abstraccion, herencia, encapsulacion y polimorfismo.
- Clases abstractas Entidad y Servicio.
- Clientes, servicios especializados y reservas.
- Variantes de calculo de costos mediante parametros opcionales y metodos auxiliares.
- Excepciones personalizadas y bloques try/except/else/finally.
- Encadenamiento de excepciones.
- Listas en memoria, sin bases de datos.
- Registro de eventos y errores en software_fj.log.
- Simulacion de mas de diez operaciones.

Ejecucion:
    python software_fj_fase4.py

Nota sobre sobrecarga:
Python no permite la sobrecarga tradicional de metodos por firma como otros
lenguajes. En este proyecto se muestran variantes mediante parametros
opcionales y metodos auxiliares que reutilizan el calculo polimorfico.
"""

from abc import ABC, abstractmethod
from datetime import datetime
import logging


# ============================================================
# 1. CONFIGURACION DE REGISTRO DE EVENTOS Y ERRORES
# ============================================================

logging.basicConfig(
    filename="software_fj.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    encoding="utf-8",
)


def registrar_evento(mensaje):
    """Guarda un evento importante en el archivo de registro."""
    logging.info(mensaje)


def registrar_error(mensaje):
    """Guarda un error controlado en el archivo de registro."""
    logging.error(mensaje)


# ============================================================
# 2. EXCEPCIONES PERSONALIZADAS
# ============================================================

class ErrorSistema(Exception):
    """Clase base para las excepciones propias de Software FJ."""


class DatosInvalidosError(ErrorSistema):
    """Se genera cuando un dato no cumple las validaciones."""


class ServicioNoDisponibleError(ErrorSistema):
    """Se genera cuando se intenta reservar un servicio no disponible."""


class ReservaNoPermitidaError(ErrorSistema):
    """Se genera cuando una accion no corresponde al estado de la reserva."""


class RegistroDuplicadoError(ErrorSistema):
    """Se genera cuando se intenta registrar un identificador repetido."""


# ============================================================
# 3. CLASE ABSTRACTA GENERAL: ENTIDAD
# ============================================================

class Entidad(ABC):
    """Representa cualquier elemento identificable del sistema."""

    def __init__(self, identificador):
        if not isinstance(identificador, str) or not identificador.strip():
            raise DatosInvalidosError("El identificador es obligatorio.")
        self._identificador = identificador.strip()

    @property
    def identificador(self):
        """Devuelve el identificador de solo lectura."""
        return self._identificador

    @abstractmethod
    def mostrar_informacion(self):
        """Obliga a las clases hijas a mostrar su informacion."""
        raise NotImplementedError


# ============================================================
# 4. CLASE CLIENTE: ENCAPSULACION Y VALIDACIONES
# ============================================================

class Cliente(Entidad):
    """Representa un cliente y protege sus datos personales."""

    def __init__(self, identificador, nombre, correo, telefono):
        super().__init__(identificador)

        if not isinstance(nombre, str) or not nombre.strip():
            raise DatosInvalidosError("El nombre del cliente es obligatorio.")
        if not isinstance(correo, str) or "@" not in correo or "." not in correo:
            raise DatosInvalidosError("El correo electronico no tiene un formato valido.")
        if not isinstance(telefono, str) or not telefono.strip():
            raise DatosInvalidosError("El telefono del cliente es obligatorio.")

        self.__nombre = nombre.strip()
        self.__correo = correo.strip()
        self.__telefono = telefono.strip()

    @property
    def nombre(self):
        return self.__nombre

    @property
    def correo(self):
        return self.__correo

    def mostrar_informacion(self):
        return (
            f"ID: {self.identificador} | Nombre: {self.__nombre} | "
            f"Correo: {self.__correo} | Telefono: {self.__telefono}"
        )


# ============================================================
# 5. CLASE ABSTRACTA SERVICIO Y VARIANTES DE COSTO
# ============================================================

class Servicio(Entidad, ABC):
    """Clase base para todos los servicios ofrecidos por la empresa."""

    def __init__(self, identificador, nombre, tarifa, disponible=True):
        super().__init__(identificador)

        if not isinstance(nombre, str) or not nombre.strip():
            raise DatosInvalidosError("El nombre del servicio es obligatorio.")
        if isinstance(tarifa, bool) or not isinstance(tarifa, (int, float)) or tarifa <= 0:
            raise DatosInvalidosError("La tarifa debe ser un numero mayor que cero.")
        if not isinstance(disponible, bool):
            raise DatosInvalidosError("La disponibilidad debe ser True o False.")

        self.nombre = nombre.strip()
        self.tarifa = float(tarifa)
        self.disponible = disponible

    @abstractmethod
    def validar_cantidad(self, cantidad):
        """Cada servicio valida su unidad de cobro."""
        raise NotImplementedError

    @abstractmethod
    def calcular_costo(self, cantidad=1, impuesto=0, descuento=0):
        """
        Calcula el costo. Los parametros opcionales permiten distintas
        variantes de uso: costo normal, con impuesto o con descuento.
        """
        raise NotImplementedError

    def calcular_costo_basico(self, cantidad=1):
        """Variante 1: calcula el costo sin impuesto ni descuento."""
        return self.calcular_costo(cantidad)

    def calcular_costo_con_impuesto(self, cantidad=1, impuesto=19):
        """Variante 2: calcula el costo agregando un porcentaje de impuesto."""
        return self.calcular_costo(cantidad, impuesto=impuesto)

    def calcular_costo_con_descuento(self, cantidad=1, descuento=10):
        """Variante 3: calcula el costo aplicando un porcentaje de descuento."""
        return self.calcular_costo(cantidad, descuento=descuento)

    def calcular_costo_completo(self, cantidad=1, impuesto=19, descuento=10):
        """Variante 4: calcula el costo con impuesto y descuento."""
        return self.calcular_costo(
            cantidad, impuesto=impuesto, descuento=descuento
        )

    def mostrar_informacion(self):
        estado = "Disponible" if self.disponible else "No disponible"
        return (
            f"ID: {self.identificador} | Servicio: {self.nombre} | "
            f"Tarifa: ${self.tarifa:,.2f} | Estado: {estado}"
        )


# ============================================================
# 6. SERVICIOS ESPECIALIZADOS: HERENCIA Y POLIMORFISMO
# ============================================================

class ServicioSala(Servicio):
    """Reserva de salas, cobrada por hora."""

    def validar_cantidad(self, cantidad):
        if isinstance(cantidad, bool) or not isinstance(cantidad, (int, float)) or cantidad <= 0:
            raise DatosInvalidosError("Las horas de sala deben ser mayores que cero.")

    def calcular_costo(self, cantidad=1, impuesto=0, descuento=0):
        self.validar_cantidad(cantidad)
        validar_porcentajes(impuesto, descuento)
        subtotal = self.tarifa * cantidad
        return subtotal + subtotal * impuesto / 100 - subtotal * descuento / 100


class ServicioEquipo(Servicio):
    """Alquiler de equipos, cobrado por dia."""

    def validar_cantidad(self, cantidad):
        if isinstance(cantidad, bool) or not isinstance(cantidad, int) or cantidad <= 0:
            raise DatosInvalidosError("Los dias de alquiler deben ser un entero positivo.")

    def calcular_costo(self, cantidad=1, impuesto=0, descuento=0):
        self.validar_cantidad(cantidad)
        validar_porcentajes(impuesto, descuento)
        subtotal = self.tarifa * cantidad
        return subtotal + subtotal * impuesto / 100 - subtotal * descuento / 100


class ServicioAsesoria(Servicio):
    """Asesorias especializadas, cobradas por sesion."""

    def validar_cantidad(self, cantidad):
        if isinstance(cantidad, bool) or not isinstance(cantidad, int) or cantidad <= 0:
            raise DatosInvalidosError("Las sesiones deben ser un entero positivo.")

    def calcular_costo(self, cantidad=1, impuesto=0, descuento=0):
        self.validar_cantidad(cantidad)
        validar_porcentajes(impuesto, descuento)
        subtotal = self.tarifa * cantidad
        return subtotal + subtotal * impuesto / 100 - subtotal * descuento / 100


def validar_porcentajes(impuesto, descuento):
    """Valida que impuesto y descuento sean porcentajes entre 0 y 100."""
    for nombre, valor in (("impuesto", impuesto), ("descuento", descuento)):
        if isinstance(valor, bool) or not isinstance(valor, (int, float)):
            raise DatosInvalidosError(f"El {nombre} debe ser numerico.")
        if valor < 0 or valor > 100:
            raise DatosInvalidosError(f"El {nombre} debe estar entre 0 y 100.")


# ============================================================
# 7. CLASE RESERVA
# ============================================================

class Reserva(Entidad):
    """Relaciona cliente y servicio, y administra el estado de la reserva."""

    ESTADOS_VALIDOS = ("Pendiente", "Confirmada", "Cancelada", "Procesada")

    def __init__(self, identificador, cliente, servicio, duracion):
        super().__init__(identificador)

        if not isinstance(cliente, Cliente):
            raise DatosInvalidosError("La reserva requiere un cliente registrado.")
        if not isinstance(servicio, Servicio):
            raise DatosInvalidosError("La reserva requiere un servicio valido.")

        servicio.validar_cantidad(duracion)
        self.cliente = cliente
        self.servicio = servicio
        self.duracion = duracion
        self.estado = "Pendiente"
        self.fecha_creacion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        registrar_evento(f"Reserva {self.identificador} creada.")

    def confirmar(self):
        if not self.servicio.disponible:
            raise ServicioNoDisponibleError(
                f"El servicio '{self.servicio.nombre}' no esta disponible."
            )
        if self.estado != "Pendiente":
            raise ReservaNoPermitidaError(
                "Solo se puede confirmar una reserva pendiente."
            )
        self.estado = "Confirmada"
        registrar_evento(f"Reserva {self.identificador} confirmada.")
        return "Reserva confirmada correctamente."

    def cancelar(self):
        if self.estado in ("Cancelada", "Procesada"):
            raise ReservaNoPermitidaError(
                f"No se puede cancelar una reserva en estado {self.estado}."
            )
        self.estado = "Cancelada"
        registrar_evento(f"Reserva {self.identificador} cancelada.")
        return "Reserva cancelada correctamente."

    def procesar(self, impuesto=0, descuento=0):
        if self.estado != "Confirmada":
            raise ReservaNoPermitidaError(
                "La reserva debe estar confirmada antes de procesarse."
            )
        if not self.servicio.disponible:
            raise ServicioNoDisponibleError("El servicio ya no esta disponible.")

        total = self.servicio.calcular_costo(
            self.duracion, impuesto=impuesto, descuento=descuento
        )
        self.estado = "Procesada"
        registrar_evento(
            f"Reserva {self.identificador} procesada. Total: {total:.2f}"
        )
        return total

    def mostrar_informacion(self):
        return (
            f"Reserva: {self.identificador} | Cliente: {self.cliente.nombre} | "
            f"Servicio: {self.servicio.nombre} | Cantidad: {self.duracion} | "
            f"Estado: {self.estado} | Fecha: {self.fecha_creacion}"
        )


# ============================================================
# 8. SISTEMA PRINCIPAL: ADMINISTRACION MEDIANTE LISTAS
# ============================================================

class SistemaSoftwareFJ:
    """Administra clientes, servicios y reservas sin usar bases de datos."""

    def __init__(self):
        self.clientes = []
        self.servicios = []
        self.reservas = []

    def registrar_cliente(self, cliente):
        if not isinstance(cliente, Cliente):
            raise DatosInvalidosError("El elemento no es un cliente.")
        if any(item.identificador == cliente.identificador for item in self.clientes):
            raise RegistroDuplicadoError("Ya existe un cliente con ese identificador.")
        self.clientes.append(cliente)
        registrar_evento(f"Cliente {cliente.identificador} registrado.")
        return cliente

    def registrar_servicio(self, servicio):
        if not isinstance(servicio, Servicio):
            raise DatosInvalidosError("El elemento no es un servicio.")
        if any(item.identificador == servicio.identificador for item in self.servicios):
            raise RegistroDuplicadoError("Ya existe un servicio con ese identificador.")
        self.servicios.append(servicio)
        registrar_evento(f"Servicio {servicio.identificador} registrado.")
        return servicio

    def crear_reserva(self, reserva):
        if not isinstance(reserva, Reserva):
            raise DatosInvalidosError("El elemento no es una reserva.")
        if any(item.identificador == reserva.identificador for item in self.reservas):
            raise RegistroDuplicadoError("Ya existe una reserva con ese identificador.")
        if not any(c.identificador == reserva.cliente.identificador for c in self.clientes):
            raise DatosInvalidosError("El cliente no esta registrado en el sistema.")
        if not any(s.identificador == reserva.servicio.identificador for s in self.servicios):
            raise DatosInvalidosError("El servicio no esta registrado en el sistema.")
        self.reservas.append(reserva)
        registrar_evento(f"Reserva {reserva.identificador} agregada al sistema.")
        return reserva

    def mostrar_lista(self, titulo, elementos):
        print(f"\n{titulo}")
        if not elementos:
            print("No hay registros.")
            return
        for elemento in elementos:
            print(elemento.mostrar_informacion())


# ============================================================
# 9. EJECUCION SEGURA DE OPERACIONES Y MANEJO DE EXCEPCIONES
# ============================================================

def ejecutar_operacion(numero, descripcion, funcion):
    """
    Ejecuta cada prueba por separado para evitar que un error detenga
    las demas operaciones. Incluye except, else y finally.
    """
    print(f"\nOPERACION {numero}: {descripcion}")
    try:
        resultado = funcion()
    except ErrorSistema as error:
        print(f"Error controlado: {error}")
        registrar_error(f"Operacion {numero} - {descripcion}: {error}")
    except Exception as error_original:
        # Encadenamiento: la excepcion propia conserva la causa original.
        try:
            raise ErrorSistema(
                "Se produjo un error inesperado al ejecutar la operacion."
            ) from error_original
        except ErrorSistema as error_encadenado:
            print(f"Error inesperado controlado: {error_encadenado}")
            logging.exception(
                "Operacion %s - %s. Causa original: %s",
                numero, descripcion, error_original
            )
    else:
        print(f"Resultado: {resultado}")
        registrar_evento(f"Operacion {numero} completada: {descripcion}")
    finally:
        print("Fin de la operacion.")


# ============================================================
# 10. PRUEBAS: 15 OPERACIONES COMPLETAS
# ============================================================

def main():
    """Crea datos de prueba y ejecuta las operaciones solicitadas."""
    sistema = SistemaSoftwareFJ()

    print("=" * 72)
    print("SISTEMA INTEGRAL DE GESTION DE CLIENTES, SERVICIOS Y RESERVAS")
    print("                         SOFTWARE FJ")
    print("=" * 72)

    # Operacion 1: registrar cliente valido.
    def op1():
        cliente = Cliente("C001", "Laura Martinez", "laura@gmail.com", "3001234567")
        sistema.registrar_cliente(cliente)
        return cliente.mostrar_informacion()
    ejecutar_operacion(1, "Registrar un cliente valido", op1)

    # Operacion 2: registrar un segundo cliente valido.
    def op2():
        cliente = Cliente("C002", "Carlos Perez", "carlos@gmail.com", "3019876543")
        sistema.registrar_cliente(cliente)
        return cliente.mostrar_informacion()
    ejecutar_operacion(2, "Registrar un segundo cliente valido", op2)

    # Operacion 3: intentar registrar cliente con correo invalido.
    def op3():
        cliente = Cliente("C003", "Ana Lopez", "correo_invalido", "3021112233")
        sistema.registrar_cliente(cliente)
        return cliente.mostrar_informacion()
    ejecutar_operacion(3, "Intentar registrar cliente con correo invalido", op3)

    # Operacion 4: intentar registrar un identificador duplicado.
    def op4():
        cliente = Cliente("C001", "Otro Nombre", "otro@gmail.com", "3000000000")
        sistema.registrar_cliente(cliente)
        return "Registro duplicado aceptado."
    ejecutar_operacion(4, "Intentar registrar un cliente duplicado", op4)

    # Operacion 5: crear servicio de sala.
    def op5():
        servicio = ServicioSala("S001", "Reserva de sala de reuniones", 50000)
        sistema.registrar_servicio(servicio)
        return servicio.mostrar_informacion()
    ejecutar_operacion(5, "Crear servicio de reserva de salas", op5)

    # Operacion 6: crear servicio de alquiler de equipos.
    def op6():
        servicio = ServicioEquipo("S002", "Alquiler de computador", 35000)
        sistema.registrar_servicio(servicio)
        return servicio.mostrar_informacion()
    ejecutar_operacion(6, "Crear servicio de alquiler de equipos", op6)

    # Operacion 7: crear servicio de asesoria.
    def op7():
        servicio = ServicioAsesoria("S003", "Asesoria de programacion", 80000)
        sistema.registrar_servicio(servicio)
        return servicio.mostrar_informacion()
    ejecutar_operacion(7, "Crear servicio de asesoria especializada", op7)

    # Operacion 8: intentar crear servicio con tarifa incorrecta.
    def op8():
        servicio = ServicioSala("S004", "Sala con tarifa invalida", -1000)
        sistema.registrar_servicio(servicio)
        return servicio.mostrar_informacion()
    ejecutar_operacion(8, "Intentar crear servicio con tarifa negativa", op8)

    # Operacion 9: demostrar variantes de calculo de costos.
    def op9():
        sala = sistema.servicios[0]
        basico = sala.calcular_costo_basico(2)
        con_impuesto = sala.calcular_costo_con_impuesto(2, 19)
        con_descuento = sala.calcular_costo_con_descuento(2, 10)
        completo = sala.calcular_costo_completo(2, 19, 10)
        return (
            f"Basico: ${basico:,.2f} | Con impuesto: ${con_impuesto:,.2f} | "
            f"Con descuento: ${con_descuento:,.2f} | "
            f"Impuesto y descuento: ${completo:,.2f}"
        )
    ejecutar_operacion(9, "Probar las variantes del calculo de costos", op9)

    # Operacion 10: crear una reserva valida.
    def op10():
        reserva = Reserva("R001", sistema.clientes[0], sistema.servicios[0], 2)
        sistema.crear_reserva(reserva)
        return reserva.mostrar_informacion()
    ejecutar_operacion(10, "Crear una reserva valida", op10)

    # Operacion 11: confirmar reserva.
    def op11():
        return sistema.reservas[0].confirmar()
    ejecutar_operacion(11, "Confirmar la reserva R001", op11)

    # Operacion 12: procesar reserva con impuesto.
    def op12():
        total = sistema.reservas[0].procesar(impuesto=19)
        return f"Reserva procesada. Total con impuesto: ${total:,.2f}"
    ejecutar_operacion(12, "Procesar reserva y calcular costo con impuesto", op12)

    # Operacion 13: intentar procesar una reserva que sigue pendiente.
    def op13():
        reserva = Reserva("R002", sistema.clientes[1], sistema.servicios[1], 3)
        sistema.crear_reserva(reserva)
        return reserva.procesar()
    ejecutar_operacion(13, "Intentar procesar una reserva sin confirmar", op13)

    # Operacion 14: intentar reservar un servicio no disponible.
    def op14():
        servicio = sistema.servicios[2]
        servicio.disponible = False
        reserva = Reserva("R003", sistema.clientes[0], servicio, 1)
        sistema.crear_reserva(reserva)
        return reserva.confirmar()
    ejecutar_operacion(14, "Intentar confirmar reserva de servicio no disponible", op14)

    # Operacion 15: cancelar una reserva pendiente correctamente.
    def op15():
        reserva = sistema.reservas[1]
        return reserva.cancelar()
    ejecutar_operacion(15, "Cancelar la reserva pendiente R002", op15)

    # Resumen final: muestra las listas que administra el sistema.
    print("\n" + "=" * 72)
    print("RESUMEN FINAL DEL SISTEMA")
    print("=" * 72)
    sistema.mostrar_lista("CLIENTES REGISTRADOS", sistema.clientes)
    sistema.mostrar_lista("SERVICIOS REGISTRADOS", sistema.servicios)
    sistema.mostrar_lista("RESERVAS REGISTRADAS", sistema.reservas)

    print("\nLas pruebas finalizaron. Revise el archivo software_fj.log.")
    print("El programa no utiliza bases de datos; usa listas y objetos en memoria.")


if __name__ == "__main__":
    main()
