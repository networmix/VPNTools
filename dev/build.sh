#!/bin/bash

set -e

IMAGE_TAG=vpntools

echo "Building docker container"
docker build . -t $IMAGE_TAG

IMAGE_ID=$(docker images --format "{{.ID}}" $IMAGE_TAG)
echo "Container image id: $IMAGE_ID"