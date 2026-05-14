"""Lectura de pedidos desde archivos de texto.

El archivo esperado usa una linea por pedido con campos separados por punto y
coma:

cliente;tipo_pedido;destino

Tambien se permiten lineas vacias, comentarios iniciados con ``#`` y una fila
de encabezado opcional.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class OrderInput:
    """Pedido leido desde un archivo de texto."""

    customer_name: str
    product_type: str
    destination: str
    line_number: int


def read_orders_from_txt(path: str | Path) -> list[OrderInput]:
    """Lee pedidos desde un archivo TXT separado por punto y coma.

    Args:
        path: Ruta del archivo a leer.

    Returns:
        Lista de pedidos leidos del archivo.

    Raises:
        ValueError: Si una linea no tiene los tres campos requeridos.
    """
    file_path = Path(path)
    orders: list[OrderInput] = []

    with file_path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.reader(file, delimiter=";")

        for line_number, row in enumerate(reader, start=1):
            clean_row = [value.strip() for value in row]

            if not clean_row or not any(clean_row):
                continue

            first_value = clean_row[0]
            if first_value.startswith("#"):
                continue

            if _is_header(clean_row):
                continue

            if len(clean_row) != 3 or not all(clean_row):
                raise ValueError(
                    f"Linea {line_number}: usa el formato "
                    "cliente;tipo_pedido;destino."
                )

            orders.append(
                OrderInput(
                    customer_name=clean_row[0],
                    product_type=clean_row[1],
                    destination=clean_row[2],
                    line_number=line_number,
                )
            )

    return orders


def _is_header(row: list[str]) -> bool:
    """Detecta una fila de encabezado comun."""
    normalized = [value.lower().replace(" ", "_") for value in row]
    return normalized == ["cliente", "tipo_pedido", "destino"]
