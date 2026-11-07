"""
test_shared.py
==============
Pruebas unitarias para las abstracciones del núcleo del dominio:
- Entity (igualdad por ID y hashing)
- AggregateRoot (registro y limpieza de eventos)
- DomainEvent
- DomainException
"""

from uuid import uuid4
import pytest

from app.domain.shared.entity import Entity
from app.domain.shared.aggregate_root import AggregateRoot
from app.domain.shared.domain_event import DomainEvent
from app.domain.shared.domain_exception import DomainException
from app.domain.shared.value_object import ValueObject


class DummyEntity(Entity):
    pass


class DummyEvent(DomainEvent):
    def __init__(self, data: str):
        super().__init__()
        self.data = data


class DummyAggregate(AggregateRoot):
    def __init__(self, aggregate_id):
        super().__init__(id=aggregate_id)

    def do_action(self):
        self.add_event(DummyEvent("acción completada"))


def test_entity_igualdad_por_id():
    id_1 = uuid4()
    id_2 = uuid4()

    e1 = DummyEntity(id=id_1)
    e2 = DummyEntity(id=id_1)
    e3 = DummyEntity(id=id_2)

    assert e1 == e2
    assert e1 != e3
    assert hash(e1) == hash(e2)
    assert e1 != "no-entity"
    assert e1 != None


def test_aggregate_root_gestion_de_eventos():
    agg = DummyAggregate(aggregate_id=uuid4())
    assert len(agg.events) == 0

    agg.do_action()
    assert len(agg.events) == 1
    assert isinstance(agg.events[0], DummyEvent)
    assert agg.events[0].data == "acción completada"
    assert agg.events[0].occurred_on is not None
    assert agg.events[0].ocurred_on == agg.events[0].occurred_on

    agg.clear_events()
    assert len(agg.events) == 0


def test_domain_exception_mensaje():
    with pytest.raises(DomainException) as excinfo:
        raise DomainException("Error de regla de negocio violada")
    assert "Error de regla de negocio violada" in str(excinfo.value)
