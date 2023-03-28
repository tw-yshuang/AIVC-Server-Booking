#!/usr/bin/env bash

# This script is for some config error that arises because of the container config conflict with the host config;
# it needs to be fixed when the container is running.

# Error 804: forward compatibility was attempted on non supported HW
host_libcuda_so=libcuda.so.$(nvidia-smi --query-gpu=driver_version --format=csv | tail -n 1)
mv /usr/lib/x86_64-linux-gnu/libcuda.so.1 /usr/lib/x86_64-linux-gnu/libcuda.so.1.bk
ln -s $host_libcuda_so /usr/lib/x86_64-linux-gnu/libcuda.so.1