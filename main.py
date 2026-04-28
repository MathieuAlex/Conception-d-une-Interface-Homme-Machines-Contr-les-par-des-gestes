"""
main.py — Entry point for the Virtual Mouse application.

Usage
-----
    python main.py

Author: Alex Mathieu
"""

from virtual_mouse import VirtualMouse
from ui import VirtualMouseUI


def main() -> None:
    vm = VirtualMouse()
    app = VirtualMouseUI(vm)
    app.run()


if __name__ == "__main__":
    main()
