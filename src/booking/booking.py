#!/usr/bin/env python3
import sys
import random
import getpass
from copy import copy
from typing import List, Union
from pathlib import Path
from datetime import datetime

import click
import numpy as np
import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parents[2]
if __name__ == '__main__':
    sys.path.append(str(PROJECT_DIR))

from lib.WordOperator import str_format, ask_yn
from src.HostInfo import BookingTime, BasicCapability, UserConfig, ScheduleDF, dump_yaml
from src.HostInfo import ScheduleColumnNames as SC
from src.booking.Checker import Checker

checker = Checker(deploy_yaml=PROJECT_DIR / 'cfg/example/host_deploy.yaml')
MONITOR_EXEC_PATH: Path = PROJECT_DIR / 'jobs/monitor_exec'

MIN_CPUS: float = 1
MIN_MEMORY: int = 1
MIN_GPUS: int = 0

DEFAULT_PASSWORD: str = '0000'
FORWARD_PORT_BEGIN: int = 10001
FORWARD_PORT_END: int = 11000

MAX_DAY: int = 14


@click.command(context_settings=dict(help_option_names=['-h', '--help'], max_content_width=120))
@click.option('-id', '--user-id', default='', help="user's account.")
@click.option('-use-opt', '--use-options', default=False, is_flag=True, help="use extra options.")
@click.option('-ls', '--list-schedule', default=False, is_flag=True, help="list schedule that already booking.")
def cli(user_id: str = None, use_options: bool = False, list_schedule: bool = False) -> bool:
    # if user input -ls True
    if list_schedule:
        print(checker.booked_df.sort_values(by='start', ignore_index=True).to_string())
        return False

    if user_id == '':
        user_id = input("Please enter the user_id: ")

    # check user_id
    if user_id not in checker.cap_config.allow_userIDs:
        print(str_format("InputError: Unknown account! Check your user account or connect to the Host Maintainer(MLOps).", fore='r'))
        return False

    # check user_id is new user
    if user_id not in checker.users_config.ids:
        password = DEFAULT_PASSWORD
        print(f"The password for the new user: {DEFAULT_PASSWORD}")
    else:
        password = checker.users_config.ids[user_id].password

    isWrong = True  # a flag for checking if tne login success
    for _ in range(3):  # There are three times chances for user to enter password correctly
        input_password = getpass.getpass(prompt="Please enter the password: ")
        if input_password == password:
            isWrong = False  # login successfully
            break
        else:
            print("Wrong password!!")
    if isWrong:
        print("ByeBye~~")  # login failed
        return False

    while True:
        cap_info = __get_caps_info(user_id)
        booking_time = __get_bookingtime(
            user_bookedtime_df=checker.booked_df[checker.booked_df.user_id.values == user_id].loc[:, [SC.start, SC.end]]
        )

        if checker.check_cap4time(cap_info, booking_time):
            break
        else:
            print(str_format(f"There is not enough computing power for the time you need, book again.", fore='y'))
            continue

    if user_id in checker.users_config.ids:
        user_config = copy(checker.users_config.ids[user_id])
    else:
        user_config = __add_new_user_config(user_id)

    if use_options:
        user_config = __setting_user_options(user_id, user_config)

    while checker.check_forward_port4time(user_config.forward_port, booking_time) is False:
        print(str_format(f"DuplicateError: Forward Port duplicated with others during the time you are booking!!", fore='r'))
        user_config.forward_port = __setting_forward_port(user_id, checker.users_config.ids[user_id].forward_port)

    booking(user_id, cap_info, booking_time, user_config)


