# Developer API Documentation

## Data Flow

This Data-Flow Chart shows that `HostInfo.py` control all the `*.yaml` & `*.csv` files, the others `*.py` need to use the APIs from `HostInfo.py` to read/write, and it also shows each `*.py` how related to `*.yaml` & `*.csv` files.
![Data-Flow](Data-Flow.drawio.svg)

## Service Flow

![Service-Flow](Service-Flow.drawio.svg)

---

---

## `jobs`

---

## **`*.csv`**

The structure of all the *.csv in the `jobs` directory, also can check it from [cfg/template/schedule.csv](../cfg/template/schedule.csv).

Example:

 | start    | end      | user_id | cpus | memory | gpus | forward_port | image | extra_command |
  | --- | --- | --- | --- | --- | --- | --- | --- | --- |
  | 2023-01-01 13:30:00.000000 | 2023-01-04 13:30:00.000000 | m11007s05 | 60 | 128 | "[0, 1, 2, 3, 4, 5, 6, 7]" | 10000 | null | null |

---
---

## **`src/booking`**

---

## `booking.py`

It is a CLI tool that communicates with users.

### import packages

```python
from pathlib import Path
from datetime import datetime
from typing import Tuple, Dict

import click

from Checker import Checker
from lib.WordOperator import str_format, ask_yn
from src.HostInfo import BookingTime, BasicCapability, UserConfig, ScheduleDF
```

### *`cli()`*

```python
def cli(user_id: str = None, use_options: bool = False, list_schedule: bool = False) -> (bool, Tuple[BookingTime, str, BasicCapability,  UserConfig]):
```

#### **Parameters**

- `user_id`: user's account.
- `use_options`: use extra options.
- `list_schedule`: list schedule that already booking.

#### **Return**

- `boolean`, `True` for booking successful, `False` for else.
- `Tuple`, booking information: (booking_time, user_id, cap_info, user_config).

This function interactive with the users.

```python
@click.command(context_settings=dict(help_option_names=['-h', '--help'], max_content_width=120))
@click.option('-id', '--user-id', help="user's account.")
@click.option('-use-opt', '--use-options', default=False, is_flag=True, help="use extra options.")
@click.option('-ls', '--list-schedule', default=False, is_flag=True, help="list schedule that already booking.")
def cli(user_id: str = None, use_options: bool = False, list_schedule: bool = False) -> bool:
    '''
    This function is the entrypoint that communicates with users.

    `user_id`: user's account.
    `use_options`: use extra options.
    `list_schedule`: list schedule that already booking.
    '''
    if list_schedule:
        ...
        return False, (...)

    ...

    if use_options:
        ...

    ...
    return True, (...)

```

If `list_schedule=True`, then sort the *`Checker.booked_df`* by `column:start` in increasing order, and send the message.

In order to Fool-proofing, it will ask user the following option:

```python
# Required
password: str
cap_info: BasicCapability
cap_info.cpus: float or str # number of cpus for container.
cap_info.memory: int or str # how much memory(ram, swap) GB for container.
cap_info.gpus: int or str # how many gpus for container.
booking_time: BookingTime
booking_time.start: datetime # start time for booking this schedule.
booking_time.end: datetime # end time for booking this schedule.

# Optional
if use_options is True:
    user_config: UserConfig
    user_config.forward_port: int  # which forward port you want to connect to port: 22(SSH).
    user_config.image: Path # which image you want to use, default is use "rober5566a/aivc-server:latest"
    user_config.extra_command: str # the extra command you want to execute when the docker runs.

    update_password: bool
    if update_password is True:
        new_password: str
        # ask twice
        user_config.password = new_password
        # after that only update the password in the user_config

    # ask user want to update the user_config?

```

#### Question List

#### 1. `password`

- <font color=#CE9178>"If you are a new user, the default password: 0000"</font>
- <font color=#CE9178>"Password: "</font>, the entry must be secret.
- If the user types the wrong password, show this: <font color=#CE9178>"Wrong password, please enter the password: "</font>, the user will have 2 times changes, over that send <font color=#CE9178>"ByeBye~~"</font>, end the program.

#### 2. `cap_info`

