import sys
import time
import os
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import Dict, List, NamedTuple, Tuple

if __name__ == "__main__":
    sys.path.append(str(Path(__file__).resolve().parents[2]))
    from run_container import run_container
    from lib.WordOperator import str_format
    from src.HostInfo import BasicCapability, BookingTime, HostInfo, ScheduleColumnNames, ScheduleDF, UserConfig


class MonitorMassage:
    # STATUS
    ERROR: str = "[ERROR]"
    WARING: str = "[WARNING]"
    INFO: str = "[INFO]"

    def __init__(self, path: Path = Path("src/jobs/monitor.log")) -> None:
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
    def __init__(self, path: Path = Path("jobs/monitor.log")) -> None:
        super().__init__(path)
        self.__name__ = "SpaceWarning"


class GPUDuplicateWarning(Warning):
    def __init__(self) -> None:
        self.__name__ = "GPUDuplicateWarning"


class Monitor(HostInfo):
    # deploy_info: HostInfo.deploy_info】
    # cap_config : HostInfo.cap_config
    # users_config: HostInfo.users_config

    # booking: HostInfo.booking
    # using: HostInfo.using
    # used: HostInfo.used
    msg: MonitorMassage

    def __init__(
        self,
        deploy_yaml: Path = Path('cfg/host_deploy.yaml'),
        booking_csv: Path = Path('jobs/booking.csv'),
        using_csv: Path = Path('jobs/using.csv'),
        used_csv: Path = Path('jobs/used.csv'),
        log_path: Path = Path('jobs/monitor.log'),
        *args,
        **kwargs,
    ) -> None:
        super(Monitor, self).__init__(deploy_yaml, booking_csv, using_csv, used_csv, *args, **kwargs)
        self.msg = MonitorMassage(log_path)

    def __get_dir_size(self, path, size: float = 0.0):
        for root, dirs, files in os.walk(path):
            for f in files:
                size += os.path.getsize(os.path.join(root, f))
        return size

    def check_space(self, user_id) -> bool:
        if self.cap_config.max_custom_capability.get(user_id) == None:  # user is not in custom config
            user_backup_capacity = self.cap_config.max_default_capability.backup_space
            user_work_capcity = self.cap_config.max_default_capability.work_space
        else:  # user is in custom config
            user_backup_capacity = self.cap_config.max_custom_capability[user_id].backup_space
            user_work_capcity = self.cap_config.max_custom_capability[user_id].work_space
        try:
            backup_capacity = round(self.__get_dir_size(path=self.users_config.ids[user_id].volume_backup_dir) / (1000**3), 2)  # Gb
            work_capacity = round(self.__get_dir_size(path=self.users_config.ids[user_id].volume_work_dir) / (1000**3), 2)
            backup_over_used = backup_capacity - user_backup_capacity
            work_over_used = work_capacity - user_work_capcity
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

    def close_containers(self, user_ids: List) -> List:
        result_ls = []
        for id in user_ids:  # user_ids is a list which contains ids need to be remove
            os.system(f"docker exec {id} python3 /root/Backup/.container_backup.py")
            os.system(f"docker container stop {id}")
            cmdInfo = os.system(f"docker container remove {id}")
            if cmdInfo == 0:  # success
                self.msg.info(msg=f"Container {id} have been closed successfully")
                result_ls.append(True)

            else:
                self.msg.error(sign="ContainerError", msg=f"Fail to close container {id}")
                result_ls.append(False)

        return result_ls

    def run_containers(self, run_df: pd.DataFrame) -> List:

        # result_ls:  List
        # ...
        # task: NamedTuple
        # for task in run_df.itertuples(index=False, name=None):
        #     ...
        #     result = run_container(..., **task._asdict())
        #     self.msg.info(...)
        #     ...
        #     ...
        #     return result_ls
        ...

    def update_tasks(self) -> List[str] and pd.DataFrame:
        remove_ids = []
        sorted_using = self.using.df.sort_values(by="end", ascending=False)  # sort by the ending time from big to small
        sorted_using.reset_index(drop=True, inplace=True)  # reset the index
        using_end_dates = sorted_using["end"]
        t_now = datetime.now()
        try:
            for i in range(0, len(using_end_dates), 1):  # find the
                time_delta = pd.Timedelta.total_seconds(t_now - using_end_dates[i])
                if time_delta >= 0:
                    move_to_used = sorted_using[i:]
                    self.used.df = pd.concat([self.used.df, move_to_used])
                    self.used.update_csv()
                    self.using.df = sorted_using.loc[sorted_using[0:i].index].copy()
                    self.using.update_csv()
                    remove_ids = move_to_used["user_id"].tolist()
                    self.msg.info(msg=f"Successfully update {remove_ids} from using to used")
                    break
        except:
            self.msg.error(sign="updateError", msg=f"fail to update {remove_ids} from using to used")
        move_to_using = pd.DataFrame(columns=self.used.df.columns)
        sorted_booking = self.booking.df.sort_values(by="start", ascending=False)  # sort by the starting time from big to small
        sorted_booking.reset_index(drop=True, inplace=True)  # reset the index
        booking_start_dates = sorted_booking["start"]
        t_now = datetime.now()
        try:
            for i in range(0, len(booking_start_dates), 1):
                time_delta = pd.Timedelta.total_seconds(t_now - booking_start_dates[i])
                if time_delta >= 0:
                    move_to_using = sorted_booking[i:]
                    self.using.df = pd.concat([self.using.df, move_to_using])
                    self.using.update_csv()
                    self.booking.df = sorted_booking.loc[sorted_booking[0:i].index].copy()
                    self.booking.update_csv()
                    move_to_using_ids = move_to_using["user_id"].to_list()
                    self.msg.info(msg=f"Successfully update {move_to_using_ids} from booking to using")
                    break
        except:
            self.msg.error(sign="updateError", msg=f"fail to update {move_to_using_ids} from booking to using")

        return (remove_ids, move_to_using)

    def exec(self) -> None:
        close_ls: List[str]
        check_ls: List[bool]
        task_df: pd.DataFrame
        run_df: pd.DataFrame

        close_ls, task_df = self.update_tasks()
        self.close_containers(close_ls)

        ...
        check_ls = [self.check_space() for user_id in task_df[ScheduleColumnNames.user_id]]
        print(check_ls)
        run_df = ...  # use check_ls to select it.

        self.run_containers(run_df)
        ...


aa = Monitor(
    deploy_yaml='cfg/test_host_deploy.yaml',
    booking_csv='jobs/booking.csv',
    using_csv='jobs/using.csv',
    used_csv='jobs/used.csv',
    log_path='jobs/monitor.log',
)
# aa.check_space("m11007s05-7")
aa.update_tasks()
