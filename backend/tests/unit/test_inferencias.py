"""
test_inferencias.py
===================
Pruebas unitarias de dominio (TDD) para el Bounded Context: Gestión de Inferencias IA.
Sin base de datos ni dependencias externas.
"""

from uuid import uuid4
import pytest

from app.domain.inferencias.value_objects import (
    EstadoInferencia,
    InferenciaId,
    TiempoInferencia,
    WorkerId,
)
from app.domain.inferencias.entities import InferenciaIA
from app.domain.inferencias.events import (
    InferenciaCompletada,
    InferenciaFallida,
    InferenciaIniciada,
)
from app.domain.shared.domain_exception import DomainException


# ============================================================================
# Value Object: EstadoInferencia
# ============================================================================

@pytest.mark.parametrize("estado", ["PENDIENTE", "EN_PROCESO", "COMPLETADO", "FALLIDO"])
def test_estado_inferencia_valido(estado):
    ei = EstadoInferencia(estado)
    assert ei.value == estado


def test_estado_inferencia_invalido():
    with pytest.raises(ValueError, match="Estado inválido"):
        EstadoInferencia("CANCELADO")


# ============================================================================
# Value Object: TiempoInferencia
# ============================================================================

def test_tiempo_inferencia_valido():
    ti = TiempoInferencia(valor_ms=250.5)
    assert ti.valor_ms == 250.5
    assert ti.en_segundos() == 0.2505


@pytest.mark.parametrize("tiempo_invalido", [0, -10.0])
def test_tiempo_inferencia_menor_igual_cero_falla(tiempo_invalido):
    with pytest.raises(ValueError, match="debe ser mayor a 0 ms"):
        TiempoInferencia(valor_ms=tiempo_invalido)


# ============================================================================
# Value Object: WorkerId
# ============================================================================

def test_worker_id_valido():
    w = WorkerId("worker-gpu-node-1")
    assert w.value == "worker-gpu-node-1"


@pytest.mark.parametrize("worker_vacio", ["", "   "])
def test_worker_id_vacio_lanza_excepcion(worker_vacio):
    with pytest.raises(ValueError, match="El worker ID no puede estar vacío"):
        WorkerId(worker_vacio)


# ============================================================================
# Entity / Aggregate Root: InferenciaIA
# ============================================================================

def test_crear_inferencia_inicia_pendiente():
    inf = InferenciaIA.crear(estudio_id=uuid4(), modelo_ml_id=uuid4())
    assert inf.id is not None
    assert inf.estado.es_pendiente() is True
    assert inf.worker_id is None
    assert inf.tiempo_inferencia is None
    assert inf.completed_at is None


def test_ciclo_de_vida_inferencia_exitoso():
    inf = InferenciaIA.crear(estudio_id=uuid4(), modelo_ml_id=uuid4())

    # Iniciar
    inf.clear_events()
    worker = WorkerId("celery-worker-1")
    inf.iniciar(worker_id=worker, gpu_utilizada="NVIDIA RTX 4090")

    assert inf.estado.es_en_proceso() is True
    assert inf.worker_id == worker
    assert len(inf.events) == 1
    assert isinstance(inf.events[0], InferenciaIniciada)

    # Completar
    inf.clear_events()
    tiempo = TiempoInferencia(valor_ms=280.0)
    inf.completar(tiempo)

    assert inf.estado.es_completado() is True
    assert inf.tiempo_inferencia == tiempo
    assert inf.completed_at is not None
    assert len(inf.events) == 1
    assert isinstance(inf.events[0], InferenciaCompletada)


def test_iniciar_inferencia_no_pendiente_lanza_excepcion():
    inf = InferenciaIA.crear(estudio_id=uuid4(), modelo_ml_id=uuid4())
    inf.iniciar(WorkerId("w1"))

    with pytest.raises(DomainException, match="Solo inferencias PENDIENTES pueden iniciarse"):
        inf.iniciar(WorkerId("w2"))


def test_fallar_inferencia_guarda_mensaje_y_emite_evento():
    inf = InferenciaIA.crear(estudio_id=uuid4(), modelo_ml_id=uuid4())
    inf.iniciar(WorkerId("w1"))

    inf.clear_events()
    inf.fallar(error_mensaje="CUDA Out of Memory Exception")

    assert inf.estado.es_fallido() is True
    assert inf.error_mensaje == "CUDA Out of Memory Exception"
    assert inf.puede_reintentarse() is True
    assert len(inf.events) == 1
    assert isinstance(inf.events[0], InferenciaFallida)


def test_fallar_con_mensaje_vacio_lanza_excepcion():
    inf = InferenciaIA.crear(estudio_id=uuid4(), modelo_ml_id=uuid4())
    inf.iniciar(WorkerId("w1"))

    with pytest.raises(DomainException, match="El mensaje de error no puede estar vacío"):
        inf.fallar(error_mensaje="   ")


def test_worker_id_supera_100_caracteres_lanza_excepcion():
    with pytest.raises(ValueError, match="El worker ID no puede superar 100 caracteres"):
        WorkerId("w" * 101)


def test_completar_inferencia_no_en_proceso_lanza_excepcion():
    inf = InferenciaIA.crear(estudio_id=uuid4(), modelo_ml_id=uuid4())
    # Estado es PENDIENTE, no EN_PROCESO
    with pytest.raises(DomainException, match="Solo inferencias EN_PROCESO pueden completarse"):
        inf.completar(TiempoInferencia(valor_ms=150.0))


def test_fallar_inferencia_no_en_proceso_lanza_excepcion():
    inf = InferenciaIA.crear(estudio_id=uuid4(), modelo_ml_id=uuid4())
    # Estado es PENDIENTE, no EN_PROCESO
    with pytest.raises(DomainException, match="Solo inferencias EN_PROCESO pueden marcarse como fallidas"):
        inf.fallar(error_mensaje="Error inesperado")

