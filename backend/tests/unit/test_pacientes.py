"""
test_pacientes.py
=================
Pruebas unitarias de dominio (TDD) para el Bounded Context: Gestión de Pacientes.
Sin base de datos ni dependencias externas.
"""

from datetime import date
import pytest
from app.domain.pacientes.value_objects import (
    DNI,
    Email,
    EstadoPaciente,
    NombreCompleto,
    Sexo,
    Telefono,
)
from app.domain.pacientes.entities import Paciente
from app.domain.pacientes.events import (
    PacienteActualizado,
    PacienteDesactivado,
    PacienteRegistrado,
)
from app.domain.shared.domain_exception import DomainException


# ============================================================================
# Value Object: DNI
# ============================================================================

def test_dni_valido():
    dni = DNI("75415745")
    assert dni.value == "75415745"


@pytest.mark.parametrize("valor_invalido", ["", "   ", None])
def test_dni_vacio_lanza_excepcion(valor_invalido):
    with pytest.raises(ValueError, match="El DNI no puede estar vacío."):
        DNI(valor_invalido)


def test_dni_con_letras_lanza_excepcion():
    with pytest.raises(ValueError, match="El DNI debe contener solo dígitos."):
        DNI("7541A745")


def test_dni_supera_8_digitos_lanza_excepcion():
    with pytest.raises(ValueError, match="El DNI no puede superar 8 dígitos."):
        DNI("123456789")


# ============================================================================
# Value Object: Telefono
# ============================================================================

def test_telefono_celular_peruano_valido():
    t = Telefono("964235456")
    assert t.value == "964235456"


def test_telefono_internacional_valido():
    t = Telefono("+51964235456")
    assert t.value == "+51964235456"


@pytest.mark.parametrize("valor_invalido", ["", "   ", None])
def test_telefono_vacio_lanza_excepcion(valor_invalido):
    with pytest.raises(ValueError, match="El teléfono no puede estar vacío."):
        Telefono(valor_invalido)


@pytest.mark.parametrize("formato_invalido", ["12345", "888888888", "abcdefghi", "9642354567890"])
def test_telefono_formato_invalido_lanza_excepcion(formato_invalido):
    with pytest.raises(ValueError, match="Formato de teléfono inválido."):
        Telefono(formato_invalido)


# ============================================================================
# Value Object: Email
# ============================================================================

def test_email_valido():
    e = Email("guisan23@gmail.com")
    assert e.value == "guisan23@gmail.com"


def test_email_con_punto_en_nombre_valido():
    e = Email("guillermo.sanchez@clinica.pe")
    assert e.value == "guillermo.sanchez@clinica.pe"


@pytest.mark.parametrize("valor_invalido", ["", "   ", None])
def test_email_vacio_lanza_excepcion(valor_invalido):
    with pytest.raises(ValueError, match="El correo no puede estar vacío."):
        Email(valor_invalido)


@pytest.mark.parametrize("correo_invalido", ["sin-arroba", "guisan@", "@gmail.com", "guisan@com"])
def test_email_formato_invalido_lanza_excepcion(correo_invalido):
    with pytest.raises(ValueError, match="Correo inválido"):
        Email(correo_invalido)


# ============================================================================
# Value Object: Sexo
# ============================================================================

@pytest.mark.parametrize("valor", ["M", "F", "OTRO"])
def test_sexo_canonico_valido(valor):
    s = Sexo(valor)
    assert s.value == valor


def test_sexo_normaliza_masculino():
    s = Sexo("MASCULINO")
    assert s.value == "M"


def test_sexo_normaliza_femenino():
    s = Sexo("FEMENINO")
    assert s.value == "F"


def test_sexo_invalido_lanza_excepcion():
    with pytest.raises(ValueError, match="Sexo inválido"):
        Sexo("X")


# ============================================================================
# Value Object: NombreCompleto
# ============================================================================

def test_nombre_completo_valido():
    nc = NombreCompleto(nombres="Guillermo", apellidos="Sánchez")
    assert nc.completo() == "Guillermo Sánchez"


def test_nombres_vacios_lanza_excepcion():
    with pytest.raises(ValueError, match="Los nombres no pueden estar vacíos."):
        NombreCompleto(nombres="", apellidos="Sánchez")


