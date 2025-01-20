#!/bin/bash
set -e

# Store Git credentials if provided
if [ -n "$GIT_CREDENTIALS" ]; then
    echo "$GIT_CREDENTIALS" > /root/.git-credentials
    git config --global credential.helper store
fi

# Execute the passed command
exec "$@"