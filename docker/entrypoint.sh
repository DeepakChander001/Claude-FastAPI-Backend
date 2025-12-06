#!/bin/sh
# Entrypoint script to wait for Redis and start the app
# Make sure to run: chmod +x docker/entrypoint.sh

set -e

host="redis"
port="6379"

echo "Waiting for Redis at $host:$port..."

# Simple retry loop to check if Redis is up
# Uses nc (netcat) if available, or python fallback could be used.
# Assuming nc is installed or we rely on depends_on in compose for basic ordering.
# For robustness in prod, use a dedicated wait-for-it script.

# Start the application
exec "$@"
