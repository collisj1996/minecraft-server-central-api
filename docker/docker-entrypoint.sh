#!/bin/sh

set -e

# active the virtual environment
. ./venv/bin/activate

# run the server
exec "$@"