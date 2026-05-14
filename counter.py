"""Simulador de desembarco de pasajeros en terminales aeroportuarias.

Este archivo es el punto de entrada del programa. Desde aqui se solicitan los
datos al usuario, se comparan varias estrategias de asignacion, se recomienda
la estrategia greedy y se ejecuta una simulacion por ticks.
"""

from __future__ import annotations

import csv
import random
from dataclasses import dataclass
from datetime import datetime
from itertools import product
from math import ceil
from pathlib import Path
from time import sleep

from plane import Plane
from terminal import Terminal


AUTOMATIC_DELAY_SECONDS = 0.35
RANDOM_SEED = 42
BRUTE_FORCE_MAX_COMBINATIONS = 100_000


@dataclass(frozen=True)
class AlgorithmResult:
    """Resultado estimado de una estrategia de asignacion."""

    name: str
    terminals: list[Terminal]
    estimated_ticks: int
    description: str


@dataclass(frozen=True)
class SimulationLogEntry:
    """Registro de lo ocurrido en una terminal durante un tick."""

    tick: int
    terminal_code: str
    plane_code: str
    processed_passengers: int
    remaining_passengers: int
    message: str


@dataclass(frozen=True)
class TerminalStatistics:
    """Estadisticas finales de una terminal."""

    terminal_code: str
    capacity: int
    assigned_planes: int
    processed_passengers: int
    work_ticks: int
    average_passengers_per_tick: float


@dataclass(frozen=True)
class SimulationStatistics:
    """Resumen estadistico de toda la simulacion."""

    total_ticks: int
    total_passengers: int
    average_passengers_per_tick: float
    most_used_terminal: TerminalStatistics
    least_used_terminal: TerminalStatistics
    terminals: list[TerminalStatistics]


@dataclass(frozen=True)
class SimulationResult:
    """Resultado completo de una simulacion."""

    total_ticks: int
    log_entries: list[SimulationLogEntry]


def read_positive_integer(prompt: str) -> int:
    """Solicita un numero entero positivo al usuario.

    La funcion se repite hasta recibir un valor valido. Esto evita errores
    comunes de entrada, como textos, numeros negativos o cero.
    """
    while True:
        raw_value = input(prompt).strip()

        try:
            value = int(raw_value)
        except ValueError:
            print("Entrada no valida. Debes ingresar un numero entero.")
            continue

        if value <= 0:
            print("Entrada no valida. El numero debe ser mayor que cero.")
            continue

        return value


def read_yes_no(prompt: str) -> bool:
    """Lee una respuesta afirmativa o negativa del usuario."""
    while True:
        answer = input(prompt).strip().lower()

        if answer in {"s", "si", "y", "yes"}:
            return True
        if answer in {"n", "no"}:
            return False

        print("Respuesta no valida. Escribe 's' para si o 'n' para no.")


def read_simulation_mode() -> str:
    """Permite al usuario elegir entre simulacion manual o automatica."""
    while True:
        mode = input("Seleccione el modo de simulacion (manual/automatico): ")
        normalized_mode = mode.strip().lower()

        if normalized_mode in {"manual", "m"}:
            return "manual"
        if normalized_mode in {"automatico", "automatic", "a"}:
            return "automatico"

        print("Modo no valido. Escribe 'manual' o 'automatico'.")


def create_terminals() -> list[Terminal]:
    """Crea las terminales a partir de los datos ingresados por el usuario."""
    terminal_count = read_positive_integer("Ingrese el numero de terminales: ")
    terminals: list[Terminal] = []

    for index in range(1, terminal_count + 1):
        capacity = read_positive_integer(
            f"Ingrese la capacidad de procesamiento de la terminal T{index}: "
        )
        terminals.append(Terminal(identifier=index, capacity=capacity))

    return terminals


def create_planes() -> list[Plane]:
    """Crea los aviones a partir de los datos ingresados por el usuario."""
    plane_count = read_positive_integer("Ingrese el numero de aviones: ")
    planes: list[Plane] = []

    for index in range(1, plane_count + 1):
        passengers = read_positive_integer(
            f"Ingrese la cantidad de pasajeros del avion A{index}: "
        )
        planes.append(Plane(identifier=index, passengers=passengers))

    return planes


def clone_plane(plane: Plane) -> Plane:
    """Crea una copia limpia de un avion para una nueva asignacion."""
    return Plane(identifier=plane.identifier, passengers=plane.passengers)


