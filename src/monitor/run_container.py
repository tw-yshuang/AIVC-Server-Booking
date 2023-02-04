import os
import click

if __name__ == '__main__':
    import sys

    sys.path.extend('../../')

from lib.WordOperator import str_format, ask_yn
from src.HostInfo import dump_yaml, HostDeployInfo, CapabilityConfig, UserConfig, UsersConfig

HostDI = HostDeployInfo('cfg/test_host_deploy.yaml')

help_dict = {
    'std_id': 'student ID.',
    'pw': 'password.',
    'fp': 'which forward port you want to connect to port: 22(SSH).',
    'cpus': 'number of cpus for container.',
    'mem': 'how much memory(ram, swap) GB for container.',
    'gpus': 'how many gpus for container. \b\
    User Guide: https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/user-guide.html',
    'im': 'which image you want to use, new std_id will use "rober5566a/aivc-server:latest"',
    'e-cmd': 'the extra command you want to execute when the docker runs.',
    's-update': f'silent mode to update users_config.json, default is interactive mode. {str_format("[None(default) | True | Fasle]",fore="y")}',
    's-default': f'silent mode to use default user config, default is interactive mode. {str_format("[None(default) | True | Fasle]",fore="y")}',
}


def check2create_dir(dir: str):
    try:
        if not os.path.exists(dir):
            os.mkdir(dir)
            print(str_format(f"Successfully created the directory: {dir}", fore='g'))
            return False
        else:
            return True
    except OSError:
        raise OSError(str_format(f"Fail to create the directory {dir} !", fore='r'))


def print_user_info(std_id: str, user_dict: dict):
    print(
        # regularize format
        f"'{std_id}': {user_dict}\n".replace("'", '"')
        .replace('{', '{\n        ')
        .replace(', ', ',\n        ')
        .replace('}', '\n}')
    )

    user_know_dict = user_dict.copy()
    del user_know_dict['volume_work_dir']
    del user_know_dict['volume_dataset_dir']
    del user_know_dict['volume_backup_dir']
    print(f"Please paste {std_id}'s personal config to the user:")
    print(
        str_format(
            # regularize format
            f"'{std_id}': {user_know_dict}\n".replace("'", '"')
            .replace('{', '{\n        ')
            .replace(', ', ',\n        ')
            .replace('}', '\n}'),
            fore='y',
        )
    )


def operate_user_config(
    user_id: str,
    password: str,
    forward_port: int,
    image: str = None,
    extra_command: str = '',
    silent_update: bool or None = None,
    silent_user_default: bool or None = None,
    *args,
    **kwargs,
):
    '''
    operate user config
    This function will compare the user's current config & default it the same or not. In most of case, we all just use one container, so this function is like a Fool-proof mechanism to check the you really want to use this user_config, and also update the user_config.

    `user_id`: student ID.\n
    `password`: password.\n
    `forward_port`: which forward port you want to connect to port: 2(SSH).\n
    `image`: which image you want to use.\n
    `extra_command`: the extra command you want to execute when the docker runs.\n
    `silent_update`: silent mode to update users_config.json, default is interactive mode. [None(default) | True | Fasle]\n
    `silent_user_default`: silent mode to use default user config, default is interactive mode. [None(default) | True | Fasle]
    '''
    volume_work_dir = f'{HostDI.volume_work_dir}/{user_id}'
    volume_backup_dir = f'{HostDI.volume_backup_dir}/{user_id}'
    isWrite = False
    if check2create_dir(volume_work_dir) is False:
        check2create_dir(f'{volume_work_dir}/.pyenv-versions')  # create an volume dir to save ~/.pyenv/versions/
        check2create_dir(f'{volume_work_dir}/.virtualenvs')  # create an volume dir to save ~/.local/share/virtualenvs

    # TODO: use backup_dir to backup envs
    if check2create_dir(volume_backup_dir) is False:
        pass

    new_user_config = UserConfig(
        password, forward_port, image, extra_command, volume_work_dir, HostDI.volume_dataset_dir, volume_backup_dir
    )
    new_user_config.to_dict()

    users_config = UsersConfig(HostDI.users_config_yaml)

    if silent_update is None:  # interactive mode
        if user_id not in users_config.ids:  # new account
            users_config.ids[user_id] = new_user_config
            isWrite = dump_yaml(users_config.to_dict(), HostDI.users_config_yaml)

        elif users_config.ids[user_id] == new_user_config:
            print(str_format(f"{user_id}'s personal config is all the same~", fore='g'))
            isWrite = True

        elif ask_yn(f"Do you want to update {user_id}'s personal configuration?(it will update all the variable)", 'y'):
            users_config.ids[user_id] = new_user_config
            print(str_format("Done !!", fore='g'))
            isWrite = dump_yaml(users_config.to_dict(), HostDI.users_config_yaml)

    elif silent_update is True:
        users_config.ids[user_id] = new_user_config
        isWrite = dump_yaml(users_config.to_dict(), HostDI.users_config_yaml)

    # get user_config stage
    user_config = users_config.ids[user_id]
    user_dict = user_config.to_dict()
    if silent_user_default or isWrite:
        pass
    elif (
        silent_user_default is False
        or ask_yn(f"Use {user_id}'s default configuration?(if is not, it will combine new config)", 'y') is False
    ):
        user_dict = {
            **user_dict,
            **new_user_config.dict,
        }

    if silent_update == None and silent_user_default == None:
        print_user_info(user_id, user_dict)
    return user_dict


