import datetime
import socket
import ipaddress
from typing import Any, Dict

from vpntools.jinja_render import render_from_template


def build_wg_server_cfg(
    wg_srv_if_cfg: Dict[str, Any], hostname: str, wg_if_name: str
) -> str:
    return render_from_template(
        "wg_server_cfg.j2",
        wg_srv_if_cfg,
        {
            "now": datetime.datetime.utcnow,
            "ipaddress": ipaddress,
            "hostname": hostname,
            "wg_if_name": wg_if_name,
        },
    )


def build_wg_peer_cfg(
    wg_peer_cfg: Dict[str, Any],
    wg_srv_if_cfg: Dict[str, Any],
    hostname: str,
) -> str:
    try:
        if ipaddress.ip_address(hostname):
            server_external_ip_address = hostname
    except ValueError:
        server_external_ip_address = socket.gethostbyname(hostname)

    return render_from_template(
        "wg_client_cfg.j2",
        wg_peer_cfg,
        {
            "wg_srv_cfg": wg_srv_if_cfg,
            "server_external_ip_address": server_external_ip_address,
            "ipaddress": ipaddress,
        },
    )
