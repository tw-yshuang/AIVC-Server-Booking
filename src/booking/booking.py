import os, sys
if __name__ == '__main__':
    # sys.path.extend('../../')
    # sys.path.insert(1, '../../lib')
    sys.path.append(os.path.abspath('./'))
    sys.path.append(os.path.abspath('../../'))
    # print(sys.path)
import datetime
from datetime import datetime, timezone, timedelta
from typing import Tuple, Dict
import getpass
import click
from pathlib import Path
from ruamel.yaml import YAML

from Checker import Checker

from lib.WordOperator import str_format, ask_yn
from HostInfo import HostInfo, BookingTime, BasicCapability, UserConfig, ScheduleDF, dump_yaml, load_yaml
checker = Checker(deploy_yaml = 'cfg/test_host_deploy.yaml')
capability_info = checker.cap_config.max_custom_capability           # get capability_config.yaml with HostInfo 

password: str
cap_info =  BasicCapability
cap_info.cpus: float or str                 # number of cpus for container.
cap_info.memory: int or str                 # how much memory(ram, swap) GB for container.
cap_info.gpus: int or str                   # how many gpus for container.
booking_time = BookingTime
booking_time.start: datetime                # start time for booking this schedule.
booking_time.end: datetime                  # end time for booking this schedule.

# Check Whether user_id is in custom_user or not.
min_cpus: float = 1
min_memory: int = 1
min_gpus: int = 1

user_config = UserConfig
user_config.forward_port: int  # which forward port you want to connect to port: 22(SSH).
user_config.image: Path # which image you want to use, default is use "rober5566a/aivc-server:latest"
user_config.extra_command: str # the extra command you want to execute when the docker runs.

@click.command(context_settings=dict(help_option_names=['-h', '--help'], max_content_width=120))
@click.option('-id', '--user-id', help="user's account.")
@click.option('-use-opt', '--use-options', default=False, help="use extra options.")
@click.option('-ls', '--list-schedule', default=False, help="list schedule that already booking.")
def cli(user_id: str = None, use_options: bool = False, list_schedule: bool = False) -> bool:

    # if user input -ls True
    if list_schedule:
        list_schedules()
    # if user input -id [user_id]
    if user_id:
        print(checker.cap_config.allow_userID)
        password: str
        # check usr acc legal or not
        if user_id not in checker.cap_config.allow_userID:
            print("unknown account! Check ur brain bro wtf??")
            exit()
        # if user_id is new user
        elif user_id in checker.cap_config.allow_userID and user_id not in checker.users_config.ids:
            password = '0000'
            yaml = YAML()
            # with open("cfg/test_users_config.yaml", "r", encoding='utf-8') as f:
            #     data = yaml.load(f)
            data = {
                    f"{user_id}":{"password":"0000", "forward_port":"XXXXX", "image":"null", "extra_command":"null",
                                "volume_work_dir":f"{'Checker.deploy_info.volume_work_dir'}/{user_id}",
                                "volume_dataset_dir":f"{'Checker.deploy_info.volume_dataset_dir'}/{user_id}",
                                "volume_backup_dir":f"{'Checker.deploy_info.volume_backup_dir'}/{user_id}"
                                }      
                    }
            with open("cfg/test_users_config.yaml", "a+", encoding="utf-8") as f:
                yaml.dump(data, f)

            # data = {
            #     f"{user_id}":{"password":"0000", "forward_port":"XXXXX", "image":"null", "extra_command":"null",
            #                 "volume_work_dir":f"{'Checker.deploy_info.volume_work_dir'}/{user_id}",
            #                 "volume_dataset_dir":f"{'Checker.deploy_info.volume_dataset_dir'}/{user_id}",
            #                 "volume_backup_dir":f"{'Checker.deploy_info.volume_backup_dir'}/{user_id}"
            #                 }      
            #         }
            # path = "/home/cc/Desktop/code/erro/AIVC-Server-Booking/cfg/test_users_config.yaml"
            # with open(path, 'w', encoding='utf-8') as f:
            #     yaml.dump(data, f, Dumper=yaml.RoundTripDumper)
        # if user_id exits in capbility_config, run the login process below
        else:
            password = checker.users_config.ids[user_id].password
        print("Please enter the password. If you are new user, your password is '0000'")
        ok = False                                      # a flag for checking if tne login success
        for i in range(3):                              # There are three times chances for user to enter password correctly
            input_password = getpass.getpass()
            if input_password == password:
                ok = True                               # login successfully
                break
            else:
                print("Wrong password, please enter the password:")
        if not ok:
            print('ByeBye~~')                           # login failed
            exit()

    while True:
        get_caps_info(user_id)
        get_bookingtime()
        
        # if checker.check_booking_info(cap_info, booking_time, user_config) == True: 
        # TypeError: Cannot compare tz-naive and tz-aware datetime-like objects.
        # line 119, in check_booking_info if df['end'][i] > booking_time.start :
        
        if True:
            print(str_format(word = f'Booking successful!', style = 'default', fore = 'g' , background = 'black'))
            break
        else:
            print(str_format(word = f'There is not enough computing power for the time you need, book again.', style = 'default', fore = 'r' , background = 'black'))
            continue
    # if user input -user-opt True
    if use_options:
        user_options(user_id)
    
    booking(user_id, cap_info, booking_time, user_config, booking_csv = 'jobs/booking.csv')
    return True, (...)