def run(
    user_id: str,
    password: str,
    forward_port: int,
    cpus: float = 2,
    memory: int = 8,
    gpus: int = 1,
    image: str = None,
    extra_command: str = '',
    volume_work_dir: str = HostDI.volume_work_dir,
    volume_dataset_dir: str = HostDI.volume_dataset_dir,
    volume_backup_dir: str = HostDI.volume_backup_dir,
    *args,
    **kwargs,
):
    '''
    `user_id`: student ID.\n
    `password`: password.\n
    `forward_port`: which forward port you want to connect to port: 2(SSH).\n
    `image`: which image you want to use, new std_id will use "rober5566a/aivc-server:latest"\n
    `extra_command`: the extra command you want to execute when the docker runs.\n
    `silent_update`: silent mode to update users_config.json, default is interactive mode. [None(default) | True | Fasle]\n
    `silent_user_default`: silent mode to use default user config, default is interactive mode. [None(default) | True | Fasle]
    '''

    exec_command = extra_command if extra_command is not None else ''

    if image is None:
        image = 'rober5566a/aivc-server:latest'

    if 'rober5566a/aivc-server' in image:
        exec_command += f' /bin/bash -c "/.script/ssh_start.sh {password}"'
        CapCig = CapabilityConfig(HostDI.capability_config_yaml)
        ram_size = memory * CapCig.max.shm_rate

        # TODO: add backup_dir
        # add '--pid=host' is not a good idea but nvidia-docker is still not solve this issue, https://github.com/NVIDIA/nvidia-docker/issues/1460
        os.system(
            f'docker run\
                -dit\
                --restart=always\
                --pid=host\
                --cpus={cpus}\
                --memory={ram_size}G\
                --memory-swap={memory}G\
                --shm-size={memory}G\
                --gpus={gpus}\
                --name={user_id}\
                -p{forward_port}:22\
                -v {volume_work_dir}:/root/Work\
                -v {volume_work_dir}/.pyenv-versions:/root/.pyenv/versions\
                -v {volume_work_dir}/.virtualenvs:/root/.local/share/virtualenvs\
                -v {volume_dataset_dir}:/root/Dataset:ro\
                -v /tmp/.X11-unix:/tmp/.X11-unix\
                -e DISPLAY=$DISPLAY\
                {image}\
                {exec_command}\
                '
        )


def run_container(
    user_id: str,
    password: str,
    forward_port: int,
    cpus: float = 2,
    memory: int = 8,
    gpus: int or str = 1,
    image: str = None,
    extra_command: str = '',
    silent_update: bool or None = None,
    silent_user_default: bool or None = None,
    *args,
    **kwargs,
):
    user_config_dict = operate_user_config(
        user_id,
        password,
        forward_port,
        image,
        extra_command,
        silent_update,
        silent_user_default,
        *args,
        **kwargs,
    )
    # print(user_config_dict)
    # exit()

    run(user_id=user_id, cpus=cpus, memory=memory, gpus=gpus, **user_config_dict)


@click.command(context_settings=dict(help_option_names=['-h', '--help'], max_content_width=120))
@click.option('-std-id', '--student-id', help=help_dict['std_id'], required=True)
@click.option('-pw', '--password', help=help_dict['pw'], required=True)
@click.option('-fp', '--forward-port', help=help_dict['fp'], required=True)
@click.option('-cpus', show_default=True, default=8, help=help_dict['cpus'])
@click.option('-mem', '--memory', show_default=True, default=32, help=help_dict['mem'])
@click.option('-gpus', show_default=True, default=1, help=help_dict['gpus'])
@click.option('-im', '--image', show_default=True, default=None, help=help_dict['im'])
@click.option('-e-cmd', '--extra-command', default=None, help=help_dict['e-cmd'])
@click.option('-s-update', '--silent-update', show_default=True, default=None, type=bool, help=help_dict['s-update'])
@click.option('-s-default', '--silent-user-default', show_default=True, default=None, type=bool, help=help_dict['s-default'])
def cli(
    user_id: str,
    password: str,
    forward_port: int,
    cpus: float = 2,
    memory: int = 8,
    gpus: int or str = 1,
    image: str = None,
    extra_command: str = '',
    silent_update: bool or None = None,
    silent_user_default: bool or None = None,
    *args,
    **kwargs,
):
    '''Repository: https://github.com/tw-yshuang/AIVC-Server

    EXAMPLES

    >>> python3 ./run_container.py -std-id m11007s05 -pw IamNo1handsome! -fp 2222  -s-update False -s-default True'''

    run_container(
        user_id,
        password,
        forward_port,
        cpus,
        memory,
        gpus,
        image,
        extra_command,
        silent_update,
        silent_user_default,
        *args,
        **kwargs,
    )


if __name__ == '__main__':
    cli()

    # # ? for test.
    # user_config_dict = operate_user_config(
    #     **{'user_id': 'm11007s05-1', 'password': '0000', 'forward_port': 2224},
    # )
    # run(user_id='m11007s05-1', cpus=2, memory=8, gpus=1, **user_config_dict)
