"""
test_repositories.py
====================
Pruebas unitarias de contratos e interfaces abstractas del dominio.
Verifica que las interfaces no puedan instanciarse directamente
y que requieran implementar todos sus métodos abstractos.
"""

from uuid import uuid4
import pytest

from app.domain.pacientes.repository import IPacienteRepository
from app.domain.estudios.repository import IEstudioRepository
from app.domain.inferencias.repository import IInferenciaRepository
from app.domain.diagnosticos.repository import IDiagnosticoRepository, IOdontologoRepository
from app.domain.diagnosticos.interfaces import IDetectorPatologias, IClasificadorImagenes


def test_paciente_repository_es_abstracto():
    with pytest.raises(TypeError, match="Can't instantiate abstract class"):
        IPacienteRepository()


def test_estudio_repository_es_abstracto():
    with pytest.raises(TypeError, match="Can't instantiate abstract class"):
        IEstudioRepository()


def test_inferencia_repository_es_abstracto():
    with pytest.raises(TypeError, match="Can't instantiate abstract class"):
        IInferenciaRepository()


def test_diagnostico_repository_es_abstracto():
    with pytest.raises(TypeError, match="Can't instantiate abstract class"):
        IDiagnosticoRepository()


def test_odontologo_repository_es_abstracto():
    with pytest.raises(TypeError, match="Can't instantiate abstract class"):
        IOdontologoRepository()


def test_detector_patologias_es_abstracto():
    with pytest.raises(TypeError, match="Can't instantiate abstract class"):
        IDetectorPatologias()


def test_clasificador_imagenes_es_abstracto():
    with pytest.raises(TypeError, match="Can't instantiate abstract class"):
        IClasificadorImagenes()


def test_implementacion_concreta_paciente_repository():
    class MemoriaPacienteRepo(IPacienteRepository):
        def __init__(self):
            self.items = {}

        def save(self, paciente):
            self.items[paciente.id] = paciente

        def get_by_id(self, paciente_id):
            return self.items.get(paciente_id)

        def get_by_dni(self, dni):
            for p in self.items.values():
                if p.dni == dni:
                    return p
            return None

        def exists_by_dni(self, dni):
            return any(p.dni == dni for p in self.items.values())

        def list_activos(self, limit=50, offset=0):
            return [p for p in self.items.values() if p.estado.es_activo()]

    repo = MemoriaPacienteRepo()
    assert isinstance(repo, IPacienteRepository)
    assert repo.exists_by_dni("00000000") is False
