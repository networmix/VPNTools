import datetime
from typing import Any, Dict

from vpntools.jinja_render import render_from_template


def build_wg_server_cfg(wg_cfg: Dict[str, Any]) -> str:
    return render_from_template(
        "wg_server_cfg.j2", wg_cfg, {"now": datetime.datetime.utcnow}
    )
