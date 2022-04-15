from vpntools.workflow import Workflow


STATUS_WF = Workflow.from_dict(
    {
        "instructions": [
            {"LOAD_CONFIG": {}},
            {"CONNECT_HOSTS": {}},
            {"GET_WIREGUARD_STATUS": {}},
        ]
    }
)

DEPLOY_WIREGUARD_WF = Workflow.from_dict(
    {
        "instructions": [
            {"LOAD_CONFIG": {}},
            {"CONNECT_HOSTS": {}},
            {"DEPLOY_WIREGUARD": {}},
            {"BUILD_WIREGUARD_CLIENTS": {}},
        ]
    }
)
