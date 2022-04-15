import io
import logging
from typing import Any, Dict, Optional, Union, IO
from datetime import datetime
from tempfile import TemporaryFile

from fabric import Connection
from paramiko.ed25519key import Ed25519Key

from vpntools.cmds import LINUX_COMMANDS

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s:%(message)s"
)
logger = logging.getLogger(__name__)


class Host:
    TMP_SCRIPT_PATH = "/tmp/tmp_script.sh"
    TMP_DATA_DIR = "/tmp"

    def __init__(
        self, hostname: str, config: Dict[str, Union[str, int, float]]
    ) -> None:
        self.hostname: str = hostname
        self.config: Dict[str, Union[str, int, float]] = config
        self.connection: Optional[Connection] = None

    def connect(self) -> None:
        connect_kwargs = {
            "pkey": Ed25519Key.from_private_key(
                file_obj=io.StringIO(self.config["ssh_private_key"])
            )
        }

        if not self.connection or not self.connection.is_connected:
            self.connection = Connection(
                self.hostname,
                user=self.config["ssh_user"],
                connect_kwargs=connect_kwargs,
            )
            logger.info("Connected: %s", self.hostname)

    def reconnect(self) -> None:
        if self.connection and self.connection.is_connected:
            self.connection.close()
        self.connection.open()
        logger.info("Reconnected: %s", self.hostname)

    def run(self, cmd: str, hide: str = "both", warn: bool = False) -> Any:
        res = self.connection.run(cmd, hide=hide, warn=warn)
        return res

    def run_linux_cmd(self, cmd_name: str) -> Any:
        cmd_bundle = LINUX_COMMANDS[cmd_name]
        res = self.run(cmd_bundle["cmd"])
        if cmd_bundle["parser"]:
            return cmd_bundle["parser"](res.stdout)
        return res.stdout

    def transfer_file(
        self, local_path: Union[str, IO], remote_path: str, chmod: Optional[str] = None
    ) -> None:
        logger.info("%s: Uploading file %s", self.hostname, remote_path)
        self.connection.put(local_path, remote_path, preserve_mode=False)

        if chmod:
            self.run(f"chmod {chmod} {remote_path}")

    def runscript(
        self,
        local_path: Union[str, IO],
        remote_path: Optional[str] = None,
        root: bool = False,
    ) -> Any:
        if remote_path is None:
            remote_path = type(self).TMP_SCRIPT_PATH
        self.transfer_file(local_path, remote_path, chmod="+x")
        logger.info("%s: Executing script %s", self.hostname, remote_path)
        if root:
            res = self.run(f"sudo su -c {remote_path} root")
        else:
            res = self.run(remote_path)

        if res.ok:
            logger.info("%s: Returned OK from %s", self.hostname, remote_path)
        else:
            logger.error("%s: Returned Fail from %s", self.hostname, remote_path)
        return res

    def put_data_into_file(self, data_str: str, remote_path: str) -> None:
        with TemporaryFile() as f:
            logger.info("%s: Writing data to a tmp file", self.hostname)
            f.write(data_str.encode())
            self.transfer_file(f, remote_path)

    def get_uptime(self) -> datetime:
        return self.run_linux_cmd("GET_UPTIME")
