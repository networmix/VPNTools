import datetime
import socket
import ipaddress
from typing import Any, Dict
from vpntools.host import Host

from vpntools.jinja_render import render_from_template


class WireguardServer:
    def __init__(self, host: Host, config: Dict[str, Any]):
        self.host = host
        self.config = config
        self.peer_key_map: Dict[str, str] = {}

        for wg_if in self.config:
            for peer_dict in self.config[wg_if].get("peers", []):
                for peer_id, peer_cfg in peer_dict.items():
                    self.peer_key_map[peer_cfg["public_key"]] = peer_id

    def get_peer_stats(self) -> Dict[str, Any]:
        return {
            self.peer_key_map[k]: v
            for k, v in self.host.run_linux_cmd("WG_STATUS").items()
        }


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


def get_wg_from_host_cfg(host_cfg: Dict[str, Any]) -> Dict[str, Any]:
    return host_cfg.get("app_config", {}).get("wireguard", {})
