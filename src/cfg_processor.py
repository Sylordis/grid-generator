from colour import Color
import logging
import re
from typing import Any


from .utils.layout import Layout, PositionFactory


class CfgProcessor:
    """
    Standalone helper for interpreting configuration from strings.
    """

    def __init__(self):
        self._position_factory: PositionFactory = PositionFactory()
        self._log = logging.getLogger()

    def interpret(self, cfg_txt: list[str]) -> dict[str, Any]:
        """
        Interprets the text of a configuration.

        :param cfg_txt: configuration text.
        :return: a dictionary of parameters to inject into the shape constructor.
        """
        cfg: dict[str, Any] = {}
        sizes = []
        colors = []
        self._log.debug(f"cfg_txt={cfg_txt}")
        for param in cfg_txt:
            match = re.match("([a-z-]+)=(.*)", param)
            size_match = re.match("\d+(px|%)", param)
            try:
                color = Color(param)
            except ValueError:
                color = None
            if match:
                cfg[match.group(1).replace("-", "_")] = match.group(2)
            elif Layout.is_layout(param):
                cfg.update(self._do_layout(param))
            elif self._position_factory.is_layouting(param):
                cfg["orientation"] = self._position_factory.get_position(param).angle
            elif size_match:
                sizes.append(param)
            elif color:
                colors.append(color)
            else:
                self._log.debug(f"unknown cfg param=[{param}]")
        cfg.update(self._do_sizes(sizes))
        cfg.update(self._do_colors(colors))
        self._log.debug(f"cfg={cfg}")
        return cfg

    def _do_layout(self, txt) -> dict[str, Any]:
        self._log.debug(f"layouting=[{txt}]")
        if "[" in txt:
            pass
        # TODO layout type
        # TODO layout start
        # TODO layout end
        return {}

    def _do_sizes(self, sizes) -> dict[str, Any]:
        "Manages sizes."
        cfg = {}
        if len(sizes) == 1:
            if "width" not in cfg:
                cfg["width"] = sizes[0]
            if "height" not in cfg:
                cfg["height"] = sizes[0]
        elif len(sizes) > 1:
            sizes = sizes + [None] * 2
            cfg["width"], cfg["height"], *_ = sizes
        return cfg

    def _do_colors(self, colors) -> dict[str, Any]:
        "Manages colours."
        cfg = {}
        if len(colors) > 0:
            colors = colors + [None] * 2
            cfg["fill"], cfg["border_color"], *_ = colors
        return cfg
