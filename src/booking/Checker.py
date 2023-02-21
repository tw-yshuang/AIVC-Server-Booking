from pathlib import Path
from datetime import datetime
from typing import Tuple, Dict,List

import pandas as pd

import sys
if __name__ == '__main__':
    sys.path.extend('../../')
from lib.WordOperator import str_format, ask_yn
from src.HostInfo import HostInfo, BookingTime, BasicCapability, UserConfig, ScheduleDF
#? 新增加import ScheduleDF

#! tasting
#! csv readed formate
#! gpus saving formate
#! get_best_gpu_ids queation
#! get_best_gpu_ids search using gpus while booking_time

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

    def __init__(
        self,
        deploy_yaml: Path = Path('cfg/host_deploy.yaml'),
        booking_csv: Path = Path('jobs/booking.csv'),
        using_csv: Path = Path('jobs/using.csv'),
        used_csv: Path = Path('jobs/used.csv'),
        ) -> None:
        '''
        ### **Parameters**
        - `deploy_yaml` : the yaml file for host deploy.
        - `booking_csv`: the csv file for already booking.
        - `using_csv`: the csv file for already using.
        - `used_csv`: the csv file for already used.
        #### **Return**
        - `None`
        '''
        #HostInfo.__init__(deploy_yaml, booking_csv, using_csv, used_csv)
        super(HostInfo, self).__init__(deploy_yaml, booking_csv, using_csv, used_csv)
        #?self. change to HostInfo.
        self.booked_df = ScheduleDF.concat(HostInfo.booking, HostInfo.using)

    def check_student_id(self, student_id:str) -> bool:
        '''
        Check student_id that has in the *`self.users_config.id`*.
        ### **Parameters**
        - `student_id` : user's account.
        ### **Return**
        - `boolean`
        '''
        return self.users_config.ids[student_id] != None
    
    def get_user_max_cap(self, student_id: str) -> BasicCapability:
        '''
        Search cap_info for student_id from the *`self.cap_config.max_default_capability`* / *`self.cap_config.max_custom_capability`*.
        # **Parameters**
        - `student_id` : user's account.
        # **Return**
        - `BasicCapability`
        '''
        if self.cap_config.max_custom_capability[student_id] != None:
            return self.cap_config.max_custom_capability[student_id]
        else:
            return self.cap_config.max_default_capability

    def check_booking_info(self, cap_info: BasicCapability, booking_time: BookingTime, user_config: UserConfig) -> bool:
        '''
        Check whether *`self.booked_df`* has satisfied cap_info during booking_time.
        ### **Parameters**
        - `cap_info` : the user requires cpus, memory, gpus.
        - `booking_time`: the user requires start time & end time.
        - `user_config`: the user config information.
        ### **Return**
        - `boolean`
        '''
        #*只比gpu就好
        #!csv read collon need change
        #self.booked_df 存了預約資料
        df = self.booked_df['end']
        for i in len(df['end']):
            if df['end'][i] > booking_time.start :
                del(df['end'][i])
        using_cpus = 0
        using_memory = 0
        using_gpus = 0
        for i in len(df['cpus','memory','gpus']):
            using_cpus = using_cpus + df['cpus'][i]
            using_memory = using_memory + df['memory'][i]
            using_gpus = using_gpus + df['gpus'][i]
        return self.cap_config.max.cpus - using_cpus >= cap_info.cpus and self.cap_config.max.memory - using_memory >= cap_info.memory and self.cap_config.max.gpus - using_gpus >= cap_info.gpus
    
    def get_best_gpu_ids(self, gpus: int, booking_time: BookingTime) -> List[int]:
        '''
        Search the fewer usages gpu_ids from *`self.booked_df`* in the `booking_time`.
        ### **Parameters**
        - `gpus` : number of gpus required.
        - `booking_time`: the user requires start time & end time.
        ### **Return**
        - `List[int]`: the available gpu devices id list.
        '''
        #* 將前幾張gpu先塞滿 所以編號小的gpu 先提供
        df = self.booked_df['gpus']
        gpu_id = [0,1,2,3,4,5,6,7]
        #search booking_time using gpu and remove
        gpu_id.remove(df)
        return gpu_id

if __name__ == '__main__':
    HostInfo = HostInfo(deploy_yaml=Path('cfg/test_host_deploy.yaml'))
    Checker = Checker(HostInfo)
    print(Checker.booked_df)
    print('123')