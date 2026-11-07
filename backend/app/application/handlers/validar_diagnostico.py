"""
validar_diagnostico.py
======================
Handler para ValidarDiagnosticoCommand.
"""

from app.application.commands.validar_diagnostico import ValidarDiagnosticoCommand
from app.domain.diagnosticos.entities import Odontologo
from app.domain.diagnosticos.repository import IDiagnosticoRepository
from app.domain.diagnosticos.value_objects import DiagnosticoId
from app.domain.shared.domain_exception import DomainException
from app.domain.diagnosticos.repository import IOdontologoRepository


class ValidarDiagnosticoHandler:
    """
    Caso de uso: validar un diagnóstico sugerido por IA.

    Orquesta:
    1. Cargar diagnóstico
    2. Cargar odontólogo y verificar autorización
    3. Ejecutar validar() en el agregado (lógica de dominio)
    4. Persistir
    """

    def __init__(
        self,
        diagnostico_repo: IDiagnosticoRepository,
        odontologo_repo: IOdontologoRepository,
    ) -> None:
        self._diagnostico_repo = diagnostico_repo
        self._odontologo_repo = odontologo_repo

    def handle(self, cmd: ValidarDiagnosticoCommand) -> None:
        """
        Raises
        ------
        DomainException
            Si el diagnóstico o el odontólogo no existen,
            o si el dominio rechaza la operación.
        """
        diagnostico = self._diagnostico_repo.get_by_id(
            DiagnosticoId(cmd.diagnostico_id)
        )
        if diagnostico is None:
            raise DomainException(
                f"No existe el diagnóstico con ID '{cmd.diagnostico_id}'."
            )

        odontologo = self._odontologo_repo.get_by_id(cmd.odontologo_id)
        if odontologo is None:
            raise DomainException(
                f"No existe el odontólogo con ID '{cmd.odontologo_id}'."
            )

        diagnostico.validar(odontologo=odontologo, notas=cmd.notas)
        self._diagnostico_repo.save(diagnostico)