"""Modelos y cola de prioridad para pedidos de entrega.

Los pedidos se ordenan por dos criterios:

1. Prioridad indicada para el pedido.
2. Orden de llegada cuando dos pedidos tienen la misma prioridad.

Python incluye ``heapq``, una implementacion eficiente de monticulos binarios.
Con ella se construye una cola de prioridad sin depender de librerias externas.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from heapq import heappop, heappush
from itertools import count


PRIORITY_LEVELS: dict[str, int] = {
    "alta": 1,
    "media": 2,
    "baja": 3,
}


@dataclass(frozen=True)
class DeliveryOrder:
    """Representa un pedido registrado en el sistema."""

    order_id: int
    customer_name: str
    product_type: str
    destination: str
    priority_value: int
    priority_label: str
    arrival_order: int


@dataclass(order=True)
class _QueuedOrder:
    """Elemento interno de la cola de prioridad.

    Los campos comparables van primero. Asi, el heap ordena por prioridad y
    despues por orden de llegada.
    """

    priority_value: int
    arrival_order: int
    order: DeliveryOrder = field(compare=False)


class PriorityOrderQueue:
    """Cola de prioridad para organizar pedidos de reparto."""

    def __init__(self) -> None:
        """Crea una cola vacia."""
        self._heap: list[_QueuedOrder] = []
        self._arrival_counter = count(1)
        self._order_counter = count(1)

    def add_order(
        self,
        customer_name: str,
        product_type: str,
        priority: str,
        destination: str,
    ) -> DeliveryOrder:
        """Registra un nuevo pedido y lo inserta en la cola."""
        normalized_type = product_type.strip().lower()
        if not normalized_type:
            raise ValueError("El tipo de pedido no puede estar vacio.")

        priority_value, priority_label = normalize_priority(priority)
        arrival_order = next(self._arrival_counter)
        order = DeliveryOrder(
            order_id=next(self._order_counter),
            customer_name=customer_name.strip(),
            product_type=normalized_type,
            destination=destination,
            priority_value=priority_value,
            priority_label=priority_label,
            arrival_order=arrival_order,
        )

        heappush(
            self._heap,
            _QueuedOrder(
                priority_value=priority_value,
                arrival_order=arrival_order,
                order=order,
            ),
        )
        return order

    def pop_next(self) -> DeliveryOrder | None:
        """Extrae el siguiente pedido por prioridad y llegada."""
        if not self._heap:
            return None

        return heappop(self._heap).order

    def peek_all(self) -> list[DeliveryOrder]:
        """Devuelve los pedidos pendientes en el orden en que se atenderian."""
        return [queued.order for queued in sorted(self._heap)]

    def is_empty(self) -> bool:
        """Indica si no hay pedidos pendientes."""
        return not self._heap

    def __len__(self) -> int:
        """Devuelve la cantidad de pedidos pendientes."""
        return len(self._heap)


def get_priority_options_text() -> str:
    """Devuelve las prioridades disponibles en formato legible."""
    lines = []

    for priority_label, priority_value in PRIORITY_LEVELS.items():
        lines.append(f"- {priority_label}: valor interno {priority_value}")

    return "\n".join(lines)


def normalize_priority(priority: str) -> tuple[int, str]:
    """Convierte una prioridad escrita por el usuario en valor numerico.

    Se aceptan las etiquetas ``alta``, ``media`` y ``baja``. Tambien se aceptan
    los numeros ``1``, ``2`` y ``3`` para facilitar la carga desde archivos.
    """
    normalized_priority = priority.strip().lower()

    if normalized_priority in PRIORITY_LEVELS:
        return PRIORITY_LEVELS[normalized_priority], normalized_priority

    numeric_aliases = {
        "1": "alta",
        "2": "media",
        "3": "baja",
    }
    if normalized_priority in numeric_aliases:
        label = numeric_aliases[normalized_priority]
        return PRIORITY_LEVELS[label], label

    valid_priorities = ", ".join(PRIORITY_LEVELS)
    raise ValueError(
        f"Prioridad no valida. Opciones: {valid_priorities} "
        "o los numeros 1, 2, 3."
    )
