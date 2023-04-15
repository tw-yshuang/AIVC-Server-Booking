#!/usr/bin/env bash

# The command that needs to be executed when the container is running.

bash /.script/fix_conflict.sh

exec "$@"