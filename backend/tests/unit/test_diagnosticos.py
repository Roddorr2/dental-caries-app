"""
test_diagnosticos.py
====================
Pruebas unitarias de dominio (TDD) para el Bounded Context: Diagnóstico Asistido por IA.
Sin base de datos ni dependencias externas.
"""

from uuid import uuid4
import pytest

from app.domain.diagnosticos.value_objects import (
    EstadoDiagnostico,
    Hallazgo,
    NivelConfianza,
    RegionDental,
    RegistroModeloML,
    Severidad,
    TipoPatologia,
)
from app.domain.diagnosticos.entities import Diagnostico, Odontologo
from app.domain.diagnosticos.events import (
    DiagnosticoEnRevision,
    DiagnosticoRechazado,
    DiagnosticoSugeridoPorIA,
    DiagnosticoValidado,
    SegundaOpinionSolicitada,
)
from app.domain.shared.domain_exception import DomainException


# ============================================================================
# Value Object: EstadoDiagnostico
# ============================================================================

@pytest.mark.parametrize("estado", ["SUGERIDO_IA", "EN_REVISION", "VALIDADO", "RECHAZADO"])
def test_estado_diagnostico_valido(estado):
    ed = EstadoDiagnostico(estado)
    assert ed.value == estado


def test_estado_diagnostico_invalido():
    with pytest.raises(ValueError, match="Estado inválido"):
        EstadoDiagnostico("EN_PROCESO")


def test_estado_transiciones_permitidas():
    assert EstadoDiagnostico("SUGERIDO_IA").puede_validarse() is True
    assert EstadoDiagnostico("EN_REVISION").puede_validarse() is True
    assert EstadoDiagnostico("VALIDADO").puede_validarse() is False
    assert EstadoDiagnostico("RECHAZADO").puede_validarse() is False


# ============================================================================
# Value Object: RegistroModeloML (Regla F1 >= 0.85)
# ============================================================================

def test_modelo_aprobado_produccion_f1_mayor_igual_085():
    m = RegistroModeloML(
        modelo_ml_id=uuid4(),
        nombre_modelo="yolov8n-dental",
        version="1.0.0",
        f1_score=0.88,
    )
    assert m.es_aprobado_para_produccion() is True


def test_modelo_no_aprobado_produccion_f1_menor_085():
    m = RegistroModeloML(
        modelo_ml_id=uuid4(),
        nombre_modelo="yolov8n-experimental",
        version="0.1.0",
        f1_score=0.82,
    )
    assert m.es_aprobado_para_produccion() is False


@pytest.mark.parametrize("f1_invalido", [-0.1, 1.2])
def test_f1_score_fuera_de_rango_lanza_excepcion(f1_invalido):
    with pytest.raises(ValueError, match="F1-Score inválido"):
        RegistroModeloML(
            modelo_ml_id=uuid4(),
            nombre_modelo="yolo",
            version="1.0",
            f1_score=f1_invalido,
        )


# ============================================================================
# Value Object: NivelConfianza
# ============================================================================

def test_nivel_confianza_clasificacion():
    assert NivelConfianza.desde_valor(0.40).categoria == "BAJA"
    assert NivelConfianza.desde_valor(0.40).requiere_revision_prioritaria() is True

    assert NivelConfianza.desde_valor(0.70).categoria == "MEDIA"
    assert NivelConfianza.desde_valor(0.70).requiere_revision_prioritaria() is False

    assert NivelConfianza.desde_valor(0.92).categoria == "ALTA"
    assert NivelConfianza.desde_valor(0.92).requiere_revision_prioritaria() is False


# ============================================================================
# Value Object: RegionDental (Notación FDI y Bounding Box)
# ============================================================================

