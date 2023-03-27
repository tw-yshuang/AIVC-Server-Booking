#!/usr/bin/env bash

#>         +---------------------------+
#>         |       run_booking.sh      |
#>         +---------------------------+
#-
#- SYNOPSIS
#-
#-    ./run_booking.sh <password> [-h]
#-    
#-    It will run booking container with specific password for booking account.
#-
#- OPTIONS
#-
#-    -h, --help             print help information.
#-
#- EXAMPLES
#-
#-    $ ./run_booking.sh IamNo1handsome!

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

# Receive arguments in slient mode.
if [ "$#" -gt 0 ]; then
    while [ "$#" -gt 0 ]; do
        case "$1" in
            # Help
            "-h"|"--help")
                show_script_help
                exit 1
            ;;
        esac
    done
fi

#====================================================
# Part 2. Main
#====================================================

PROJ_PATH=/root
password=$1
if [ "$1" = "" ]; then
    printf "Please enter a password for booking account: "
    read password
fi

docker run \
-dit \
--cpus="0.5" \
--restart=always \
-p 10000:22 \
--name=booking \
-v ./cfg/:$PROJ_PATH/cfg \
-v ./jobs/:$PROJ_PATH/jobs \
-v ./lib/:$PROJ_PATH/lib \
-v ./src/:$PROJ_PATH/src \
-v $PROJ_PATH/src/monitor/ \
rober5566a/aivc-server:booking-v1.0.0 \
/bin/bash -c "ln -s $PROJ_PATH/src/booking/booking.py /usr/sbin/booking && /.script/ssh_start.sh $password"
