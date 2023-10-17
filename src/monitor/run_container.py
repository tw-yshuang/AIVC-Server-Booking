#!/usr/bin/env python3
import os, subprocess, shutil, math
from pathlib import Path
from typing import List, Tuple

import click
from pandas import isna

PROJECT_DIR = Path(__file__).resolve().parents[2]
if __name__ == '__main__':
    import sys

    sys.path.append(str(PROJECT_DIR))

from src.HostInfo import load_yaml, HostDeployInfo, CapabilityConfig, UserConfig, MaxCapability

DEFAULT_BACKUP_DIR = PROJECT_DIR / 'cfg/templates/Backup'
DEFAULT_BACKUP_YAML_FILENAME = 'backup.yaml'
DEFAULT_IMAGE = 'rober5566a/aivc-server'
DEFAULT_IMAGE_TAG = 'latest'

CONTAINER_WORK_DIR = '/root/Work'
CONTAINER_BACKUP_DIR = '/root/Backup'
CONTAINER_DATASET_DIR = '/root/Dataset'

HELP_DICT = {
    'user_id': 'User ID.',
    'pw': 'password.',
    'fp': 'which forward port you want to connect to port: 22(SSH).',
    'cpus': 'number of cpus for container.',
    'mem': 'how much memory(ram, swap) GB for container.',
    'gpus': 'how many gpus for container. \b\
    User Guide: https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/user-guide.html',
    'im': 'which image you want to use, new std_id will use "rober5566a/aivc-server:latest"',
    'e-cmd': 'the extra command you want to execute when the docker runs.',
}


class BackupInfo:
    '''
    `Dir`: The backup information for the directories.
    `File`: The backup information for the files.
    '''

    Dir: List[List[str]]
    File: List[List[str]]

    def __init__(self, yaml=PROJECT_DIR / 'cfg/templates/backup.yaml') -> None:
        for k, v in load_yaml(yaml).items():
            setattr(self, k, v)


def prepare_deploy(
    user_config: UserConfig,
    cap_max: MaxCapability,
    memory: int,
    image: str or None,
    extra_command: str or None,
) -> Tuple[str, str, int, List[List[str]]]:
    '''
    `user_config`: The user_config from users_config.yaml, for docker volume used.
    `cap_max`: The maximum capability information, for memory used.
    `image`: The image from booking.csv.
    `extra_command`: The extra_command from booking.csv.
    '''

    if image is None:
        image = f'{DEFAULT_IMAGE}:{DEFAULT_IMAGE_TAG}' if user_config.image is None else user_config.image

    exec_command = extra_command if extra_command is not None else ''
    if DEFAULT_IMAGE in image:
        if exec_command != '':
            exec_command += ' && '
        exec_command += f'/.script/ssh_start.sh {user_config.password}'
        ram_size: int = math.ceil(memory * cap_max.shm_rate)

    # volumes_ls = [[host_path, container_path, operate_flag(Optional)]...]
    volumes_ls: List[List[str]] = [
        [user_config.volume_work_dir, CONTAINER_WORK_DIR],
        [user_config.volume_backup_dir, CONTAINER_BACKUP_DIR],
        [user_config.volume_dataset_dir, CONTAINER_DATASET_DIR, 'ro'],
    ]

    if not os.path.exists(user_config.volume_backup_dir):
        shutil.copytree(DEFAULT_BACKUP_DIR, user_config.volume_backup_dir)
    else:
        backup_info = BackupInfo(f'{user_config.volume_backup_dir}/{DEFAULT_BACKUP_YAML_FILENAME}')
        for backup_path, container_path in [*backup_info.Dir, *backup_info.File]:
            backup_path = f'{user_config.volume_backup_dir}/{backup_path}'
            if os.path.exists(backup_path):
                volumes_ls.append([backup_path, container_path])

    return image, exec_command, ram_size, volumes_ls


