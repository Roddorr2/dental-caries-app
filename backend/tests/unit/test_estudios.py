"""
test_estudios.py
================
Pruebas unitarias de dominio (TDD) para el Bounded Context: Adquisición Imagenológica.
Sin base de datos ni dependencias externas.
"""

from uuid import uuid4
import pytest

from app.domain.estudios.value_objects import (
    CalidadImagen,
    EstadoProcesamiento,
    FormatoImagen,
    HashSHA256,
    RutaAlmacenamiento,
    TipoExamen,
    TipoVista,
)
from app.domain.estudios.entites import EstudioImagenologico, ImagenIntraoral
from app.domain.estudios.events import (
    AnalisisIASolicitado,
    EstudioCreado,
    EstudioProcesado,
    ImagenAgregada,
)
from app.domain.shared.domain_exception import DomainException


# ============================================================================
# Value Object: FormatoImagen
# ============================================================================

@pytest.mark.parametrize("fmt", ["jpg", "jpeg", "png", "JPG", "JPEG", "PNG"])
def test_formato_imagen_optico_valido(fmt):
    f = FormatoImagen(fmt)
    assert f.value == fmt


@pytest.mark.parametrize("fmt_invalido", ["dcm", "dicom", "pdf", "gif", "bmp"])
def test_formato_imagen_rechaza_no_opticos(fmt_invalido):
    with pytest.raises(ValueError, match="Formato inválido"):
        FormatoImagen(fmt_invalido)


# ============================================================================
# Value Object: HashSHA256
# ============================================================================

def test_hash_sha256_valido():
    h = HashSHA256("fd689600b53526bc21db1bdfd7c656e5b7413a183644a4ea1c68052fb1d46dca")
    assert h.value == "fd689600b53526bc21db1bdfd7c656e5b7413a183644a4ea1c68052fb1d46dca"


@pytest.mark.parametrize("hash_invalido", [
    "fd689600b53526bc21db1bdfd7c656e5b7413a183644a4ea1c68052fb1d46dc",  # 63 chars
    "fd689600b53526bc21db1bdfd7c656e5b7413a183644a4ea1c68052fb1d46dcaa",  # 65 chars
    "zzzz9600b53526bc21db1bdfd7c656e5b7413a183644a4ea1c68052fb1d46dca",  # non-hex
])
def test_hash_sha256_invalido_lanza_excepcion(hash_invalido):
    with pytest.raises(ValueError, match="hash SHA-256"):
        HashSHA256(hash_invalido)


# ============================================================================
# Value Object: CalidadImagen
# ============================================================================

def test_calidad_imagen_valida():
    c = CalidadImagen(suficiente=True, nitidez=0.92, iluminacion=0.88)
    assert c.suficiente is True
    assert c.nitidez == 0.92
    assert c.iluminacion == 0.88


@pytest.mark.parametrize("nitidez_invalida", [-0.1, 1.05, 2.0])
def test_calidad_nitidez_fuera_de_rango(nitidez_invalida):
    with pytest.raises(ValueError, match="La nitidez debe estar entre 0.0 y 1.0"):
        CalidadImagen(suficiente=True, nitidez=nitidez_invalida, iluminacion=0.8)


@pytest.mark.parametrize("iluminacion_invalida", [-0.5, 1.5])
def test_calidad_iluminacion_fuera_de_rango(iluminacion_invalida):
    with pytest.raises(ValueError, match="La iluminación debe estar entre 0.0 y 1.0"):
        CalidadImagen(suficiente=True, nitidez=0.8, iluminacion=iluminacion_invalida)


# ============================================================================
# Value Object: RutaAlmacenamiento
# ============================================================================

def test_ruta_almacenamiento_valida():
    r = RutaAlmacenamiento("/storage/estudios/molar_1.jpg")
    assert r.value == "/storage/estudios/molar_1.jpg"


@pytest.mark.parametrize("ruta_vacia", ["", "   "])
def test_ruta_vacia_lanza_excepcion(ruta_vacia):
    with pytest.raises(ValueError, match="La ruta de almacenamiento no puede estar vacía."):
        RutaAlmacenamiento(ruta_vacia)


def test_ruta_supera_500_caracteres_lanza_excepcion():
    with pytest.raises(ValueError, match="La ruta no puede superar 500 caracteres."):
        RutaAlmacenamiento("a" * 501)


# ============================================================================
# Entity / Aggregate Root: EstudioImagenologico
# ============================================================================

def _crear_imagen_valida(estudio_id, nombre="test.jpg", suficiente=True):
    return ImagenIntraoral(
        id=uuid4(),
        estudio_id=estudio_id,
        tipo_vista=TipoVista("OCLUSAL_MANDIBULAR"),
        ruta_almacenamiento=RutaAlmacenamiento(f"/storage/estudios/{nombre}"),
        nombre_archivo=nombre,
        formato=FormatoImagen("jpg"),
        calidad=CalidadImagen(suficiente=suficiente, nitidez=0.9, iluminacion=0.85),
        hash_sha256=HashSHA256("a" * 64),
    )