@pytest.mark.parametrize("diente_permanente", [11, 16, 21, 36, 48])
def test_region_dental_diente_permanente_valido(diente_permanente):
    r = RegionDental(diente_numero=diente_permanente, cuadrante=diente_permanente // 10)
    assert r.diente_numero == diente_permanente


@pytest.mark.parametrize("diente_deciduo", [51, 55, 61, 74, 85])
def test_region_dental_diente_deciduo_pediatrico_valido(diente_deciduo):
    """
    TDD Test: Verifica que los dientes deciduos/primarios (notación FDI 51-85)
    y cuadrantes pediátricos (5-8) sean válidos según RF-04.
    """
    r = RegionDental(diente_numero=diente_deciduo, cuadrante=diente_deciduo // 10)
    assert r.diente_numero == diente_deciduo


@pytest.mark.parametrize("diente_invalido", [99, 10, -1, 19, 56, 0])
def test_region_dental_diente_invalido_lanza_excepcion(diente_invalido):
    with pytest.raises(ValueError, match="Número de diente inválido"):
        RegionDental(diente_numero=diente_invalido)


@pytest.mark.parametrize("cuadrante_invalido", [0, 9, -1])
def test_region_dental_cuadrante_invalido_lanza_excepcion(cuadrante_invalido):
    with pytest.raises(ValueError, match="Cuadrante inválido"):
        RegionDental(cuadrante=cuadrante_invalido)


def test_region_dental_bounding_box():
    r = RegionDental(bbox_x=0.15, bbox_y=0.20, bbox_width=0.30, bbox_height=0.25)
    assert r.tiene_bbox() is True


# ============================================================================
# Entity / Aggregate Root: Diagnostico
# ============================================================================

def _crear_hallazgo_mock():
    return Hallazgo(
        imagen_id=uuid4(),
        tipo_patologia=TipoPatologia("CARIES"),
        severidad=Severidad("MODERADA"),
        confianza=0.88,
        region=RegionDental(diente_numero=36, cuadrante=3, bbox_x=0.2, bbox_y=0.3, bbox_width=0.2, bbox_height=0.2),
    )


def _crear_odontologo(autorizado=True):
    return Odontologo(
        id=uuid4(),
        nombres="Rodrigo",
        apellidos="Cuya",
        numero_colegiatura="COP-45892",
        autorizado_validar=autorizado,
    )


def test_crear_diagnostico_desde_ia_exitoso():
    modelo = RegistroModeloML(
        modelo_ml_id=uuid4(),
        nombre_modelo="yolov8n",
        version="1.0.0",
        f1_score=0.89,
    )
    diag = Diagnostico.crear_desde_ia(
        estudio_id=uuid4(),
        paciente_id=uuid4(),
        modelo=modelo,
        hallazgos=[_crear_hallazgo_mock()],
    )
    assert diag.estado.es_sugerido_ia() is True
    assert len(diag.hallazgos) == 1
    assert len(diag.events) >= 1
    assert isinstance(diag.events[0], DiagnosticoSugeridoPorIA)


def test_crear_diagnostico_con_modelo_no_aprobado_lanza_excepcion():
    modelo_invalido = RegistroModeloML(
        modelo_ml_id=uuid4(),
        nombre_modelo="yolo-beta",
        version="0.1",
        f1_score=0.79,  # Menor a 0.85
    )
    with pytest.raises(DomainException, match="no está aprobado para producción"):
        Diagnostico.crear_desde_ia(
            estudio_id=uuid4(),
            paciente_id=uuid4(),
            modelo=modelo_invalido,
            hallazgos=[_crear_hallazgo_mock()],
        )


def test_crear_diagnostico_sin_hallazgos_lanza_excepcion():
    modelo = RegistroModeloML(
        modelo_ml_id=uuid4(),
        nombre_modelo="yolov8n",
        version="1.0",
        f1_score=0.90,
    )
    with pytest.raises(DomainException, match="No se puede crear un diagnóstico sin hallazgos"):
        Diagnostico.crear_desde_ia(
            estudio_id=uuid4(),
            paciente_id=uuid4(),
            modelo=modelo,
            hallazgos=[],
        )


def test_flujo_validacion_odontologica_completo():
    modelo = RegistroModeloML(modelo_ml_id=uuid4(), nombre_modelo="yolov8n", version="1.0", f1_score=0.90)
    diag = Diagnostico.crear_desde_ia(estudio_id=uuid4(), paciente_id=uuid4(), modelo=modelo, hallazgos=[_crear_hallazgo_mock()])
    odontologo = _crear_odontologo(autorizado=True)

    # Iniciar revisión
    diag.clear_events()
    diag.iniciar_revision(odontologo)
    assert diag.estado.es_en_revision() is True
    assert len(diag.events) == 1
    assert isinstance(diag.events[0], DiagnosticoEnRevision)

    # Validar
    diag.clear_events()
    diag.validar(odontologo, notas="Confirmada caries en pieza 36")
    assert diag.estado.es_validado() is True
    assert diag.notas_validacion == "Confirmada caries en pieza 36"
    assert len(diag.events) == 1
    assert isinstance(diag.events[0], DiagnosticoValidado)


def test_odontologo_no_autorizado_no_puede_validar():
    modelo = RegistroModeloML(modelo_ml_id=uuid4(), nombre_modelo="yolov8n", version="1.0", f1_score=0.90)
    diag = Diagnostico.crear_desde_ia(estudio_id=uuid4(), paciente_id=uuid4(), modelo=modelo, hallazgos=[_crear_hallazgo_mock()])
    odontologo_no_autorizado = _crear_odontologo(autorizado=False)

    with pytest.raises(DomainException, match="no está autorizado"):
        diag.validar(odontologo_no_autorizado, notas="Notas")


def test_validar_con_notas_vacias_lanza_excepcion():
    modelo = RegistroModeloML(modelo_ml_id=uuid4(), nombre_modelo="yolov8n", version="1.0", f1_score=0.90)
    diag = Diagnostico.crear_desde_ia(estudio_id=uuid4(), paciente_id=uuid4(), modelo=modelo, hallazgos=[_crear_hallazgo_mock()])
    odontologo = _crear_odontologo(autorizado=True)

    with pytest.raises(DomainException, match="Las notas de validación no pueden estar vacías"):
        diag.validar(odontologo, notas="   ")


def test_diagnostico_validado_es_irreversible():
    modelo = RegistroModeloML(modelo_ml_id=uuid4(), nombre_modelo="yolov8n", version="1.0", f1_score=0.90)
    diag = Diagnostico.crear_desde_ia(estudio_id=uuid4(), paciente_id=uuid4(), modelo=modelo, hallazgos=[_crear_hallazgo_mock()])
    odontologo = _crear_odontologo(autorizado=True)
    diag.validar(odontologo, notas="Validado")

    with pytest.raises(DomainException, match="no puede validarse desde el estado 'VALIDADO'"):
        diag.validar(odontologo, notas="Re-validar")

    with pytest.raises(DomainException, match="no puede rechazarse desde el estado 'VALIDADO'"):
        diag.rechazar(odontologo, motivo="Intento de descarte posterior")


def test_tipo_patologia_invalida_lanza_excepcion():
    with pytest.raises(ValueError, match="Tipo de patología inválido"):
        TipoPatologia("LESION_PERIAPICAL")


def test_severidad_invalida_lanza_excepcion():
    with pytest.raises(ValueError, match="Severidad inválida"):
        Severidad("CRITICA")


@pytest.mark.parametrize("confianza_invalida", [-0.1, 1.05, 2.0])
def test_hallazgo_confianza_fuera_de_rango_lanza_excepcion(confianza_invalida):
    with pytest.raises(ValueError, match="La confianza debe estar entre 0.0 y 1.0"):
        Hallazgo(
            imagen_id=uuid4(),
            tipo_patologia=TipoPatologia("CARIES"),
            severidad=Severidad("MODERADA"),
            confianza=confianza_invalida,
            region=RegionDental(diente_numero=11),
        )


def test_nivel_confianza_validaciones_directas():
    with pytest.raises(ValueError, match="El valor de confianza debe estar entre 0.0 y 1.0"):
        NivelConfianza(valor=1.5, categoria="ALTA")

    with pytest.raises(ValueError, match="Categoría inválida"):
        NivelConfianza(valor=0.75, categoria="DESCONOCIDA")


def test_iniciar_revision_desde_estado_invalido_lanza_excepcion():
    modelo = RegistroModeloML(modelo_ml_id=uuid4(), nombre_modelo="yolo", version="1.0", f1_score=0.9)
    diag = Diagnostico.crear_desde_ia(estudio_id=uuid4(), paciente_id=uuid4(), modelo=modelo, hallazgos=[_crear_hallazgo_mock()])
    odontologo = _crear_odontologo(autorizado=True)
    diag.iniciar_revision(odontologo)

    # Ya está EN_REVISION, no puede iniciar revisión de nuevo
    with pytest.raises(DomainException, match="Solo diagnósticos SUGERIDO_IA pueden iniciar revisión"):
        diag.iniciar_revision(odontologo)


def test_iniciar_revision_odontologo_no_autorizado_lanza_excepcion():
    modelo = RegistroModeloML(modelo_ml_id=uuid4(), nombre_modelo="yolo", version="1.0", f1_score=0.9)
    diag = Diagnostico.crear_desde_ia(estudio_id=uuid4(), paciente_id=uuid4(), modelo=modelo, hallazgos=[_crear_hallazgo_mock()])
    odontologo_no_autorizado = _crear_odontologo(autorizado=False)

    with pytest.raises(DomainException, match="no está autorizado"):
        diag.iniciar_revision(odontologo_no_autorizado)


def test_rechazar_diagnostico_exitoso():
    modelo = RegistroModeloML(modelo_ml_id=uuid4(), nombre_modelo="yolov8n", version="1.0", f1_score=0.90)
    diag = Diagnostico.crear_desde_ia(estudio_id=uuid4(), paciente_id=uuid4(), modelo=modelo, hallazgos=[_crear_hallazgo_mock()])
    odontologo = _crear_odontologo(autorizado=True)
    diag.clear_events()

    diag.rechazar(odontologo, motivo="Falso positivo: mancha por fluorosis dental.")

    assert diag.estado.es_rechazado() is True
    assert diag.motivo_rechazo == "Falso positivo: mancha por fluorosis dental."
    assert diag.odontologo == odontologo
    assert len(diag.events) == 1
    assert isinstance(diag.events[0], DiagnosticoRechazado)
    assert diag.events[0].motivo == "Falso positivo: mancha por fluorosis dental."


def test_rechazar_diagnostico_motivo_vacio_lanza_excepcion():
    modelo = RegistroModeloML(modelo_ml_id=uuid4(), nombre_modelo="yolov8n", version="1.0", f1_score=0.90)
    diag = Diagnostico.crear_desde_ia(estudio_id=uuid4(), paciente_id=uuid4(), modelo=modelo, hallazgos=[_crear_hallazgo_mock()])
    odontologo = _crear_odontologo(autorizado=True)

    with pytest.raises(DomainException, match="El motivo de rechazo no puede estar vacío"):
        diag.rechazar(odontologo, motivo="   ")


def test_rechazar_diagnostico_odontologo_no_autorizado_lanza_excepcion():
    modelo = RegistroModeloML(modelo_ml_id=uuid4(), nombre_modelo="yolov8n", version="1.0", f1_score=0.90)
    diag = Diagnostico.crear_desde_ia(estudio_id=uuid4(), paciente_id=uuid4(), modelo=modelo, hallazgos=[_crear_hallazgo_mock()])
    odontologo_no_aut = _crear_odontologo(autorizado=False)

    with pytest.raises(DomainException, match="no está autorizado"):
        diag.rechazar(odontologo_no_aut, motivo="Motivo válido")


def test_diagnostico_baja_confianza_emite_segunda_opinion_solicitada():
    modelo = RegistroModeloML(modelo_ml_id=uuid4(), nombre_modelo="yolov8n", version="1.0", f1_score=0.90)
    hallazgo_dudoso = Hallazgo(
        imagen_id=uuid4(),
        tipo_patologia=TipoPatologia("CARIES"),
        severidad=Severidad("LEVE"),
        confianza=0.35,  # Baja (< 0.5)
        region=RegionDental(diente_numero=21),
    )
    diag = Diagnostico.crear_desde_ia(
        estudio_id=uuid4(),
        paciente_id=uuid4(),
        modelo=modelo,
        hallazgos=[hallazgo_dudoso],
    )

    assert diag.requiere_segunda_opinion() is True
    assert diag.nivel_confianza.categoria == "BAJA"
    # Debe emitir tanto DiagnosticoSugeridoPorIA como SegundaOpinionSolicitada
    assert len(diag.events) == 2
    assert isinstance(diag.events[0], DiagnosticoSugeridoPorIA)
    assert isinstance(diag.events[1], SegundaOpinionSolicitada)

