#!/usr/bin/env bash

# The command that needs to be executed when the container is running.

if ! [ -z "${LOGO}" ]; then
    sed -i "s/^LOGO.*/LOGO='$LOGO'/g" /etc/environment
fi

if ! [ -z "${PASSWORD}" ]; then
    bash /.script/ssh_start.sh $PASSWORD
fi

if ! [ -z "${CONTAINER_DIR}" ]; then
    ln -s $CONTAINER_DIR/src/booking/booking.py /usr/sbin/booking
fi

exec "$@"
/bin/bash
