from __future__ import annotations
from abc import ABC, abstractmethod
import subprocess

from dataclasses import dataclass
from datetime import datetime
from collections import deque
import os.path
import logging
from typing import Any, Dict, List, Optional

from termcolor import cprint
from prettytable import PrettyTable

from vpntools.helpers import get_resource_path, yaml_to_dict
from vpntools.host import Host
from vpntools.wireguard import (
    WireguardServer,
    build_wg_peer_cfg,
    build_wg_server_cfg,
    get_wg_from_host_cfg,
)
from vpntools.resources import scripts


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s:%(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class DataContainer:
    ...


class ExecutionContext:
    def __init__(self, args: Optional[Dict[str, Any]] = None):
        self._instr_queue = deque([])
        self._args: Dict[str, Any] = {} if args is None else args
        self.data: Dict[str, DataContainer] = {}
        self.config: Dict[str, Any] = {}
        self.hosts: Dict[str, Host] = {}

    def set_data(self, key: str, container: DataContainer) -> None:
        self.data[key] = container

    def del_data(self, key: str) -> None:
        del self.data[key]

    def get_data(self, key: Optional[str] = None) -> DataContainer:
        if key:
            return self.data[key]
        return self.data

    def get_next_instr(self) -> Instruction:
        if self._instr_queue:
            return self._instr_queue.popleft()
        return None

    def set_instr(self, instr_list: List[Instruction]) -> None:
        self._instr_queue = deque(instr_list)

    def get_args(self, key: Optional[str] = None) -> Dict[str, Any]:
        if key is not None:
            return self._args[key]
        return self._args


class Instruction(ABC):
    def __init__(self, **kwargs: Dict[str, Any]):
        self._attr = kwargs

    def __repr__(self):
        return f"{type(self).__name__}(attr={self._attr})"

    @abstractmethod
    def run(self, ctx: ExecutionContext) -> ExecutionContext:
        return ctx


class Workflow:
    def __init__(self, instr_list: List[Instruction]):
        self.instr_list = instr_list

    @classmethod
    def from_dict(cls, workflow_dict: Dict[str, Any]) -> Workflow:
        instr_list = []
        for instr_item in workflow_dict["instructions"]:
            ((instr_name, instr_attr),) = instr_item.items()
            instr_list.append(INSTRUCTIONS[instr_name](**instr_attr))
        return cls(instr_list)

    def run(
        self,
        ctx: Optional[ExecutionContext] = None,
        args: Optional[Dict[str, Any]] = None,
    ) -> ExecutionContext:
        if ctx is None:
            ctx = ExecutionContext(args)
            ctx.set_instr(self.instr_list)
        while instr := ctx.get_next_instr():
            logger.info("Executing: %s", instr)
            ctx = instr.run(ctx)
        return ctx


class LoadConfig(Instruction):
    def run(self, ctx: ExecutionContext) -> ExecutionContext:
        with open(ctx.get_args("vpn_yaml"), encoding="utf-8") as f:
            ctx.config = yaml_to_dict(f.read())
        return ctx


class ConnectHosts(Instruction):
    def run(self, ctx: ExecutionContext) -> ExecutionContext:
        for hostname, host_config in ctx.config.items():
            host = Host(hostname, host_config)
            host.connect()
            ctx.hosts[hostname] = host
        return ctx


class GetWireguardStatus(Instruction):
    def run(self, ctx: ExecutionContext) -> ExecutionContext:
        hosts_tbl = PrettyTable()
        hosts_tbl.field_names = [
            "Hostname",
            "Description",
            "Server Uptime",
        ]
        hosts_tbl.align["Hostname"] = "r"
        hosts_tbl.align["Description"] = "l"
        hosts_tbl.align["Server Uptime"] = "l"
        host_tables = {}
        for hostname, host in ctx.hosts.items():
            wg_app_config = get_wg_from_host_cfg(ctx.config[hostname])

            wg_srv = WireguardServer(host, wg_app_config)
            wg_srv_status = wg_srv.get_peer_stats()

            host_table = PrettyTable()
            host_table.field_names = ["Client", "Latest Endpoint", "Latest Active"]
            host_table.align = "r"
            host_tables[hostname] = host_table

            for peer_id, peer_status in wg_srv_status.items():
                host_table.add_row(
                    [
                        peer_id,
                        peer_status.get("endpoint", ""),
                        peer_status.get("latest handshake", ""),
                    ]
                )

            hosts_tbl.add_row(
                [
                    hostname,
                    host.config.get("description", ""),
                    str(datetime.utcnow() - host.run_linux_cmd("GET_UPTIME")),
                ]
            )

        cprint("All active servers:", color="cyan")
        print(hosts_tbl)
        for hostname, host_tbl in host_tables.items():
            cprint(f"Details for {hostname}:", color="cyan")
            print(host_tbl.get_string(sortby="Client"))
        return ctx


class DeployWireguard(Instruction):
    def run(self, ctx: ExecutionContext) -> ExecutionContext:
        wg_script_path = get_resource_path("deploy_wireguard.sh", scripts)

        for hostname, host in ctx.hosts.items():
            logger.info("%s: Deploying Wireguard", hostname)
            wg_app_config = get_wg_from_host_cfg(ctx.config[hostname])

            for wg_if_name, wg_if_dict in wg_app_config.items():
                logger.info(
                    "%s: Generating Wireguard configuration for %s",
                    hostname,
                    wg_if_name,
                )
                wg_cfg_str = build_wg_server_cfg(wg_if_dict, hostname, wg_if_name)
                wg_cfg_path = os.path.join(host.TMP_DATA_DIR, f"{wg_if_name}.conf")
                logger.info("%s: Uploading Wireguard configuration", hostname)
                host.put_data_into_file(
                    wg_cfg_str,
                    wg_cfg_path,
                )
            res = host.runscript(wg_script_path, root=True)
            if res.ok:
                logger.info("%s: Wireguard deployed", hostname)
        return ctx


class BuildWireguardClients(Instruction):
    def run(self, ctx: ExecutionContext) -> ExecutionContext:
        for hostname, _ in ctx.hosts.items():
            logger.info("%s: Generating Wireguard client configurations", hostname)
            wg_app_config = get_wg_from_host_cfg(ctx.config[hostname])

            for _, wg_if_dict in wg_app_config.items():
                for peer in wg_if_dict["peers"]:
                    for peer_name, peer_dict in peer.items():
                        logger.info(
                            "%s: Generating Wireguard client configuration for %s",
                            hostname,
                            peer_name,
                        )
                        wg_peer_cfg_str = build_wg_peer_cfg(
                            peer_dict, wg_if_dict, hostname
                        )
                        wg_peer_cfg_path = os.path.join(
                            os.path.curdir, f"{peer_name}.conf"
                        )
                        print(f"Configuration for {peer_name}:")
                        print(wg_peer_cfg_str)
                        print(f"QR code for {peer_name}:")
                        ret = subprocess.run(
                            f"echo '{wg_peer_cfg_str}' | qrencode -t ansiutf8",
                            capture_output=True,
                            shell=True,
                            check=True,
                        )
                        print(ret.stdout.decode("utf8"))
        return ctx


INSTRUCTIONS = {
    "LOAD_CONFIG": LoadConfig,
    "CONNECT_HOSTS": ConnectHosts,
    "GET_WIREGUARD_STATUS": GetWireguardStatus,
    "DEPLOY_WIREGUARD": DeployWireguard,
    "BUILD_WIREGUARD_CLIENTS": BuildWireguardClients,
}
