# Input files format

1. [Properties](#properties)
1. [Sizes](#sizes)
1. [Directions and Positions](#directions-and-positions)
1. [Cells](#cells)
   1. [Cell configuration properties](#cell-configuration-properties-cell_cfg_property)
   1. [Cell layouts](#cell-layouts)
1. [Shapes](#shapes)
   1. [Shapes configuration properties](#shapes-configuration-properties-shape_cfg_property)

Input files are written in a simple format: each line of the file will correspond of to a line in the grid.
Cells are split with the pipe character `|`. Grid width will be determined by the longest line.

```
Cell_content = {Cell_configuration}Shapes_list | Shapes_list | ø
Cell_configuration = Cell_configuration;Cell_configuration | Cell_cfg_property
Shapes_list = Shape_group;Shapes_list | Shape_group
Shape_group = Shape_def{Shape_configuration} | Shape_def
Shape_configuration = Shape_configuration;Shape_configuration | Shape_cfg_property
Shape_def = <int>Shape | Shape
```

Some samples of input files are available in the [test samples directory](tests/test_data/samples).

## Properties

Properties can be declared with `name=value` or chained with their values without name as long they are declared as "native" (native = `y` or a number). A native property annotated with a number indicates the order in which they are parsed natively.

Some properties can 

## Sizes

Sizes can be described in two manners: either fixed or relative.

- Fixed: a straight number or annotated with `px` (ex: `14` or `16px`).
- Relative: in percentage of the cell (ex: `75%`). If relative, the size will be determined according to the size of the cell.

## Directions and Positions

Directions, positions and angles are all managed in the same way, with a premade list of simple directions/positions.

Angles are managed according to the mathematical [unit circle](https://en.wikipedia.org/wiki/Unit_circle) ([shortcut to picture](https://en.wikipedia.org/wiki/File:Unit_circle_angles_color.svg)).

Directions and positions both accept either the mnemonic or the shortcut.

**Full descriptions:**

| Direction | Mnemonic | Shortcut | Angle |
| ---       | :---:    | :---:    | ---   |
| Bottom | `bottom` | `B` | 270° |
| Bottom Left | `bottom_left` | `Z` | 225° |
| Bottom Right | `bottom_right` | `C` | 315° |
| Center | `center` | `S` | Cannot be an angle! |
| Left | `left` | `L` | 180° |
| Top | `top` | `T` | 90° |
| Top Left | `top_left` | `Q` | 135° |
| Top Right | `top_right` | `E` | 45° |

In case you find the shortcuts confusing, diagonal directions/positions are determined by QWERTY keyboard layout, centered on WQSD, `S` being at the center.

| | | |
| --- | --- | --- |
| `Q` | | `E` |
| | `S` | |
| `Z` | | `C` |

## Cells

### Cell configuration properties (Cell_cfg_property)

| property | native? | default | description |
| ---      | :---:   | :---:   | ---         |
| `bg_color` | y | `None` | Background color of the cell. |
| `layout` | y | `stack` | Layout of the shapes in the cell. |
| `orientation` | y | `right` | Default orientation of the shapes in the cell (see ). |

### Cell layouts

For all purposes and intent, shapes don't mix. A latter shape will be layed "on top" of any formerly declared shape in a matter of layers. Mind your own layers.

- `horizontal`: a `line` from left to right (equivalent to `line[L,R]`).
- `line`: a line starting from a position (start) to another position (end).
- `rhorizontal`: a `line` from right to left (equivalent to `line[R,L]`).
- `rvertical`: a `line` from bottom to top (reverse vertical, equivalent to `line[B,T]`).
- `stack`: all shapes are stacked.
- `vertical`: a `line` from top to bottom (equivalent to `line[T,B]`).

Planned:
- different geometric shapes (square, arrow, triangle, circle)
- `arc`
- letter shaped
- `grid`

## Shapes

- `A` arrow
- `C` Circle

Planned:
- `D` Diamond
- `I` Image
- `R` Rectangle
- `Sq` Square
- `St` Star
- `T` Triangle

### Shapes configuration properties (Shape_cfg_property)

| property | native? | default | shapes | description |
| ---      | :---:   | :---:   | :---:  | ---         |
| `border_color` | n | `None` | all | Colour of the shape border.<br/>Only applicable if `border_width` is set. |
| `border_width` | n | `0` | all | Width of the shape border.<br/>Only applicable if `border_color` is set. |
| `fill` | 1 | `#FF0000` | all | Fill colour of the shape. |
| `height` | 3 | `80%` | all | Height of the shape as size. |
| `width` | 2 | `80%` | all | Width of the shape as  size. |
