import logging
from typing import Callable

from .grid import Cell, Grid
from .utils.layout import LayoutType, PositionFactory
from .utils.geometry import Coordinates


class BasicLayoutGenerators:

    @staticmethod
    def stacked(grid: Grid, cell_pos: Coordinates):
        while True:
            yield grid.calculate_cell_center(cell_pos)


class LayoutGenerator:

    def __init__(self):
        self._log = logging.getLogger()
        self._position_factory = PositionFactory()

    def generate(self, grid: Grid, cell_pos: Coordinates):
        """
        Creates the generator of shapes' positions for the proper layout.
        """
        # TODO
        cell = grid.cell(cell_pos)
        generator = None
        self._log.debug(f"Layout {cell.layout}")
        if not cell.layout or cell.layout.display_type == LayoutType.STACK:
            generator = BasicLayoutGenerators.stacked(grid, cell_pos)
        elif cell.layout.display_type == LayoutType.LINE:
            generator = self.generate_lined(grid, cell_pos)
        else:
            self._log.error(
                f"Unknown or unmanaged layout type {cell.layout.display_type}, defaulting to stack."
            )
            generator = BasicLayoutGenerators.stacked(grid, cell_pos)
        return generator

    def generate_lined(self, grid: Grid, cell_pos: Coordinates):
        cell = grid.cell(cell_pos)
        nshapes = len(cell.content)
        start = grid.get_position_coordinates(
            cell_pos,
            (
                cell.layout.start
                if cell.layout.start
                else self._position_factory.get_position("left")
            ),
        )
        end = grid.get_position_coordinates(
            cell_pos,
            (
                cell.layout.end
                if cell.layout.end
                else self._position_factory.get_position("right")
            ),
        )
        item_vector = (end - start) / (nshapes + 1)
        for n in range(nshapes):
            yield start + item_vector * (n + 1)
