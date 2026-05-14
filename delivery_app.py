"""Aplicacion de consola para simular rutas de entrega.

La aplicacion combina tres ideas principales:

- un grafo ponderado para representar el mapa de la ciudad;
- Dijkstra para calcular la ruta mas corta entre dos puntos;
- una cola de prioridad para atender pedidos segun urgencia y llegada.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isinf

from city_graph import RouteResult, WeightedGraph, build_default_city_graph
from order_file import read_orders_from_txt
from orders import DeliveryOrder, PriorityOrderQueue, get_priority_options_text


DEFAULT_START_LOCATION = "Bodega"


@dataclass(frozen=True)
class DeliveredOrder:
    """Resumen de un pedido entregado."""

    order: DeliveryOrder
    route: RouteResult


class DeliveryApp:
    """Controla el menu principal y la simulacion de entregas."""

    def __init__(self, graph: WeightedGraph | None = None) -> None:
        """Inicializa el sistema con un mapa y una cola de pedidos."""
        self.graph = graph if graph is not None else build_default_city_graph()
        self.order_queue = PriorityOrderQueue()
        self.current_location = DEFAULT_START_LOCATION
        self.delivered_orders: list[DeliveredOrder] = []
        self.total_delivery_time = 0.0

    def run(self) -> None:
        """Ejecuta el menu interactivo hasta que el usuario decida salir."""
        print("=" * 78)
        print("SISTEMA DE RUTAS DE ENTREGA CON GRAFOS Y DIJKSTRA")
        print("=" * 78)

        while True:
            self._print_menu()
            option = input("Seleccione una opcion: ").strip()

            if option == "1":
                self.show_city_map()
            elif option == "2":
                self.show_available_locations()
            elif option == "3":
                self.register_order()
            elif option == "4":
                self.show_pending_orders()
            elif option == "5":
                self.calculate_route_between_locations()
            elif option == "6":
                self.load_orders_from_txt()
            elif option == "7":
                self.process_next_order()
            elif option == "8":
                self.process_all_orders()
            elif option == "9":
                self.show_final_report()
            elif option == "0":
                print("Programa finalizado.")
                break
            else:
                print("Opcion no valida. Intente nuevamente.")

    def show_city_map(self) -> None:
        """Muestra el mapa como lista de conexiones."""
        print("\nMAPA DE LA CIUDAD")
        print("-" * 78)
        print(self.graph.describe())

    def show_available_locations(self) -> None:
        """Muestra todos los nodos disponibles en el mapa."""
        print("\nPUNTOS DISPONIBLES")
        print("-" * 78)
        for index, node in enumerate(self.graph.nodes(), start=1):
            print(f"{index}. {node}")

    def register_order(self) -> None:
        """Registra un pedido ingresado por el usuario."""
        print("\nREGISTRAR PEDIDO")
        print("-" * 78)
        print("Tipos de pedido disponibles:")
        print(get_priority_options_text())

        customer_name = input("Nombre del cliente: ").strip()
        product_type = input("Tipo de pedido: ").strip()
        destination = self._read_location("Destino del pedido: ")

        try:
            order = self.order_queue.add_order(
                customer_name=customer_name,
                product_type=product_type,
                destination=destination,
            )
        except ValueError as error:
            print(error)
            return

        print(
            f"Pedido #{order.order_id} registrado con prioridad "
            f"{order.priority_label}."
        )

    def show_pending_orders(self) -> None:
        """Muestra la cola de pedidos en el orden de atencion."""
        print("\nPEDIDOS PENDIENTES")
        print("-" * 78)

        pending_orders = self.order_queue.peek_all()
        if not pending_orders:
            print("No hay pedidos pendientes.")
            return

        for order in pending_orders:
            print(self._format_order(order))

    def calculate_route_between_locations(self) -> None:
        """Permite consultar una ruta sin registrar un pedido."""
        print("\nCONSULTAR RUTA MAS CORTA")
        print("-" * 78)
        origin = self._read_location("Origen: ")
        destination = self._read_location("Destino: ")
        route = self.graph.dijkstra(origin, destination)
        self._print_route(route)

    def load_orders_from_txt(self) -> None:
        """Carga pedidos desde un archivo TXT separado por punto y coma."""
        print("\nCARGAR PEDIDOS DESDE TXT")
        print("-" * 78)
        print("Formato esperado: cliente;tipo_pedido;destino")
        path = input("Ruta del archivo TXT: ").strip().strip('"')

        try:
            order_inputs = read_orders_from_txt(path)
        except OSError as error:
            print(f"No se pudo leer el archivo: {error}")
            return
        except ValueError as error:
            print(error)
            return

        loaded_count = 0
        errors: list[str] = []

        for order_input in order_inputs:
            if not self.graph.has_node(order_input.destination):
                errors.append(
                    f"Linea {order_input.line_number}: destino inexistente "
                    f"'{order_input.destination}'."
                )
                continue

            try:
                self.order_queue.add_order(
                    customer_name=order_input.customer_name,
                    product_type=order_input.product_type,
                    destination=order_input.destination,
                )
                loaded_count += 1
            except ValueError as error:
                errors.append(f"Linea {order_input.line_number}: {error}")

        print(f"Pedidos cargados correctamente: {loaded_count}")

        if errors:
            print("Lineas no cargadas:")
            for error in errors:
                print(f"- {error}")

    def process_next_order(self) -> None:
        """Procesa el siguiente pedido pendiente."""
        order = self.order_queue.pop_next()

        if order is None:
            print("\nNo hay pedidos pendientes para entregar.")
            return

        delivered_order = self._deliver_order(order)
        self.delivered_orders.append(delivered_order)
        self.current_location = order.destination
        self.total_delivery_time += delivered_order.route.total_cost

    def process_all_orders(self) -> None:
        """Procesa todos los pedidos pendientes en orden de prioridad."""
        if self.order_queue.is_empty():
            print("\nNo hay pedidos pendientes para entregar.")
            return

        while not self.order_queue.is_empty():
            self.process_next_order()

        print("\nTodos los pedidos pendientes fueron procesados.")

    def show_final_report(self) -> None:
        """Muestra un reporte de pedidos entregados y tiempo recorrido."""
        print("\nREPORTE FINAL")
        print("=" * 78)
        print(f"Ubicacion actual del repartidor: {self.current_location}")
        print(f"Pedidos entregados: {len(self.delivered_orders)}")
        print(f"Pedidos pendientes: {len(self.order_queue)}")
        print(f"Tiempo total recorrido: {self.total_delivery_time:g} minutos")

        if not self.delivered_orders:
            print("Aun no se han entregado pedidos.")
            print("=" * 78)
            return

        print("\nDetalle de entregas")
        print("-" * 78)
        for delivered in self.delivered_orders:
            order = delivered.order
            route = delivered.route
            print(self._format_order(order))
            print(f"Ruta: {' -> '.join(route.path)}")
            print(f"Tiempo de esta entrega: {route.total_cost:g} minutos")
            print("-" * 78)

        print(
            "Conclusion: los pedidos se atendieron primero por prioridad y, "
            "cuando compartian prioridad, por orden de llegada."
        )
        print("=" * 78)

    def _deliver_order(self, order: DeliveryOrder) -> DeliveredOrder:
        """Calcula la ruta del pedido y registra su entrega."""
        print("\nENTREGA DE PEDIDO")
        print("-" * 78)
        print(self._format_order(order))
        route = self.graph.dijkstra(self.current_location, order.destination)

        if isinf(route.total_cost):
            print("No existe una ruta disponible para este pedido.")
            return DeliveredOrder(order=order, route=route)

        self._print_route(route)
        return DeliveredOrder(order=order, route=route)

    def _print_route(self, route: RouteResult) -> None:
        """Muestra una ruta calculada por Dijkstra."""
        if isinf(route.total_cost):
            print(f"No existe ruta entre {route.origin} y {route.destination}.")
            return

        print(f"Ruta mas corta: {' -> '.join(route.path)}")
        print(f"Tiempo total estimado: {route.total_cost:g} minutos")
        print(f"Nodos revisados por Dijkstra: {', '.join(route.visited_nodes)}")

    def _read_location(self, prompt: str) -> str:
        """Lee un nodo valido del mapa."""
        while True:
            location = input(prompt).strip()

            if self.graph.has_node(location):
                return location

            print("Ese punto no existe en el mapa. Opciones disponibles:")
            print(", ".join(self.graph.nodes()))

    def _format_order(self, order: DeliveryOrder) -> str:
        """Devuelve un pedido en formato legible."""
        return (
            f"Pedido #{order.order_id} | Cliente: {order.customer_name} | "
            f"Tipo: {order.product_type} | Prioridad: {order.priority_label} | "
            f"Llegada: {order.arrival_order} | Destino: {order.destination}"
        )

    def _print_menu(self) -> None:
        """Muestra las opciones principales."""
        print("\nMENU PRINCIPAL")
        print("-" * 78)
        print("1. Ver mapa de la ciudad")
        print("2. Ver puntos disponibles")
        print("3. Registrar pedido")
        print("4. Ver pedidos pendientes")
        print("5. Consultar ruta mas corta entre dos puntos")
        print("6. Cargar pedidos desde TXT")
        print("7. Procesar siguiente pedido")
        print("8. Procesar todos los pedidos")
        print("9. Ver reporte final")
        print("0. Salir")
