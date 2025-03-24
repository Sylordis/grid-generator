# Input files format

1. [Grammar](#grammar)
1. [Properties](#properties)
1. [Data types](#data-types)
   1. [Angle or Direction](#angle-or-direction)
   1. [Color](#color)
   1. [Size](#size)
   1. [Directions and Positions](#directions-and-positions)
1. [Cells](#cells)
   1. [Cell configuration properties](#cell-configuration-properties-cell_cfg_property)
   1. [Cell layouts](#cell-layouts)
1. [Shapes](#shapes)
   1. [Shapes configuration properties](#shapes-configuration-properties-shape_cfg_property)

Input files are written in a simple format: each line of the file will correspond of to a line in the grid.
Cells are split with the pipe character `|`. Grid width will be determined by the longest line.

## Grammar

```ebnf
cell_content = '{', cell_cfg, '}', shapes_list | shapes_list | ø ;
cell_cfg = cell_cfg, ';', cell_cfg | cell_cfg_property ;
shapes_list = shape_group, ';', shapes_list | shape_group ;
shape_group = shape_def, '{', shape_cfg, '}' | shape_def ;
shape_cfg = shape_cfg, ';', shape_cfg | shape_cfg_property ;
shape_def = integer, shape | shape ;
integer = ['0'-'9']+ ;
```

Some samples of input files are available in the [test samples directory](../test/data/samples).

## Properties

Properties can be declared with `name=value` or chained with their values without name as long they are declared as "native" (native = `y` or a number). A native property annotated with a number indicates the order in which they are considered when provided.

## Data types

### Angle or Direction

A fixed number (int) affixed with `d` or a pre-existing [position/direction](#directions-and-positions).

*Ex:* `48d`, `-930d`, `T`

### Color

An hexadecimal value or a string with the name of a colour.

*Ex:* `#FFF000`, `#0AC`, `yellow`.

### Size

Either a fixed number (positive int or float) or a percentage. If percentile, the size is calculated based on the cell size.

*Ex:* `160`, `483.9`,  `76%`.

Both `width` and `height` can be combined in one declaration with `Size x Size` (whitespace not mandatory) and combined however you want.

*Ex:* `37x` (width=37), `x5%` (width default and height=5%), `83x70%` (width=83 and height=70%)

### Directions and Positions

Directions, positions and angles are all managed in the same way, with a premade list of simple directions/positions.

Angles are managed according to the mathematical [unit circle](https://en.wikipedia.org/wiki/Unit_circle) ([shortcut to picture](https://en.wikipedia.org/wiki/File:Unit_circle_angles_color.svg)) and the default orientation (0°) is towards the **top**.

Orientations and positions both accept either the mnemonic or the shortcut.

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

In the following table, the `monospace` characters are the normal keyboard ones, *italics* are the "language native" ones:

| | | |
| :---: | :---: | :---: |
| `Q` | `W`, *T* | `E` |
| `A`, *L* | `S`, *M* | `D`, *R* |
| `Z` | `X`, *B* | `C` |

## Cells

### Cell configuration properties (cell_cfg_property)

Properties do not have to be provided in the order indicated by the table.

| Property | Native? | Default | Type | Description |
| ---      | :---:   | :---:   | ---  | ---         |
| `bg_color` | n | `None` | Color | Background color of the cell. |
| `layout` | y | `stack` | [Cell layout](#cell-layouts) | Layout of the shapes in the cell. |
| `orientation` | y | `right` | Angle | Default orientation of the shapes in the cell. |
| `size` | n | `None` | Size | Default size of the shapes in the cell. |

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
| Arrow | `A` | `width` = length, no height (yet). |
| Circle | `C` | `width` = diameter, no height. |
| Diamond | `D` | Uses default `width`(2). |
| Ellipse | `E` | Uses default `width`(2). |
| Hexagon | `H` | `width` = diameter, no height. |
| Rectangle | `R` | ø |
| Square | `Sq` | no `height`, `width` will be used for both. |
| Star | `St` | `width` will be used for external diameter.<br/>`height` is used for internal diameter (uses default `width`(2)).<br/>Uses `sides`. |
| Triangle | `T` | ø |

Planned:
- `Cr` Cross
- `I` Image
- `L` Line
- `P` Polygon
- `Te` Text

### Shapes configuration properties (shape_cfg_property)

Properties do not have to be provided in the order indicated by the table, although the native index order is important to consider.

| Property | Native? | Unit | Default | Shapes | Description |
| ---      | :---:   | :---:| :---:   | :---:  | ---         |
| `border-color` | n | int | `None` | all | Colour of the shape border.<br/>Only applicable if `border_width` is set. |
| `border-radius` | n | int | `0` | `Square`, `Rectangle` | Radius of the corners (in pixels). |
| `border-width` | n | int | `0` | all | Width of the shape border (in pixels).<br/>Only applicable if `border_color` is set. |
| `fill` | 1 | Color | `#FF0000` | all | Fill colour of the shape. |
| `height` | 3 | Size | `80%`(1) or `50%`(2) | all | Height of the shape. Shapes use (1) if not specified otherwise. |
| `orientation` | 4 | Angle/Direction | `0°` | all | Orientation of the shape. |
| `sides` | n | int | `5` | `Star` | Number of vertices outside. |
| `width` | 2 | Size | `80%`(1) or `50%`(2) | all | Width of the shape. Shapes use (1) if not specified otherwise. |

**Example:**
- `{width=45%;fill=blue}` will set `width` to 45% and the fill colour will be blue, all other properties will use their default (a.k.a. no border/stroke, `height` is default).
- `{45%;blue}` or `{45%x;blue}` are similar to the previous example.
- `{fill=orange;x15;B}` will set `height` to 15px, `fill` with color orange and `orientation` to bottom (180°).
- `{80;23%;}` will set `width` to 80 and `height` to 23%.
