# Developer API Documentation

## Data Flow

This Data-Flow Chart shows that `HostInfo.py` control all the `*.yaml` & `*.csv` files, the others `*.py` need to use the APIs from `HostInfo.py` to read/write, and it also shows each `*.py` how related to `*.yaml` & `*.csv` files.
![Data-Flow](Data-Flow.drawio.svg)

## Service Flow

![Service-Flow](Service-Flow.drawio.svg)

---
---

# `src/booking`

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
def cli(student_id: str = None, use_options: bool = False, list_schedule: bool = False) -> bool:
```

#### **Parameters**

- `student_id`: user's account.
- `use_options`: use extra options.
- `list_schedule`: list schedule that already booking.

#### **Return**

- `boolean`

This function interactive with the users.

```python
@click.command(context_settings=dict(help_option_names=['-h', '--help'], max_content_width=120))
@click.option('-std-id', '--student-id', help="user's account.")
@click.option('-use-opt', '--use-options', default=False, help="use extra options.")
@click.option('-ls', '--list-schedule', default=False, help="list schedule that already booking.")
def cli(student_id: str = None, use_options: bool = False, list_schedule: bool = False) -> bool:
    '''
    This function is the entrypoint that communicates with users.

    `student_id`: user's account.
    `use_options`: use extra options.
    `list_schedule`: list schedule that already booking.
    '''
    if list_schedule:
        ...
        return True

    ...

    if use_options:
        ...
        return True

    ...
    return True

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

- <font color=#CE9178>"Please enter the password: "</font>, the entry must be secret.
- If the user types the wrong password, show this: <font color=#CE9178>"Wrong password, please enter the password: "</font>, the user will have 2 times changes, over that send <font color=#CE9178>"ByeBye~~"</font>, end the program.

#### 2. `cap_info`

- <font color=#CE9178>"Your Maximum Capability Information: cpus=xx memory=xx gpus=xx"</font>, show this message first, the maximum cap_info can find it from *`Checker.cap_config.max_default_capability`* / *`Checker.cap_config.max_custom_capability`*.
- <font color=#CE9178>"Please enter the capability information 'cpus(float) memory(int) gpus(int)': "</font>.
- If over the maximum required, then send (red-font)<font color=#CE9178>"Over the maximum required."</font>, back to the [Q.2](#2-cap_info).

#### 3. `booking_time`

- `start`, <font color=#CE9178>"Please enter the start time 'YYYY MM DD hh mm': "</font>

  - The start time must not in the past, and during 2 weeks.
  - If is wrong, send the message (red-font)<font color=#CE9178>"Wrong Input!"</font>, back to the [Q.3.start](#3-booking_time).
- `end`, <font color=#CE9178>"Please enter the end time 'YYYY MM DD hh mm': "</font>.
  - The maximum end time is 2 weeks from the start time.
  - If is wrong, send the message (red-font)<font color=#CE9178>"Wrong Input!"</font>, back to the [Q.3.end](#3-booking_time).
- If *`Checker.check_booking_info()`* return:

  - `True`, then send (green-font)<font color=#CE9178>"Booking successful!"</font>.
  - `False`, then send (red-font)<font color=#CE9178>"There is not enough computing power for the time you need, book again."</font>, back to the [Q.2](#2-cap_info).

