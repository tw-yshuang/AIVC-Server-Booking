# Developer API Documentation

This Data-Flow Chart shows that `HostInfo.py` control all the `*.yaml` & `*.csv` files, the others `*.py` need to use the APIs from `HostInfo.py` to read/write, and it also shows each `*.py` how related to `*.yaml` & `*.csv` files.
![Data-Flow](Data-Flow.drawio.svg)

---

## `booking.py`

It is a CLI tool that communicates with users.

### import packages

```python
from pathlib import Path
from datetime import datetime
from typing import Tuple, Dict

from checker import Checker
from lib.WordOperator import str_format, ask_yn
from src.HostInfo import BookingTime, BasicCapability, UserConfig, ScheduleDF
```

### _`cli()`_

```python
def cli(student_id: str = None, use_options: bool = False, list_schedule: bool = False) -> bool:
```

#### **Input Parameters**

- `student_id`: user's account.
- `use_options`: use extra options.
- `list_schedule`: list schedule that already booking.

#### **Return Value**

- True / False

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

In order to Fool-proofing, it will ask user the following option:

```python
# Required
password: str
booking_time: BookingTime
booking_time.start: datetime # start time for booking this schedule.
booking_time.end: datetime # end time for booking this schedule.
cap_info: BasicCapability
cap_info.cpus: int or str # number of cpus for container.
cap_info.memory: int or str # how much memory(ram, swap) GB for container.
cap_info.gpus: int or str # how many gpus for container.

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

### _`booking()`_

```python
def booking(student_id:str, cap_info: BasicCapability, booking_time: BookingTime, user_config: UserConfig, booking_csv: Path = Path('jobs/booking.csv')) -> bool:
```

#### **Input Parameters**

- `student_id`: user's account.
- `cap_info`: cpus, memory, gpus.
- `booking_time`: checked available times.
- `user_config`: the config for this student_id.
- `booking_csv`: the csv for booking, default: 'jobs/booking.csv'.

#### **Return Value**

- True / False

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
    ...
```

---

## `checker.py`

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

### _`Checker()`_

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

### _`Checker.__init__()`_

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

#### **Input Parameters**

- `deploy_yaml` : the yaml file for host deploy.
- `booking_csv`: the csv file for already booking.
- `using_csv`: the csv file for already using.
- `used_csv`: the csv file for already used.

#### **Output Parameters**

- None

### _`Checker.check_student_id()`_

```python
def check_student_id(self, student_id:str) -> bool:
```

Check student_id that has in the `self.users_config.id`.

#### **Input Parameters**

- `student_id` : user's account.

#### **Output Parameters**

- True / False

### _`Checker.check_max_cap()`_

```python
def check_max_cap(self, student_id: str, cap_info: BasicCapability) -> bool:
```

Check cap_info for student_id that is under the `self.max_default_capability` / `self.max_custom_capability`.

#### **Input Parameters**

- `student_id` : user's account.
- `cap_info`: the user requires cpus, memory, gpus.

#### **Output Parameters**

- True / False

### _`Checker.check_booking_info()`_

```python
def check_booking_info(self, cap_info: BasicCapability, booking_time: BookingTime, user_config: UserConfig) -> bool:
```

Check whether `self.booked_df` has satisfied cap_info during booking_time.

#### **Input Parameters**

- `cap_info` : the user requires cpus, memory, gpus.
- `booking_time`: the user requires start time & end time.
- `user_config`: the user config information.

#### **Output Parameters**

- True / False
