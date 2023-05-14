'''
    This code edit by YU-SHUN,
    Welcome to contact me if you have any questions.
    e-mail: tw.yshuang@gmail.com
    Github: https://github.com/tw-yshuang
'''

import os
import subprocess


def get_dir_size_py(path: str = '.'):  # slow way
    '''
    The function calculates the total size of a directory in kilobytes by iterating through all files
    and directories within it.

    Args:
        `path` (str): The path to the directory for which we want to get the size. By default, it is set to
    the current directory ('.').

    Returns:
        the size of the directory in kilobytes as an integer.
    '''
    total_size = 0.0

    for root, dirs, files in os.walk(path, onerror=StopIteration):
        if len(files) == 0:
            continue

        for file in files:
            fp = os.path.join(root, file)
            # skip if it is symbolic link
            if os.path.islink(fp):
                total_size += os.lstat(fp).st_size
            else:
                total_size += os.path.getsize(fp)
    return total_size // 1024  # kilobytes as an integer


def get_dir_size_unix(path: str = '.'):  # faster way
    '''
    This function returns the size of a directory in kilobytes using the Unix command "du".

    Args:
        `path` (str): The path to the directory for which we want to get the size. By default, it is set to
    the current directory ('.').

    Returns:
        the size of the directory in kilobytes as an integer.
    '''
    return int(subprocess.run(['du', '-sk', path], stdout=subprocess.PIPE).stdout.split()[0].decode('utf-8'))


get_dir_size = get_dir_size_py  # general used but slow than get_dir_size_unix