def create_empty_terminal_copies(terminals: list[Terminal]) -> list[Terminal]:
    """Crea copias vacias de las terminales base.

    Cada algoritmo necesita su propia lista de terminales para que las
    asignaciones no se mezclen entre estrategias.
    """
    return [
        Terminal(identifier=terminal.identifier, capacity=terminal.capacity)
        for terminal in terminals
    ]


def calculate_total_estimated_ticks(terminals: list[Terminal]) -> int:
    """Calcula el tiempo total estimado de una configuracion."""
    return max((terminal.estimated_total_ticks() for terminal in terminals), default=0)


def assign_planes_fifo(planes: list[Plane], terminals: list[Terminal]) -> list[Terminal]:
    """Asigna aviones en orden de llegada alternando terminales.

    Esta estrategia sirve como punto de comparacion basico. No intenta optimizar;
    simplemente reparte los aviones segun su orden original.
    """
    assigned_terminals = create_empty_terminal_copies(terminals)

    for index, plane in enumerate(planes):
        terminal = assigned_terminals[index % len(assigned_terminals)]
        terminal.assign_plane(clone_plane(plane))

    return assigned_terminals


def assign_planes_randomly(
    planes: list[Plane],
    terminals: list[Terminal],
    seed: int = RANDOM_SEED,
) -> list[Terminal]:
    """Asigna aviones de forma aleatoria usando una semilla reproducible."""
    assigned_terminals = create_empty_terminal_copies(terminals)
    generator = random.Random(seed)

    for plane in planes:
        terminal = generator.choice(assigned_terminals)
        terminal.assign_plane(clone_plane(plane))

    return assigned_terminals


def assign_planes_greedily(planes: list[Plane], terminals: list[Terminal]) -> list[Terminal]:
    """Asigna aviones a terminales usando una estrategia greedy.

    La heuristica ordena los aviones de mayor a menor cantidad de pasajeros.
    Luego, cada avion se asigna a la terminal donde produzca el menor tiempo
    acumulado estimado de desembarco.

    Esta estrategia no revisa todas las combinaciones posibles; por eso se
    considera una solucion aproximada. Sin embargo, es practica, facil de
    entender y adecuada para escenarios academicos de simulacion.
    """
    assigned_terminals = create_empty_terminal_copies(terminals)
    sorted_planes = sorted(planes, key=lambda plane: plane.passengers, reverse=True)

    for plane in sorted_planes:
        best_terminal = min(
            assigned_terminals,
            key=lambda terminal: (
                terminal.estimated_total_ticks()
                + ceil(plane.passengers / terminal.capacity),
                terminal.estimated_total_passengers(),
                terminal.identifier,
            ),
        )
        best_terminal.assign_plane(clone_plane(plane))

    return assigned_terminals


def assign_planes_by_brute_force(
    planes: list[Plane],
    terminals: list[Terminal],
) -> list[Terminal] | None:
    """Busca la mejor asignacion exacta cuando el caso es pequeno.

    La fuerza bruta prueba todas las combinaciones posibles. Por eso se limita
    a casos pequenos; de lo contrario, el numero de combinaciones crece muy
    rapido y el programa se vuelve lento.
    """
    total_combinations = len(terminals) ** len(planes)
    if total_combinations > BRUTE_FORCE_MAX_COMBINATIONS:
        return None

    best_assignment: tuple[int, ...] | None = None
    best_score: tuple[int, int, int] | None = None

    for assignment in product(range(len(terminals)), repeat=len(planes)):
        terminal_ticks = [0 for _ in terminals]
        terminal_passengers = [0 for _ in terminals]

        for plane_index, terminal_index in enumerate(assignment):
            plane = planes[plane_index]
            capacity = terminals[terminal_index].capacity
            terminal_ticks[terminal_index] += ceil(plane.passengers / capacity)
            terminal_passengers[terminal_index] += plane.passengers

        score = (
            max(terminal_ticks),
            sum(terminal_ticks),
            max(terminal_passengers),
        )

        if best_score is None or score < best_score:
            best_score = score
            best_assignment = assignment

    assigned_terminals = create_empty_terminal_copies(terminals)

    if best_assignment is None:
        return assigned_terminals

    for plane_index, terminal_index in enumerate(best_assignment):
        assigned_terminals[terminal_index].assign_plane(clone_plane(planes[plane_index]))

    return assigned_terminals


