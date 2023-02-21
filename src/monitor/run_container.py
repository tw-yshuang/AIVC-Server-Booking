import os, shutil
from pathlib import Path
from typing import List
from dataclasses import asdict

import click

if __name__ == '__main__':
    import sys

    sys.path.extend('../../')

from lib.WordOperator import str_format
from src.HostInfo import load_yaml, HostDeployInfo, CapabilityConfig, UserConfig

default_backup_dir = Path('cfg/templates/Backup')
default_backup_yaml_path = Path('cfg/templates/Backup/backup.yaml')

container_work_dir = '/root/Work'
container_backup_dir = '/root/Backup'
container_dataset_dir = '/root/Dataset'

help_dict = {
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
    Dir: List[List[str]] = [[]]
    File: List[List[str]] = [[]]

    def __init__(self, yaml='cfg/templates/backup.yaml') -> None:
        for k, v in load_yaml(yaml).items():
            setattr(self, k, v)


def check2create_dir(dir: Path):
    try:
        if not os.path.exists(dir):
            os.mkdir(dir)
            print(str_format(f"Successfully created the directory: {dir}", fore='g'))
            return False
        else:
            return True
    except OSError:
        raise OSError(str_format(f"Fail to create the directory {dir} !", fore='r'))


def prepare_deploy(
    user_config: UserConfig,
    cap_max: CapabilityConfig().max,
    memory: int,
    image: str or None,
    extra_command: str or None,
):
    '''
    `user_config`: The user_config from users_config.yaml, for docker volume used.
    `cap_max`: The maximum capability information, for memory used.
    `image`: The image from booking.csv.
    `extra_command`: The extra_command from booking.csv.
    '''

    if image is None:
        image = 'rober5566a/aivc-server:latest'

    exec_command = extra_command if extra_command is not None else ''
    if 'rober5566a/aivc-server' in image:
        if exec_command != '':
            exec_command += ' && '
        exec_command += f'/.script/ssh_start.sh {user_config.password}'
        ram_size: int = int(memory * cap_max.shm_rate)

    # volumes_ls = [[host_dir, container_dir, operate_flag(Optional)]...]
    volumes_ls: List[List[str]] = [
        [user_config.volume_work_dir, container_work_dir],
        [user_config.volume_backup_dir, container_backup_dir],
        [user_config.volume_dataset_dir, container_dataset_dir, 'ro'],
    ]

    if not os.path.exists(user_config.volume_backup_dir):
        shutil.copytree(default_backup_dir, user_config.volume_backup_dir)
    else:
        backup_info = BackupInfo(default_backup_yaml_path)
        for backup_dir, container_dir in backup_info.Dir:
            backup_dir = f'{user_config.volume_backup_dir}/{backup_dir}'
            if os.path.exists(backup_dir):
                volumes_ls.append([backup_dir, container_dir])

        for backup_path, container_path in backup_info.File:
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

    if type(gpus) is list:
        if len(gpus) == 1:
            gpus = gpus[0]
        else:
            gpus = ','.join(gpus)

    # add '--pid=host' is not a good idea but nvidia-docker is still not solve this issue, https://github.com/NVIDIA/nvidia-docker/issues/1460
    os.system(
        f'docker run\
                -dit\
                --restart=always\
                --pid=host\
                --cpus={cpus}\
                --memory={ram_size}G\
                --memory-swap={memory}G\
                --shm-size={ram_size}G\
                --gpus={gpus}\
                --name={user_id}\
                -p{forward_port}:22\
                -v {volume_info}\
                -e DISPLAY=$DISPLAY\
                {image}\
                {exec_command}\
                '
    )


def run_container(
    user_id: str,
    forward_port: int,
    cpus: float = 2,
    memory: int = 8,
    gpus: List[int] = 1,
    image: str or None = None,
    extra_command: str = '',
    user_config: UserConfig = None,
    cap_max: CapabilityConfig().max = None,
    *args,
    **kwargs,
):

    image, exec_command, ram_size, volumes_ls = prepare_deploy(user_config, cap_max, memory, image, extra_command)

    run(user_id, forward_port, cpus, memory, gpus, image, exec_command, ram_size, volumes_ls)


@click.command(context_settings=dict(help_option_names=['-h', '--help'], max_content_width=120))
@click.option('-id', '--user-id', help=help_dict['user_id'], required=True)
@click.option('-pw', '--password', help=help_dict['pw'], required=True)
@click.option('-fp', '--forward-port', help=help_dict['fp'], required=True)
@click.option('-cpus', show_default=True, default=8, help=help_dict['cpus'])
@click.option('-mem', '--memory', show_default=True, default=32, help=help_dict['mem'])
@click.option('-gpus', show_default=True, default='0', help=help_dict['gpus'])
@click.option('-im', '--image', show_default=True, default=None, help=help_dict['im'])
@click.option('-e-cmd', '--extra-command', default=None, help=help_dict['e-cmd'])
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
):
    '''Repository: https://github.com/tw-yshuang/AIVC-Server

    EXAMPLES

    >>> python3 ./run_container.py -std-id m11007s05 -pw IamNo1handsome! -fp 2222'''

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
        cap_max=CapabilityConfig(HostDI.capability_config_yaml).max,
    )


if __name__ == '__main__':
    HostDI = HostDeployInfo('cfg/test_host_deploy.yaml')
    cli()

    # # ? for test.

    # user_id = 'm11007s05-4'
    # user_config = UserConfig(
    #     password='0000',
    #     forward_port='2224',
    #     volume_work_dir=f'{HostDI.volume_work_dir}/{user_id}',
    #     volume_backup_dir=f'{HostDI.volume_backup_dir}/{user_id}',
    #     volume_dataset_dir=HostDI.volume_dataset_dir,
    # )

    # run_container(
    #     user_id,
    #     user_config.forward_port,
    #     cpus=8,
    #     memory=16,
    #     gpus=[0],
    #     user_config=user_config,
    #     cap_max=CapabilityConfig(HostDI.capability_config_yaml).max,
    # )
