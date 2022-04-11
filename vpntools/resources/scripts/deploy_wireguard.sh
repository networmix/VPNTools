#!/usr/bin/env bash

set -e

WG_FOLDER="/etc/wireguard/"
TMP_FOLDER="/tmp"
DEBIAN_FRONTEND="noninteractive"

apt-get update
apt-get install -y wireguard

mkdir -p -m 0700 $WG_FOLDER
mv $TMP_FOLDER/wg0.conf $WG_FOLDER

sysctl -w net.ipv4.ip_forward=1

systemctl enable wg-quick@wg0
systemctl start wg-quick@wg0
systemctl restart wg-quick@wg0