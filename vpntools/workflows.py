from vpntools.workflow import Workflow


STATUS_WF = Workflow.from_dict(
    {
        "instructions": [
            {"LOAD_CONFIG": {}},
            {"CONNECT_HOSTS": {}},
            {"GET_HOST_STATUS": {}},
        ]
    }
)

DEPLOY_WIREGUARD_WF = Workflow.from_dict(
    {
        "instructions": [
            {"LOAD_CONFIG": {}},
            {"CONNECT_HOSTS": {}},
            {"DEPLOY_WIREGUARD": {}},
        ]
    }
)
