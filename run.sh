#!/bin/sh
#
# Brings up all the containers needed by the webservice via docker-compose
# and follows the logs.
#
# Prerequisite: run ./init.sh once beforehand (it creates the external
# network, builds the image and creates the superuser).

set -e

NETWORK=sensoriando

# The external network is created by init.sh; here we only validate it
if ! docker network inspect "$NETWORK" >/dev/null 2>&1; then
    echo "Error: external network $NETWORK not found."
    echo "Run ./init.sh before bringing the containers up."
    exit 1
fi

# Bring the containers up in the background
docker-compose up -d

# Follow the logs
docker-compose logs -f
