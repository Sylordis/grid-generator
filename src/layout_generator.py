"Module for layout generation, i.e. the way to place objects in a grid and/or cell."

import logging

from .grid import Grid
from .utils.layout import LayoutType, PositionFactory
from .utils.geometry import Coordinates


class BasicLayoutGenerators:
    """
    Generator for simple layouts.
    """

    @staticmethod
    def stacked(grid: Grid, cell_pos: Coordinates):
        """
        Generates the positions for objects in a stacked layout, i.e. all objects stacked in the middle.

        :param grid: the grid where to generated the layout for
        :param cell_pos: the position of the cell to generate the layout for
        """
        while True:
            yield grid.calculate_cell_center(cell_pos)


class LayoutGenerator:
    """
    Generates layouts.
    """

    def __init__(self):
        self._log = logging.getLogger()
        "Class logger."
        self._position_factory = PositionFactory()
        "Factory for creating positions."

    def generate(self, grid: Grid, cell_pos: Coordinates):
        """
        Creates the generator of shapes' positions for the proper layout.
        This method is a dispatcher to other methods in order to create generators according to layouts.

        :param grid: grid
        :param cell_pos: coordinates of the cell in the grid
        :return: a generator with all center positions for the cell's shapes.
        """
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
        """
        Generates the positions for a line layout.

        :param grid: grid
        :param cell_pos: coordinates of the cell in the grid
        :return: a generator with all center positions for the cell's shapes.
        """
        cell = grid.cell(cell_pos)
        start = grid.get_position_coordinates(
            cell_pos,
            (
                cell.layout.start
                if cell.layout.has_keypoints and cell.layout.start
                else self._position_factory.get_position("left")
            ),
        )
        end = grid.get_position_coordinates(
            cell_pos,
            (
                cell.layout.end
                if cell.layout.has_keypoints and cell.layout.end
                else self._position_factory.get_position("right")
            ),
        )
        return self._generate_segment(start, end, len(cell.content))

    def _generate_segment(self, start: Coordinates, end: Coordinates, n: int):
        """
        Generates positions of entities in a segment, i.e. distributing entities at equidistant points along the segment itself.

        For N entities, the segment will be split in N+1 space and the entities will be placed in between those spaces.

        :param start: start coordinates of the segment
        :param end: end coordinates of the segment
        :param n: amount of entities to place on this segment
        :return: a generator of positions
        """
        item_vector = (end - start) / (n + 1)
        for i in range(n):
            yield start + item_vector * (i + 1)
