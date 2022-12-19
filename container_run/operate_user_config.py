import sys
import json

from WordOperator import str_format, ask_yn


def get_stdID_config(opts: dict) -> dict:
    (
        password,
        forward_port,
        image,
        execute_command,
        __volume_work_dir,
        __volume_dataset_dir,
    ) = opts

    return {
        'password': password,
        'forward_port': forward_port,
        'image': image,
        'execute_command': execute_command,
        '__volume_work_dir': __volume_work_dir,
        '__volume_dataset_dir': __volume_dataset_dir,
    }


def write_user_config(__user_config_json: str, users_dict: dict):
    with open(__user_config_json, 'w') as f:
        json.dump(users_dict, f, indent=4)

    return True


def print_user_info(std_id: str, user_dict: dict):
    print(
        # regularize format
        f"'{std_id}': {user_dict}\n".replace("'", '"')
        .replace('{', '{\n        ')
        .replace(', ', ',\n        ')
        .replace('}', '\n}')
    )

    user_know_dict = user_dict.copy()
    del user_know_dict['__volume_work_dir']
    del user_know_dict['__volume_dataset_dir']
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


def write_tmpFile(tmpFile: str, user_dict: dict):
    with open(tmpFile, 'w') as f:
        f.write(f"{list(user_dict.values())}".replace('[', '').replace(']', '').replace(',', '').replace("'", ''))


def main():
    '''
    >>> # The order of input args is must

    input args:

    >>> std_id: str, (required)
    >>> password: str, (required)
    >>> forward_port: int, (required)
    >>> image: str, (required) # The image that already builded.
    >>> execute_command: str, (required) # Extra command want to put it, follow `bash` order.
    >>> __volume_work_dir: str, (required)
    >>> __volume_dataset_dir: str, (required)
    >>> silentUpdate: bool, (optional) # Use silent mode, interactive-update will follow this arg.
    >>> silentUseDefault: bool, (optional) # Use silent mode, interactive-useDefault will follow this arg.
    >>> tmpFile: str, (optional) # save pure return values to this file.
    '''

    tmpFile = sys.argv.pop() if len(sys.argv) == 12 else None  # optional
    silentUseDefault = eval(sys.argv.pop()) if len(sys.argv) == 11 else None  # optional
    silentUpdate = eval(sys.argv.pop()) if len(sys.argv) == 10 else None  # optional

    __user_config_json = sys.argv.pop()
    std_id = sys.argv[1]
    opts = sys.argv[2:]

    isWrite = False
    DEFAULT_IMAGE = "rober5566a/aivc-server:latest"
    opts[2] = DEFAULT_IMAGE if opts[2] == 'None' else opts[2]  # image arg

    # load user config
    with open(__user_config_json, 'r') as f:
        users_dict = json.load(f)

    # update user_config stage
    if silentUpdate is None:  # interactive mode
        if std_id not in users_dict:  # new account
            users_dict[std_id] = get_stdID_config(opts)
            isWrite = write_user_config(__user_config_json, users_dict)

        elif list(users_dict[std_id].values()) == opts:
            print(str_format(f"{std_id}'s personal config is all the same~", fore='g'))
            isWrite = True

        elif ask_yn(f"Do you want to update {std_id}'s personal configuration?(it will update all the variable)", 'y'):
            users_dict[std_id] = get_stdID_config(opts)
            print(str_format("Done !!", fore='g'))
            isWrite = write_user_config(__user_config_json, users_dict)

    elif silentUpdate is True:
        users_dict[std_id] = get_stdID_config(opts)
        isWrite = write_user_config(__user_config_json, users_dict)

    # get user_dict stage
    user_dict = users_dict[std_id]
    if silentUseDefault or isWrite:
        pass
    elif silentUseDefault is False or ask_yn(f"Use {std_id}'s default configuration?(if is not, it will combine new config)", 'y'):
        user_dict = {
            **user_dict,
            **get_stdID_config(opts),
        }

    # write user_dict to the tmpFile
    if tmpFile:
        with open(tmpFile, 'w') as f:
            f.write(f"{list(user_dict.values())}".replace('[', '').replace(']', '').replace(',', '').replace("'", ''))

    print_user_info(std_id, user_dict)
    return list(user_dict.values())


main()
