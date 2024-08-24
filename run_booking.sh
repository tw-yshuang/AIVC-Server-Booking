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

LOGO="A I V C"
CONTAINER_DIR=/root
PROJ_DIR=$(dirname $(realpath $0))
if [ "$password" = "" ]; then
    printf "Please enter a password for booking account: "
    read password
fi

docker run \
-dit \
--cpus="0.5" \
--memory="50"M \
--restart=always \
-p 10000:22 \
--name=booking \
-v $PROJ_DIR/cfg/:$CONTAINER_DIR/cfg \
-v $PROJ_DIR/jobs/:$CONTAINER_DIR/jobs \
-v $PROJ_DIR/lib/:$CONTAINER_DIR/lib \
-v $PROJ_DIR/src/:$CONTAINER_DIR/src \
-v $CONTAINER_DIR/src/monitor/ \
-e CONTAINER_DIR="$CONTAINER_DIR" \
-e LOGO="$LOGO" \
-e PASSWORD="$password" \
rober5566a/aivc-server:booking-v1.2.0
