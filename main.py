"""Punto de entrada del sistema de entregas."""

from delivery_app import DeliveryApp


def main() -> None:
    """Inicia la aplicacion de consola."""
    app = DeliveryApp()
    app.run()


if __name__ == "__main__":
    main()
