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

## Directions and Positions

Directions, positions and angles are all managed in the same way, with a premade list of simple directions/positions.

Angles are managed according to the mathematical [unit circle](https://en.wikipedia.org/wiki/Unit_circle) ([shortcut to picture](https://en.wikipedia.org/wiki/File:Unit_circle_angles_color.svg)) and the default orientation is towards the **top**.

Directions and positions both accept either the mnemonic or the shortcut.

**Full descriptions:**

| Direction | Mnemonic | Shortcut | Angle |
| ---       | :---:    | :---:    | ---   |
| Bottom | `bottom` | `B` | 180° |
| Bottom Left | `bottom_left` | `Z` | 135° |
| Bottom Right | `bottom_right` | `C` | 225° |
| Center | `center` | `S` | Cannot be an angle! |
| Left | `left` | `L` | 90° |
| Right | `right` | `R` | 270° |
| Top | `top` | `T` | 0° |
| Top Left | `top_left` | `Q` | 45° |
| Top Right | `top_right` | `E` | 315° |

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
- different geometric shapes (square, arrow, triangle, circle, cross)
- `arc`
- letter shaped
- `grid`

## Shapes

Shapes can be used in the input file as the shortcut or the full name.

| Shape | Shortcut | Comment |
| ---   | :---:    | ---     |
| Arrow | `A` | `width` = length, no height yet.
Circle | `C` | `width` = diameter, no height.
Diamond | `D` | Uses default `width`(2).
Ellipse | `E` | Uses default `width`(2).
Hexagon | `H` | `width` = diameter, no height.
Rectangle | `R` |
Square | `Sq` | no `height`, `width` will be used for both.
Star | `St` | `width` will be used for external diameter.<br/>`height` is used for internal diameter (uses default `width`(2)).<br/>Uses `sides`.
Triangle | `T` |

Planned:
- `Cr` Cross
- `I` Image
- `L` Line
- `P` Polygon
- `Te` Text

### Shapes configuration properties

| property | native? | unit | default | shapes | description |
| ---      | :---:   | :---:| :---:   | :---:  | ---         |
| `border-color` | n | int | `None` | all | Colour of the shape border.<br/>Only applicable if `border_width` is set. |
| `border-radius` | n | int | `0` | `Square`, `Rectangle` | Radius of the corners (in pixels). |
| `border-width` | n | int | `0` | all | Width of the shape border (in pixels).<br/>Only applicable if `border_color` is set. |
| `fill` | 1 | Color | `#FF0000` | all | Fill colour of the shape. |
| `height` | 3 | Size | `80%`(1) or `50%`(2) | all | Height of the shape. Shapes use (1) if not specified otherwise. |
| `orientation` | Angle/Direction | 3 | `None` | all except `Circle` | Orientation of the shape. |
| `sides` | n | int | `5` | `Star` | Number of vertices outside. |
| `width` | 2 | Size | `80%`(1) or `50%`(2) | all | Width of the shape. Shapes use (1) if not specified otherwise. |

## Types

**Angle or Direction {#type-angle}**

A fixed number (int or float, can be negative) affixed with `d` or a pre-existing [position/direction](#directions-and-positions).

*Ex:* `48d`, `T`

**Color {#type-color}**

An hexadecimal value or a string representing a colour.

*Ex:* `#FFF000`, `#0AC`, `yellow`.

**Size {#type-size}**

Either a fixed number (int or float) or a percentage.

*Ex:* `160`,  `76%`.

Both `width` and `height` can be combined in one declaration with `Size x Size` (whitespace not mandatory) and combined however you want.

*Ex:* `37x` (width=37), `x5%` (width not set and height=5%), `83x70%` (width=83 and height=70%)
