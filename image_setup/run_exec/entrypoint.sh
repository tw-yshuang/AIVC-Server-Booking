#!/usr/bin/env bash

# The command that needs to be executed when the container is running.

bash /.script/fix_conflict.sh

# pyenv & pipenv upgrade
cd ~/.pyenv && git pull && cd ~
pip3 install --upgrade pipenv

exec "$@"