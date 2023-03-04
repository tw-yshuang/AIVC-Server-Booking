#!/bin/bash

password='password'
if [[ -n $1 ]]; then
    password=$1
fi

# check container have users or only root
target_user=root
home_users=($(ls /home/))
if [ "$home_users" != '' ]; then
    target_user=${home_users[0]} # set the first user be the target_user
fi

echo "$target_user:"$password | chpasswd  # set password for target_user

service ssh start
/bin/bash