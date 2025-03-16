import pytest

from utils.geometry import Vector
from grid import Cell, Grid, GridConfig, ShapesConfig


CELL_SIZE = 20


@pytest.fixture
def my_grid_cfg():
    return GridConfig(cell_size=CELL_SIZE)


@pytest.fixture
def my_shapes_cfg():
    return ShapesConfig()


@pytest.fixture
def my_grid(my_grid_cfg, my_shapes_cfg):
    content = [Cell()] * 5
    return Grid(content=[content] * 3, cfg=my_grid_cfg, shapes_cfg=my_shapes_cfg)


class TestGrid:

    @pytest.mark.parametrize(
        "cell_pos,expected", [(0, 0), (CELL_SIZE / 2, CELL_SIZE / 2)]
    )
    def test_calculate_cell_center(self, my_grid, cell_pos, expected):
        assert my_grid.calculate_cell_center(Vector(cell_pos)) == Vector(expected)
