#!/bin/bash

password='rootpassword'
if [[ -n $1 ]]; then
    password=$1
fi
echo "root:"$password | chpasswd

service ssh start
/bin/bash