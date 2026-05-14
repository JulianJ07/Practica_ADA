"""Interfaz grafica simple para el sistema de entregas.

La ventana permite visualizar el mapa como grafo, registrar pedidos, ordenar por
prioridad o por precio mayor y procesar entregas resaltando la ruta calculada
con Dijkstra.
"""

from __future__ import annotations

import tkinter as tk
from dataclasses import dataclass
from math import isinf
from tkinter import filedialog, messagebox, ttk

from city_graph import (
    DEFAULT_CITY_POSITIONS,
    DEFAULT_CUSTOMER_DESTINATIONS,
    RouteResult,
    WeightedGraph,
    build_default_city_graph,
)
from order_file import read_orders_from_txt
from orders import (
    DeliveryOrder,
    PRIORITY_LEVELS,
    PriorityOrderQueue,
    get_sort_mode_text,
)


DEFAULT_START_LOCATION = "Bodega"


@dataclass(frozen=True)
class DeliveryRecord:
    """Resumen de una entrega realizada desde la interfaz."""

    order: DeliveryOrder
    route: RouteResult


class DeliveryGUI:
    """Ventana principal del simulador grafico de entregas."""

    def __init__(self) -> None:
        """Configura el estado inicial de la aplicacion grafica."""
        self.graph: WeightedGraph = build_default_city_graph()
        self.positions = DEFAULT_CITY_POSITIONS
        self.order_queue = PriorityOrderQueue()
        self.current_location = DEFAULT_START_LOCATION
        self.delivery_records: list[DeliveryRecord] = []
        self.total_time = 0.0
        self.last_route: RouteResult | None = None
        self.highlighted_path: list[str] = []

        self.root = tk.Tk()
        self.root.title("Rutas de entrega con Dijkstra")
        self.root.geometry("1450x820")
        self.root.minsize(1280, 720)

        self._configure_style()
        self._build_layout()
        self._refresh_all()

    def run(self) -> None:
        """Inicia el ciclo principal de Tkinter."""
        self.root.mainloop()

    def _configure_style(self) -> None:
        """Define estilos basicos para widgets ttk."""
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TButton", padding=6)
        style.configure("TLabel", padding=2)
        style.configure("Title.TLabel", font=("Segoe UI", 15, "bold"))
        style.configure("Section.TLabelframe.Label", font=("Segoe UI", 10, "bold"))

    def _build_layout(self) -> None:
        """Crea los paneles principales de la interfaz."""
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=0)
        self.root.rowconfigure(0, weight=1)

        map_frame = ttk.Frame(self.root, padding=12)
        map_frame.grid(row=0, column=0, sticky="nsew")
        map_frame.rowconfigure(1, weight=1)
        map_frame.columnconfigure(0, weight=1)

        title = ttk.Label(
            map_frame,
            text="Mapa de entregas: grafo de la ciudad",
            style="Title.TLabel",
        )
        title.grid(row=0, column=0, sticky="w")

        self.canvas = tk.Canvas(
            map_frame,
            width=940,
            height=660,
            bg="#f7fafc",
            highlightthickness=1,
            highlightbackground="#cbd5e1",
        )
        self.canvas.grid(row=1, column=0, sticky="nsew", pady=(8, 0))

        side_frame = ttk.Frame(self.root, padding=(0, 12, 12, 12), width=330)
        side_frame.grid(row=0, column=1, sticky="ns")
        side_frame.grid_propagate(False)

        self._build_order_form(side_frame)
        self._build_pending_panel(side_frame)
        self._build_actions_panel(side_frame)
        self._build_report_panel(side_frame)

    def _build_order_form(self, parent: ttk.Frame) -> None:
        """Crea el formulario para registrar pedidos."""
        form = ttk.LabelFrame(parent, text="Registrar pedido", padding=10)
        form.pack(fill="x", pady=(0, 10))

        ttk.Label(form, text="Cliente").pack(anchor="w")
        self.customer_entry = ttk.Entry(form)
        self.customer_entry.pack(fill="x", pady=(0, 8))

        ttk.Label(form, text="Tipo de pedido").pack(anchor="w")
        self.product_type_entry = ttk.Entry(form)
        self.product_type_entry.pack(fill="x", pady=(0, 8))

        ttk.Label(form, text="Prioridad").pack(anchor="w")
        self.priority_combo = ttk.Combobox(
            form,
            values=list(PRIORITY_LEVELS.keys()),
            state="readonly",
        )
        self.priority_combo.current(0)
        self.priority_combo.pack(fill="x", pady=(0, 8))

        ttk.Label(form, text="Precio total").pack(anchor="w")
        self.price_entry = ttk.Entry(form)
        self.price_entry.pack(fill="x", pady=(0, 8))

        ttk.Label(form, text="Destino").pack(anchor="w")
        self.destination_combo = ttk.Combobox(
            form,
            values=list(DEFAULT_CUSTOMER_DESTINATIONS),
            state="readonly",
        )
        self.destination_combo.set("Ana")
        self.destination_combo.pack(fill="x", pady=(0, 10))

        ttk.Button(form, text="Agregar pedido", command=self.add_order).pack(fill="x")
        ttk.Button(
            form,
            text="Cargar pedidos desde TXT",
            command=self.load_orders_from_txt,
        ).pack(fill="x", pady=(6, 0))

    def _build_pending_panel(self, parent: ttk.Frame) -> None:
        """Crea el panel de pedidos pendientes."""
        pending = ttk.LabelFrame(parent, text="Pedidos pendientes", padding=10)
        pending.pack(fill="both", expand=True, pady=(0, 10))

        self.pending_listbox = tk.Listbox(
            pending,
            height=9,
            activestyle="dotbox",
            exportselection=False,
        )
        self.pending_listbox.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(
            pending,
            orient="vertical",
            command=self.pending_listbox.yview,
        )
        scrollbar.pack(side="right", fill="y")
        self.pending_listbox.configure(yscrollcommand=scrollbar.set)

    def _build_actions_panel(self, parent: ttk.Frame) -> None:
        """Crea botones de procesamiento y consulta de rutas."""
        actions = ttk.LabelFrame(parent, text="Acciones", padding=10)
        actions.pack(fill="x", pady=(0, 10))

        ttk.Button(
            actions,
            text="Calcular ruta de pedidos desde Bodega",
            command=self.preview_pending_orders_route,
        ).pack(fill="x", pady=(0, 6))

        ttk.Button(
            actions,
            text="Ordenar por prioridad",
            command=self.order_by_priority,
        ).pack(fill="x", pady=(0, 6))

        ttk.Button(
            actions,
            text="ORDENAR POR PRECIO",
            command=self.order_by_price,
        ).pack(fill="x", pady=(0, 6))

        ttk.Button(
            actions,
            text="Procesar siguiente pedido",
            command=self.process_next_order,
        ).pack(fill="x", pady=(0, 6))

        ttk.Button(
            actions,
            text="Procesar todos",
            command=self.process_all_orders,
        ).pack(fill="x", pady=(0, 6))

        ttk.Button(
            actions,
            text="Limpiar pedidos",
            command=self.clear_orders,
        ).pack(fill="x")

    def _build_report_panel(self, parent: ttk.Frame) -> None:
        """Crea el panel de estado y reporte."""
        report = ttk.LabelFrame(parent, text="Reporte", padding=10)
        report.pack(fill="both", expand=True)

        self.status_label = ttk.Label(report, text="", justify="left")
        self.status_label.pack(anchor="w", fill="x", pady=(0, 8))

        text_frame = ttk.Frame(report)
        text_frame.pack(fill="both", expand=True)

        self.route_text = tk.Text(text_frame, height=9, wrap="word")
        self.route_text.pack(side="left", fill="both", expand=True)
        route_scrollbar = ttk.Scrollbar(
            text_frame,
            orient="vertical",
            command=self.route_text.yview,
        )
        route_scrollbar.pack(side="right", fill="y")
        self.route_text.configure(yscrollcommand=route_scrollbar.set)
        self.route_text.configure(state="disabled")

    def add_order(self) -> None:
        """Agrega un pedido a la cola y actualiza el mapa."""
        customer = self.customer_entry.get().strip()
        product_type = self.product_type_entry.get().strip()
        priority = self.priority_combo.get().strip()
        price = self.price_entry.get().strip()
        destination = self.destination_combo.get().strip()

        if not customer:
            messagebox.showwarning("Dato faltante", "Ingrese el nombre del cliente.")
            return

        try:
            order = self.order_queue.add_order(
                customer,
                product_type,
                priority,
                price,
                destination,
            )
        except ValueError as error:
            messagebox.showerror("Pedido no valido", str(error))
            return

        self.customer_entry.delete(0, tk.END)
        self.product_type_entry.delete(0, tk.END)
        self.price_entry.delete(0, tk.END)
        self._clear_route_highlight()
        self._set_route_message(
            f"Pedido #{order.order_id} agregado.\n"
            f"Prioridad: {order.priority_label}.\n"
            f"Precio: ${order.price:g}.\n"
            f"Destino: {order.destination}."
        )
        self._refresh_all()

    def load_orders_from_txt(self) -> None:
        """Carga varios pedidos desde un archivo TXT."""
        path = filedialog.askopenfilename(
            title="Seleccionar archivo de pedidos",
            filetypes=[
                ("Archivos de texto", "*.txt"),
                ("Archivos CSV", "*.csv"),
                ("Todos los archivos", "*.*"),
            ],
        )

        if not path:
            return

        try:
            order_inputs = read_orders_from_txt(path)
        except OSError as error:
            messagebox.showerror("No se pudo leer el archivo", str(error))
            return
        except ValueError as error:
            messagebox.showerror("Formato invalido", str(error))
            return

        self._reset_for_new_order_list()
        loaded_orders: list[DeliveryOrder] = []
        errors: list[str] = []

        for order_input in order_inputs:
            if order_input.destination not in DEFAULT_CUSTOMER_DESTINATIONS:
                errors.append(
                    f"Linea {order_input.line_number}: destino invalido "
                    f"'{order_input.destination}'. Debe ser un cliente del mapa."
                )
                continue

            try:
                loaded_orders.append(
                    self.order_queue.add_order(
                        customer_name=order_input.customer_name,
                        product_type=order_input.product_type,
                        priority=order_input.priority,
                        price=order_input.price,
                        destination=order_input.destination,
                    )
                )
            except ValueError as error:
                errors.append(f"Linea {order_input.line_number}: {error}")

        message = f"Pedidos cargados correctamente: {len(loaded_orders)}"

        if errors:
            message += "\n\nLineas no cargadas:\n" + "\n".join(errors)

        self._set_route_message(message)
        self._refresh_all()
        messagebox.showinfo("Carga finalizada", message)

    def order_by_priority(self) -> None:
        """Activa la atencion por prioridad y llegada."""
        self.order_queue.use_priority_order()
        self._clear_route_highlight()
        self._set_route_message("Pedidos ordenados por prioridad y orden de llegada.")
        self._refresh_all()

    def order_by_price(self) -> None:
        """Activa la atencion por precio mayor usando Merge Sort."""
        self.order_queue.use_price_order()
        self._clear_route_highlight()
        self._set_route_message(
            "Pedidos ordenados por precio mayor usando Merge Sort."
        )
        self._refresh_all()

    def preview_pending_orders_route(self) -> None:
        """Calcula la ruta completa para pedidos pendientes desde la bodega."""
        pending_orders = self.order_queue.peek_all()

        if not pending_orders:
            messagebox.showinfo("Sin pedidos", "No hay pedidos pendientes.")
            return

        current_location = DEFAULT_START_LOCATION
        total_cost = 0.0
        full_path = [DEFAULT_START_LOCATION]
        lines = [
            "Ruta planificada desde Bodega",
            f"Criterio: {get_sort_mode_text(self.order_queue.sort_mode)}",
            "",
        ]

        for order in pending_orders:
            route = self.graph.dijkstra(current_location, order.destination)

            if isinf(route.total_cost):
                lines.append(
                    f"Pedido #{order.order_id}: no hay ruta disponible hacia "
                    f"{order.destination}."
                )
                continue

            total_cost += route.total_cost
            full_path.extend(route.path[1:])
            lines.append(
                f"Pedido #{order.order_id} ({order.customer_name}) -> "
                f"{order.destination}: {' -> '.join(route.path)} "
                f"({route.total_cost:g} min)"
            )
            current_location = order.destination

        lines.append("")
        lines.append(f"Ruta completa: {' -> '.join(full_path)}")
        lines.append(f"Tiempo total estimado: {total_cost:g} minutos")

        self.last_route = None
        self.highlighted_path = full_path
        self._set_route_message("\n".join(lines))
        self._refresh_all()

    def process_next_order(self) -> None:
        """Atiende el siguiente pedido segun el criterio activo."""
        order = self.order_queue.pop_next()

        if order is None:
            messagebox.showinfo("Sin pedidos", "No hay pedidos pendientes.")
            return

        route = self.graph.dijkstra(self.current_location, order.destination)
        self.last_route = route
        self.highlighted_path = route.path
        self.delivery_records.append(DeliveryRecord(order=order, route=route))

        if not isinf(route.total_cost):
            self.current_location = order.destination
            self.total_time += route.total_cost

        self._set_route_message(
            f"Pedido entregado: #{order.order_id}\n"
            f"Cliente: {order.customer_name}\n"
            f"Tipo: {order.product_type}\n"
            f"Prioridad: {order.priority_label}\n"
            f"Precio: ${order.price:g}\n\n"
            f"{self._format_route_message(route)}"
        )
        self._refresh_all()

    def process_all_orders(self) -> None:
        """Procesa todos los pedidos pendientes."""
        if self.order_queue.is_empty():
            messagebox.showinfo("Sin pedidos", "No hay pedidos pendientes.")
            return

        while not self.order_queue.is_empty():
            self.process_next_order()

        messagebox.showinfo("Entregas finalizadas", "Todos los pedidos fueron procesados.")

    def clear_orders(self) -> None:
        """Limpia los pedidos y reinicia la simulacion del lote actual."""
        self._reset_for_new_order_list()
        self._set_route_message(
            "Pedidos limpiados.\n"
            "La simulacion volvio a iniciar desde Bodega."
        )
        self._refresh_all()

    def _refresh_all(self) -> None:
        """Actualiza lista, reporte y canvas."""
        self._refresh_pending_list()
        self._refresh_status()
        self._draw_map()

    def _refresh_pending_list(self) -> None:
        """Actualiza la lista visible de pedidos pendientes."""
        self.pending_listbox.delete(0, tk.END)

        for order in self.order_queue.peek_all():
            self.pending_listbox.insert(tk.END, self._format_order_summary(order))

    def _refresh_status(self) -> None:
        """Actualiza el resumen visible del estado de la simulacion."""
        self.status_label.configure(
            text=(
                f"Ubicacion actual: {self.current_location}\n"
                f"Criterio: {get_sort_mode_text(self.order_queue.sort_mode)}\n"
                f"Pendientes: {len(self.order_queue)}\n"
                f"Entregados: {len(self.delivery_records)}\n"
                f"Tiempo total: {self.total_time:g} min"
            )
        )

    def _draw_map(self) -> None:
        """Dibuja el grafo, pedidos y ruta actual en el canvas."""
        self.canvas.delete("all")
        highlighted_edges = self._route_edges(self.highlighted_path)
        pending_destinations = {order.destination for order in self.order_queue.peek_all()}

        for origin, destination, cost in self.graph.edges():
            x1, y1 = self.positions[origin]
            x2, y2 = self.positions[destination]
            edge_key = frozenset({origin, destination})
            is_highlighted = edge_key in highlighted_edges
            color = "#16a34a" if is_highlighted else "#94a3b8"
            width = 5 if is_highlighted else 2

            self.canvas.create_line(x1, y1, x2, y2, fill=color, width=width)
            self.canvas.create_text(
                (x1 + x2) / 2,
                (y1 + y2) / 2 - 10,
                text=f"{cost:g}",
                fill="#334155",
                font=("Segoe UI", 9, "bold"),
            )

        for node in self.graph.nodes():
            x, y = self.positions[node]
            fill = "#ffffff"
            outline = "#334155"
            width = 2

            if node == DEFAULT_START_LOCATION:
                fill = "#dbeafe"
                outline = "#2563eb"
            if node in pending_destinations:
                fill = "#fee2e2"
                outline = "#dc2626"
                width = 3
            if node == self.current_location:
                fill = "#dcfce7"
                outline = "#16a34a"
                width = 4

            self.canvas.create_oval(
                x - 15,
                y - 15,
                x + 15,
                y + 15,
                fill=fill,
                outline=outline,
                width=width,
            )
            self.canvas.create_text(
                x,
                y + 27,
                text=node,
                fill="#0f172a",
                font=("Segoe UI", 8, "bold"),
            )

        self._draw_legend()

    def _draw_legend(self) -> None:
        """Dibuja una leyenda breve en el mapa."""
        x, y = 20, 20
        items = [
            ("#dcfce7", "#16a34a", "Ubicacion actual"),
            ("#fee2e2", "#dc2626", "Destino pendiente"),
            ("#dbeafe", "#2563eb", "Bodega"),
            ("#16a34a", "#16a34a", "Ruta calculada"),
        ]

        self.canvas.create_rectangle(10, 10, 210, 118, fill="#ffffff", outline="#cbd5e1")
        for index, (fill, outline, label) in enumerate(items):
            item_y = y + index * 24
            if label == "Ruta calculada":
                self.canvas.create_line(x, item_y, x + 22, item_y, fill=outline, width=4)
            else:
                self.canvas.create_oval(
                    x,
                    item_y - 8,
                    x + 16,
                    item_y + 8,
                    fill=fill,
                    outline=outline,
                    width=2,
                )
            self.canvas.create_text(
                x + 32,
                item_y,
                text=label,
                anchor="w",
                fill="#0f172a",
                font=("Segoe UI", 9),
            )

    def _route_edges(self, path: list[str]) -> set[frozenset[str]]:
        """Convierte una ruta en un conjunto de aristas resaltables."""
        if not path:
            return set()

        return {
            frozenset({path[index], path[index + 1]})
            for index in range(len(path) - 1)
        }

    def _format_route_message(self, route: RouteResult) -> str:
        """Devuelve la ruta calculada en texto."""
        if isinf(route.total_cost):
            return f"No existe ruta entre {route.origin} y {route.destination}."

        return (
            f"Ruta: {' -> '.join(route.path)}\n"
            f"Tiempo estimado: {route.total_cost:g} minutos\n"
            f"Nodos revisados: {', '.join(route.visited_nodes)}"
        )

    def _format_order_summary(self, order: DeliveryOrder) -> str:
        """Devuelve un pedido pendiente como linea corta."""
        return (
            f"#{order.order_id} | ${order.price:g} | "
            f"{order.priority_label.upper()} | {order.product_type} | "
            f"{order.destination}"
        )

    def _set_route_message(self, message: str) -> None:
        """Actualiza el panel de texto de ruta y reporte."""
        self.route_text.configure(state="normal")
        self.route_text.delete("1.0", tk.END)
        self.route_text.insert(tk.END, message)
        self.route_text.configure(state="disabled")

    def _clear_route_highlight(self) -> None:
        """Limpia la ruta resaltada cuando cambia la lista de pedidos."""
        self.last_route = None
        self.highlighted_path = []

    def _reset_for_new_order_list(self) -> None:
        """Reinicia la simulacion al cargar un nuevo archivo de pedidos."""
        self.order_queue.clear()
        self.current_location = DEFAULT_START_LOCATION
        self.delivery_records.clear()
        self.total_time = 0.0
        self._clear_route_highlight()


def main() -> None:
    """Inicia la interfaz grafica."""
    app = DeliveryGUI()
    app.run()


if __name__ == "__main__":
    main()
