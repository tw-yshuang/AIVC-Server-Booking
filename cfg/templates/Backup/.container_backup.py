import os, shutil
from typing import List

import yaml

BACKUP_DIR = '/root/Backup'


def load_yaml(filename: str) -> dict:
    with open(filename, 'r') as f:
        return yaml.load(f, Loader=yaml.SafeLoader)


class BackupInfo:
    Dir: List[List[str]] = [[]]
    File: List[List[str]] = [[]]

    def __init__(self, yaml=f'{BACKUP_DIR}/backup.yaml') -> None:
        for k, v in load_yaml(yaml).items():
            setattr(self, k, v)


def check2create_dir(dir: str):
    try:
        if not os.path.exists(dir):
            os.mkdir(dir)
            print(f"Successfully created the directory: {dir} !")
            return False
        else:
            return True
    except OSError:
        raise OSError(f"Fail to create the directory {dir} !")


def main():
    backup_info = BackupInfo()

    for backup_dir, target_dir in backup_info.Dir:
        backup_dir = str(backup_dir)
        target_dir = str(target_dir)
        if os.path.exists(target_dir) is False:
            continue

        backup_dir = f'{BACKUP_DIR}/{backup_dir}'
        if os.path.exists(backup_dir) is False:
            # symlinks=True is must, because it needs to copy the exact same container's file, even the file that is a symbolic link.
            shutil.copytree(target_dir, backup_dir, symlinks=True)

    for backup_path, target_path in backup_info.File:
        backup_path = str(backup_path)
        target_path = str(target_path)
        if os.path.exists(target_path) is False:
            continue

        bk_dir_ls = backup_path.split('/')
        if len(bk_dir_ls) > 1:
            bk_dir_ls = bk_dir_ls[:-1]
            bk_dir = BACKUP_DIR

            # recursive to check2create_dir from the first bk_dir_ls
            for bk_sub_dir in bk_dir_ls:
                bk_dir = f'{bk_dir}/{bk_sub_dir}'
                check2create_dir(bk_dir)

        backup_path = f'{BACKUP_DIR}/{backup_path}'
        if os.path.exists(backup_path) is False:
            # follow_symlinks=False is must, because it needs to copy the exact same container's file, even the file that is a symbolic link.
            shutil.copy2(target_path, backup_path, follow_symlinks=False)


if __name__ == '__main__':
    main()
