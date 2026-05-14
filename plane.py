"""Modulo que define la clase Plane.

Este archivo contiene la representacion de un avion dentro de la simulacion.
Cada avion conserva su cantidad inicial de pasajeros y tambien el numero de
pasajeros que faltan por desembarcar durante la ejecucion del programa.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Plane:
    """Representa un avion que debe desembarcar pasajeros.

    Attributes:
        identifier: Numero identificador del avion dentro de la simulacion.
        passengers: Cantidad inicial de pasajeros del avion.
        remaining_passengers: Cantidad de pasajeros que todavia no han
            desembarcado. Se inicializa automaticamente con el total de
            pasajeros del avion.
    """

    identifier: int
    passengers: int
    remaining_passengers: int = field(init=False)

    def __post_init__(self) -> None:
        """Valida los datos iniciales y prepara el estado de simulacion."""
        if self.identifier <= 0:
            raise ValueError("El identificador del avion debe ser positivo.")
        if self.passengers <= 0:
            raise ValueError("La cantidad de pasajeros debe ser mayor que cero.")

        self.remaining_passengers = self.passengers

    @property
    def code(self) -> str:
        """Devuelve un codigo corto y legible para mostrar el avion."""
        return f"A{self.identifier}"

    @property
    def is_finished(self) -> bool:
        """Indica si el avion ya termino su proceso de desembarco."""
        return self.remaining_passengers == 0

    def disembark(self, terminal_capacity: int) -> int:
        """Desembarca pasajeros de acuerdo con la capacidad de una terminal.

        Args:
            terminal_capacity: Numero maximo de pasajeros que la terminal puede
                procesar en un tick.

        Returns:
            La cantidad real de pasajeros desembarcados durante el tick.
        """
        if terminal_capacity <= 0:
            raise ValueError("La capacidad de la terminal debe ser positiva.")

        processed = min(self.remaining_passengers, terminal_capacity)
        self.remaining_passengers -= processed
        return processed

    def reset(self) -> None:
        """Restaura el avion a su estado inicial antes de una simulacion."""
        self.remaining_passengers = self.passengers

    def __str__(self) -> str:
        """Devuelve una descripcion breve del avion."""
        return f"{self.code} ({self.passengers} pasajeros)"
