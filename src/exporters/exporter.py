from abc import ABC, abstractmethod
import logging
from pathlib import Path

from ..grid import Grid, GridConfig


class Exporter(ABC):

  def __init__(self):
    self._log = logging.getLogger()

  @abstractmethod
  def export(self, grid: Grid, cfg: GridConfig, output_file: Path):
    """
    Main method to export a grid.

    :param grid: object representation of the grid
    :param cfg: base configuration of the grid
    :param output_file: output file
    """
    pass