def get_caps_info(user_id):
    if user_id in capability_info:
        max_cpus: float = checker.cap_config.max_custom_capability[user_id].cpus
        max_memory: int = checker.cap_config.max_custom_capability[user_id].memory
        max_gpus: int = checker.cap_config.max_custom_capability[user_id].gpus
    else:
        max_cpus: float = checker.cap_config.max_default_capability.cpus
        max_memory: int = checker.cap_config.max_default_capability.memory
        max_gpus: int = checker.cap_config.max_default_capability.gpus
    print(
        f'Your Maximum Capability Information:\n'
        f'cpus = {max_cpus}, '
        f'memory = {max_memory}, '
        f'gpus = {max_gpus}'
    )

    # check whether input legal or not  
    while True:
        print("Please enter the capability informationcpus(float) memory(int) gpus(int):")
        args = list(filter(lambda x: x, input().split(' ')))            # use filter lambda to remove overflow
        if len(args) != 3:
            output = str_format(word = f"Incorrect number of parameters: expected 3, received {len(args)}", style = 'default', fore = 'r' , background = 'black')
            print(output)
            continue
        try:
            cap_info.cpus = float(args[0])
        except ValueError:   
            print(str_format(word = 'ValueError: cpus must be float or int', style = 'default', fore = 'r' , background = 'black'))
            continue
        try:
            cap_info.memory = int(args[1])
        except ValueError:
            print(str_format(word = 'ValueError: memory must be int', style = 'default', fore = 'r' , background = 'black'))
            continue
        try:
            cap_info.gpus = int(args[2])
        except ValueError:
            print(str_format(word = 'ValueError: gpus must be int', style = 'default', fore = 'r' , background = 'black'))
            continue
        if cap_info.cpus < min_cpus or cap_info.cpus > max_cpus:
            print(str_format(word = f'cpus rate domain error: expected {min_cpus} ~ {max_cpus}', style = 'default', fore = 'r' , background = 'black'))
            continue
        if cap_info.memory < min_memory or cap_info.memory > max_memory:
            print(str_format(word = f'memory amount domain error: expected {min_memory} ~ {max_memory}', style = 'default', fore = 'r' , background = 'black'))
            continue
        if cap_info.gpus < min_gpus or cap_info.gpus > max_gpus:
            print(str_format(word = f'gpus number domain error: expected {min_gpus} ~ {max_gpus}', style = 'default', fore = 'r' , background = 'black'))
            continue
        break