- <font color=#CE9178>"Your Maximum Capability Information: cpus=xx memory=xx gpus=xx"</font>, show this message first, the maximum cap_info can find it from *`Checker.cap_config.max_default_capability`* / *`Checker.cap_config.max_custom_capability`*.
- <font color=#CE9178>"Please enter the capability information 'cpus(float) memory(int) gpus(int)': "</font>.
- If over the maximum required, then send (red-font)<font color=#CE9178>"Over the maximum required."</font>, back to the [Q.2](#2-cap_info).
- If is lower than 1 than, then send (red-font)<font color=#CE9178>"The value can not lower than 1."</font>, back to the [Q.2](#2-cap_info).

#### 3. `booking_time`

- `start`, <font color=#CE9178>"Please enter the start time 'YYYY MM DD hh mm': "</font>

  - The start time must not in the past, and during 2 weeks.
  - If is wrong, send the message (red-font)<font color=#CE9178>"Wrong Input!"</font>, back to the [Q.3.start](#3-booking_time).
- `end`, <font color=#CE9178>"Please enter the end time 'YYYY MM DD hh mm': "</font>.
  - The maximum end time is 2 weeks from the start time.
  - If is wrong, send the message (red-font)<font color=#CE9178>"Wrong Input!"</font>, back to the [Q.3.end](#3-booking_time).
- If *`Checker.check_cap4time()`* return:

  - `True`, then send (green-font)<font color=#CE9178>"Booking successful!"</font>.
  - `False`, then send (red-font)<font color=#CE9178>"There is not enough computing power for the time you need, book again."</font>, back to the [Q.2](#2-cap_info).

