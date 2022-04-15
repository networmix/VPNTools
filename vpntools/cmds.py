from datetime import datetime

from vpntools.parsers import TextParser

LINUX_COMMANDS = {
    "WIREGUARD_SVC_STATUS": {"cmd": "systemctl status wg-quick@wg0", "parser": None},
    "GET_UPTIME": {
        "cmd": "uptime -s",
        "parser": lambda x: datetime.strptime(x.strip(), "%Y-%m-%d %H:%M:%S"),
    },
    "WG_STATUS": {
        "cmd": "wg show all",
        "parser": TextParser(
            [r"peer: (?P<pub_key>.*)", r"(?P<key>.*?):(?P<value>.*)"]
        ).parse_text,
    },
    "APTGET_UPD&UPG": {"cmd": "apt-get update && apt-get -y upgrade", "parser": None},
}