def __get_caps_info(user_id: str) -> BasicCapability:
    if user_id in checker.cap_config.max_custom_capability:
        max_cpus: float = checker.cap_config.max_custom_capability[user_id].cpus
        max_memory: int = checker.cap_config.max_custom_capability[user_id].memory
        max_gpus: int = checker.cap_config.max_custom_capability[user_id].gpus
    else:
        max_cpus: float = checker.cap_config.max_default_capability.cpus
        max_memory: int = checker.cap_config.max_default_capability.memory
        max_gpus: int = checker.cap_config.max_default_capability.gpus
    print(
        f"Your Maximum Capability Information:\n{str_format(f'cpus={float(max_cpus)}, memory={max_memory}, gpus={max_gpus}', fore='g')}"
    )

    cap_info_ls: List[float, int, int]
    while True:
        isWrong = False

        args = list(
            filter(lambda x: x, input("Please enter the capability information 'cpus(float) memory(int) gpus(int)': ").split(' '))
        )  # use filter lambda to remove overflow
        if len(args) != 3:
            print(str_format(f"InputError: Incorrect number of parameters: expected 3, received {len(args)}", fore='r'))
            continue

        cap_info_ls: List[float, int, int] = []
        cap_str_ls: List[str] = ['cpus', 'memory', 'gpus']

        for arg, cap_str in zip(args, cap_str_ls):
            try:
                cap_info_ls.append(float(arg) if cap_str == 'cpus' else int(arg))
            except ValueError:
                cap_str += " must be float or int" if cap_str == 'cpus' else " must be int"
                print(str_format(f"ValueError: {cap_str}", fore='r'))
                isWrong = True

        if isWrong:
            continue

        for cap, cap_str, max_info, min_info in zip(
            cap_info_ls, cap_str_ls, [max_cpus, max_memory, max_gpus], [MIN_CPUS, MIN_MEMORY, MIN_GPUS]
        ):
            if cap < min_info or cap > max_info:
                cap_str += f": {min_info} ~ {max_info}"
                print(str_format(f"RequireError: {cap_str}", fore='r'))
                isWrong = True

        if isWrong:
            continue
        break

    return BasicCapability(*cap_info_ls, defaultCap=checker.cap_config.max_default_capability, maxCap=checker.cap_config.max)


def __filter_time_flags(input_time_args: List[str], time_flag: str) -> int:
    time_flag_value = 0
    for input_time_arg in input_time_args:
        if time_flag in input_time_arg:
            try:
                time_flag_value += int(input_time_arg[: -(len(time_flag) + 1)])
            except ValueError:
                return -1  # InputError signal

    return time_flag_value


