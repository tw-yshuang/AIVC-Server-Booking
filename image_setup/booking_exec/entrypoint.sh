#!/usr/bin/env bash

# The command that needs to be executed when the container is running.

chmod 755 /.script/booking.sh
ln -s /.script/booking.sh /usr/bin/booking

exec "$@"