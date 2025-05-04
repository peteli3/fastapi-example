#!/bin/bash

if ! command -v git &> /dev/null; then
    echo "Error: git is not installed. Please install git first."
    exit 1
fi

dir=$(git rev-parse --git-dir 2>/dev/null)
if [ -z "$dir" ]; then
    echo "Error: This script must be run from a git repository."
    exit 1
fi

dir=$(git rev-parse --show-toplevel)
if [ "$(pwd)" != "$dir" ]; then
    echo "Error: This script must be run from the root of the git repository."
    exit 1
fi

docker compose down

docker compose build \
    --no-cache \
    --build-arg GIT_COMMIT=$(git rev-parse --short HEAD)

docker compose up --detach
