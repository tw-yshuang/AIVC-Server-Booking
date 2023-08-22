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


def get_dir_size_unix(path: str = '.', timeout: float = 300.0):  # faster way
    '''
        The function `get_dir_size_unix` calculates the size of a directory in kilobytes using the `du`
    command in Unix.

    Args:
        `path` (str): A string that represents the directory path for which you want to calculate the size. You
        can provide a different directory path if you want to calculate the size of a specific directory. Defaults to `'.'`

        `timeout` (float): The maximum amount of time (in seconds) that the function will wait for the
        `du` command to complete. If the command takes longer than the specified timeout, the function
        will return `0`. Default to `300.0` sec

    Returns:
        the size of the directory specified by the `path` parameter in kilobytes.
    '''

    try:
        return int(
            subprocess.run(
                ['du', '-sk', path], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, encoding='utf-8', timeout=timeout
            ).stdout.split()[0]
        )
    except subprocess.TimeoutExpired:
        return 0


get_dir_size = get_dir_size_py  # general used but slow than get_dir_size_unix
