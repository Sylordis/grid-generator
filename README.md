# Grid Generator

Python tool to generate shapes in a grid from a simple text representative file.

**This project is still under construction.**

## Dependencies

This software uses Python 3.13.

The rest of the dependencies can be seen in the [requirements.txt file](requirements.txt).

## Installation

In the root directory of this repo:

1. Setup a virtual environment `python -m venv .venv`
2. Install the requirements `pip install -r requirements.txt`

## Usage

From outside this repo, in the virtual environment:

```bash
python -m grid-generator [options] <input_files..>
```

SVG files will be created in the directory of the input files, or in the directory specified by `--dist`/`-d`.

You can also run `python -m grid-generator --help` for help.

**Using test data as inputs:**

From outside this repo, inside the virtual environment:

```bash
python -m grid-generator -d grid-generator/dist grid-generator/test/data
```

## Input files

Grammar of the input file is described in its own [documentation file](doc/input_file_definition.md).

## Development

Unit tests can be run with `pytest grid-generator` from outside the root of this repository.

Coverage results can be obtained with `coverage run -m pytest grid-generator` then `coverage report -m`

## Author / Contributing

* Sylvain Domenjoud aka "[Sylordis](https://github.com/Sylordis)" (creator and maintainer)

## License

This project is licensed under the GPL-3.0 license - see the [LICENSE](LICENSE) file for details

## Links

Project website: <https://github.com/Sylordis/grid-generator/>

## Issues

Issues are reported here: <https://github.com/Sylordis/grid-generator/issues>
