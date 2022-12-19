#!/usr/bin/env bash
#>            +----------------------+
#>            |  build_container.sh  |
#>            +----------------------+
#> Repository: https://github.com/tw-yshuang/AIVC-Server
#-
#-
#- SYNOPSIS
#-
#-    bash ./build_container.sh [OPTIONS]
#-
#- OPTIONS
#-
#-    -h, --help                  print help information.
#-    -std-id, --student-id       student ID. [required]
#-    -pw, --password             password. [required]
#-    -fp, --forward_port         which forward port you want to connect to port: 22(SSH). [required]
#-    -cpus                       number of cpus for container, default: 8
#-    -mem, --memory              how much memory(ram, swap) GB for container, default: 32
#-    -gpus                       how many gpus for container, default: 2
#-                                  User Guide: https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/user-guide.html
#-    -im, --image                which image you want to use, default: None
#-                                  if is None and also a new std_id it will use "rober5566a/aivc-server:latest"
#-    -exec, --execute-script     which image you want to use, default: None
#-
#-    -s-update, --silent-update          silent mode to update users_config.json, value: None(default) | True | False,
#-                                                                                 None, interactive mode.
#-                                                                                 True | Fasle,  update users_config.json or not.
#-    -s-default, --silent-use-default    silent mode to use default user config, value: None(default) | True | False,
#-                                                                                None, interactive mode.
#-                                                                                True | Fasle,   use default user config or not.
#-
#- EXAMPLES
#-
#-    $ ./build_container.sh -std-id m11007s05 -pw IamNo1handsome! -fp 2222  -s-update False -s-default True

#====================================================
# Part 1. Option Tool
#====================================================
# Print script help
function show_script_help(){
    echo
    head -35 $0 | # find this file top 25 lines.
    grep "^#[-|>]" | # show the line that include "#-" or "#>".
    sed -e "s/^#[-|>]*//1" # use nothing to replace "#-" or "#>" that the first keyword in every line.  
    echo 
}

#* Design: if you want change some default config.
std_id=""
password=""
forward_port=""
cpus="8"
memory="32"
gpus="2" # https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/user-guide.html
image=None
execute_script=None
silentUpdate=None
silentUseDefault=None

# private variables
__volume_work_dir="./test/Users"
__volume_dataset_dir='./test/Dataset'
__user_config_json='./test_users_config.json'

if [ "$#" -gt 0 ]; then
    while [ "$#" -gt 0 ]; do
        case "$1" in
            # Help
            "-h"|"--help")
                show_script_help
                exit 1
            ;;
            # student ID
            "-std-id"|"--student-id")
                std_id=$2
                shift 2
            ;;
            # password
            "-pw"|"--password")
                password=$2
                shift 2
            ;;
            # which forward port you want to connect to port: 22(SSH)
            "-fp"|"--forward-port")
                forward_port=$2
                shift 2
            ;;
            # number of cpus for container
            "-cpus")
                cpus=$2
                shift 2
            ;;
            # how much memory(ram, swap) GB for container
            "-mem"|"--memory")
                memory=$2
                shift 2
            ;;
            # how many gpus for container
            "--gpus")
                gpus=$2
                shift 2
            ;;
            # which image you want to use
            "-im"|"--image")
                image=$2
                shift 2
            ;;
            "-exec"|"--execute-script")
                execute_script=$2
                shift 2
            ;;
            "-s-update"|"--silent-update")
                silentUpdate=$2
                shift 2
            ;;
            "-s-default"|"--silent-use-default")
                silentUseDefault=$2
                shift 2
            ;;
            * )
            break
            ;;
        esac
    done
fi

function Echo_Color(){
    case $1 in
        r* | R* )
        COLOR='\033[0;31m'
        ;;
        g* | G* )
        COLOR='\033[0;32m'
        ;;
        y* | Y* )
        COLOR='\033[0;33m'
        ;;
        b* | B* )
        COLOR='\033[0;34m'
        ;;
        *)
        echo "$COLOR Wrong COLOR keyword!\033[0m" 
        ;;
        esac
        echo -e "$COLOR$2\033[0m"
    }

function Ask_yn(){
    printf "\033[0;33m$1\033[0m\033[0;33m [y/n] \033[0m"
    if [ $all_accept = 1 ]; then
        echo '-y'
        return 1
    fi
    read respond
    if [ "$respond" = "y" -o "$respond" = "Y" -o "$respond" = "" ]; then
        return 1
    elif [ "$respond" = "n" -o "$respond" = "N" ]; then
        return 0
    else
        Echo_Color r 'wrong command!!'
        Ask_yn $1
        return $?
    fi
    unset respond
}

#====================================================
# Part 2. Main
#====================================================

# required variable
var_ls=($std_id $password $forward_port)
if [ ${#var_ls[*]} != 3 ]; then
    Echo_Color r "ERROR, required variable is less!"
    exit 0
fi

# locate a work_dir
__volume_work_dir="$__volume_work_dir/$std_id"
if [ -d "$__volume_work_dir" ]; then
    Echo_Color g "You already have work space: $__volume_work_dir"
else
    Echo_Color y "Create a work space in $__volume_work_dir"
    mkdir $__volume_work_dir
fi

python3 container_run/operate_user_config.py $std_id $password $forward_port $image $execute_script $__volume_work_dir $__volume_dataset_dir $__user_config_json $silentUpdate $silentUseDefault .$$ # save result to the .PID

# update variable from user_config.py
user_config=($(cat .$$))
password=${user_config[0]}
forward_port=${user_config[1]}
image=${user_config[2]}
execute_script=${user_config[3]}
__volume_work_dir=${user_config[4]}
__volume_dataset_dir=${user_config[5]}
rm -f .$$ # remove .PID

# TODO: run container