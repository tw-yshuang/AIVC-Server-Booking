#!/usr/bin/env python3
import os, sys
from pathlib import Path

if __name__ == '__main__':
    PROJECT_DIR = Path(__file__).resolve().parents[2]
    sys.path.append(str(PROJECT_DIR))

import random
import datetime
from datetime import datetime, timezone, timedelta
from typing import Tuple, Dict
import getpass
import click
from pathlib import Path
from ruamel.yaml import YAML
import pandas as pd

from Checker import Checker

from lib.WordOperator import str_format, ask_yn
from HostInfo import HostInfo, BookingTime, BasicCapability, UserConfig, ScheduleDF, dump_yaml, load_yaml, ScheduleColumnNames

checker = Checker(deploy_yaml='cfg/test_host_deploy.yaml')
capability_info = checker.cap_config.max_custom_capability  # get capability_config.yaml with HostInfo

password: str
cap_info = BasicCapability
cap_info.cpus: float or str  # number of cpus for container.
cap_info.memory: int or str  # how much memory(ram, swap) GB for container.
cap_info.gpus: int or str  # how many gpus for container.
booking_time = BookingTime
booking_time.start: datetime  # start time for booking this schedule.
booking_time.end: datetime  # end time for booking this schedule.

# Check Whether user_id is in custom_user or not.
min_cpus: float = 1
min_memory: int = 1
min_gpus: int = 0

forword_port_begin: int = 10001
forword_port_end: int = 11000

user_config = UserConfig
user_config.forward_port: int  # which forward port you want to connect to port: 22(SSH).
user_config.image: Path  # which image you want to use, default is use "rober5566a/aivc-server:latest"
user_config.extra_command: str  # the extra command you want to execute when the docker runs.


@click.command(context_settings=dict(help_option_names=['-h', '--help'], max_content_width=120))
@click.option('-id', '--user-id', help="user's account.")
@click.option('-use-opt', '--use-options', default=False, is_flag=True, help="use extra options.")
@click.option('-ls', '--list-schedule', default=False, is_flag=True, help="list schedule that already booking.")
# @click.option('--yes', is_flag = True, default=False, help="?")
def cli(user_id: str = None, use_options: bool = False, list_schedule: bool = False) -> bool:

    # if user input -ls True
    if list_schedule:
        __list_schedules()
        return False
    # if user input -id [user_id]
    if user_id:
        password: str
        # check usr acc legal or not
        if user_id not in checker.cap_config.allow_userID:
            print("unknown account! Check ur brain bro wtf??")
            return False
        # if user_id is new user
        elif user_id in checker.cap_config.allow_userID and user_id not in checker.users_config.ids:
            password = '0000'
        else:
            password = checker.users_config.ids[user_id].password
        print("Please enter the password. If you are new user, your password is '0000'")
        ok = False  # a flag for checking if tne login success
        for i in range(3):  # There are three times chances for user to enter password correctly
            input_password = getpass.getpass()
            if input_password == password:
                ok = True  # login successfully
                break
            else:
                print("Wrong password, please enter the password:")
        if not ok:
            print('ByeBye~~')  # login failed
            exit()

    while True:
        __get_caps_info(user_id)
        __get_bookingtime()

        # if checker.check_booking_info(cap_info, booking_time) == True:
        # TypeError: Cannot compare tz-naive and tz-aware datetime-like objects.
        # line 119, in check_booking_info if df['end'][i] > booking_time.start :
        if checker.check_booking_info(cap_info, booking_time) == True:
            print(str_format(word=f'Booking successful!', style='default', fore='g', background='black'))
            break
        else:
            print(
                str_format(
                    word=f'There is not enough computing power for the time you need, book again.',
                    style='default',
                    fore='r',
                    background='black',
                )
            )
            continue

    if user_id in checker.cap_config.allow_userID and user_id not in checker.users_config.ids:
        __New_user_config(user_id)

    if use_options:
        __user_options(user_id, password)
    booking(user_id, cap_info, booking_time, user_config, checker.booking.path)