- The user must follow the rules:

  - The user can type [*Time_Flags*](#time_flags) and datetime, the datetime format must be <font color=#CE9178>'YYYY MM DD hh mm'</font>.
  - <font color=#CE9178>'mm'</font> must be "00" or "30".

- #### Time_Flags

  | Flag                                  | Description                                                                                                                                                  |
  | ------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
  | <font color=#CE9178>now</font>        | `start` use, the booking information will be active immediately if the usage is available, and the "mm" will discard unconditionally record to the schedule. |
  | <font color=#CE9178>{num}-day</font>  | `end` use, the range of the <font color=#CE9178>num</font> is `1~14`, 24 hrs for a unit.                                                                     |
  | <font color=#CE9178>{num}-week</font> | `end` use, the range of the <font color=#CE9178>num</font> is `1~2`, 7 days for a unit.                                                                      |

#### 4. Optional(use_options=True)

#### 4.1. `forward_port`

- <font color=#CE9178>"Please enter the forward port(default: xxxxx, none by default): "</font>, the default forward_port can find it from *`Checker.users_config.ids[student_id].forward_port`*.
- The forward port only can assign port: `10000~11000`, consideration for application service port. please check [List of TCP and UDP port numbers](https://en.wikipedia.org/wiki/List_of_TCP_and_UDP_port_numbers).
- The forward port can not duplicate assigned with other users.

#### 4.2. `image`

- Using *`Checker.deploy_info.images`* to show the docker images first.
- <font color=#CE9178>"Please enter the image 'repository/tag'(default: xxx, none by default): "</font>, the default image can find it from *`Checker.users_config.ids[student_id].image`*, if is `None`, then show the image <font color=#CE9178>"rober5566a/aivc-server:latest"</font>.
- If the response is <font color=#CE9178>""</font>, then `Checker.users_config.ids[student_id].image = None`.

#### 4.3. `extra_command`

- <font color=#CE9178>"Please enter the extra command when running the image. (default: None, none by default): "</font>, no need to check.
- Note: if the image repository is <font color=#CE9178>"rober5566a/aivc-server"</font> actually it has an extra command: `/bin/bash -c "/.script/ssh_start.sh {password}"`, see [monitor.run_container](TODO).<!-- TODO -->

#### 4.4. Update Password

- <font color=#CE9178>"Do you want to update the password?"</font>, using `ask_yn()` to ask, return:
  - `False`, pass it.
  - `True`, <font color=#CE9178>"Please enter the new password: "</font>, after entering, <font color=#CE9178>"Please enter the new password again: "</font>, both new_password must be same.
    - If there are not the same, (red-font)<font color=#CE9178>"Incorrect!!"</font>, back to [Q.4.4.](#44-update-password)

### *`booking()`*

```python
def booking(student_id:str, cap_info: BasicCapability, booking_time: BookingTime, user_config: UserConfig, booking_csv: Path = Path('jobs/booking.csv')) -> bool:
```

#### **Parameters**

- `student_id`: user's account.
- `cap_info`: cpus, memory, gpus.
- `booking_time`: checked available times.
- `user_config`: the config for this student_id.
- `booking_csv`: the csv for booking, default: 'jobs/booking.csv'.

#### **Return**

- `boolean`

After in `cli()` confirm all the parameter, it time to booking the schedule to the `booking.csv`.

```python
def booking(student_id:str, cap_info: BasicCapability, booking_time: BookingTime, user_config: UserConfig, booking_csv: Path) -> bool:
    '''
    Write the booking_info to the booking schedule.

    `student_id`: user's account.
    `cap_info`: cpus, memory, gpus.
    `booking_time`: checked available times.
    `user_config`: the config for this student_id.
    `booking_csv`: the csv for booking, default: 'jobs/booking.csv'.
    '''
    booking_df = Schedule_DF(booking_csv)
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
from src.HostInfo import HostInfo, BookingTime, BasicCapability, UserConfig
```

### *`Checker()`*

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
    deploy_info: HostInfo.deploy_info
    cap_config: HostInfo.cap_config
    users_config: HostInfo.users_config

    booking: HostInfo.booking
    using: HostInfo.using
    used: HostInfo.used

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
    super(HostInfo, self).__init__(deploy_yaml, booking_csv, using_csv, used_csv)

```

#### **Parameters**

- `deploy_yaml` : the yaml file for host deploy.
- `booking_csv`: the csv file for already booking.
- `using_csv`: the csv file for already using.
- `used_csv`: the csv file for already used.

#### **Return**

- `None`

### *`Checker.check_student_id()`*

```python
def check_student_id(self, student_id:str) -> bool:
```

Check student_id that has in the *`self.users_config.id`*.

#### **Parameters**

- `student_id` : user's account.

#### **Return**

- `boolean`

### *`Checker.get_user_max_cap()`*

```python
def get_user_max_cap(self, student_id: str) -> bool:
```

Search cap_info for student_id from the *`self.cap_config.max_default_capability`* / *`self.cap_config.max_custom_capability`*.

#### **Parameters**

- `student_id` : user's account.

#### **Return**

- `BasicCapability`

### *`Checker.check_booking_info()`*

```python
def check_booking_info(self, cap_info: BasicCapability, booking_time: BookingTime, user_config: UserConfig) -> bool:
```

Check whether *`self.booked_df`* has satisfied cap_info during booking_time.

#### **Parameters**

- `cap_info` : the user requires cpus, memory, gpus.
- `booking_time`: the user requires start time & end time.
- `user_config`: the user config information.

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
<!-- TODO -->
# `src/monitor`

## *`monitor.py`*
<!-- TODO -->
---

## *`run_container.py`*

### *`run()`*

```python
def run(
    student_id: str,
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
```

Search the fewer usages gpu_ids from *`self.booked_df`* in the `booking_time`.

#### **Parameters**

- `gpus` : number of gpus required.
- `booking_time`: the user requires start time & end time.

#### **Return**

- `List[int]`: the available gpu devices id list.