def compare_algorithms(
    planes: list[Plane],
    terminals: list[Terminal],
) -> tuple[list[AlgorithmResult], str | None]:
    """Ejecuta varias estrategias y devuelve sus resultados estimados."""
    results: list[AlgorithmResult] = []

    strategies = [
        (
            "FIFO simple",
            assign_planes_fifo(planes, terminals),
            "Asigna en orden de llegada alternando terminales.",
        ),
        (
            "Aleatorio",
            assign_planes_randomly(planes, terminals),
            f"Asigna con seleccion aleatoria reproducible, semilla {RANDOM_SEED}.",
        ),
        (
            "Greedy",
            assign_planes_greedily(planes, terminals),
            "Ordena de mayor a menor y elige la terminal con menor carga estimada.",
        ),
    ]

    for name, assigned_terminals, description in strategies:
        results.append(
            AlgorithmResult(
                name=name,
                terminals=assigned_terminals,
                estimated_ticks=calculate_total_estimated_ticks(assigned_terminals),
                description=description,
            )
        )

    brute_force_terminals = assign_planes_by_brute_force(planes, terminals)
    brute_force_note = None

    if brute_force_terminals is None:
        combinations = len(terminals) ** len(planes)
        brute_force_note = (
            "La fuerza bruta no se ejecuto porque el caso tiene "
            f"{combinations} combinaciones posibles, mas que el limite de "
            f"{BRUTE_FORCE_MAX_COMBINATIONS}."
        )
    else:
        results.append(
            AlgorithmResult(
                name="Fuerza bruta",
                terminals=brute_force_terminals,
                estimated_ticks=calculate_total_estimated_ticks(brute_force_terminals),
                description="Prueba todas las combinaciones posibles en casos pequenos.",
            )
        )

    return results, brute_force_note


def get_result_by_name(results: list[AlgorithmResult], name: str) -> AlgorithmResult:
    """Busca un resultado de algoritmo por nombre."""
    for result in results:
        if result.name == name:
            return result

    raise ValueError(f"No se encontro el algoritmo {name}.")


def format_assigned_planes(terminal: Terminal) -> str:
    """Convierte la lista de aviones asignados a texto legible."""
    assigned_planes = ", ".join(str(plane) for plane in terminal.planes)
    return assigned_planes if assigned_planes else "Sin aviones"


def show_algorithm_comparison(
    results: list[AlgorithmResult],
    brute_force_note: str | None,
) -> None:
    """Muestra una tabla comparativa de las estrategias evaluadas."""
    print("\nCOMPARACION DE ESTRATEGIAS")
    print("-" * 88)
    print(f"{'Estrategia':<18}{'Ticks':<10}{'Descripcion'}")
    print("-" * 88)

    for result in sorted(results, key=lambda item: item.estimated_ticks):
        print(f"{result.name:<18}{result.estimated_ticks:<10}{result.description}")

    if brute_force_note:
        print("-" * 88)
        print(brute_force_note)

    print("-" * 88)
    print(
        "Nota: el greedy es una solucion aproximada. En muchos casos mejora "
        "las estrategias simples, pero no siempre garantiza el optimo absoluto."
    )


def show_recommended_configuration(result: AlgorithmResult) -> None:
    """Muestra la distribucion sugerida de aviones por terminal."""
    print(f"\nCONFIGURACION RECOMENDADA ({result.name.upper()})")
    print("-" * 72)

    for terminal in result.terminals:
        print(
            f"{terminal.code} | "
            f"capacidad: {terminal.capacity} pasajeros/tick | "
            f"ticks estimados: {terminal.estimated_total_ticks()}"
        )
        print(f"Aviones asignados: {format_assigned_planes(terminal)}")
        print("-" * 72)

    print(f"Tiempo total estimado del proceso: {result.estimated_ticks} ticks\n")


def show_tick_results(tick: int, terminals: list[Terminal]) -> list[SimulationLogEntry]:
    """Procesa y muestra el avance de todas las terminales en un tick."""
    print(f"\nTick {tick}")
    print("-" * 72)
    entries: list[SimulationLogEntry] = []

    for terminal in terminals:
        result = terminal.process_tick()
        plane_code = result.plane_code if result.plane_code is not None else "-"

        if result.plane_code is None:
            print(f"{result.terminal_code}: {result.message}")
        else:
            print(
                f"{result.terminal_code} atiende {result.plane_code}: "
                f"desembarcan {result.processed_passengers} pasajero(s), "
                f"quedan {result.remaining_passengers}. {result.message}"
            )

        entries.append(
            SimulationLogEntry(
                tick=tick,
                terminal_code=result.terminal_code,
                plane_code=plane_code,
                processed_passengers=result.processed_passengers,
                remaining_passengers=result.remaining_passengers,
                message=result.message,
            )
        )

    return entries