def __get_caps_info(user_id):
    if user_id in capability_info:
        max_cpus: float = checker.cap_config.max_custom_capability[user_id].cpus
        max_memory: int = checker.cap_config.max_custom_capability[user_id].memory
        max_gpus: int = checker.cap_config.max_custom_capability[user_id].gpus
    else:
        max_cpus: float = checker.cap_config.max_default_capability.cpus
        max_memory: int = checker.cap_config.max_default_capability.memory
        max_gpus: int = checker.cap_config.max_default_capability.gpus
    print(f'Your Maximum Capability Information:\n' f'cpus = {float(max_cpus)}, ' f'memory = {max_memory}, ' f'gpus = {max_gpus}')

    # check whether input legal or not
    while True:
        print("Please enter the capability information 'cpus(float) memory(int) gpus(int)':")
        args = list(filter(lambda x: x, input().split(' ')))  # use filter lambda to remove overflow
        if len(args) != 3:
            output = str_format(
                word=f"Incorrect number of parameters: expected 3, received {len(args)}", style='default', fore='r', background='black'
            )
            print(output)
            continue
        try:
            cap_info.cpus = float(args[0])
        except ValueError:
            print(str_format(word='ValueError: cpus must be float or int', style='default', fore='r', background='black'))
            continue
        try:
            cap_info.memory = int(args[1])
        except ValueError:
            print(str_format(word='ValueError: memory must be int', style='default', fore='r', background='black'))
            continue
        try:
            cap_info.gpus = int(args[2])
        except ValueError:
            print(str_format(word='ValueError: gpus must be int', style='default', fore='r', background='black'))
            continue

        error_msg_ls = []
        if cap_info.cpus < min_cpus or cap_info.cpus > max_cpus:
            error_msg_ls.append(f'cpus rate domain error: expected {min_cpus} ~ {max_cpus}')
        if cap_info.memory < min_memory or cap_info.memory > max_memory:
            error_msg_ls.append(f'memory amount domain error: expected {min_memory} ~ {max_memory}')
        if cap_info.gpus < min_gpus or cap_info.gpus > max_gpus:
            error_msg_ls.append(f'gpus number domain error: expected {min_gpus} ~ {max_gpus}')
        if len(error_msg_ls) > 0:
            print(str_format("\n".join(error_msg_ls), fore='r'))
            continue
        break


