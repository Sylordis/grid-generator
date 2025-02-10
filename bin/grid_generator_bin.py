# This is a small program that will generate simple grids and shapes according to configuration files
# in a harmonised way.

import argparse
import logging
from pathlib import Path


from ..src.grid_drawing_tool import GridDrawingTool


class ArgParser:
    """
    Class to organise and setup the different options for the software.
    """

    def __init__(self):
        self.parser = argparse.ArgumentParser(
            prog=__name__, description="Runs a python coding puzzle."
        )
        self.parser.add_argument("input_file", help="Input file.", nargs="+")
        self.parser.add_argument(
            "--debug",
            help="Sets debug mode (equivalent to '--log debug')",
            action="store_const",
            dest="loglevel",
            const="debug",
            default="info",
        )
        self.parser.add_argument(
            "-d",
            "--dist",
            help="Destination directory where to generate the images.",
            metavar="PATH",
        )

    def parse(self):
        return self.parser.parse_args()


def main():
    args = ArgParser().parse()
    log_format = "%(levelname)s - %(message)s"
    if args.loglevel.upper() == "DEBUG":
        log_format = "%(levelname)s[%(module)s:%(lineno)d]: %(message)s"
    logging.basicConfig(
        level=getattr(logging, args.loglevel.upper(), None), format=log_format
    )
    draw_tool = GridDrawingTool()
    if args.dist:
        draw_tool.dist_dir = Path(args.dist)
    draw_tool.draw_all(args.input_file)