def test_crear_estudio_exitoso():
    paciente_id = uuid4()
    estudio = EstudioImagenologico.crear(
        paciente_id=paciente_id,
        tipo_examen=TipoExamen("OCLUSAL_MANDIBULAR"),
    )
    assert estudio.id is not None
    assert estudio.estado_procesamiento.es_pendiente() is True
    assert len(estudio.imagenes) == 0
    assert estudio.puede_ser_analizado() is False
    assert len(estudio.events) == 1
    assert isinstance(estudio.events[0], EstudioCreado)


def test_agregar_imagen_estudio_exitoso():
    estudio = EstudioImagenologico.crear(
        paciente_id=uuid4(),
        tipo_examen=TipoExamen("OCLUSAL_MANDIBULAR"),
    )
    estudio.clear_events()
    img = _crear_imagen_valida(estudio.id)
    estudio.agregar_imagen(img)

    assert len(estudio.imagenes) == 1
    assert estudio.puede_ser_analizado() is True
    assert len(estudio.events) == 1
    assert isinstance(estudio.events[0], ImagenAgregada)


def test_agregar_imagen_sin_calidad_suficiente_falla():
    estudio = EstudioImagenologico.crear(
        paciente_id=uuid4(),
        tipo_examen=TipoExamen("OCLUSAL_MANDIBULAR"),
    )
    img_baja_calidad = _crear_imagen_valida(estudio.id, suficiente=False)

    with pytest.raises(DomainException, match="no tiene calidad suficiente"):
        estudio.agregar_imagen(img_baja_calidad)


def test_limite_maximo_10_imagenes_por_estudio():
    estudio = EstudioImagenologico.crear(
        paciente_id=uuid4(),
        tipo_examen=TipoExamen("SERIE_COMPLETA"),
    )
    for i in range(10):
        img = _crear_imagen_valida(estudio.id, nombre=f"foto_{i}.jpg")
        estudio.agregar_imagen(img)

    assert len(estudio.imagenes) == 10

    # Intento de agregar la imagen número 11
    img_11 = _crear_imagen_valida(estudio.id, nombre="foto_11.jpg")
    with pytest.raises(DomainException, match="máximo de 10 imágenes"):
        estudio.agregar_imagen(img_11)


def test_no_se_pueden_agregar_imagenes_a_estudio_en_analisis():
    estudio = EstudioImagenologico.crear(
        paciente_id=uuid4(),
        tipo_examen=TipoExamen("OCLUSAL_MANDIBULAR"),
    )
    img = _crear_imagen_valida(estudio.id)
    estudio.agregar_imagen(img)
    estudio.iniciar_analisis()

    img2 = _crear_imagen_valida(estudio.id, nombre="foto_2.jpg")
    with pytest.raises(DomainException, match="No se pueden agregar imágenes a un estudio en análisis"):
        estudio.agregar_imagen(img2)


def test_tipo_examen_invalido_lanza_excepcion():
    with pytest.raises(ValueError, match="Tipo de examen inválido"):
        TipoExamen("TOMOGRAFIA_CONE_BEAM")


def test_tipo_vista_invalida_lanza_excepcion():
    with pytest.raises(ValueError, match="Tipo de vista inválida"):
        TipoVista("PANORAMICA")


def test_estado_procesamiento_invalido_lanza_excepcion():
    with pytest.raises(ValueError, match="Estado inválido"):
        EstadoProcesamiento("CANCELADO")


def test_iniciar_analisis_sin_imagenes_lanza_excepcion():
    estudio = EstudioImagenologico.crear(
        paciente_id=uuid4(),
        tipo_examen=TipoExamen("OCLUSAL_MANDIBULAR"),
    )
    with pytest.raises(DomainException, match="El estudio no puede iniciar análisis"):
        estudio.iniciar_analisis()


def test_ciclo_completo_estudio_analisis_a_procesado():
    paciente_id = uuid4()
    estudio = EstudioImagenologico.crear(
        paciente_id=paciente_id,
        tipo_examen=TipoExamen("SERIE_COMPLETA"),
    )
    img = _crear_imagen_valida(estudio.id)
    estudio.agregar_imagen(img)
    estudio.clear_events()

    # PENDIENTE -> EN_ANALISIS
    estudio.iniciar_analisis()
    assert estudio.estado_procesamiento.es_en_analisis() is True
    assert len(estudio.events) == 1
    assert isinstance(estudio.events[0], AnalisisIASolicitado)
    assert estudio.events[0].total_imagenes == 1

    # EN_ANALISIS -> PROCESADO
    estudio.clear_events()
    estudio.marcar_como_procesado()
    assert estudio.estado_procesamiento.es_procesado() is True
    assert len(estudio.events) == 1
    assert isinstance(estudio.events[0], EstudioProcesado)
    assert estudio.events[0].paciente_id == paciente_id

    # No se pueden agregar imágenes a un estudio ya procesado
    img_extra = _crear_imagen_valida(estudio.id, nombre="extra.jpg")
    with pytest.raises(DomainException, match="No se pueden agregar imágenes a un estudio ya procesado"):
        estudio.agregar_imagen(img_extra)


def test_marcar_como_procesado_estudio_pendiente_lanza_excepcion():
    estudio = EstudioImagenologico.crear(
        paciente_id=uuid4(),
        tipo_examen=TipoExamen("OCLUSAL_MANDIBULAR"),
    )
    with pytest.raises(DomainException, match="Solo estudios en EN_ANALISIS pueden marcarse como procesados"):
        estudio.marcar_como_procesado()

