#!/bin/sh
#
# Brings the webservice cluster up, down or shows its logs.
#
# Run ./init.sh ONCE before the first start; it provisions the external docker
# network, builds the image and creates the superuser. This script only
# starts/stops/inspects the already-prepared cluster.
#
# Usage:
#   ./run.sh           Start the containers (detached)
#   ./run.sh down      Tear down the containers
#   ./run.sh logs      Follow the containers logs
#
set -eu

cd "$(dirname "$0")"

NETWORK=sensoriando

# Load the environment variables (ports, credentials, ...)
if [ ! -f .env ]; then
    echo "Error: .env file not found. Copy env.example to .env and edit it." >&2
    exit 1
fi
. ./.env

# Pick docker compose v2 (plugin) or v1 (standalone)
if docker compose version >/dev/null 2>&1; then
    COMPOSE="docker compose"
elif command -v docker-compose >/dev/null 2>&1; then
    COMPOSE="docker-compose"
else
    echo "Error: docker compose is not installed." >&2
    exit 1
fi

case "${1:-up}" in
    down)
        $COMPOSE down
        exit 0
        ;;
    logs)
        $COMPOSE logs -f
        exit 0
        ;;
    up)
        ;;
    *)
        echo "Usage: $0 [up|down|logs]" >&2
        exit 1
        ;;
esac

# The external network is provisioned by ./init.sh. Fail early with a clear
# hint if it was not run.
if ! docker network inspect "$NETWORK" >/dev/null 2>&1; then
    echo "Error: docker network '$NETWORK' is missing. Run ./init.sh first." >&2
    exit 1
fi

# Start the containers
$COMPOSE up -d

echo
$COMPOSE ps