def run(
    user_id: str,
    forward_port: int,
    cpus: float,
    memory: int,
    gpus: List[int] or str,
    image: str or None,
    exec_command: str or None,
    ram_size: int,
    volumes_ls: List[List[str]],
):
    '''
    `user_id`: student ID.\n
    `forward_port`: which forward port you want to connect to port: 2(SSH).\n
    `cpus`: Number of CPU utilities.\n
    `memory`: Number of memory utilities.\n
    `gpus`: List of gpu id used for the container.\n
    `image`: Which image you want to use, new std_id will use "rober5566a/aivc-server:latest"\n
    `exec_command`: The exec command you want to execute when the docker runs.\n
    `ram_size`: The DRAM size that you want to assign to this container,\n
    `volumes_ls`: List of volume information, format: [[host, container, ]...]
    '''

    volume_info = ' -v '.join(':'.join(volume_ls) for volume_ls in volumes_ls)

    if isinstance(gpus, (int, str)):
        gpus = [gpu for gpu in range(0, int(gpus))]

    gpus = ','.join(str(gpu) for gpu in gpus) if len(gpus) != 0 else 'none'

    exec_str = f'docker run\
                -dit\
                --restart=always\
                --pid=host\
                --cpus={cpus}\
                --memory={ram_size}G\
                --memory-swap={memory}G\
                --shm-size={memory-ram_size}G\
                --gpus "device={gpus}"\
                --name={user_id}\
                -p {forward_port}:22\
                -v {volume_info}\
                -e DISPLAY=$DISPLAY\
                {image}\
                {exec_command}\
                '

    return subprocess.run(exec_str.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8').stderr.split('\n')[0]


def run_container(
    user_id: str,
    forward_port: int,
    cpus: float = 2,
    memory: int = 8,
    gpus: List[int] = 1,
    image: str or None = None,
    extra_command: str = '',
    user_config: UserConfig = None,
    cap_max: MaxCapability = None,
    *args,
    **kwargs,
) -> None:
    # the value of image & extra_command maybe is nan, pd.NA, np.nan ..., use this method to convert it first.
    image = None if isna(image) else image
    extra_command = None if isna(extra_command) else extra_command

    image, exec_command, ram_size, volumes_ls = prepare_deploy(user_config, cap_max, memory, image, extra_command)

    return run(user_id, forward_port, cpus, memory, gpus, image, exec_command, ram_size, volumes_ls)


@click.command(context_settings=dict(help_option_names=['-h', '--help'], max_content_width=120))
@click.option('-id', '--user-id', help=HELP_DICT['user_id'], required=True, prompt=True)
@click.option('-pw', '--password', help=HELP_DICT['pw'], required=True, prompt="Please enter the Password", hide_input=True)
@click.option('-fp', '--forward-port', help=HELP_DICT['fp'], required=True, prompt=True)
@click.option('-cpus', show_default=True, default=8, help=HELP_DICT['cpus'])
@click.option('-mem', '--memory', show_default=True, default=32, help=HELP_DICT['mem'])
@click.option('-gpus', show_default=True, default='0', help=HELP_DICT['gpus'])
@click.option('-im', '--image', show_default=True, default=None, help=HELP_DICT['im'])
@click.option('-e-cmd', '--extra-command', default=None, help=HELP_DICT['e-cmd'])
def cli(
    user_id: str,
    password: str,
    forward_port: int,
    cpus: float = 2,
    memory: int = 8,
    gpus: int or str = '0',
    image: str = None,
    extra_command: str = '',
    *args,
    **kwargs,
) -> None:
    '''Repository: https://github.com/tw-yshuang/AIVC-Server-Booking
    Examples:
    >>> python3 ./run_container.py --user-id tw-yshuang -pw IamNo1handsome! -fp 10001
    '''

    user_config = UserConfig(
        password=password,
        forward_port=forward_port,
        volume_work_dir=f'{HostDI.volume_work_dir}/{user_id}',
        volume_backup_dir=f'{HostDI.volume_backup_dir}/{user_id}',
        volume_dataset_dir=HostDI.volume_dataset_dir,
    )

    run_container(
        user_id,
        user_config.forward_port,
        cpus=cpus,
        memory=memory,
        gpus=gpus,
        image=image,
        extra_command=extra_command,
        user_config=user_config,
        cap_max=CapabilityConfig(PROJECT_DIR / HostDI.capability_config_yaml).max,
    )


if __name__ == '__main__':
    HostDI = HostDeployInfo(PROJECT_DIR / 'cfg/host_deploy.yaml')
    cli()
