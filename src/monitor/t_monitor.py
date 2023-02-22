import sys
import time
import os
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import Dict, List, NamedTuple, Tuple
# from pandas import Timedelta
sys.path.extend("../../")
from run_container import run_container
from lib.get_dir_size import get_dir_size
from lib.WordOperator import str_format
from src.HostInfo import BasicCapability, BookingTime, HostInfo, ScheduleColumnNames, ScheduleDF, UserConfig


class MonitorMassage:
    # STATUS
    ERROR: str = "[ERROR]"
    WARING: str = "[WARNING]"
    DONE: str = "[DONE]"
    INFO: str = "[INFO]"

    def __init__(self, path: Path = Path("src/jobs/t_monitor.log")) -> None:
        self.log_path = path
        # self.__name__ = "MonitorMassage"

    def update_log(self, status: str, msg: str, sign) -> bool:
        with open(self.log_path, 'a') as f:
            timeStr = time.strftime("%Y%m%d %H:%M", time.localtime())
            if sign == None:
                history = f"{timeStr} {status} {msg}\n"
            else:
                history = f"{timeStr} {status} {sign}, {msg}\n"
            f.write(history)

    def warning(self, sign: Warning, msg) -> None:
        self.update_log(self.WARING, msg, sign)
        timeStr = time.strftime("%Y%m%d %H:%M", time.localtime())
        send_msg = f"{timeStr} {self.WARING} {sign}, {msg}\n"
        send_msg = str_format(send_msg, fore="y")
        print(send_msg)

    def info(self, msg: str) -> None:
        self.update_log(self.INFO, msg, sign=None)
        timeStr = time.strftime("%Y%m%d %H:%M", time.localtime())
        send_msg = f"{timeStr} {self.INFO} {msg}\n"
        send_msg = str_format(send_msg, fore="g")
        print(send_msg)

    def error(self, sign, msg: str) -> None:
        self.update_log(self.ERROR, msg, sign)
        timeStr = time.strftime("%Y%m%d %H:%M", time.localtime())
        send_msg = f"{timeStr} {self.ERROR} {sign}, {msg}\n"
        send_msg = str_format(send_msg, fore="r")
        print(send_msg)


class SpaceWarning(Warning):
    def __init__(self, path: Path = Path("src/jobs/t_monitor.log")) -> None:
        super().__init__(path)
        self.__name__ = "SpaceWarning"


class GPUDuplicateWarning(Warning):
    def __init__(self) -> None:
        self.__name__ = "GPUDuplicateWarning"