def test_apellidos_vacios_lanza_excepcion():
    with pytest.raises(ValueError, match="Los apellidos no pueden estar vacíos."):
        NombreCompleto(nombres="Guillermo", apellidos="")


# ============================================================================
# Entity / Aggregate Root: Paciente
# ============================================================================

def test_registrar_paciente_exitoso():
    p = Paciente.registrar(
        dni=DNI("75415745"),
        nombre=NombreCompleto("Guillermo", "Sánchez"),
        fecha_nacimiento=date(1995, 5, 20),
        sexo=Sexo("M"),
        telefono=Telefono("964235456"),
        email=Email("guisan23@gmail.com"),
    )
    assert p.id is not None
    assert p.estado.es_activo() is True
    assert p.puede_recibir_nuevo_estudio() is True
    assert len(p.events) == 1
    assert isinstance(p.events[0], PacienteRegistrado)
    assert p.events[0].dni == "75415745"


def test_desactivar_paciente_activo():
    p = Paciente.registrar(
        dni=DNI("75415745"),
        nombre=NombreCompleto("Guillermo", "Sánchez"),
        fecha_nacimiento=date(1995, 5, 20),
        sexo=Sexo("M"),
        telefono=Telefono("964235456"),
        email=Email("guisan23@gmail.com"),
    )
    p.clear_events()
    p.desactivar()

    assert p.estado.es_activo() is False
    assert p.puede_recibir_nuevo_estudio() is False
    assert len(p.events) == 1
    assert isinstance(p.events[0], PacienteDesactivado)


def test_email_supera_150_caracteres_lanza_excepcion():
    email_largo = "a" * 145 + "@gmail.com"
    with pytest.raises(ValueError, match="El correo no puede superar los 150 caracteres"):
        Email(email_largo)


def test_estado_paciente_invalido_lanza_excepcion():
    with pytest.raises(ValueError, match="Estado inválido"):
        EstadoPaciente("SUSPENDIDO")


def test_estado_paciente_metodos():
    activo = EstadoPaciente("ACTIVO")
    inactivo = EstadoPaciente("INACTIVO")
    assert activo.es_activo() is True
    assert inactivo.es_activo() is False


def test_actualizar_contacto_exitoso():
    p = Paciente.registrar(
        dni=DNI("75415745"),
        nombre=NombreCompleto("Guillermo", "Sánchez"),
        fecha_nacimiento=date(1995, 5, 20),
        sexo=Sexo("M"),
        telefono=Telefono("964235456"),
        email=Email("guisan23@gmail.com"),
    )
    p.clear_events()
    nuevo_tel = Telefono("+51999888777")
    nuevo_email = Email("nuevo_guillermo@clinica.pe")
    p.actualizar_contacto(telefono=nuevo_tel, email=nuevo_email)

    assert p.telefono == nuevo_tel
    assert p.email == nuevo_email
    assert len(p.events) == 1
    assert isinstance(p.events[0], PacienteActualizado)
    assert p.events[0].campos_actualizados == ["telefono", "email"]


def test_actualizar_contacto_paciente_inactivo_lanza_excepcion():
    p = Paciente.registrar(
        dni=DNI("75415745"),
        nombre=NombreCompleto("Guillermo", "Sánchez"),
        fecha_nacimiento=date(1995, 5, 20),
        sexo=Sexo("M"),
        telefono=Telefono("964235456"),
        email=Email("guisan23@gmail.com"),
    )
    p.desactivar()

    with pytest.raises(DomainException, match="No se puede actualizar un paciente inactivo."):
        p.actualizar_contacto(
            telefono=Telefono("+51999888777"),
            email=Email("nuevo@clinica.pe"),
        )


def test_desactivar_paciente_ya_inactivo_lanza_excepcion():
    p = Paciente.registrar(
        dni=DNI("75415745"),
        nombre=NombreCompleto("Guillermo", "Sánchez"),
        fecha_nacimiento=date(1995, 5, 20),
        sexo=Sexo("M"),
        telefono=Telefono("964235456"),
        email=Email("guisan23@gmail.com"),
    )
    p.desactivar()

    with pytest.raises(DomainException, match="El paciente ya se encuentra inactivo."):
        p.desactivar()


