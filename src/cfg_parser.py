from colour import Color
import logging
import re
from typing import Any


from .utils.geometry import Angle
from .utils.layout import Layout, PositionFactory
from .utils.symbols import GridSymbol


class CfgParser:
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
            match = re.match(r"([a-z]+(-[a-z-]+)?)=(.*)", param)
            angle_match = re.match(r"(-?\d+)d", param)
            size_match = re.match(
                r"(\d+%? *x *\d+%?)|(\d+%? *x)|(x *\d+%?)|(\d+%?)", param
            )
            try:
                color = Color(param)
            except ValueError:
                color = None
            if match:
                cfg[match.group(1).replace("-", "_")] = match.group(3)
            elif Layout.is_layout(param):
                cfg.update(self._do_layout(param))
            elif self._position_factory.is_layouting(param):
                cfg["orientation"] = self._position_factory.get_position(param).angle
            elif angle_match:
                cfg["orientation"] = Angle(float(angle_match.group(1)))
            elif size_match:
                if "x" in param:
                    sizes.extend([None if not p else p for p in param.split("x")])
                else:
                    sizes.append(param)
            elif color:
                colors.append(color)
            else:
                self._log.warning(f"Unknown cfg param '{param}'")
        cfg.update(self._do_sizes(sizes))
        cfg.update(self._do_colors(colors))
        self._log.debug(f"cfg={cfg}")
        return cfg

    def _do_layout(self, txt: str) -> dict[str, Any]:
        self._log.debug(f"layouting=[{txt}]")
        ret = {}
        ntxt = txt
        if Layout.is_layout_shortcut(ntxt):
            ntxt = Layout.expand_shortcut(ntxt)
        if GridSymbol.PARAMS_START in ntxt:
            layout_cfg = ntxt[ntxt.index(GridSymbol.PARAMS_START) :]
            ntxt = ntxt[: -len(layout_cfg)]
            options = layout_cfg[1:-1].split(GridSymbol.PARAMS_SEPARATOR)
            self._log.debug(f"layout options: {options}")
            if len(options) > 0:
                ret["layout.start"] = self._position_factory.get_position(options[0])
            if len(options) > 1:
                ret["layout.end"] = self._position_factory.get_position(options[1])
        ret["layout.display_type"] = ntxt
        return ret

    def _do_sizes(self, sizes) -> dict[str, Any]:
        "Manages sizes."
        cfg = {}
        self._log.debug(f"Sizes: {sizes}")
        for p, v in zip(["width", "height"], sizes):
            cfg[p] = v
        return cfg

    def _do_colors(self, colors) -> dict[str, Any]:
        "Manages colours."
        cfg = {}
        if len(colors) > 0:
            colors = colors + [None] * 2
            cfg["fill"], cfg["border_color"], *_ = colors
        return cfg
