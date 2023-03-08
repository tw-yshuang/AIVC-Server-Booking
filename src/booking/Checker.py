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
        super().__init__(deploy_yaml, booking_csv, using_csv, used_csv)
        self.booked_df = ScheduleDF.concat(HostInfo.booking, HostInfo.using)
        #? self. change to HostInfo.

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
        #? check api : user_config not been used
        #self.booked_df 存了預約資料
        df = self.booked_df
        for i in len(df['end']):
            # del booking time before
            if df['end'][i] > booking_time.start :
                df = df.drop(index=[i])
        for j in len(df['start']):
            # del booking time after
            if df['start'][j] > booking_time.end :
                df = df.drop(index=[j])
        using_gpus = []
        for i in len(df['gpus']):
            using_gpus = using_gpus + df['gpus'][i]
        # retrun ((max) - (how many been used) >= (how many cap_info asked)) -> boolen
        return self.cap_config.max.gpus - len(using_gpus) >= cap_info.gpus
    
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
        # find booking_time imformation
        df = self.booked_df
        for i in len(df['end']):
            # del booing before
            if df['end'][i] > booking_time.start :
                df = df.drop(index=[i])
        for j in len(df['start']):
            # del booking after
            if df['start'][j] > booking_time.end :
                df = df.drop(index=[j])
        # del using gpus
        gpu_id = [0,1,2,3,4,5,6,7]
        for i in df['gpus']:    # [[0,1],[2,3]]
            for j in i:     # [0,1]
                for k in j:     # 0 1
                    gpu_id.remove(k)
        # return gpu list been asked start from 0 to gpus
        #? do I need to check was it satisfy the config?
        return gpu_id[0:gpus]
    
    #? where is api?: def check_forward_port_empty()

if __name__ == '__main__':
    Checker = Checker(deploy_yaml=Path('cfg/host_deploy.yaml')
        ,booking_csv = Path('jobs/booking.csv')
        ,using_csv = Path('jobs/using.csv')
        ,used_csv = Path('jobs/used.csv')
        )
    print(Checker.booked_df)
    print('123')