def __get_bookingtime():
    while True:
        print("Please enter the start time, the form is YYYY MM DD hh mm:")
        start_time_args = list(filter(lambda x: x, input().split(' ')))

        # set now time
        now_time = datetime.timestamp(datetime.now())
        now_sec = now_time % 3600
        if now_sec > 1800:
            now_time = now_time + (1800 - now_sec)
        else:
            now_time = now_time - now_sec
            # now_time = datetime.strftime(datetime.fromtimestamp(now_time), '%Y-%m-%d %H:%M:%S')

        # using time flag 'now'
        if len(start_time_args) == 1 and start_time_args[0] == 'now':
            booking_time.start = now_time
            break
        # using time flag 'days or weeks'
        if len(start_time_args) == 1:
            day_flag = list(filter(lambda x: '-day' in x, start_time_args))
            week_flag = list(filter(lambda x: '-week' in x, start_time_args))
            if len(day_flag) + len(week_flag) == 0:
                print(str_format(word=f'Wrong input!!! ValueError', style='default', fore='r', background='black'))
                continue
            if len(week_flag + day_flag) > 1:
                print(str_format(word=f'Wrong input!!! ValueError', style='default', fore='r', background='black'))
                continue
            else:
                if len(day_flag) == 1:
                    day_info: str
                    try:
                        day_info = day_flag[0].replace('-day', '')
                    except ValueError:
                        print(str_format(word=f'Wrong input!!! ValueError', style='default', fore='r', background='black'))
                        continue
                    try:
                        day_info = int(day_info)
                    except ValueError:
                        print(str_format(word=f'Wrong input!!! ValueError', style='default', fore='r', background='black'))
                        continue
                    if day_info > 14 or day_info < 1:
                        print(str_format(word=f'Wrong input!!! ValueError', style='default', fore='r', background='black'))
                        continue
                    else:
                        booking_time.start = now_time + day_info * 86400  # 86400 sec -> 1 day
                        # booking_time.start = datetime.strftime(datetime.fromtimestamp(booking_time.start), '%Y-%m-%d %H:%M:%S')
                        # print(booking_time.start)
                    break
                elif len(week_flag) == 1:
                    week_info: str
                    week_info = week_flag[0].replace('-week', '')
                    try:
                        week_info = int(week_info)
                    except ValueError:
                        print(str_format(word=f'Wrong input!!! ValueError', style='default', fore='r', background='black'))
                        continue
                    if week_info > 2 or week_info < 1:
                        print(str_format(word=f'Wrong input!!! ValueError', style='default', fore='r', background='black'))
                        continue
                    else:
                        booking_time.start = now_time + week_info * 604800  # 604800 sec -> 1 week
                        # booking_time.start = datetime.strftime(datetime.fromtimestamp(booking_time.start), '%Y-%m-%d %H:%M:%S')
                        # print(booking_time.start)
                    break
        # using datetime
        else:
            try:
                start_time_args = list(map(int, start_time_args))  # str -> int
            except ValueError:
                print(str_format(word=f'Wrong input!!! ValueError', style='default', fore='r', background='black'))
                continue
            if len(start_time_args) != 5:
                print(
                    str_format(
                        word=f'Wrong input!!! Incorrect number of parameters: expected 5, received {len(start_time_args)}',
                        style='default',
                        fore='r',
                        background='black',
                    )
                )
                continue
            if start_time_args[4] % 30 != 0:
                print(str_format(word=f'Wrong input!!! "mm" must be "00" or "30"', style='default', fore='r', background='black'))
                continue
            try:
                booking_time.start = datetime(*start_time_args[:4], *start_time_args[4:])
            except ValueError:
                print(str_format(word=f'Wrong input!!! ValueError', style='default', fore='r', background='black'))
                continue
            except OverflowError:
                print(str_format(word=f'Wrong input!!! OverflowError', style='default', fore='r', background='black'))
                continue

            dif = datetime.timestamp(booking_time.start) - datetime.timestamp(datetime.now())
            if dif > 1209600:
                print(
                    str_format(
                        word=f'Wrong input!!! The reserverd time must be wtihin two weeks',
                        style='default',
                        fore='r',
                        background='black',
                    )
                )
                continue
            elif dif < 0:
                print(
                    str_format(
                        word=f'Wrong input!!! The reserverd time must be wtihin two weeks',
                        style='default',
                        fore='r',
                        background='black',
                    )
                )
                continue
            else:
                booking_time.start = datetime.timestamp(booking_time.start)
                break

    while True:
        print("Please enter the end time, the form is YYYY MM DD hh mm:")
        end_time_args = list(filter(lambda x: x, input().split(' ')))
        # using time flag
        day_flag = list(filter(lambda x: '-day' in x, end_time_args))
        week_flag = list(filter(lambda x: '-week' in x, end_time_args))
        if len(week_flag + day_flag) > 1:
            print(str_format(word=f'Wrong input!!! Only accept one time flag', style='default', fore='r', background='black'))
            continue
        else:
            if len(day_flag) == 1:
                day_info: str
                try:
                    day_info = day_flag[0].replace('-day', '')
                except ValueError:
                    print(str_format(word=f'Wrong input!!! ValueError', style='default', fore='r', background='black'))
                try:
                    day_info = int(day_info)
                except ValueError:
                    print(str_format(word=f'Wrong input!!! ValueError', style='default', fore='r', background='black'))
                    continue
                if day_info > 14 or day_info < 1:
                    print(str_format(word=f'Wrong input!!! ValueError', style='default', fore='r', background='black'))
                    continue
                else:
                    booking_time.end = booking_time.start + day_info * 86400  # 86400 sec -> 1 day
                    booking_time.end = datetime.strftime(datetime.fromtimestamp(booking_time.end), '%Y-%m-%d %H:%M:%S')
                    booking_time.start = datetime.strftime(datetime.fromtimestamp(booking_time.start), '%Y-%m-%d %H:%M:%S')
                    print(booking_time.end)
                break
            elif len(week_flag) == 1:
                week_info: str
                week_info = week_flag[0].replace('-week', '')
                try:
                    week_info = int(week_info)
                except ValueError:
                    print(str_format(word=f'Wrong input!!! ValueError', style='default', fore='r', background='black'))
                    continue
                if week_info > 2 or week_info < 1:
                    print(str_format(word=f'Wrong input!!! ValueError', style='default', fore='r', background='black'))
                    continue
                else:
                    booking_time.end = booking_time.start + week_info * 604800  # 604800 sec -> 1 week
                    booking_time.end = datetime.strftime(datetime.fromtimestamp(booking_time.end), '%Y-%m-%d %H:%M:%S')
                    booking_time.start = datetime.strftime(datetime.fromtimestamp(booking_time.start), '%Y-%m-%d %H:%M:%S')
                    print(booking_time.end)
                break
            # using datetime
            else:
                try:
                    end_time_args = list(map(int, end_time_args))  # str -> int
                except ValueError:
                    print(str_format(word=f'Wrong input!!! ValueError', style='default', fore='r', background='black'))
                    continue
                if len(end_time_args) != 5:
                    print(
                        str_format(
                            word=f'Wrong input!!! Incorrect number of parameters: expected 3, received {len(end_time_args)}',
                            style='default',
                            fore='r',
                            background='black',
                        )
                    )
                    continue
                if end_time_args[4] % 30 != 0:
                    print(str_format(word=f'Wrong input!!! "mm" must be "00" or "30"', style='default', fore='r', background='black'))
                    continue
                try:
                    booking_time.end = datetime(*end_time_args[:4], *end_time_args[4:], tzinfo=timezone.utc)
                except ValueError:
                    print(str_format(word=f'Wrong input!!! ValueError', style='default', fore='r', background='black'))
                    continue
                except OverflowError:
                    print(str_format(word=f'Wrong input!!! OverflowError', style='default', fore='r', background='black'))
                    continue
                dif = booking_time.end.timestamp() - booking_time.start - 28800

                if dif < 0 or dif > 1209600:  # 1209600 = 2 weeks -> sec
                    print(
                        str_format(
                            word=f'Wrong input!!! The reserverd time must be wtihin two weeks',
                            style='default',
                            fore='r',
                            background='black',
                        )
                    )
                    continue
                else:
                    booking_time.end = datetime.strftime(
                        datetime.fromtimestamp(booking_time.end.timestamp() - 28800), '%Y-%m-%d %H:%M:%S'
                    )  # for same structure
                    booking_time.start = datetime.strftime(datetime.fromtimestamp(booking_time.start), '%Y-%m-%d %H:%M:%S')
                    break
    # Optional


