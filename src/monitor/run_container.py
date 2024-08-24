#!/usr/bin/env python3
import os, subprocess, shutil, math, shlex
from pathlib import Path
from typing import List, Tuple

import click
from pandas import isna

PROJECT_DIR = Path(__file__).resolve().parents[2]
if __name__ == '__main__':
    import sys

    sys.path.append(str(PROJECT_DIR))

from src.HostInfo import load_yaml, HostDeployInfo, CapabilityConfig, UserConfig, MaxCapability

DEFAULT_BACKUP_TEMPLATES = PROJECT_DIR / 'cfg/templates/Backup'
DEFAULT_BACKUP_YAML_FILENAME = 'backup.yaml'
DEFAULT_IMAGE = 'rober5566a/aivc-server'
DEFAULT_IMAGE_TAG = 'latest'

CONTAINER_LOGO = 'A I V C'
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
) -> Tuple[str, str, int, List[List[str]]]:
    '''
    `user_config`: The current user's configuration of the task.
    `cap_max`: The maximum capability information, for memory used.
    '''

    if user_config.image is None:
        user_config.image = f'{DEFAULT_IMAGE}:{DEFAULT_IMAGE_TAG}' if user_config.image is None else user_config.image

    ram_size: int = math.ceil(memory * cap_max.shm_rate)

    # volumes_ls = [[host_path, container_path, operate_flag(Optional)]...]
    volumes_ls: List[List[str]] = [
        [user_config.volume_work_dir, CONTAINER_WORK_DIR],
        [user_config.volume_backup_dir, CONTAINER_BACKUP_DIR],
        [user_config.volume_dataset_dir, CONTAINER_DATASET_DIR, 'ro'],
    ]

    if not os.path.exists(user_config.volume_backup_dir):
        shutil.copytree(DEFAULT_BACKUP_TEMPLATES, user_config.volume_backup_dir)
    else:
        backup_info = BackupInfo(f'{user_config.volume_backup_dir}/{DEFAULT_BACKUP_YAML_FILENAME}')
        for backup_path, container_path in [*backup_info.Dir, *backup_info.File]:
            backup_path = f'{user_config.volume_backup_dir}/{backup_path}'
            if os.path.exists(backup_path):
                volumes_ls.append([backup_path, container_path])

    return ram_size, volumes_ls


def run(
    user_id: str,
    user_config: UserConfig,
    cpus: float,
    memory: int,
    gpus: List[int] | str,
    ram_size: int,
    volumes_ls: List[List[str]],
):
    '''
    `user_id`: student ID.\n
    `user_config`: The current user's configuration of the task.\n
    `cpus`: Number of CPU utilities.\n
    `memory`: Number of memory utilities.\n
    `gpus`: List of gpu id used for the container.\n
    `ram_size`: The DRAM size that you want to assign to this container,\n
    `volumes_ls`: List of volume information, format: [[host, container, ]...]
    '''

    volume_info = ' -v '.join(':'.join(volume_ls) for volume_ls in volumes_ls)

    if isinstance(gpus, (int, str)):
        gpus = [gpu for gpu in range(0, int(gpus))]

    gpus = ','.join(str(gpu) for gpu in gpus) if len(gpus) != 0 else 'none'

    exec_str = f'''docker run\
                -dit\
                --restart=always\
                --pid=host\
                --cpus={cpus}\
                --memory={ram_size}G\
                --memory-swap={memory}G\
                --shm-size={memory-ram_size}G\
                --gpus 'device={gpus}'\
                --name={user_id}\
                -p {user_config.forward_port}:22\
                -v {volume_info}\
                -e DISPLAY=$DISPLAY\
                -e LOGO="{CONTAINER_LOGO}"\
                -e PASSWORD={user_config.password}\
                {user_config.image}\
                '''

    exec_str_ls = shlex.split(exec_str)
    if user_config.extra_command is not None:
        exec_str_ls.extend(['bash -c', user_config.extra_command])

    # print("\n".join(exec_str_ls))

    return subprocess.run(exec_str_ls, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8').stderr.split('\n')[0]


def run_container(
    user_id: str,
    user_config: UserConfig,
    forward_port: int,
    cpus: float = 2,
    memory: int = 8,
    gpus: List[int] = 1,
    image: str | None = None,
    extra_command: str = '',
    cap_max: MaxCapability = None,
    *args,
    **kwargs,
) -> None:

    user_config.forward_port = forward_port
    user_config.image = None if isna(image) else image  # the value maybe is nan, pd.NA, np.nan ...
    user_config.extra_command = None if isna(extra_command) else extra_command  # the value maybe is nan, pd.NA, np.nan ...

    ram_size, volumes_ls = prepare_deploy(user_config, cap_max, memory)

    return run(user_id, user_config, cpus, memory, gpus, ram_size, volumes_ls)


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
    gpus: int | str = '0',
    image: str = None,
    extra_command: str | None = None,
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