class Monitor(HostInfo):
    # deploy_info: HostInfo.deploy_info
    # cap_config : HostInfo.cap_config
    # users_config: HostInfo.users_config

    # booking: HostInfo.booking
    # using: HostInfo.using
    # used: HostInfo.used
    msg: MonitorMassage

    def __init__(
        self,
        deploy_yaml: Path = Path('cfg/test_host_deploy.yaml'),
        booking_csv: Path = Path('src/jobs/booking.csv'),
        using_csv: Path = Path('src/jobs/using.csv'),
        used_csv: Path = Path('src/jobs/used.csv'),
        log_path: Path = Path('src/jobs/t_monitor.log'),
        *args,
        **kwargs,
    ) -> None:
        super().__init__(deploy_yaml, booking_csv, using_csv, used_csv, *args, **kwargs)
        self.msg = MonitorMassage(log_path)

    def check_space(self, user_id):
        if self.cap_config.max_custom_capability.get(user_id) == None:  # 沒有custom中的話
            try:
                backup_capacity = round(get_dir_size(path=self.users_config.ids[user_id].volume_backup_dir) / (1000**3), 2)  # Gb
                work_capacity = round(get_dir_size(path=self.users_config.ids[user_id].volume_work_dir) / (1000**3), 2)
                backup_over_used = backup_capacity - self.cap_config.max_default_capability.backup_space
                work_over_used = work_capacity - self.cap_config.max_default_capability.work_space
            except:
                send_msg = f"Fail to caculate the storage space of backup_dir or work_dir used by {user_id}."
                self.msg.error(sign="PathError", msg=send_msg)
                return False
            
        else:  # 有在custom中
            try:
                backup_capacity = round(get_dir_size(path=self.users_config.ids[user_id].volume_backup_dir) / (1000**3), 2)  # Gb
                work_capacity = round(get_dir_size(path=self.users_config.ids[user_id].volume_work_dir) / (1000**3), 2)
                backup_over_used = backup_capacity - self.cap_config.max_custom_capability[user_id].backup_space
                work_over_used = work_capacity - self.cap_config.max_custom_capability[user_id].work_space
            except:
                send_msg = f"Fail to caculate the storage space of backup_dir or work_dir used by {user_id}."
                self.msg.error(sign="PathError", msg=send_msg)
                return False
            
        # print(f"backup:{backup_over_used}Gb, work:{work_over_used}Gb")
        if (work_over_used > 0) and (backup_over_used > 0):
            send_msg = f"{user_id} is over-use the work_dir {work_over_used}GB, and backup_dir {backup_over_used}GB."
        elif work_over_used < 0 and backup_over_used > 0:
            send_msg = f"{user_id} is over-use the backup_dir {backup_over_used}GB."
        elif work_over_used > 0 and backup_over_used < 0:
            send_msg = f"{user_id} is over-use the work_dir {work_over_used}GB."
        else:
            return True

        self.msg.warning(sign=SpaceWarning.__name__, msg=send_msg)
        return False

    def close_containers(self, user_ids: List):
        result_ls = []
        for id in user_ids:  # user_ids is a list which contains ids need to be remove
            os.system(f"docker container stop {id}")
            os.system(f"docker exec {id} python3 /root/Backup/.container_backup.py")
            cmdInfo = os.system(f"docker container remove {id}")
            if cmdInfo == 0:  # success
                self.msg.info(msg=f"Container {id} have been closed successfully")
                result_ls.append(True)

            else:
                self.msg.error(sign="ContainerError", msg=f"Fail to close container {id}")
                result_ls.append("Error")

        return result_ls

    # def run_containers(self, run_df: pd.DataFrame) -> List:
    #     result_ls:  List
    #     ...
    #     task: NamedTuple
    #     for task in run_df.itertuples(index=False, name=None):
    #         ...
    #         result = run_container(..., **task._asdict())
    #         self.msg.info(...)
    #         ...
    #         ...
    #         return result_ls

    def update_tasks(self) -> List[str] and pd.DataFrame:
        remove_ids = []    
        enable_frame = pd.DataFrame(columns = self.used.df.columns)
        using_user_ids = self.using.df["user_id"]
        using_start_dates = self.using.df["end"]#先判斷要remove的task
        t_now = datetime.now()       
        for i in range(len(using_start_dates)-1, -1, -1):#從最後一筆資料開始到第一筆
            try:
                time_delta = pd.Timedelta.total_seconds(t_now - using_start_dates[i])
                if time_delta >= 0:#時間到了
                    remove_ids.append(using_user_ids[i]) 
                    # print(remove_ids)
                    self.used.df.loc[len(self.used.df.index)] = self.using.df.iloc[i]#將該列資料放入usd    
                    self.using.df = self.using.df.drop(i, axis='rows')#清除還在using的資料
                    self.used.update_csv()
                    self.using.update_csv()
                    self.msg.info(msg=f"{using_user_ids[i]} in using.csv and used.csv have been updated successfully")     

                else:#時間還沒到
                    pass
            except:
                self.msg.error("updateTaskError", msg=f"Fail to update using.csv and used.csv for {using_user_ids[i]}")     
        booking_start_dates = self.booking.df["start"]#判斷要開始的task
        booking_user_ids = self.booking.df["user_id"]
        t_now = datetime.now()
        for i in range(len(booking_start_dates)-1 , -1, -1):
            try:
                time_delta = pd.Timedelta.total_seconds(t_now - booking_start_dates[i])
                if time_delta >= 0:#時間到了
                    enable_info = self.booking.df.iloc[i]
                    enable_frame.loc[len(enable_frame)] = enable_info
                    self.using.df.loc[len(self.using.df.index)] = enable_info#將該列資料放入using
                    self.booking.df = self.booking.df.drop(i, axis='rows')#清除還在booking的資料
                    self.using.update_csv()
                    self.booking.update_csv()
                    self.msg.info(msg=f"{booking_user_ids[i]} in booking.csv and using.csv have been updated successfully")
                else:#時間還沒到
                    pass
            except:
                self.msg.error("updateTaskError", msg=f"Fail to update booking.csv and using.csv for {booking_user_ids[i]}")     
        return (remove_ids, enable_frame)

# user_ids = ["m11007s05", "m11007s05-1", "m11007s05-2"]
# user_ids2 = ["B10930010", "B10930011", "B10930012"]
# aa.check_space("m11007s05-2")
# aa.close_containers(user_ids2)
aa = Monitor()
out = aa.update_tasks()
print(out[0], "\n", out[1])