import os, sys
if __name__ == '__main__':
    # sys.path.extend('../../')
    # sys.path.insert(1, '../../lib')
    sys.path.append(os.path.abspath('./'))
    sys.path.append(os.path.abspath('../../'))
    # print(sys.path)
import datetime
from datetime import datetime, timezone
from typing import Tuple, Dict
import getpass
import click
from pathlib import Path
import yaml

from Checker import Checker

from lib.WordOperator import str_format, ask_yn
from HostInfo import HostInfo, BookingTime, BasicCapability, UserConfig, ScheduleDF, dump_yaml
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

    if list_schedule:
        list_schedules()
        return False

    if user_id:
        print(checker.cap_config.allow_userID)
        
        # check usr acc legal or not
        if user_id not in checker.cap_config.allow_userID:
            print("unknown account! Check ur brain bro wtf??")
            exit()

        # if user_id exits in capbility_config, run the login process below
        else:
            password = checker.users_config.ids[user_id].password
            print("Please enter the password: ")
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

    # Login part end -----------------------------------------------------------------------------------------------

    while True:
        get_caps_info(user_id)
        get_bookingtime()
        
        # if checker.check_booking_info(cap_info, booking_time, user_config) == True: 
        # TypeError: Cannot compare tz-naive and tz-aware datetime-like objects.
        # line 119, in check_booking_info if df['end'][i] > booking_time.start :
        
        if False:
            print(str_format(word = f'Booking successful!', style = 'default', fore = 'g' , background = 'black'))
            break
        else:
            print(str_format(word = f'There is not enough computing power for the time you need, book again.', style = 'default', fore = 'r' , background = 'black'))
            continue
        

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
        if user_config.image == "rober5566a/aivc-server":
            break
        else:
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
                new_password_dict: dict = {"password", new_password}
                dump_yaml(new_password_dict, "/home/cc/Desktop/code/erro/AIVC-Server-Booking/cfg/test_users_config.yaml")
                print(str_format(word = 'Update default Password!', style = 'default', fore = 'g' , background = 'black'))

                
            

        # update_password: bool
        # if update_password is True:
        #     new_password: str
        #     # ask twice
        #     user_config.password = new_password
        #     # after that only update the password in the user_config

    # ask user want to update the user_config?
    # Login part start -----------------------------------------------------------------------------------------------

    # open capability_config.yaml to get allowed usr's info.


def list_schedules():
    data = checker.booking.df
    data = data.sort_values(by = 'start')
    print(data.head())

# yaml_path = '/home/cc/Desktop/code/erro/AIVC-Server-Booking/cfg/test_users_config.yaml'
# def read_yaml_all():
#     try:
#         # 打开文件
#         with open(yaml_path,"r",encoding="utf-8") as f:
#             data=yaml.load(f,Loader=yaml.FullLoader)
#             return data
#     except:
#         return None

# def update_password_ymal(new_pass, user_id):
#     old_data = checker.users_config.ids
#     old_data[user_id].password = new_pass 
#     with open(yaml_path, "w", encoding="utf-8") as f:
#         yaml.dump(old_data, f)


if __name__ == '__main__':
    user_options('m11007s05')
    # a = 5
    # print (type(a))
    # print(type(checker.users_config.ids))
    # # data = checker.users_config.ids
    # # print(data)