def __get_bookingtime(user_bookedtime_df: Union[pd.DataFrame, None]) -> BasicCapability:

    sec2day = 86400
    sec2week = sec2day * 7
    start2end_float = [0.0, 0.0]
    start2end_datetime: List[datetime] = []
    booked_checkcode = np.zeros_like(user_bookedtime_df, dtype=np.uint8).T

    # now time unit setting.
    now = datetime.timestamp(datetime.now())
    now_sec = now % 3600
    now += now_sec // 1800 * 1800 - now_sec

    for i, bk_str in enumerate(['start', 'end']):
        while True:
            useDatetimeFormat = False
            input_time_args = list(
                filter(lambda x: x, input(f"Please enter the {bk_str} time, the form is YYYY MM DD hh mm: ").split(' '))
            )
            now_float = now * (1 - i) + start2end_float[0] * i

            # using time flag 'now'
            if 'now' in input_time_args:
                if i == 0 and len(input_time_args) == 1:
                    start2end_float[i] = now_float
                    break
                elif i == 1:
                    print(str_format("InputError: end time can not user 'now' flag!!", fore='r'))
                    continue
                else:
                    print(str_format("InputError: Can not use multiple Time_Flags with 'now'!!", fore='r'))
                    continue

            checkCode = 2
            start2end_float[i] = 0.0
            for time_flag, max_value, sec2convert in zip(['day', 'week'], [MAX_DAY, MAX_DAY // 7], [sec2day, sec2week]):
                time_flag_value = __filter_time_flags(input_time_args, time_flag)

                if time_flag_value == 0:
                    continue
                elif time_flag_value == -1:
                    print(str_format("InputError: Time_Flag format is wrong!!", fore='r'))
                    checkCode += 2
                elif time_flag_value < 1 or time_flag_value > max_value:
                    print(str_format(f"ValueError: The range of Time_Flag: {time_flag} must be 1 ~ {max_value}.", fore='r'))
                    checkCode += 2
                else:
                    start2end_float[i] += time_flag_value * sec2convert
                    checkCode -= 1

            if checkCode < 2:  # user is correctly use time_flag
                start2end_float[i] += now_float
            elif checkCode == 2:  # user is using datetime format
                useDatetimeFormat = True
            else:  # user has wrong Time_Flag format.
                continue

            if useDatetimeFormat:
                try:
                    time_args = list(map(int, input_time_args))  # str -> int
                except ValueError:
                    print(str_format("InputError: Datetime format is wrong!!", fore='r'))
                    continue

                time_args_len = len(time_args)
                if time_args_len != 5:
                    print(str_format(f"InputError: Incorrect number of parameters: expected 5, received {time_args_len}!!", fore='r'))
                    continue

                if time_args[4] % 30 != 0:
                    print(str_format(f'ValueError: "mm" must be "00" or "30"', fore='r'))
                    continue

                try:
                    start2end_float[i] = datetime(*time_args).timestamp()
                except ValueError as e:
                    print(str_format(f"ValueError: {e}", fore='r'))
                    continue

            time_accept = -(start2end_float[i] - now_float * (1 - i) - start2end_float[0] * i) // (sec2day * MAX_DAY) * -1

            if time_accept != 1:
                from_str = "now + 30min" if i == 0 else "start time"
                print(str_format(f"ValueError: The {bk_str} time must be within 2 weeks from {from_str}!!", fore='r'))
                continue

            start2end_datetime.append(datetime.fromtimestamp(start2end_float[i]))

            booked_checkcode[0] = user_bookedtime_df[SC.start] < start2end_datetime[i]
            booked_checkcode[1] = user_bookedtime_df[SC.end] > start2end_datetime[i]
            if (booked_checkcode.sum(axis=0) == 2).any():
                print(str_format(f"OverlapError: The {bk_str} time is overlap with your previous booking!!", fore='r'))
                continue

            break

    return BookingTime(*start2end_datetime)


def __update_users_config_and_yaml(user_id: str, user_config: UserConfig):
    checker.users_config.ids[user_id] = user_config

    dump_yaml(checker.users_config.to_dict(), PROJECT_DIR / checker.deploy_info.users_config_yaml)


def __add_new_user_config(user_id: str) -> UserConfig:
    while True:
        random_forward_ports = random.randint(FORWARD_PORT_BEGIN, FORWARD_PORT_END)
        if checker.check_forward_port_empty(user_id, random_forward_ports) == True:
            break

    user_config = UserConfig(
        password=DEFAULT_PASSWORD,
        forward_port=random_forward_ports,
        image=None,
        extra_command=None,
        volume_work_dir=f"{checker.deploy_info.volume_work_dir}/{user_id}",
        volume_dataset_dir=f"{checker.deploy_info.volume_dataset_dir}",
        volume_backup_dir=f"{checker.deploy_info.volume_backup_dir}/{user_id}",
    )

    __update_users_config_and_yaml(user_id, user_config)
    print(str_format(f"{user_id}'s profile:", fore='y'))
    for k, v in user_config.dict.items():
        if 'volume' not in k:
            print(f"    {k}: {v}")

    return user_config


def __setting_forward_port(user_id: str, default_forward_port: int):
    while True:
        forward_port = input(f"Please enter the forward port(default:{default_forward_port}, none by default): ")
        try:
            forward_port = int(forward_port) if forward_port != '' else default_forward_port
            if forward_port < FORWARD_PORT_BEGIN or forward_port > FORWARD_PORT_END:
                raise ValueError
        except ValueError:
            print(str_format(f"ValueError: must be int, and the range in {FORWARD_PORT_BEGIN} ~ {FORWARD_PORT_END}", fore='r'))
            continue

        if checker.check_forward_port_empty(user_id, forward_port) is False:
            print(str_format(f"DuplicateError: Forward Port duplicated with other user's config!!", fore='r'))
            continue

        break
    return forward_port


def __setting_user_options(user_id: str, user_config: UserConfig):
    # Forward Port
    user_config.forward_port = __setting_forward_port(user_id, user_config.forward_port)

    # Image
    while True:
        print("\nImage available list:")
        print(str_format("\n".join(checker.deploy_info.images), fore='g'))
        print(str_format("If there is no image you wish, please contact your host maintainer(MLOps).", fore='y'))

        image = checker.users_config.ids[user_id].image
        if image == None:
            image = "rober5566a/aivc-server:latest"

        image = input(f"Please enter the image 'repository/tag'(default: {image}, none by default): ")

        if image == '':
            user_config.image = None
            break

        if not checker.check_image_isexists(image):
            print(str_format("AvailableError: Not the available image!", fore='r'))
            continue

        user_config.image = image
        break

    # extra_commands
    extra_command = input("Please enter the extra command when running the image. (default: None, none by default): ")
    user_config.extra_command = extra_command if extra_command != '' else None

    # Update Password
    isUpdate = ask_yn("Do you want to update the password?")
    while isUpdate:
        new_password = getpass.getpass(prompt="Please enter the new Password: ")
        if new_password == '':
            print(str_format("Incorrect!! The password can't be empty!!", fore='r'))
            continue
        else:
            check_new_password = getpass.getpass(prompt="Please enter the new password again: ")

        if new_password != check_new_password:
            print(str_format("UpdatePasswordError: Two input passwords are not the same!!", fore='r'))
            continue
        else:
            checker.users_config.ids[user_id].password = new_password
            __update_users_config_and_yaml(user_id, checker.users_config.ids[user_id])
            print(str_format("Update default Password!", fore='g'))
            break

    # Update users_config.yaml
    if ask_yn("The previous setting is for the once, do you want to update the default config?"):
        __update_users_config_and_yaml(user_id, user_config)
        print(str_format("Update your user_config!", fore='g'))

    return user_config


def booking(user_id: str, cap_info: BasicCapability, booking_time: BookingTime, user_config: UserConfig) -> bool:
    '''
    Write the booking_info to the booking schedule.

    `user_id`: user's account.
    `cap_info`: cpus, memory, gpus.
    `booking_time`: checked available times.
    `user_config`: the config for this user_id.
    '''
    best_gpus = checker.get_best_gpu_ids(cap_info.gpus, booking_time)

    df1 = checker.booking.df
    df2 = pd.DataFrame(
        {
            SC.start: [booking_time.start],
            SC.end: [booking_time.end],
            SC.user_id: [user_id],
            SC.cpus: [cap_info.cpus],
            SC.memory: [cap_info.memory],
            SC.gpus: [best_gpus],
            SC.forward_port: [user_config.forward_port],
            SC.image: [user_config.image],
            SC.extra_command: [user_config.extra_command],
        }
    )
    checker.booking.df = ScheduleDF.concat(df1, df2)
    checker.booking.update_csv()

    # if use Time_Flag: 'now'
    if booking_time.start < datetime.now():
        with open(MONITOR_EXEC_PATH, 'a') as f:
            f.write('now\n')

    print(str_format(f"Booking successful!", fore='g'))


if __name__ == '__main__':
    # sys.argv = ['booking.py', '-id', 'm11007s05-2', '-use-opt']
    cli()

    # cap_info = __get_caps_info('m11007s05-3')

    # booking_time = __get_bookingtime()
    # print(f"start: {booking_time.start}")
    # print(f"end: {booking_time.end}")
