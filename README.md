# VPNTools

🚧 Work in progress! 🚧

## Introduction
It is a simple tool to build and manage VPN servers.
For now supports only Wireguard.

## How to use

1. Clone this repo (or download as a ZIP archive)
1. Go to the source code directory

    ```text
    cd `path_to_the_source_code_dir` 
    ```
1. Build development docker image by running:

    ```text
    ./dev/buildenv.sh build
    ```
1. Run a dev container (it will mount the source code directory):

    ```text
    ./dev/buildenv.sh run
    ```
1. Install mounted source code inside the container (in "edit" mode):

    ```text
    pip install -e .
    ```
1. Run the workflow. For example, `deploy_wg`:
    ```text
    python3 vpntools/cli.py deploy_wg `path_to_the_vpn_yaml`
    ```

## VPN Yaml Example

```yaml
# server IP address or a hostname
1.1.1.1:
  description: some_server_description
  ssh_user: "ssh_user_name"
  # ssh-keygen -t ed25519 -C "some@tag"
  ssh_private_key: |2
    -----BEGIN OPENSSH PRIVATE KEY-----
    ssh_private_key_goes_here...
    -----END OPENSSH PRIVATE KEY-----

  app_config:
    wireguard:
      wg0:
        server_private_ip: 192.168.101.1/24
        server_port: 52101
        # wg genkey | tee privatekey | wg pubkey > publickey
        private_key: SERVER_PRIVATE_KEY_GOES_HERE=
        public_key: SERVER_PUBLIC_KEY_GOES_HERE=
        peers:
          - peer_1:
              # wg genkey | tee privatekey | wg pubkey > publickey
              private_key: PEER_PRIVATE_KEY_GOES_HERE=
              public_key: PEER_PUBLIC_KEY_GOES_HERE=
              private_ip_prefix: 192.168.101.2/32
          - peer_2:
              # wg genkey | tee privatekey | wg pubkey > publickey
              private_key: PEER_PRIVATE_KEY_GOES_HERE=
              public_key: PEER_PUBLIC_KEY_GOES_HERE=
              private_ip_prefix: 192.168.101.3/32
```