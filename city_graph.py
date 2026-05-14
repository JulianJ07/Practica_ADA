"""Estructura de grafo y algoritmo de Dijkstra.

El mapa de la ciudad se modela como un grafo ponderado no dirigido. Cada nodo
representa un punto importante de la ciudad y cada arista representa una calle
con un costo asociado, expresado en minutos de recorrido.
"""

from __future__ import annotations

from dataclasses import dataclass
from heapq import heappop, heappush
from math import inf


@dataclass(frozen=True)
class RouteResult:
    """Resultado de buscar una ruta en el grafo.

    Attributes:
        origin: Punto inicial de la ruta.
        destination: Punto final de la ruta.
        path: Lista ordenada de nodos que forman la ruta encontrada.
        total_cost: Costo total de la ruta.
        visited_nodes: Nodos que Dijkstra reviso durante la busqueda.
    """

    origin: str
    destination: str
    path: list[str]
    total_cost: float
    visited_nodes: list[str]


class WeightedGraph:
    """Representa un grafo ponderado usando listas de adyacencia."""

    def __init__(self) -> None:
        """Inicializa el grafo sin nodos ni aristas."""
        self._adjacency: dict[str, dict[str, float]] = {}

    def add_node(self, node: str) -> None:
        """Agrega un nodo al grafo si todavia no existe."""
        normalized_node = node.strip()
        if not normalized_node:
            raise ValueError("El nombre del nodo no puede estar vacio.")

        self._adjacency.setdefault(normalized_node, {})

    def add_edge(
        self,
        origin: str,
        destination: str,
        cost: float,
        bidirectional: bool = True,
    ) -> None:
        """Agrega una calle entre dos nodos.

        Args:
            origin: Nodo de origen.
            destination: Nodo de destino.
            cost: Peso de la arista. En este proyecto representa minutos.
            bidirectional: Si es verdadero, la calle se puede recorrer en ambos
                sentidos.
        """
        if cost <= 0:
            raise ValueError("El costo de una arista debe ser mayor que cero.")

        normalized_origin = origin.strip()
        normalized_destination = destination.strip()

        self.add_node(normalized_origin)
        self.add_node(normalized_destination)
        self._adjacency[normalized_origin][normalized_destination] = cost

        if bidirectional:
            self._adjacency[normalized_destination][normalized_origin] = cost

    def nodes(self) -> list[str]:
        """Devuelve los nodos disponibles ordenados alfabeticamente."""
        return sorted(self._adjacency)

    def neighbors(self, node: str) -> dict[str, float]:
        """Devuelve los vecinos de un nodo."""
        self._validate_node(node)
        return dict(self._adjacency[node])

    def edges(self) -> list[tuple[str, str, float]]:
        """Devuelve las aristas del grafo sin repetir calles bidireccionales."""
        edges: list[tuple[str, str, float]] = []
        seen_edges: set[frozenset[str]] = set()

        for origin, neighbors in self._adjacency.items():
            for destination, cost in neighbors.items():
                edge_key = frozenset({origin, destination})

                if edge_key in seen_edges:
                    continue

                seen_edges.add(edge_key)
                edges.append((origin, destination, cost))

        return edges

    def has_node(self, node: str) -> bool:
        """Indica si un nodo existe dentro del grafo."""
        return node in self._adjacency

    def dijkstra(self, origin: str, destination: str) -> RouteResult:
        """Calcula la ruta de menor costo usando el algoritmo de Dijkstra.

        Dijkstra trabaja con pesos positivos. En esta aplicacion, cada peso
        representa el tiempo estimado para recorrer una calle.
        """
        self._validate_node(origin)
        self._validate_node(destination)

        distances = {node: inf for node in self._adjacency}
        previous_nodes: dict[str, str | None] = {
            node: None for node in self._adjacency
        }
        visited: set[str] = set()
        visited_order: list[str] = []
        priority_queue: list[tuple[float, str]] = []

        distances[origin] = 0
        heappush(priority_queue, (0, origin))

        while priority_queue:
            current_distance, current_node = heappop(priority_queue)

            if current_node in visited:
                continue

            visited.add(current_node)
            visited_order.append(current_node)

            if current_node == destination:
                break

            for neighbor, edge_cost in self._adjacency[current_node].items():
                new_distance = current_distance + edge_cost

                if new_distance < distances[neighbor]:
                    distances[neighbor] = new_distance
                    previous_nodes[neighbor] = current_node
                    heappush(priority_queue, (new_distance, neighbor))

        path = self._reconstruct_path(previous_nodes, origin, destination)
        total_cost = distances[destination]

        if total_cost == inf:
            return RouteResult(origin, destination, [], inf, visited_order)

        return RouteResult(origin, destination, path, total_cost, visited_order)

    def describe(self) -> str:
        """Genera una descripcion textual de las conexiones del mapa."""
        lines: list[str] = []

        for origin in self.nodes():
            connections = [
                f"{destination} ({cost:g} min)"
                for destination, cost in sorted(self._adjacency[origin].items())
            ]
            lines.append(f"{origin}: {', '.join(connections)}")

        return "\n".join(lines)

    def _validate_node(self, node: str) -> None:
        """Valida que un nodo exista en el grafo."""
        if node not in self._adjacency:
            raise ValueError(f"El nodo '{node}' no existe en el mapa.")

    def _reconstruct_path(
        self,
        previous_nodes: dict[str, str | None],
        origin: str,
        destination: str,
    ) -> list[str]:
        """Reconstruye la ruta desde el destino hasta el origen."""
        path: list[str] = []
        current_node: str | None = destination

        while current_node is not None:
            path.append(current_node)

            if current_node == origin:
                break

            current_node = previous_nodes[current_node]

        path.reverse()
        return path if path and path[0] == origin else []


