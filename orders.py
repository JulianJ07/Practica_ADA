"""Modelos y organizacion de pedidos de entrega.

Los pedidos pueden organizarse de dos formas:

1. Por prioridad y orden de llegada.
2. Por precio mayor usando Merge Sort.

El modo por prioridad atiende primero los pedidos mas urgentes. El modo por
precio atiende primero los pedidos de mayor valor economico.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import count
from typing import Callable


PRIORITY_LEVELS: dict[str, int] = {
    "alta": 1,
    "media": 2,
    "baja": 3,
}

SORT_BY_PRIORITY = "prioridad"
SORT_BY_PRICE = "precio"


@dataclass(frozen=True)
class DeliveryOrder:
    """Representa un pedido registrado en el sistema."""

    order_id: int
    customer_name: str
    product_type: str
    priority_value: int
    priority_label: str
    price: float
    destination: str
    arrival_order: int


class PriorityOrderQueue:
    """Administra los pedidos pendientes y su criterio de ordenamiento."""

    def __init__(self) -> None:
        """Crea una coleccion de pedidos pendientes."""
        self._orders: list[DeliveryOrder] = []
        self._arrival_counter = count(1)
        self._order_counter = count(1)
        self._sort_mode = SORT_BY_PRIORITY

    @property
    def sort_mode(self) -> str:
        """Devuelve el criterio de ordenamiento activo."""
        return self._sort_mode

    def set_sort_mode(self, mode: str) -> None:
        """Cambia el criterio usado para atender pedidos."""
        if mode not in {SORT_BY_PRIORITY, SORT_BY_PRICE}:
            raise ValueError("Modo de ordenamiento no valido.")

        self._sort_mode = mode

    def use_priority_order(self) -> None:
        """Activa el ordenamiento por prioridad."""
        self.set_sort_mode(SORT_BY_PRIORITY)

    def use_price_order(self) -> None:
        """Activa el ordenamiento por precio mayor."""
        self.set_sort_mode(SORT_BY_PRICE)

    def add_order(
        self,
        customer_name: str,
        product_type: str,
        priority: str,
        price: str | float,
        destination: str,
    ) -> DeliveryOrder:
        """Registra un nuevo pedido.

        El pedido se guarda en la lista de pendientes. El orden de atencion se
        calcula cada vez segun el modo activo: prioridad o precio.
        """
        normalized_type = product_type.strip().lower()
        if not normalized_type:
            raise ValueError("El tipo de pedido no puede estar vacio.")

        normalized_customer = customer_name.strip()
        if not normalized_customer:
            raise ValueError("El nombre del cliente no puede estar vacio.")

        priority_value, priority_label = normalize_priority(priority)
        normalized_price = normalize_price(price)
        arrival_order = next(self._arrival_counter)
        order = DeliveryOrder(
            order_id=next(self._order_counter),
            customer_name=normalized_customer,
            product_type=normalized_type,
            priority_value=priority_value,
            priority_label=priority_label,
            price=normalized_price,
            destination=destination,
            arrival_order=arrival_order,
        )

        self._orders.append(order)
        return order

    def pop_next(self) -> DeliveryOrder | None:
        """Extrae el siguiente pedido segun el modo activo."""
        if not self._orders:
            return None

        ordered_orders = self.peek_all()
        next_order = ordered_orders[0]
        self._orders = [
            order for order in self._orders if order.order_id != next_order.order_id
        ]
        return next_order

    def peek_all(self) -> list[DeliveryOrder]:
        """Devuelve los pedidos pendientes en el orden en que se atenderian."""
        if self._sort_mode == SORT_BY_PRICE:
            return sort_orders_by_price(self._orders)

        return sort_orders_by_priority(self._orders)

    def is_empty(self) -> bool:
        """Indica si no hay pedidos pendientes."""
        return not self._orders

    def __len__(self) -> int:
        """Devuelve la cantidad de pedidos pendientes."""
        return len(self._orders)


def sort_orders_by_priority(orders: list[DeliveryOrder]) -> list[DeliveryOrder]:
    """Ordena pedidos por prioridad y llegada usando Merge Sort."""
    return merge_sort_orders(
        orders,
        key=lambda order: (order.priority_value, order.arrival_order),
    )


def sort_orders_by_price(orders: list[DeliveryOrder]) -> list[DeliveryOrder]:
    """Ordena pedidos por precio mayor usando Merge Sort.

    Si dos pedidos tienen el mismo precio, se conserva primero el que llego
    antes.
    """
    return merge_sort_orders(
        orders,
        key=lambda order: (-order.price, order.arrival_order),
    )


def merge_sort_orders(
    orders: list[DeliveryOrder],
    key: Callable[[DeliveryOrder], tuple[float, int] | tuple[int, int]],
) -> list[DeliveryOrder]:
    """Ordena pedidos con Merge Sort segun una llave de comparacion.

    Merge Sort divide la lista en mitades, ordena cada mitad y luego las une.
    Esta implementacion devuelve una nueva lista y no modifica la lista original.
    """
    if len(orders) <= 1:
        return orders[:]

    middle = len(orders) // 2
    left = merge_sort_orders(orders[:middle], key)
    right = merge_sort_orders(orders[middle:], key)
    return _merge(left, right, key)


def _merge(
    left: list[DeliveryOrder],
    right: list[DeliveryOrder],
    key: Callable[[DeliveryOrder], tuple[float, int] | tuple[int, int]],
) -> list[DeliveryOrder]:
    """Une dos listas ordenadas de pedidos."""
    merged: list[DeliveryOrder] = []
    left_index = 0
    right_index = 0

    while left_index < len(left) and right_index < len(right):
        if key(left[left_index]) <= key(right[right_index]):
            merged.append(left[left_index])
            left_index += 1
        else:
            merged.append(right[right_index])
            right_index += 1

    merged.extend(left[left_index:])
    merged.extend(right[right_index:])
    return merged


def get_priority_options_text() -> str:
    """Devuelve las prioridades disponibles en formato legible."""
    lines = []

    for priority_label, priority_value in PRIORITY_LEVELS.items():
        lines.append(f"- {priority_label}: valor interno {priority_value}")

    return "\n".join(lines)


def get_sort_mode_text(mode: str) -> str:
    """Devuelve una descripcion breve del criterio activo."""
    if mode == SORT_BY_PRICE:
        return "precio mayor (Merge Sort)"

    return "prioridad y orden de llegada"


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


def normalize_price(price: str | float) -> float:
    """Valida y convierte el precio de un pedido."""
    if isinstance(price, (int, float)):
        numeric_price = float(price)
    else:
        clean_price = price.strip().replace("$", "").replace(",", "")

        try:
            numeric_price = float(clean_price)
        except ValueError as error:
            raise ValueError("El precio debe ser un numero mayor que cero.") from error

    if numeric_price <= 0:
        raise ValueError("El precio debe ser mayor que cero.")

    return numeric_price
