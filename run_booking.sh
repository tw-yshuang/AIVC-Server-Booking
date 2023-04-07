#!/usr/bin/env bash

#>         +---------------------------+
#>         |       run_booking.sh      |
#>         +---------------------------+
#-
#- SYNOPSIS
#-
#-    bash run_booking.sh <password> [-h]
#-    
#-    It will run booking container with specific password for booking account.
#-
#- OPTIONS
#-
#-    -h, --help             print help information.
#-
#- EXAMPLES
#-
#-    $ bash run_booking.sh IamNo1handsome!

#====================================================
# Part 1. Option Tool
#====================================================
# Print script help
function show_script_help(){
    echo
    head -22 $0 | # find this file top 16 lines.
    grep "^#[-|>]" | # show the line that include "#-" or "#>".
    sed -e "s/^#[-|>]*//1" # use nothing to replace "#-" or "#>" that the first keyword in every line.  
    echo 
}

password=""
# Receive arguments in slient mode.
if [ "$#" -gt 0 ]; then
    while [ "$#" -gt 0 ]; do
        case "$1" in
            # Help
            "-h"|"--help")
                show_script_help
                exit 1
            ;;
            * )
                password=$1
                shift 1
            ;;
        esac
    done
fi

#====================================================
# Part 2. Main
#====================================================

DOCKER_PATH=/root
PROJ_PATH=$(dirname $(realpath $0))
if [ "$password" = "" ]; then
    printf "Please enter a password for booking account: "
    read password
fi

docker run \
-dit \
--cpus="0.5" \
--restart=always \
-p 10000:22 \
--name=booking \
-v $PROJ_PATH/cfg/:$DOCKER_PATH/cfg \
-v $PROJ_PATH/jobs/:$DOCKER_PATH/jobs \
-v $PROJ_PATH/lib/:$DOCKER_PATH/lib \
-v $PROJ_PATH/src/:$DOCKER_PATH/src \
-v $DOCKER_PATH/src/monitor/ \
rober5566a/aivc-server:booking-v1.1.1 \
/bin/bash -c "( ln -s $DOCKER_PATH/src/booking/booking.py /usr/sbin/booking || true ) && /.script/ssh_start.sh $password"