def simulate_disembarkation(terminals: list[Terminal], mode: str) -> SimulationResult:
    """Ejecuta la simulacion por ticks hasta terminar el desembarco.

    Args:
        terminals: Lista de terminales con sus aviones ya asignados.
        mode: Puede ser ``manual`` o ``automatico``.

    Returns:
        Un objeto con el total de ticks y el registro detallado de la simulacion.
    """
    for terminal in terminals:
        terminal.reset_simulation()

    tick = 0
    log_entries: list[SimulationLogEntry] = []
    print("\nINICIO DE LA SIMULACION")
    print("-" * 72)

    while any(terminal.has_pending_work() for terminal in terminals):
        tick += 1
        log_entries.extend(show_tick_results(tick, terminals))

        if any(terminal.has_pending_work() for terminal in terminals):
            if mode == "manual":
                input("\nPresione Enter para avanzar al siguiente tick...")
            else:
                sleep(AUTOMATIC_DELAY_SECONDS)

    print("\nSIMULACION FINALIZADA")
    print("-" * 72)
    print(f"Todos los pasajeros han desembarcado en {tick} tick(s).")
    return SimulationResult(total_ticks=tick, log_entries=log_entries)


def calculate_statistics(
    terminals: list[Terminal],
    total_ticks: int,
) -> SimulationStatistics:
    """Calcula estadisticas finales por terminal y de toda la simulacion."""
    terminal_statistics: list[TerminalStatistics] = []

    for terminal in terminals:
        processed_passengers = terminal.estimated_total_passengers()
        work_ticks = terminal.estimated_total_ticks()
        average = processed_passengers / total_ticks if total_ticks else 0

        terminal_statistics.append(
            TerminalStatistics(
                terminal_code=terminal.code,
                capacity=terminal.capacity,
                assigned_planes=len(terminal.planes),
                processed_passengers=processed_passengers,
                work_ticks=work_ticks,
                average_passengers_per_tick=average,
            )
        )

    total_passengers = sum(item.processed_passengers for item in terminal_statistics)
    average_passengers = total_passengers / total_ticks if total_ticks else 0
    most_used = max(
        terminal_statistics,
        key=lambda item: (item.work_ticks, item.processed_passengers),
    )
    least_used = min(
        terminal_statistics,
        key=lambda item: (item.work_ticks, item.processed_passengers),
    )

    return SimulationStatistics(
        total_ticks=total_ticks,
        total_passengers=total_passengers,
        average_passengers_per_tick=average_passengers,
        most_used_terminal=most_used,
        least_used_terminal=least_used,
        terminals=terminal_statistics,
    )


def show_final_statistics(statistics: SimulationStatistics) -> None:
    """Muestra las estadisticas finales de la simulacion."""
    print("\nESTADISTICAS FINALES")
    print("-" * 88)
    print(f"Tiempo total: {statistics.total_ticks} tick(s)")
    print(f"Total de pasajeros procesados: {statistics.total_passengers}")
    print(
        "Promedio general de pasajeros por tick: "
        f"{statistics.average_passengers_per_tick:.2f}"
    )
    print(
        "Terminal mas usada: "
        f"{statistics.most_used_terminal.terminal_code} "
        f"({statistics.most_used_terminal.work_ticks} tick(s) de trabajo)"
    )
    print(
        "Terminal menos usada: "
        f"{statistics.least_used_terminal.terminal_code} "
        f"({statistics.least_used_terminal.work_ticks} tick(s) de trabajo)"
    )
    print("-" * 88)
    print(
        f"{'Terminal':<12}{'Aviones':<10}{'Pasajeros':<12}"
        f"{'Ticks':<10}{'Promedio/tick'}"
    )
    print("-" * 88)

    for item in statistics.terminals:
        print(
            f"{item.terminal_code:<12}"
            f"{item.assigned_planes:<10}"
            f"{item.processed_passengers:<12}"
            f"{item.work_ticks:<10}"
            f"{item.average_passengers_per_tick:.2f}"
        )


