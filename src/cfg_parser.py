from colour import Color
import logging
import re
from typing import Any


from .utils.geometry import Angle
from .utils.layout import Layout, PositionFactory
from .utils.symbols import GridSymbol
from .utils.units import Size


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
            try:
                color = Color(param)
            except ValueError:
                color = None
            if match:
                cfg[match.group(1).replace("-", "_")] = match.group(3)
            elif Layout.is_layout(param):
                cfg.update(self._parse_layout(param))
            elif self._position_factory.is_position(param):
                cfg["orientation"] = self._position_factory.get_position(param).angle
            elif angle_match:
                cfg["orientation"] = Angle(float(angle_match.group(1)))
            elif Size.is_size(param):
                sizes = self._manage_sizes(param, sizes)
            elif color:
                colors.append(color)
            else:
                self._log.warning(f"Unknown cfg param '{param}'")
        cfg.update(self._do_sizes(sizes))
        cfg.update(self._do_colors(colors))
        self._log.debug(f"cfg={cfg}")
        return cfg

    def _manage_sizes(self, param: str, sizes: list):
        if "x" in param:
            sizes = sizes + [None if not p else Size(p) for p in param.split("x")]
        else:
            sizes = sizes + [Size(param)]
        return sizes

    def _parse_layout(self, txt: str) -> dict[str, Any]:
        self._log.debug(f"layouting=[{txt}]")
        ret = {}
        ntxt = txt
        sizes = []
        keypoints = []
        if Layout.is_layout_shortcut(ntxt):
            ntxt = Layout.expand_shortcut(ntxt)
        self._log.debug(f"Layout txt={ntxt}")
        if GridSymbol.PARAMS_START in ntxt:
            layout_cfg = ntxt[ntxt.index(GridSymbol.PARAMS_START) :]
            ntxt = ntxt[: -len(layout_cfg)]
            params = layout_cfg[1:-1].split(GridSymbol.PARAMS_SEPARATOR)
            self._log.debug(f"layout options: {params}")
            for param in params:
                if self._position_factory.is_position(param):
                    keypoints.append(self._position_factory.get_position(param))
                elif Size.is_size(param):
                    sizes.append(Size(param))
                else:
                    self._log.warning(f"Unknown layout parameter '{param}'.")
        ret.update({f"layout.{k}": p for k, p in self._do_sizes(sizes)})
        ret["layout.keypoints"] = keypoints
        ret["layout.display_type"] = ntxt
        return ret

    def _do_sizes(self, sizes) -> dict[str, Any]:
        "Manages sizes."
        return {p: v for p, v in zip(["width", "height"], sizes)}

    def _do_colors(self, colors) -> dict[str, Any]:
        "Manages colours."
        cfg = {}
        if len(colors) > 0:
            colors = colors + [None] * 2
            cfg["fill"], cfg["border_color"], *_ = colors
        return cfg
