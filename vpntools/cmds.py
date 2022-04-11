LINUX_COMMANDS = {
    "WIREGUARD_SVC_STATUS": {"cmd": "systemctl status wg-quick@wg0", "parser": None},
    "GET_UPTIME": {"cmd": "uptime -s", "parser": None},
    "APTGET_UPD&UPG": {"cmd": "apt-get update && apt-get -y upgrade", "parser": None},
}