def build_default_city_graph() -> WeightedGraph:
    """Crea un mapa de ciudad de ejemplo para la simulacion.

    Los pesos representan minutos aproximados de recorrido. El mapa incluye
    zonas principales y 20 clientes distintos como destinos de pedidos.
    """
    graph = WeightedGraph()

    streets = [
        ("Bodega", "Centro", 4),
        ("Bodega", "Parque", 6),
        ("Bodega", "Olivia", 3),
        ("Bodega", "Nicolas", 5),
        ("Bodega", "Ana", 4),
        ("Centro", "Hospital", 5),
        ("Centro", "Universidad", 7),
        ("Centro", "Zona Comercial", 4),
        ("Centro", "Pablo", 3),
        ("Centro", "Bruno", 4),
        ("Centro", "Olivia", 2),
        ("Parque", "Barrio Norte", 3),
        ("Parque", "Zona Comercial", 5),
        ("Parque", "Mariana", 3),
        ("Parque", "Lucas", 5),
        ("Parque", "Nicolas", 4),
        ("Hospital", "Renata", 3),
        ("Hospital", "Zoe", 4),
        ("Hospital", "Barrio Sur", 6),
        ("Universidad", "Camila", 3),
        ("Universidad", "Diego", 4),
        ("Universidad", "Bruno", 5),
        ("Universidad", "Barrio Sur", 3),
        ("Barrio Norte", "Diego", 4),
        ("Barrio Norte", "Elena", 3),
        ("Barrio Norte", "Fabio", 6),
        ("Zona Comercial", "Samuel", 3),
        ("Zona Comercial", "Valentina", 4),
        ("Zona Comercial", "Zoe", 3),
        ("Zona Comercial", "Barrio Sur", 5),
        ("Barrio Sur", "Irene", 3),
        ("Barrio Sur", "Julian", 4),
        ("Barrio Sur", "Hugo", 4),
        ("Barrio Sur", "Valentina", 3),
        ("Barrio Sur", "Estacion Metro", 5),
        ("Estacion Metro", "Samuel", 4),
        ("Estacion Metro", "Gabriela", 3),
        ("Estacion Metro", "Hugo", 4),
        ("Estacion Metro", "Fabio", 3),
        ("Plaza", "Karla", 3),
        ("Plaza", "Lucas", 3),
        ("Plaza", "Julian", 4),
        ("Plaza", "Zoe", 3),
        ("Plaza", "Hospital", 5),
        ("Plaza", "Barrio Sur", 4),
    ]

    for origin, destination, cost in streets:
        graph.add_edge(origin, destination, cost)

    return graph


DEFAULT_CUSTOMER_DESTINATIONS: tuple[str, ...] = (
    "Ana",
    "Bruno",
    "Camila",
    "Diego",
    "Elena",
    "Fabio",
    "Gabriela",
    "Hugo",
    "Irene",
    "Julian",
    "Karla",
    "Lucas",
    "Mariana",
    "Nicolas",
    "Olivia",
    "Pablo",
    "Renata",
    "Samuel",
    "Valentina",
    "Zoe",
)


DEFAULT_CITY_POSITIONS: dict[str, tuple[int, int]] = {
    "Bodega": (70, 310),
    "Centro": (230, 300),
    "Parque": (200, 500),
    "Hospital": (430, 300),
    "Universidad": (390, 120),
    "Zona Comercial": (600, 310),
    "Barrio Norte": (620, 120),
    "Barrio Sur": (620, 500),
    "Estacion Metro": (790, 310),
    "Plaza": (400, 500),
    "Ana": (80, 160),
    "Bruno": (170, 90),
    "Camila": (310, 50),
    "Diego": (520, 60),
    "Elena": (740, 80),
    "Fabio": (865, 160),
    "Gabriela": (870, 310),
    "Hugo": (850, 460),
    "Irene": (740, 575),
    "Julian": (580, 615),
    "Karla": (420, 610),
    "Lucas": (260, 610),
    "Mariana": (90, 545),
    "Nicolas": (60, 430),
    "Olivia": (100, 250),
    "Pablo": (330, 220),
    "Renata": (500, 220),
    "Samuel": (670, 240),
    "Valentina": (670, 390),
    "Zoe": (470, 430),
}