def get_bookingtime():
    while True:
        print("Please enter the start time, the form is YYYY MM DD hh mm:")
        start_time_args = list(filter(lambda x: x, input().split(' ')))
        # using time flag
        if start_time_args[0] == 'now':
            booking_time.start = datetime.now()
            break
        # using datetime
        else:              
            try:
                start_time_args = list(map(int, start_time_args))                                 # str -> int
            except ValueError:
                print(str_format(word = f'Wrong input!!! ValueError', style = 'default', fore = 'r' , background = 'black'))
                continue
            if len(start_time_args) != 5:
                print(str_format(word = f'Wrong input!!! Incorrect number of parameters: expected 3, received {len(start_time_args)}', style = 'default', fore = 'r' , background = 'black'))
                continue
            if start_time_args[4] % 30 != 0:
                print(str_format(word = f'Wrong input!!! "mm" must be "00" or "30"', style = 'default', fore = 'r' , background = 'black'))
                continue
            try:
                booking_time.start = datetime(*start_time_args[:4], *start_time_args[4:], tzinfo = timezone.utc)
            except ValueError:
                print(str_format(word = f'Wrong input!!! ValueError', style = 'default', fore = 'r' , background = 'black'))
                continue
            except OverflowError:
                print(str_format(word = f'Wrong input!!! OverflowError', style = 'default', fore = 'r' , background = 'black'))
                continue
            now_timeStamp = datetime.timestamp(datetime.now())
            dif = booking_time.start.timestamp() - now_timeStamp
            if dif < 0 or dif > 1209600:                        # 1209600 = 2 weeks -> sec
                print(str_format(word = f'Wrong input!!! The reserverd time must be wtihin two weeks', style = 'default', fore = 'r' , background = 'black'))
                continue
            else:
                break

    while True:
        print("Please enter the end time, the form is YYYY MM DD hh mm:")
        end_time_args = list(filter(lambda x: x, input().split(' ')))
        # using time flag
        day_flag = list(filter(lambda x: '-day' in x, end_time_args))                   
        week_flag = list(filter(lambda x: '-week' in x, end_time_args))
        if len(week_flag + day_flag) > 1:
            print(str_format(word = f'Wrong input!!! ValueError', style = 'default', fore = 'r' , background = 'black'))
            continue
        else:
            if len(day_flag) == 1:
                day_info: str
                day_info = day_flag[0].replace('-day', '')
                day_info = int(day_info)
                if day_info > 14 or day_info < 1:
                    print(str_format(word = f'Wrong input!!! ValueError', style = 'default', fore = 'r' , background = 'black'))
                    continue
                else:
                    delta = timedelta(day_info)
                    booking_time.end = booking_time.start + delta
                    print(booking_time.end)
                break
            elif len(week_flag) == 1:
                week_info: str
                week_info = week_flag[0].replace('-week', '')
                week_info = int(week_info)
                if week_info > 2 or week_info < 1:
                    print(str_format(word = f'Wrong input!!! ValueError', style = 'default', fore = 'r' , background = 'black'))
                    continue
                else:
                    delta = timedelta(weeks = week_info)
                    booking_time.end = booking_time.start + delta
                    print(booking_time.end)
                break
            # using datetime
            else:
                try:
                    end_time_args = list(map(int, end_time_args))                                 # str -> int
                except ValueError:
                    print(str_format(word = f'Wrong input!!! ValueError', style = 'default', fore = 'r' , background = 'black'))
                    continue
                if len(end_time_args) != 5:
                    print(str_format(word = f'Wrong input!!! Incorrect number of parameters: expected 3, received {len(end_time_args)}', style = 'default', fore = 'r' , background = 'black'))
                    continue
                if end_time_args[4] % 30 != 0:
                    print(str_format(word = f'Wrong input!!! "mm" must be "00" or "30"', style = 'default', fore = 'r' , background = 'black'))
                    continue
                try:
                    booking_time.end = datetime(*end_time_args[:4], *end_time_args[4:], tzinfo = timezone.utc)
                except ValueError:
                    print(str_format(word = f'Wrong input!!! ValueError', style = 'default', fore = 'r' , background = 'black'))
                    continue
                except OverflowError:
                    print(str_format(word = f'Wrong input!!! OverflowError', style = 'default', fore = 'r' , background = 'black'))
                    continue
                dif = booking_time.end.timestamp() - booking_time.start.timestamp()
                
                if dif < 0 or dif > 1209600:                        # 1209600 = 2 weeks -> sec
                    print(str_format(word = f'Wrong input!!! The reserverd time must be wtihin two weeks', style = 'default', fore = 'r' , background = 'black'))
                    continue
                else:
                    break

    # Optional
