#!/bin/bash

set -e

IMAGE_TAG=vpntools
IMAGE_ID=$(docker images --format "{{.ID}}" $IMAGE_TAG)

USAGE="Usage: $0 COMMAND IMAGE_TAG\n"
USAGE+="    COMMAND is what you expect script to do:\n"
USAGE+="        build - Builds an image from a Dockerfile.\n"
USAGE+="        run - Runs a container.\n"
USAGE+="        killall - Stops and removes all running containers.\n"
USAGE+="        forcecleanall - Clean-up Docker.\n"

if [[ $# -lt 1 ]]; then
    echo>&2 "ERROR: Must specify the command"
    printf "$USAGE" >&2
    exit 2
fi

[[ $(uname) -eq "Darwin" ]] && MODHACK="-v /lib/modules:/lib/modules:ro" || MODHACK=""

function build {
    echo "Building docker container"
    docker build ./dev -t $IMAGE_TAG

    IMAGE_ID=$(docker images --format "{{.ID}}" $IMAGE_TAG)
    echo "Container image id: $IMAGE_ID"
    return 0
}

function run {
    name=$(basename "`pwd`")
    echo "Starting a container with the name $name using $IMAGE_TAG image..."
    CONTAINER_ID=$(docker create --rm -it --name $name -v "$PWD":/root/env --entrypoint=/bin/bash --privileged $MODHACK --cap-add ALL $IMAGE_TAG)
    docker start $CONTAINER_ID
    echo "Started $CONTAINER_ID with the name $name"

    echo "Attaching to a container"
    docker attach $CONTAINER_ID
    return 0
}

function killall {
    for container_id in $(docker ps -q --filter "ancestor=$IMAGE_TAG"); do
        echo "$(docker kill $container_id) - stopped and removed"
    done

    return 0
}

function forcecleanall {
    for container in $(docker container ls --format "{{.ID}}"); do docker container kill $container; done
    for container in $(docker container ls -a --format "{{.ID}}"); do docker container rm $container; done
    for image in $(docker images --format "{{.ID}}"); do docker image rm --force $image; done
    echo "Docker has been cleaned up"
    return 0
}

case $1 in
    build)
        echo "Executing BUILD command..."
        build "$@"
        ;;

    run)
        echo "Executing RUN command..."
        run "$@"
        ;;

    killall)
        echo "Executing KILLALL command..."
        killall "$@"
        ;;

    forcecleanall)
        echo "Executing FORCECLEANALL command..."
        forcecleanall "$@"
        ;;

    *)
      echo>&2 "ERROR: Unknown command $1"
        printf "$USAGE" >&2
        exit 2
        ;;
esac
