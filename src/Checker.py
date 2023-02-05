from pathlib import Path
from datetime import datetime
from typing import Tuple, Dict

import pandas as pd

from lib.WordOperator import str_format, ask_yn
from src.HostInfo import HostInfo, BookingTime, BasicCapability, UserConfig

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

    def __init__(
        self,
        deploy_yaml: Path = Path('cfg/host_deploy.yaml'),
        booking_csv: Path = Path('jobs/booking.csv'),
        using_csv: Path = Path('jobs/using.csv'),
        used_csv: Path = Path('jobs/used.csv'),
        ) -> None:
        #### **Parameters**
        #- `deploy_yaml` : the yaml file for host deploy.
        #- `booking_csv`: the csv file for already booking.
        #- `using_csv`: the csv file for already using.
        #- `used_csv`: the csv file for already used.
        ##### **Return**
        #- `None`
        super(HostInfo, self).__init__(deploy_yaml, booking_csv, using_csv, used_csv)

    def check_student_id(self, student_id:str) -> bool:
        #Check student_id that has in the *`self.users_config.id`*.
        #### **Parameters**
        #- `student_id` : user's account.
        #### **Return**
        #- `boolean`
        a=1
    
    def get_user_max_cap(self, student_id: str) -> BasicCapability:
        #Search cap_info for student_id from the *`self.cap_config.max_default_capability`* / *`self.cap_config.max_custom_capability`*.
        #### **Parameters**
        #- `student_id` : user's account.
        #### **Return**
        #- `BasicCapability`
        a=1

    def check_booking_info(self, cap_info: BasicCapability, booking_time: BookingTime, user_config: UserConfig) -> bool:
        #Check whether *`self.booked_df`* has satisfied cap_info during booking_time.
        #### **Parameters**
        #- `cap_info` : the user requires cpus, memory, gpus.
        #- `booking_time`: the user requires start time & end time.
        #- `user_config`: the user config information.
        #### **Return**
        #- `boolean`
        a=1
    
    def get_best_gpu_ids(self, gpus: int, booking_time: BookingTime) -> List[int]:
        #Search the fewer usages gpu_ids from *`self.booked_df`* in the `booking_time`.
        #### **Parameters**
        #- `gpus` : number of gpus required.
        #- `booking_time`: the user requires start time & end time.
        #### **Return**
        #- `List[int]`: the available gpu devices id list.
        a=1

if "__name__"=="__main__":
    a=0