#!/bin/sh
#
# Prepares the environment for the FIRST run of the webservice.
# Performs the one-time setup actions:
#   - creates the external "sensoriando" network
#   - builds the webservice image
#   - starts the container so the entrypoint applies the migrations
#   - creates the Django superuser from the DJANGO_SUPERUSER_* env vars
#
# Prerequisites: Docker, docker compose, a populated .env file and the
# sensoriando_database (sensoriando_core repo) reachable on the network.
#
# Run this script ONCE before ./run.sh.

set -eu

cd "$(dirname "$0")"

NETWORK=sensoriando
SERVICE=framework

# Ensure the .env file exists
if [ ! -f .env ]; then
    echo "Error: .env file not found. Copy env.example to .env and fill it in." >&2
    exit 1
fi

# Pick docker compose v2 (plugin) or v1 (standalone)
if docker compose version >/dev/null 2>&1; then
    COMPOSE="docker compose"
elif command -v docker-compose >/dev/null 2>&1; then
    COMPOSE="docker-compose"
else
    echo "Error: docker compose is not installed." >&2
    exit 1
fi

# Create the external network if it does not exist yet
if ! docker network inspect "$NETWORK" >/dev/null 2>&1; then
    echo "Creating external network $NETWORK..."
    docker network create "$NETWORK"
fi

# Build the webservice image
echo "Building the webservice image..."
$COMPOSE build

# Start the container (the entrypoint applies the migrations automatically)
echo "Starting the container to apply the migrations..."
$COMPOSE up -d

# Wait for the migrations to be applied (depends on the database being reachable)
echo "Waiting for the database and the migrations..."
attempt=0
until $COMPOSE exec -T "$SERVICE" python manage.py migrate --check >/dev/null 2>&1; do
    attempt=$((attempt + 1))
    if [ "$attempt" -ge 30 ]; then
        echo "Error: timed out waiting for the migrations. Check that sensoriando_database is up."
        exit 1
    fi
    sleep 2
done

# Create the superuser only if one does not exist yet
echo "Checking the Django superuser..."
has_superuser=$($COMPOSE exec -T "$SERVICE" python manage.py shell -c \
    "from django.contrib.auth import get_user_model; print(get_user_model().objects.filter(is_superuser=True).exists())" \
    2>/dev/null)

if echo "$has_superuser" | grep -q "True"; then
    echo "Superuser already exists; skipping creation."
else
    echo "Creating the superuser from the DJANGO_SUPERUSER_* env vars..."
    $COMPOSE exec -T "$SERVICE" python manage.py createsuperuser --noinput
fi

echo ""
echo "Initialization complete. Use ./run.sh to start the service."
