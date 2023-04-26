#!/usr/bin/env bash

#====================================================
# Prepare config file
#====================================================
monitor_files=('jobs/monitor_exec' 'jobs/monitor.log')
schedule_files=('jobs/booking.csv' 'jobs/using.csv' 'jobs/used.csv')
cfg_files=('capability_config.yaml' 'host_deploy.yaml' 'users_config.yaml')
monitor_program_file="$(pwd)/src/monitor/Monitor.py"

mkdir jobs
# check and create
for key in ${!monitor_files[*]}; do
    if ! [ -f "${monitor_files[$key]}" ]; then
        touch "${monitor_files[$key]}"
    fi
done

# check and copy
for key in ${!schedule_files[*]}; do
    if ! [ -f "${schedule_files[$key]}" ]; then
        cp cfg/templates/schedule.csv "${schedule_files[$key]}"
    fi
done

# check and copy
for key in ${!cfg_files[*]}; do
    if ! [ -f "cfg/${cfg_files[$key]}" ]; then
        cp "cfg/templates/${cfg_files[$key]}" cfg
    fi
done


#====================================================
# Add command to the cron job
#====================================================
#write out current crontab
crontab -l > temp_crontab
#echo new cron into cron file
if [ "$(grep "${monitor_program_file}" temp_crontab)" == "" ]; then
    echo "*/30 * * * * python3 ${monitor_program_file}" >> temp_crontab
    
    #install new cron file
    crontab temp_crontab
fi
rm temp_crontab


#====================================================
# Install package and images 
#====================================================
pip3 install -r requirements.txt
docker pull --all-tags rober5566a/aivc-server


#====================================================
# Deploy booking container
#====================================================
bash run_booking.sh