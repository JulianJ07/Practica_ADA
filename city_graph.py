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

    Los pesos representan minutos aproximados de recorrido. El mapa es pequeno
    para que sea facil de entender en una sustentacion academica.
    """
    graph = WeightedGraph()

    streets = [
        ("Bodega", "Centro", 4),
        ("Bodega", "Parque", 6),
        ("Centro", "Hospital", 5),
        ("Centro", "Universidad", 7),
        ("Centro", "Zona Comercial", 4),
        ("Parque", "Barrio Norte", 3),
        ("Parque", "Zona Comercial", 5),
        ("Barrio Norte", "Cliente Ana", 5),
        ("Hospital", "Cliente Ana", 4),
        ("Hospital", "Barrio Sur", 6),
        ("Universidad", "Cliente Luis", 6),
        ("Universidad", "Barrio Sur", 3),
        ("Zona Comercial", "Cliente Marta", 4),
        ("Zona Comercial", "Barrio Sur", 5),
        ("Barrio Sur", "Cliente Luis", 4),
        ("Barrio Sur", "Cliente Marta", 6),
    ]

    for origin, destination, cost in streets:
        graph.add_edge(origin, destination, cost)

    return graph


DEFAULT_CITY_POSITIONS: dict[str, tuple[int, int]] = {
    "Bodega": (80, 280),
    "Centro": (250, 250),
    "Parque": (220, 430),
    "Barrio Norte": (430, 470),
    "Cliente Ana": (610, 430),
    "Hospital": (500, 230),
    "Universidad": (440, 90),
    "Cliente Luis": (680, 80),
    "Zona Comercial": (420, 330),
    "Barrio Sur": (620, 250),
    "Cliente Marta": (700, 360),
}