def __New_user_config(user_id):

    while True:
        randon_forward_ports = random.randint(10001, 11000)
        if checker.check_forward_port_empty(randon_forward_ports) == True:
            break
    user_config_dict = checker.users_config.to_dict()
    new_user_data = {
        "password": "0000",
        "forward_port": f"{randon_forward_ports}",
        "image": "null",
        "extra_command": "null",
        "volume_work_dir": f"{'Checker.deploy_info.volume_work_dir'}/{user_id}",
        "volume_dataset_dir": f"{'Checker.deploy_info.volume_dataset_dir'}/{user_id}",
        "volume_backup_dir": f"{'Checker.deploy_info.volume_backup_dir'}/{user_id}",
    }
    user_config_dict[user_id] = new_user_data
    dump_yaml(user_config_dict, checker.deploy_info.users_config_yaml)
    print(
        'user_id:{' f"{user_id}" '}\n',
        'password:0000\n',
        'forward_port:' f"{randon_forward_ports}" '\n',
        'image: null\n',
        'extra_command:null',
    )
    return True


def __user_options(user_id, password):
    checker = Checker(deploy_yaml='cfg/test_host_deploy.yaml')

    # Part Forward_ports
    while True:
        user_config.forward_port = input(
            f"Please enter the forward port(default:{checker.users_config.ids[user_id].forward_port}, none by default):\n"
        )
        if len(user_config.forward_port) == 0:
            user_config.forward_port = checker.users_config.ids[user_id].forward_port
            break
        try:
            user_config.forward_port = int(user_config.forward_port)
        except ValueError:
            print(str_format(word='ValueError!', style='default', fore='r', background='black'))
            continue
        if user_config.forward_port < forword_port_begin or user_config.forward_port > forword_port_end:
            print(
                str_format(
                    word=f'Forward Port must between {forword_port_begin}~{forword_port_end}!',
                    style='default',
                    fore='r',
                    background='black',
                )
            )
            continue
        if checker.check_forward_port_empty(user_config.forward_port) == False:
            print(str_format(word='Forward Port Duplicated!', style='default', fore='r', background='black'))
            continue
        else:
            break

    # Part image
    while True:
        empty_string = ""
        print("\nImage available list:")
        print(str_format("\n".join(checker.deploy_info.images), fore='g'))
        print(str_format("If there is no image you wish, please contact your host maintainer(MLOps).", fore='y'))
        image = checker.users_config.ids[user_id].image
        if image == None:
            image = "rober5566a/aivc-server:latest"
        try:
            user_config.image = str(input(f"Please enter the image 'repository/tag'(default: {image}, none by default):\n"))
        except ValueError:
            print(str_format(word='ValueError!', style='default', fore='r', background='black'))
            continue
        if user_config.image == empty_string:
            user_config.image = image
            break
        if user_config.image not in checker.deploy_info.images:
            print(str_format(word='Image available!', style='default', fore='r', background='black'))
            continue
        if checker.check_image_isexists(user_config.image) == False:
            print(
                str_format(
                    word=f"Not found your default image{user_config.image} Use system's default rober5566a/aivc-server:latest ",
                    style='default',
                    fore='r',
                    background='black',
                )
            )
            continue
        else:
            break

    # Part extra_commands
    while True:
        print("Please enter the extra command when running the image. (default: None, none by default):\n")
        break

    # Part Update_password
    while True:
        try:
            update_password: bool = ask_yn(question="Do you want to update the password?", fore="white")
        except IndexError:
            print(str_format(word='IndexError!, please check your input!!!', style='default', fore='r', background='black'))
            continue
        if update_password is False:
            new_password = password
            break
        if update_password is True:
            new_password = getpass.getpass(
                prompt="Please enter the new Password: ",
            )
            if new_password == '':
                print(str_format(word="Incorrect!! The password can't be empty!!", style='default', fore='r', background='black'))
                continue
            else:
                check_new_password = getpass.getpass(prompt="Please enter the new password again:")
            if new_password != check_new_password:
                print(str_format(word='Incorrect!!', style='default', fore='r', background='black'))
                continue
            else:
                yaml = YAML()
                with open("cfg/test_users_config.yaml", "r", encoding='utf-8') as f:
                    data = yaml.load(f)
                data[user_id]['password'] = new_password
                with open("cfg/test_users_config.yaml", "w", encoding="utf-8") as f:
                    yaml.dump(data, f)
                print(str_format(word='Update default Password!', style='default', fore='g', background='black'))
                break

    # Part Update users_config.yaml
    while True:
        try:
            update_users_config: bool = ask_yn(
                question="The previous setting is for the once, do you want to update the default config?", fore="white"
            )
        except IndexError:
            print(str_format(word='ValueError!', style='default', fore='r', background='black'))
        if update_users_config == False:
            break
        if update_users_config == True:
            temp_user_config_dict = checker.users_config.to_dict()
            temp_user_config_dict[user_id]['forward_port'] = f'{user_config.forward_port}'
            temp_user_config_dict[user_id]['image'] = f'{user_config.image}'
            temp_user_config_dict[user_id]['extra_command'] = f'{user_config.extra_command}'
            temp_user_config_dict[user_id]['password'] = f'{new_password}'
            dump_yaml(temp_user_config_dict, checker.deploy_info.users_config_yaml)
            print(str_format(word='Update success!', style='default', fore='g', background='black'))
            break