def user_options(user_id):
    user_config.image: str

    # Part Forward_ports
    while True:
        try:
            user_config.forward_port = int(input(f"Please enter the forward port(default:{checker.users_config.ids[user_id].forward_port}, none by default):\n"))
        except ValueError:
            print(str_format(word = 'ValueError!', style = 'default', fore = 'r' , background = 'black'))
            continue
        if user_config.forward_port < 10000 or user_config.forward_port > 11000:
            print(str_format(word = 'Forward Port must between 10000~11000!', style = 'default', fore = 'r' , background = 'black'))
            continue
        if checker.check_forward_port_empty(user_config.forward_port) == False:
            print(str_format(word = 'Forward Port Duplicated!', style = 'default', fore = 'r' , background = 'black'))
            continue
        else:
            break

    # Part image
    while True:
        empty_string = ""
        print(checker.deploy_info.images)
        try:
            user_config.image = str(input(f"Please enter the image 'repository/tag'(default: {checker.users_config.ids[user_id].image}, none by default):\n"))
        except ValueError:
            print(str_format(word = 'ValueError!', style = 'default', fore = 'r' , background = 'black'))
            continue
        if checker.users_config.ids[user_id].image == None:
            print("rober5566a/aivc-server:latest")
            break
        if user_config.image == empty_string:
            checker.users_config.ids[user_id].image == None
            break
        if checker.check_image_isexists(user_config.image) == False:
            print(str_format(word = f"Not found your default image{user_config.image} Use system's default rober5566a/aivc-server:latest ", style = 'default', fore = 'r' , background = 'black'))
            continue
    
    # Part extra_commands
    while True:
        print("Please enter the extra command when running the image. (default: None, none by default):\n")
        break
    
    # Part Update_password
    while True:
        update_password: bool = ask_yn(question = "Do you want to update the password?", fore = "white")
        if update_password is False:
            break
        if update_password is True:
            new_password: str = str(input("Please enter the new password:"))
            check_new_password: str = str(input("Please enter the new password again:"))
            if new_password != check_new_password:
                print(str_format(word = 'Incorrect!!', style = 'default', fore = 'r' , background = 'black'))
                continue
            else:
                yaml = YAML()
                with open("cfg/test_users_config.yaml", "r", encoding='utf-8') as f:
                    data = yaml.load(f)
                data[user_id]['password'] = new_password
                with open("cfg/test_users_config.yaml", "w", encoding="utf-8") as f:
                    yaml.dump(data, f)
                print(str_format(word = 'Update default Password!', style = 'default', fore = 'g' , background = 'black'))
                break

def list_schedules():
    data = checker.booking.df
    # Checker.booking_df got two data, need checker fix it !!!
    data = data.sort_values(by = 'start')
    print(data.head())

def booking(user_id:str, cap_info: BasicCapability, booking_time: BookingTime, user_config: UserConfig, booking_csv: Path) -> bool:
    '''
    Write the booking_info to the booking schedule.

    `user_id`: user's account.
    `cap_info`: cpus, memory, gpus.
    `booking_time`: checked available times.
    `user_config`: the config for this user_id.
    `booking_csv`: the csv for booking, default: 'jobs/booking.csv'.
    '''
    booking_df = ScheduleDF(booking_csv)
    ...

if __name__ == '__main__':
    cli()