- The user must follow the rules:

  - The user can type [*Time_Flags*](#time_flags) and datetime, the datetime format must be <font color=#CE9178>'YYYY MM DD hh mm'</font>.
  - <font color=#CE9178>'mm'</font> must be "00" or "30".

- #### Time_Flags

  | Flag                                  | Description                                                                                                                                                  |
  | ------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
  | <font color=#CE9178>now</font>        | `start` use, the booking information will be active immediately if the usage is available, and the "mm" will discard unconditionally record to the schedule. |
  | <font color=#CE9178>{num}-day</font>  | The range of the <font color=#CE9178>num</font> is `1~14`, 24 hrs for a unit, and the "mm" will discard unconditionally record to the schedule.                                                                     |
  | <font color=#CE9178>{num}-week</font> | The range of the <font color=#CE9178>num</font> is `1~2`, 7 days for a unit, and the "mm" will discard unconditionally record to the schedule.                                                                      |

#### 4. New User Config

- If user has config in the `users_config.yaml` then pass it.

- If user has no config in the `users_config.yaml`(`Checker.users_config` has no this `user_id` attribute) it will generate an `auto_config` for the user and send it and write it to the `users_config.yaml`.

  - `auto_config`, the problem in here is `forward_port`, assign a random forward_port, the range for the port is `10000~11000`, and use *`Checker.check_forward_port_empty()`* to check the forward port is not duplicated.

  - Write the user's config to the `users_config.yaml` the format is like:

    ```yaml
    {user_id}:
      password: "0000"
      forward_port: XXXXX
      image: null
      extra_command: null
      volume_work_dir: "{`Checker.deploy_info.volume_work_dir`}/{user_id}"
      volume_dataset_dir: "{`Checker.deploy_info.volume_dataset_dir`}/{user_id}"
      volume_backup_dir: "{`Checker.deploy_info.volume_backup_dir`}/{user_id}"
    ```
  
  - Sent the message:

    ```bash
    {user_id}:
      password: "0000"
      forward_port: XXXXX
      image: null
      extra_command: null
    ```

#### 5. Optional(use_options=True)

#### 5.1. `forward_port`

- <font color=#CE9178>"Please enter the forward port(default: xxxxx, none by default): "</font>, the default forward_port can find it from *`Checker.users_config.ids[user_id].forward_port`*.
- The forward port only can assign port: `10000~11000`, due to application service port. please check [List of TCP and UDP port numbers](https://en.wikipedia.org/wiki/List_of_TCP_and_UDP_port_numbers).
<!-- - The forward port can not duplicate assigned with other users. -->
- Use *`Checker.check_forward_port_empty()`* to check the forward port is not duplicated.
  - `False`, sent message (red-font)<font color=#CE9178>"Forward Port Duplicated!!"</font>, back to [Q.5.1.](#51-forward_port).

#### 5.2. `image`

- Using *`Checker.deploy_info.images`* to show the docker images first.
- <font color=#CE9178>"Please enter the image 'repository/tag'(default: xxx, none by default): "</font>, the default image can find it from *`Checker.users_config.ids[user_id].image`*, if is `None`, then show the image <font color=#CE9178>"rober5566a/aivc-server:latest"</font>.
- If the response is <font color=#CE9178>""</font>, then `Checker.users_config.ids[user_id].image = None`.
- Using *`Checker.check_image_isexists()`* to check image is exists.

#### 5.3. `extra_command`

- <font color=#CE9178>"Please enter the extra command when running the image. (default: None, none by default): "</font>, no need to check.
- Note: if the image repository is <font color=#CE9178>"rober5566a/aivc-server"</font> actually it has an extra command: `/.script/ssh_start.sh {password}`, see [monitor/run_container.py](#run_containerpy).

#### 5.4. Update Password

- <font color=#CE9178>"Do you want to update the password?"</font>, using `ask_yn()` to ask, return:
  - `False`, pass it.
  - `True`, <font color=#CE9178>"Please enter the new password: "</font>, after entering, <font color=#CE9178>"Please enter the new password again: "</font>, both new_password must be same.
    - If there are not the same, (red-font)<font color=#CE9178>"Incorrect!!"</font>, back to [Q.5.4.](#54-update-password)
    - Only update the password in `users_config.yaml`, (green-font)<font color=#CE9178>"Update default Password!"</font>

#### 5.5. Update `users_config.yaml`

- <font color=#CE9178>"The previous setting is for the once, do you want to update the default config?"</font>, using `ask_yn()` to ask, return:
  - `False`, pass it.
  - `True`, update the user's config for the `users_config.yaml`.

### *`booking()`*

```python
def booking(user_id:str, cap_info: BasicCapability, booking_time: BookingTime, user_config: UserConfig) -> bool:
```

#### **Parameters**

- `user_id`: user's account.
- `cap_info`: cpus, memory, gpus.
- `booking_time`: checked available times.
- `user_config`: the config for this user_id.

#### **Return**

- `boolean`

After in `cli()` confirm all the parameter, it is time to booking the schedule to the `booking.csv`.

```python
def booking(user_id:str, cap_info: BasicCapability, booking_time: BookingTime, user_config: UserConfig, booking_csv: Path) -> bool:
    '''
    Write the booking_info to the booking schedule.

    `user_id`: user's account.
    `cap_info`: cpus, memory, gpus.
    `booking_time`: checked available times.
    `user_config`: the config for this user_id.
    '''
    ...
```

#### GPU Assign

- Using *`Checker.get_best_gpu_ids()`* to get the gpu device id list.

#### Update booking.csv

- Using *`Schedule_DF.update_csv()`* to update it.
- If the `booking_time.start` is at the now-time unit, then write <font color=#CE9178>"now"</font> to the `jobs/monitor_exec`.

---

## `Checker.py`

Check information from `cfg/` & `jobs/`.

### import packages

```python
from pathlib import Path
from datetime import datetime
from typing import Tuple, Dict

import pandas as pd

from lib.WordOperator import str_format, ask_yn
from src.HostInfo import HostInfo, BookingTime, BasicCapability, UserConfig, ScheduleDF
```

### *`Checker`*

```python
class Checker(HostInfo):
```

#### **Attributes**

- `deploy_info`: the deploy information that from yaml file.
- `cap_config`: the capability config that from yaml file.
- `users_config`: the users config that from yaml file.
- `booking`: the booking schedule frame that from csv file.
- `using`: the using data schedule frame that from csv file.
- `used`: the used data schedule frame that from csv file.
- `booked_df`: all the schedule that already booking & using.

```python
class Checker(HostInfo):
    '''
    `deploy_info`: the deploy information that from yaml file.
    `cap_config`: the capability config that from yaml file.
    `users_config`: the users config that from yaml file.
    `booking`: the booking schedule frame that from csv file.
    `using`: the using data schedule frame that from csv file.
    `used`: the used data schedule frame that from csv file.
    '''
    # deploy_info: HostInfo.deploy_info
    # cap_config: HostInfo.cap_config
    # users_config: HostInfo.users_config

    # booking: HostInfo.booking
    # using: HostInfo.using
    # used: HostInfo.used

    booked_df: pd.DataFrame
```

### *`Checker.__init__()`*

```python
def __init__(
    self,
    deploy_yaml: Path = Path('cfg/host_deploy.yaml'),
    booking_csv: Path = Path('jobs/booking.csv'),
    using_csv: Path = Path('jobs/using.csv'),
    used_csv: Path = Path('jobs/used.csv'),
) -> None:
    super(Checker, self).__init__(deploy_yaml, booking_csv, using_csv, used_csv)

    self.booked_df = ScheduleDF.concat(self.booking.df, self.using.df)

```

#### **Parameters**

- `deploy_yaml` : the yaml file for host deploy.
- `booking_csv`: the csv file for already booking.
- `using_csv`: the csv file for already using.
- `used_csv`: the csv file for already used.

#### **Return**

- `None`

### *`Checker.check_user_id()`*

```python
def check_user_id(self, user_id:str) -> bool:
```

Check user_id that has in the *`self.cap_config.allow_userIDs`*.

#### **Parameters**

- `user_id` : user's account.

#### **Return**

- `boolean`

### *`Checker.check_forward_port_empty()`*

```python
def check_forward_port_empty(self, forward_port: int) -> bool:
```

Check forward_port that is not exists in *`self.users_config[*].forward_port`*.

#### **Parameters**

- `forward_port` : the forward port that wants to assign.

#### **Return**

- `boolean`

### *`Checker.check_forward_port4time()`*

```python
def check_forward_port4time(self, forward_port: int, booking_time: BookingTime) -> bool:
```

Check forward_port duplicate problem during the time that user booking.

#### **Parameters**

- `forward_port` : the user requires cpus, memory, gpus.
- `booking_time`: the user requires start time & end time.

#### **Return**

- `boolean`

### *`Checker.check_image_isexists()`*

```python
def check_image_isexists(self, image: str) -> bool:
```

Check image that is exists from the *`self.deploy_info.images`*.

#### **Parameters**

- `image` : the image that wants to assign.

#### **Return**

- `boolean`

### *`Checker.get_user_max_cap()`*

```python
def get_user_max_cap(self, user_id: str) -> bool:
```

Search cap_info for user_id from the *`self.cap_config.max_default_capability`* / *`self.cap_config.max_custom_capability`*.

#### **Parameters**

- `user_id` : user's account.

#### **Return**

- `BasicCapability`

### *`Checker.check_cap4time()`*

```python
def check_cap4time(self, cap_info: BasicCapability, booking_time: BookingTime) -> bool:
```

Check whether *`self.booked_df`* has satisfied cap_info during booking_time.

#### **Parameters**

- `cap_info` : the user requires cpus, memory, gpus.
- `booking_time`: the user requires start time & end time.

#### **Return**

- `boolean`

### *`Checker.get_best_gpu_ids()`*

```python
def get_best_gpu_ids(self, gpus: int, booking_time: BookingTime) -> List[int]:
```

Search the fewer usages gpu_ids from *`self.booked_df`* in the `booking_time`.

#### **Parameters**

- `gpus` : number of gpus required.
- `booking_time`: the user requires start time & end time.

#### **Return**

- `List[int]`: the available gpu devices id list.

---
---

## **`src/monitor`**

---

## *`Monitor.py`*

---

### import packages

```python
import os, warnings
from pathlib import Path
from datetime import dactetime
from typing import Tuple, Dict, NamedTuple

from lib.WordOperator import str_format
from run_container import run_container
from src.HostInfo import  HostInfo, BookingTime, BasicCapability, UserConfig, ScheduleDF, ScheduleColumnNames
```

### *`SpaceWarning`*

```python
class SpaceWarning(Warning):
    pass
```

The user over-use the space.

### *`GPUDuplicateWarning`*

```python
class GPUDuplicateWarning(Warning):
    pass
```

The GPU is being utilized by multiple users simultaneously.

** Only design this warning, not complete!!
<!-- TODO -->

### *`MonitorMessage`*

** The better way is using `logging` module, but I don't know how to use it, it is welcome to change the API if result won't be change.

```python
class MonitorMessage():
```

Control the message for `Monitor`, and record it to the `self.log_path`.

#### **Attributes**

- `ERROR`: the `[ERROR]` flag.
- `WARNING`: the `[WARNING]` flag.
- `INFO`: the `[INFO]` flag.
- `log_path`: the path for record the `Monitor` action for host maintainer & MLOps to check.

```python
class MonitorMessage():
    '''
    Control the `Monitor` message
    '''
    ERROR: str = '[ERROR]'
    WARNING: str = '[WARNING]'
    INFO: str = '[INFO]'
```

### *`MonitorMessage.__init__()`*

```python
def __init__(self, path: Path = Path('jobs/monitor.log')) -> None:
    self.log_path = path 
```

#### **Parameters**

- `path`: the path for record the `Monitor` action for host maintainer & MLOps to check.

#### **Return**

- `None`

### *`MonitorMessage.update_log()`*

```python
def update_log(self, status: str, msg:str, sign:str=None) -> bool
```

Add message to the `self.log_path`

```python
def update_log(self.log_path, status: str, msg:str, sign:str=None) -> bool
    with open(self.log_path, 'a') as f:
      ...
```

format:

```log
yyyymmdd HH:MM [STATUS] SIGN, message.
```

e.g.

```log
20230101 13:30 [WARNING] SpaceWarning, m11007s05 is over-use the work_dir 10GB, and backup_dir 2GB.

20230101 13:30 [INFO] m11007s05 is successfully run the container. 
```

note: [INFO] has no SIGN.

### *`MonitorMessage.warning()`*

```python
def warning(self, sign: Warning, msg:str) -> None
```

Warning message use this function to send it.

```python
def warning(self, sign: Warning, msg:str) -> None
    send_msg:str
    ...
    str_format(send_msg, fore='y')
    self.update_log(self.WARNING, msg, sign=sign.__name__)
    ...
```

e.g.
"<font color=#FFFF00>20230101 13:30 [WARNING] SpaceWarning, m11007s05 is over-use the work_dir 10GB, and backup_dir 2GB.</font>"

### *`MonitorMessage.info()`*

```python
def info(self, msg:str) -> None
```

Warning message use this function to send it.

```python
def info(self, msg:str) -> None
    send_msg:str
    ...
    print(sen_msg)
    self.update_log(self.INFO, msg)
    ...
```

e.g.
"<font color=#CE9178>20230101 13:30 [INFO] m11007s05 is successfully run the container.</font>"

### *`Monitor`*

```python
class Monitor(HostInfo):
```

#### **Attributes**

- `deploy_info`: the deploy information that from yaml file.
- `cap_config`: the capability config that from yaml file.
- `users_config`: the users config that from yaml file.
- `booking`: the booking schedule frame that from csv file.
- `using`: the using data schedule frame that from csv file.
- `used`: the used data schedule frame that from csv file.
- `msg`: control the message and record it to the log file.

```python
class Monitor(HostInfo):
    '''
    `deploy_info`: the deploy information that from yaml file.
    `cap_config`: the capability config that from yaml file.
    `users_config`: the users config that from yaml file.
    `booking`: the booking schedule frame that from csv file.
    `using`: the using data schedule frame that from csv file.
    `used`: the used data schedule frame that from csv file.
    `msg`: control the message and record it to the log file.
    '''
    # deploy_info: HostInfo.deploy_info
    # cap_config: HostInfo.cap_config
    # users_config: HostInfo.users_config

    # booking: HostInfo.booking
    # using: HostInfo.using
    # used: HostInfo.used

    msg: MonitorMessage
```

### *`Monitor.__init__()`*

```python
def __init__(
    self,
    deploy_yaml: Path = Path('cfg/host_deploy.yaml'),
    booking_csv: Path = Path('jobs/booking.csv'),
    using_csv: Path = Path('jobs/using.csv'),
    used_csv: Path = Path('jobs/used.csv'),
    log_path: Path = Path('jobs/monitor.log'),
) -> None:
    super(Monitor, self).__init__(deploy_yaml, booking_csv, using_csv, used_csv)
    
    self.msg = MonitorMessage(log_path)

    self.exec()
```

### *`Monitor.update_tasks()`*

```python
def update_tasks(self) -> List[str], pd.DataFrame:
```

Detect all the tasks status, this function will do 4 things:

1. Find containers that are due on the *`self.using`* from `column:end`.
2. Find tasks that are time up on the *`self.booking`* from the `column:start`.
3. Move the information that time up on each data frame, `self.using` → `self.booking` → `self.used`.
4. Update csv, using *`self.booking.update_csv()`* & *`self.using.update_csv()`* & *`self.used.update_csv()`*.

#### **Parameters**

- `None`

#### **Return**

- `List[str]`: close_ls, the containers name(user_id) that need to stop & remove.
- `pd.DataFrame`: task_df, the `pd.DataFrame` saves the tasks that need to be enabled.

### *`Monitor.check_space()`*

```python
def check_space(self, user_id: str) -> bool:
```

Check the user_ids that are over-using the backup_space & work_space, use *`self.cap_config.max_default_capability`*/*`self.cap_config.max_custom_capability`* to find the `backup_space` & `work_space`, the unit is GB.
If space is over-using, use `self.msg.warning()` & `SpaceWarning` to send the message.

#### **Parameters**

- `user_id`, the user_id that need to be check.

#### **Return**

- `bool`: user_id is pass or not.
  - `True`, pass it.
  - `False`, fail it.

### *`Monitor.close_containers()`*

```python
def close_containers(self, user_ids:List[str]) -> List[bool or Error]:
```

Stop and remove containers, use (shell)`docker container stop {user_id} && docker container remove {user_id}`, and send message by using `self.msg.info()`.

#### **Parameters**

- `user_ids`, list of the user_id that need to be stop & remove.

#### **Return**

- `List[bool or Error]`: list of correspond user_id is pass or not.
  - `True`, pass it.
  - `False`, fail it.

```python
def close_containers(self, user_ids:List[str]) -> List[bool or Error]:
    result_ls:  List[bool or Error]
    ...
    for user_id in users_ids:
      try:
          ...
          self.msg.info(...)
          result_ls.append(True)

      except ...:
          ...
          result_ls.append(Error)
    ...
    return result_ls
```

### *`Monitor.run_containers()`*

```python
def run_containers(self, run_df: pd.DataFrame) -> List[bool or Error]:
```

Run containers, using `run_container()`. Send message by using `self.msg.info()`

#### **Parameters**

- `run_df`, the `pd.DataFrame` saves the information that needs to be run.

#### **Return**

- `List[bool]`: list of correspond user_id is pass or not.
  - `True`, pass it.
  - `False`, fail it.

```python
def run_containers(self, run_df: pd.DataFrame) -> List[bool or Error]:
    result_ls:  List[bool or Error]
    ...
    task: NamedTuple
    for task in run_df.itertuples(index=False, name=None):
      ...
      result = run_container(..., **task._asdict())
      self.msg.info(...)
      ...
    ...
    return result_ls
```

### *`Monitor.exec()`*

```python
def exec(self) -> None:
```

Execute the monitoring, use methods that are in the `self`, this method will execute the following processes:

1. Get the close_ls & task_df from *`self.update_tasks()`*.
2. Use *`self.close_containers()`* to close containers form close_ls.
3. Use *`self.check_space()`* from close_ls & task_df. The run_df is from task_df that is passed *`self.check_space()`*.
4. Use *`self.run_containers()`* from task_df.

#### **Parameters**

- `None`

#### **Return**

- `None`

```python
def exec(self) -> None:
    close_ls: List[str]
    check_ls: List[bool]
    task_df: pd.DataFrame
    run_df: pd.DataFrame

    close_ls, task_df = self.update_tasks()
    self.close_containers(close_ls)

    ...
    check_ls = [self.check_space() for user_id in task_df[ScheduleColumnNames.user_id]]
    
    run_df = ... # use check_ls to select it.

    self.run_containers(run_df)
    ...
```

---

## *`run_container.py`*

### *`BackupInfo()`*

```python
class BackupInfo:
```

This is for the [backup.yaml](../cfg/templates/Backup/backup.yaml) used, for convert the format to the `BackupInfo` object.

#### **Attributes**

- `Dir`: The backup information for the directories.
- `File`: The backup information for the files.

```python
class BackupInfo:
    '''
    `Dir`: The backup information for the directories.
    `File`: The backup information for the files.
    '''
    Dir: List[List[str]]
    File: List[List[str]]
```

### *`BackupInfo.__init__()`*

```python
def __init__(self, yaml='cfg/templates/backup.yaml') -> None:
    for k, v in load_yaml(yaml).items():
        setattr(self, k, v)
```

#### **Parameters**

- `yaml`, The file path for the user's `backup.yaml`.

#### **Return**

- `None`

### *`prepare_deploy()`*

```python
def prepare_deploy(user_config: UserConfig, cap_max: MaxCapability, memory: int, image: str, extra_command: str) -> Tuple[str, str, int, List[List[str]]]
```

Setting & generate the related dirs/files and information; prepared for the `run()`.

#### **Parameters**

- `user_config`: The `UserConfig` object, it contains the user default setting.
- `cap_max`: The `MaxCapability` object, it contains the maximum capability setting for this computing device.
- `memory`: The memory size you want to used for this time, unit: GB.
- `image`: The image/tag name for the docker image.
- `extra_command`: The extra command that user want to execute  for this time.

#### **Return**

- `str`: the image/tag name for running container.
- `str`: the command for running container.
- `int`: the DRAM size assign for the container.
- `List[List[str]]]`: the volumes information for running container, format: `[[host_path, container_path]...]`.

### *`run()`*

```python
def run(
    user_id: str,
    forward_port: int,
    cpus: float,
    memory: int,
    gpus: List[int] or str,
    image: str or None,
    exec_command: str or None,
    ram_size: int,
    volumes_ls: List[List[str]]
) -> None:
```

#### **Parameters**

- `user_id`: user ID.
- `forward_port`: which forward port you want to connect to port: 2(SSH).
- `cpus`: Number of CPU utilities.
- `memory`: The memory size you want to used for this time, unit: GB.
- `gpus`: List of gpu id used for the container.
- `image`: Which image you want to use, new std_id will use "rober5566a/aivc-
- `exec_command`: The exec command you want to execute when the docker runs.
- `ram_size`: The DRAM size that you want to assign to this container,
- `volumes_ls`: List of volume information, format: [[host, container, ]...]

#### **Return**

- `None`

```python
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
) -> None:
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
    ...
```

### *`run_container()`*

```python
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
```

#### **Parameters**

- `user_id`: user ID.
- `forward_port`: which forward port you want to connect to port: 2(SSH).
- `cpus`: Number of CPU utilities.
- `memory`: The memory size you want to used for this time, unit: GB.
- `gpus`: List of gpu id used for the container.
- `image`: The image/tag name for the docker image.
- `extra_command`: The extra command that user want to execute  for this time.
- `user_config`: The `UserConfig` object, it contains the user default setting.
- `cap_max`: The `MaxCapability` object, it contains the maximum capability setting for this computing device.

#### **Return**

- `None`

### *`cli()`*

```python
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
) -> None:
```

The CLI tool for host maintainer used, under the `MaxCapability`, unlimited user capability.

#### **Parameters**

- `user_id`: user ID.
- `forward_port`: which forward port you want to connect to port: 2(SSH).
- `cpus`: Number of CPU utilities.
- `memory`: The memory size you want to used for this time, unit: GB.
- `gpus`: List of gpu id used for the container.
- `image`: The image/tag name for the docker image.
- `extra_command`: The extra command that user want to execute for this time.
- `user_config`: The `UserConfig` object, it contains the user default setting.
- `cap_max`: The `MaxCapability` object, it contains the maximum capability setting for this computing device.

#### **Return**

- `None`

```python
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
) -> None:
    '''Repository: https://github.com/tw-yshuang/AIVC-Server-Booking

    EXAMPLES

    >>> python3 ./run_container.py --user-id tw-yshuang -pw IamNo1handsome! -fp 10000'''
    ...
```