def __list_schedules():
    data = checker.booking.df
    # Checker.booking_df got two data, need checker fix it !!!
    data = data.sort_values(by='start')
    print(data.head())


def booking(user_id: str, cap_info: BasicCapability, booking_time: BookingTime, user_config: UserConfig, booking_csv: Path) -> bool:
    '''
    Write the booking_info to the booking schedule.

    `user_id`: user's account.
    `cap_info`: cpus, memory, gpus.
    `booking_time`: checked available times.
    `user_config`: the config for this user_id.
    `booking_csv`: the csv for booking, default: 'jobs/booking.csv'.
    '''
    sc = ScheduleColumnNames()
    # best_gpus = checker.get_best_gpu_ids(cap_info.gpus, booking_time.start)

    df1 = checker.booking.df
    checker.booking.update_csv
    df2 = pd.DataFrame(
        {
            sc.start: [booking_time.start],
            sc.end: [booking_time.end],
            sc.user_id: [user_id],
            sc.cpus: [cap_info.cpus],
            sc.memory: [cap_info.memory],
            sc.gpus: f'[{cap_info.gpus}]',
            # sc.gpus: f'[{best_gpus}]',
            sc.forward_port: [user_config.forward_port],
            sc.image: [user_config.image],
            sc.extra_command: [user_config.extra_command],
        }
    )
    checker.booking.df = ScheduleDF.concat(df1, df2)
    checker.booking.update_csv()
    # right "now" to jobs/monitor_exec


if __name__ == '__main__':
    cli()
