#!/bin/bash

# Configuration
CONTAINER_NAME="odoo-odoo-1"  # Default name from docker-compose
DB_NAME="salon_db"
MODULE="salon_appointment"

echo "Checking if container $CONTAINER_NAME is running..."
if [ ! "$(docker ps -q -f name=$CONTAINER_NAME)" ]; then
    echo "Error: Container $CONTAINER_NAME is not running."
    echo "Please start it with: docker compose up -d"
    exit 1
fi

echo "Running tests for module: $MODULE in database: $DB_NAME..."
docker exec -it $CONTAINER_NAME odoo --test-enable --stop-after-init -d $DB_NAME -i $MODULE

echo "Test run completed."
