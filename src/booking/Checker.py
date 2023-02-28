from pathlib import Path
from datetime import datetime
from typing import Tuple, Dict,List

import pandas as pd

import sys
if __name__ == '__main__':
    # sys.path.insert(1,"../../src")
    sys.path.extend('../../')
#     print(sys.path)
# print(sys.path)
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
        super(Checker, self).__init__(deploy_yaml, booking_csv, using_csv, used_csv)
        self.booked_df = ScheduleDF.concat(self.booking.df, self.using.df)
        #? ScheduleDF.concat只吃Dataframe 所以後面要加.df

    def check_student_id(self, student_id:str) -> bool:
        '''
        Check student_id that has in the *`self.users_config.id`*.
        ### **Parameters**
        - `student_id` : user's account.
        ### **Return**
        - `boolean`
        '''
        try :
            return self.users_config.ids[student_id] != None
        except KeyError:
            return False
    
    def get_user_max_cap(self, student_id: str) -> BasicCapability:
        '''
        Search cap_info for student_id from the *`self.cap_config.max_default_capability`* / *`self.cap_config.max_custom_capability`*.
        # **Parameters**
        - `student_id` : user's account.
        # **Return**
        - `BasicCapability`
        '''
        try:
            # print(student_id,':max_custom_capability')
            return self.cap_config.max_custom_capability[student_id]
        except KeyError:
            print('max_default_capability')
            return self.cap_config.max_default_capability
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
        df['start'] =  pd.to_datetime(df['start'], format='%Y-%b-%d %H:%M:%S.%f')
        df['end'] =  pd.to_datetime(df['end'], format='%Y-%b-%d %H:%M:%S.%f')
        df['gpus'] = df['gpus'].values.tolist()
        # see = df['gpus']
        # print(see)
        # print(type(see))
        #* del none using date
        for i in range(len(df['end'])):
            # del booking time before
            if df['end'][i] > booking_time.start :
                df = df.drop(index=[i])
        for j in range(len(df['start'])):
            # del booking time after
            if df['start'][j] > booking_time.end :
                df = df.drop(index=[j])
        # print(df)
        using_gpus = []
        # print(type(gpu_list[1][1]))
        for i in df['gpus']:
            ii = i[1:-1].split(', ') # 依照', '去切割字串
            # print(ii)
            # print(type(ii))
            for j in ii:
                j=int(j)
                # print('j:',j)
                # print(type(j))
                using_gpus.append(j)
        using_gpus = list(set(using_gpus))
        # retrun ((max) - (how many been used) >= (how many cap_info asked)) -> boolen
        # print(using_gpus)
        # print(f'{self.cap_config.max.gpus} - {len(using_gpus)} >= {cap_info.gpus}')
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
        df['start'] =  pd.to_datetime(df['start'], format='%Y-%b-%d %H:%M:%S.%f')
        df['end'] =  pd.to_datetime(df['end'], format='%Y-%b-%d %H:%M:%S.%f')
        df['gpus'] = df['gpus'].values.tolist()
        #* del none using date
        for i in range(len(df['end'])):
            # del booking time before
            if df['end'][i] > booking_time.start :
                df = df.drop(index=[i])
        for j in range(len(df['start'])):
            # del booking time after
            if df['start'][j] > booking_time.end :
                df = df.drop(index=[j])
        # del using gpus
        gpu_id = [0,1,2,3,4,5,6,7]
        print(df['gpus'])
        for i in df['gpus']:
            ii = i[1:-1].split(', ') # 依照', '去切割字串
            # print('ii:',ii)
            for j in ii:
                j=int(j)
                # print(j)
                if gpu_id.count(j) != 0:
                    gpu_id.remove(j)
        # return gpu list been asked start from 0 to gpus
        #? do I need to check was it satisfy the config?
        return gpu_id[0:gpus]
    
    #? where is api?: def check_forward_port_empty()
    def check_forward_port_empty(self, forward_port):
        return True
    
    def check_image_isexists(self, root):
        return 
if __name__ == '__main__':
    checker = Checker(deploy_yaml=Path('cfg/test_host_deploy.yaml')
        ,booking_csv = Path('jobs/booking.csv')
        ,using_csv = Path('jobs/using.csv')
        ,used_csv = Path('jobs/used.csv')
        )
    # print(checker.booked_df)
    # print('123')

    # test check_student_id
    # student_ids = ['m11007s05','m11007s05-1','m11007s05-2','m11007s05-3','m11007s05-4','m11007s05-5']
    # for student_id in student_ids:
    #     print(student_id,':',checker.check_student_id(student_id))

    # test get_user_max_cap
    # student_ids = ['m11007s05','m11007s05-1','m11007s05-2','m11007s05-3','m11007s05-4','m11007s05-5']
    # for student_id in student_ids:
    #     print(checker.get_user_max_cap(student_id))

    # test check_booking_info
    # from datetime import timedelta
    # capinfos = []
    # for i in range(1,5):
    #     aa = BasicCapability(cpus=i*10,memory=i*10,gpus = i,backup_space =i,work_space=i)
    #     # print(aa.cpus)
    #     capinfos.append(aa)
    # # print(capinfos)
    # booktimes = []
    # for i in range(1,5):
    #     tt = datetime( 2000+i , i , i , i , 0 , 0 )
    #     aa = BookingTime()
    #     aa.start = tt 
    #     aa.end = tt + timedelta(minutes=30)
    #     booktimes.append(aa)
    # # print(booktimes)
    # userconfigs = [checker.users_config.ids['m11007s05'],checker.users_config.ids['m11007s05-1'],checker.users_config.ids['m11007s05-3'],checker.users_config.ids['m11007s05-4']]
    # # print(userconfigs)
    # # print(len(capinfos),len(booktimes),len(userconfigs))
    # for i in range(1):
    #     print(f'!!!Check whether self.booked_df has satisfied gpu:{capinfos[i].cpus} during {booktimes[i].start}~{booktimes[i].end}.i:{i}')
    #     print(checker.check_booking_info(capinfos[i],booktimes[i],userconfigs[i]))

    # test get_best_gpu_ids
    # from datetime import timedelta
    # booktimes = []
    # for i in range(1,5):
    #     tt = datetime( 2000+i , i , i , i , 0 , 0 )
    #     aa = BookingTime()
    #     aa.start = tt 
    #     aa.end = tt + timedelta(minutes=30)
    #     booktimes.append(aa)
    # requears = [1,2,3]
    # for i in range(3):
    #     print(checker.get_best_gpu_ids(requears[i],booktimes[i]))
