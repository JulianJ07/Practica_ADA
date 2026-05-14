"""Modulo que define la clase Terminal.

Una terminal aeroportuaria tiene una capacidad de procesamiento, es decir, la
cantidad maxima de pasajeros que puede desembarcar por cada tick de la
simulacion. Tambien conserva la lista de aviones que le fueron asignados.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from math import ceil

from plane import Plane


@dataclass(frozen=True)
class TickResult:
    """Resultado producido por una terminal durante un tick de simulacion."""

    terminal_code: str
    plane_code: str | None
    processed_passengers: int
    remaining_passengers: int
    finished_plane: bool
    next_plane_code: str | None
    message: str


@dataclass
class Terminal:
    """Representa una terminal aeroportuaria.

    Attributes:
        identifier: Numero identificador de la terminal.
        capacity: Cantidad de pasajeros que puede procesar por tick.
        planes: Lista de aviones asignados a la terminal.
        active_plane_index: Posicion del avion que se esta atendiendo en la
            simulacion.
    """

    identifier: int
    capacity: int
    planes: list[Plane] = field(default_factory=list)
    active_plane_index: int = 0

    def __post_init__(self) -> None:
        """Valida la informacion basica de la terminal."""
        if self.identifier <= 0:
            raise ValueError("El identificador de la terminal debe ser positivo.")
        if self.capacity <= 0:
            raise ValueError("La capacidad de la terminal debe ser mayor que cero.")

    @property
    def code(self) -> str:
        """Devuelve un codigo corto y legible para mostrar la terminal."""
        return f"T{self.identifier}"

    def assign_plane(self, plane: Plane) -> None:
        """Agrega un avion a la cola de atencion de la terminal."""
        self.planes.append(plane)

    def estimated_total_ticks(self) -> int:
        """Calcula los ticks estimados para procesar todos sus aviones.

        Este valor se usa durante la asignacion greedy para comparar la carga
        acumulada de cada terminal.
        """
        return sum(ceil(plane.passengers / self.capacity) for plane in self.planes)

    def estimated_total_passengers(self) -> int:
        """Calcula el total de pasajeros asignados a la terminal."""
        return sum(plane.passengers for plane in self.planes)

    def current_plane(self) -> Plane | None:
        """Devuelve el avion actualmente atendido, si existe."""
        if self.active_plane_index >= len(self.planes):
            return None
        return self.planes[self.active_plane_index]

    def has_pending_work(self) -> bool:
        """Indica si la terminal aun tiene pasajeros por desembarcar."""
        current = self.current_plane()
        return current is not None

    def process_tick(self) -> TickResult:
        """Procesa un tick de desembarco para la terminal.

        Durante un tick, la terminal solo atiende un avion. Si ese avion termina
        de desembarcar, la terminal queda lista para atender el siguiente avion
        en el tick posterior.
        """
        plane = self.current_plane()

        if plane is None:
            return TickResult(
                terminal_code=self.code,
                plane_code=None,
                processed_passengers=0,
                remaining_passengers=0,
                finished_plane=False,
                next_plane_code=None,
                message="Sin aviones pendientes.",
            )

        processed = plane.disembark(self.capacity)
        finished = plane.is_finished
        next_plane_code = None

        if finished:
            self.active_plane_index += 1
            next_plane = self.current_plane()
            next_plane_code = next_plane.code if next_plane else None

        if finished and next_plane_code:
            message = f"{plane.code} termino. Siguiente avion: {next_plane_code}."
        elif finished:
            message = f"{plane.code} termino. La terminal queda libre."
        else:
            message = f"{plane.code} continua en desembarco."

        return TickResult(
            terminal_code=self.code,
            plane_code=plane.code,
            processed_passengers=processed,
            remaining_passengers=plane.remaining_passengers,
            finished_plane=finished,
            next_plane_code=next_plane_code,
            message=message,
        )

    def reset_simulation(self) -> None:
        """Reinicia el estado de la terminal y de todos sus aviones."""
        self.active_plane_index = 0
        for plane in self.planes:
            plane.reset()

    def __str__(self) -> str:
        """Devuelve una descripcion breve de la terminal."""
        return f"{self.code} (capacidad: {self.capacity} pasajeros/tick)"
