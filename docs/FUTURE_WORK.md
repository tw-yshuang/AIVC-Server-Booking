# Future Work

---

## `booking.csv`, `using.csv`, `used.csv`

Convert it to the database(suggest use `sqlite`), more efficient, more easy to manipulate.

Another reason is that `pandas` is a slow tool.

---

## Password exposure issue

Password needs to encode!!!

1. Save password with a encode method, e.g. `base64`.
2. Create a class `PasswordCoder` in the `HostInfo.py` to decode it.

    ```python
    import os
    import random
    import string

    class PasswordCoder:
        ...
        def __init__(self):
            self.__env_var = 'PWD_' + ''.join(string.ascii_letters(letters, 5))

        def set_os_env(self, user_password: str):
            pwd = ... # decode method
            os.environ[self.__env_var] = pwd
        
        def delete_os_env(self):
            del os.environ[self.__env_var]
            ...

        def __repr__(self):
            ... # maybe set a method that access serval time it will reset the self.__env_var ??
            return self.__env_var
    ```

3. When running the container, immediately execute `PasswordCoder.delete_os_env()`

---

## `src/booking/booking.py`

1. Add new CLI feature
    - **remove task**: `-rm`, `--remove-task`, for remove the schedule task, must have `--user-id` in the command.

---

## `src/monitor/Monitor.py`

1. Watchdog to monitor jobs/monitor_exec

2. Balance the GPUs Usage Rate
   - After reboot system, re-schedule the gpus assign, change the order of assign mechanician.

3. Avoid Assign Duplicate GPUs
    - Scheduling algorithm to re-schedule the gpus assign to get the better assign method.

---

## Idle Container

> Create an idle container, letting users that are not running the booking container can access the server to move the files.
>
### `Idle.Dockerfile`

Base on `Dokcerfile`.

- user name: idle
- shell setup
- welcome message
- install python env tool & some dotfile

### `src/monitor/run_container.py`

#### `run_idle_container()`

- cpus: 0.5
- volume like `run_container()`
