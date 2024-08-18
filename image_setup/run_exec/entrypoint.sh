#!/usr/bin/env bash

# The command that needs to be executed when the container is running.

bash /.script/fix_conflict.sh

# pyenv & pipenv upgrade
cd ~/.pyenv && git pull && cd ~
pip3 install --no-cache-dir --upgrade pipenv

if ! [ -z "${LOGO}" ]; then
    sed -i "s/^LOGO.*/LOGO='$LOGO'/g" /etc/environment
fi

if ! [ -z "${PASSWORD}" ]; then
    bash /.script/ssh_start.sh $PASSWORD
fi

exec "$@"
/bin/bash