def export_results(
    selected_result: AlgorithmResult,
    comparison_results: list[AlgorithmResult],
    brute_force_note: str | None,
    simulation_result: SimulationResult,
    statistics: SimulationStatistics,
) -> tuple[Path, Path]:
    """Exporta la simulacion a archivos TXT y CSV."""
    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    txt_path = reports_dir / f"reporte_simulacion_{timestamp}.txt"
    csv_path = reports_dir / f"simulacion_{timestamp}.csv"

    with txt_path.open("w", encoding="utf-8") as report:
        report.write("REPORTE DE SIMULACION DE DESEMBARCO\n")
        report.write("=" * 72 + "\n\n")
        report.write(f"Estrategia simulada: {selected_result.name}\n")
        report.write(f"Tiempo total: {simulation_result.total_ticks} tick(s)\n")
        report.write(f"Pasajeros procesados: {statistics.total_passengers}\n")
        report.write(
            "Promedio general de pasajeros por tick: "
            f"{statistics.average_passengers_per_tick:.2f}\n\n"
        )

        report.write("COMPARACION DE ESTRATEGIAS\n")
        report.write("-" * 72 + "\n")
        for result in sorted(comparison_results, key=lambda item: item.estimated_ticks):
            report.write(f"{result.name}: {result.estimated_ticks} tick(s)\n")
        if brute_force_note:
            report.write(f"{brute_force_note}\n")

        report.write("\nCONFIGURACION SIMULADA\n")
        report.write("-" * 72 + "\n")
        for terminal in selected_result.terminals:
            report.write(
                f"{terminal.code} | capacidad {terminal.capacity} | "
                f"ticks {terminal.estimated_total_ticks()}\n"
            )
            report.write(f"Aviones: {format_assigned_planes(terminal)}\n")

        report.write("\nESTADISTICAS POR TERMINAL\n")
        report.write("-" * 72 + "\n")
        for item in statistics.terminals:
            report.write(
                f"{item.terminal_code}: {item.assigned_planes} avion(es), "
                f"{item.processed_passengers} pasajero(s), "
                f"{item.work_ticks} tick(s), "
                f"promedio {item.average_passengers_per_tick:.2f} pasajeros/tick\n"
            )

        report.write("\nREGISTRO POR TICKS\n")
        report.write("-" * 72 + "\n")
        for entry in simulation_result.log_entries:
            report.write(
                f"Tick {entry.tick} | {entry.terminal_code} | "
                f"Avion {entry.plane_code} | "
                f"Procesados {entry.processed_passengers} | "
                f"Restantes {entry.remaining_passengers} | {entry.message}\n"
            )

    with csv_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(
            [
                "tick",
                "terminal",
                "avion",
                "pasajeros_desembarcados",
                "pasajeros_restantes",
                "mensaje",
            ]
        )
        for entry in simulation_result.log_entries:
            writer.writerow(
                [
                    entry.tick,
                    entry.terminal_code,
                    entry.plane_code,
                    entry.processed_passengers,
                    entry.remaining_passengers,
                    entry.message,
                ]
            )

    return txt_path, csv_path


def main() -> None:
    """Controla el flujo principal de la aplicacion."""
    print("=" * 72)
    print("SIMULADOR DE DESEMBARCO DE PASAJEROS")
    print("=" * 72)

    terminals = create_terminals()
    planes = create_planes()

    comparison_results, brute_force_note = compare_algorithms(planes, terminals)
    show_algorithm_comparison(comparison_results, brute_force_note)

    selected_result = get_result_by_name(comparison_results, "Greedy")
    show_recommended_configuration(selected_result)

    mode = read_simulation_mode()
    simulation_result = simulate_disembarkation(selected_result.terminals, mode)
    statistics = calculate_statistics(
        selected_result.terminals,
        simulation_result.total_ticks,
    )
    show_final_statistics(statistics)

    if read_yes_no("\nDesea exportar los resultados a TXT y CSV? (s/n): "):
        txt_path, csv_path = export_results(
            selected_result=selected_result,
            comparison_results=comparison_results,
            brute_force_note=brute_force_note,
            simulation_result=simulation_result,
            statistics=statistics,
        )
        print(f"Reporte TXT guardado en: {txt_path}")
        print(f"Registro CSV guardado en: {csv_path}")


if __name__ == "__main__":
    main()
