import sys
import time
import os
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
from typing import List, NamedTuple

PROJECT_DIR = Path(__file__).resolve().parents[2]
if __name__ == '__main__':
    sys.path.append(str(PROJECT_DIR))

from lib.WordOperator import str_format
from lib.FileOperator import get_dir_size_unix
from src.HostInfo import HostInfo, ScheduleColumnNames
from src.monitor.run_container import run_container


class MonitorMassage:
    # STATUS
    ERROR: str = '[ERROR]'
    WARING: str = '[WARNING]'
    INFO: str = '[INFO]'

    def __init__(self, path: Path = PROJECT_DIR / 'src/jobs/monitor.log') -> None:
        self.log_path = path

    def update_log(self, status: str, msg: str, sign) -> bool:
        with open(self.log_path, 'a') as f:
            timeStr = time.strftime('%Y%m%d %H:%M', time.localtime())
            if sign == None:
                history = f'{timeStr} {status} {msg}\n'
            else:
                history = f'{timeStr} {status} {sign}, {msg}\n'
            f.write(history)

    def warning(self, sign: Warning, msg) -> None:
        self.update_log(self.WARING, msg, sign)
        timeStr = time.strftime('%Y%m%d %H:%M', time.localtime())
        send_msg = f"{timeStr} {self.WARING} {sign}, {msg}\n"
        send_msg = str_format(send_msg, fore='y')
        print(send_msg)

    def info(self, msg: str) -> None:
        self.update_log(self.INFO, msg, sign=None)
        timeStr = time.strftime('%Y%m%d %H:%M', time.localtime())
        send_msg = f"{timeStr} {self.INFO} {msg}\n"
        send_msg = str_format(send_msg, fore='g')
        print(send_msg)

    def error(self, sign, msg: str) -> None:
        self.update_log(self.ERROR, msg, sign)
        timeStr = time.strftime('%Y%m%d %H:%M', time.localtime())
        send_msg = f"{timeStr} {self.ERROR} {sign}, {msg}\n"
        send_msg = str_format(send_msg, fore='r')
        print(send_msg)


class SpaceWarning(Warning):
    def __init__(self, path: Path = PROJECT_DIR / 'jobs/monitor.log') -> None:
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
        deploy_yaml: Path = PROJECT_DIR / 'cfg/host_deploy.yaml',
        booking_csv: Path = PROJECT_DIR / 'jobs/booking.csv',
        using_csv: Path = PROJECT_DIR / 'jobs/using.csv',
        used_csv: Path = PROJECT_DIR / 'jobs/used.csv',
        log_path: Path = PROJECT_DIR / 'jobs/monitor.log',
        *args,
        **kwargs,
    ) -> None:
        super(Monitor, self).__init__(deploy_yaml, booking_csv, using_csv, used_csv, *args, **kwargs)
        self.msg = MonitorMassage(log_path)

    def check_gpus_duplicate(self, run_df):
        count = []
        for i in range(len(run_df)):
            count.extend(run_df['gpus'].iloc[i])
        u, c = np.unique(count, return_counts=True)
        dup = u[c > 1]
        dup_ids = []
        for k in range(len(run_df)):
            for ele in dup:
                if ele in run_df['gpus'].iloc[k]:
                    dup_ids.append(run_df['user_id'].iloc[k])
        dup_ids = list(set(dup_ids))
        if dup_ids != []:
            self.msg.warning(
                sign=GPUDuplicateWarning.__name__,
                msg=f"{dup_ids} containers encounter GPU duplicate",
            )

    def check_space(self, user_id) -> bool:
        user_id = user_id.lower()
        if self.cap_config.max_custom_capability.get(user_id) == None:  # user is not in custom config
            user_backup_capacity = self.cap_config.max_default_capability.backup_space
            user_work_capacity = self.cap_config.max_default_capability.work_space
        else:  # user is in custom config
            user_backup_capacity = self.cap_config.max_custom_capability[user_id].backup_space
            user_work_capacity = self.cap_config.max_custom_capability[user_id].work_space

        isNotExist = False
        for path in [self.users_config.ids[user_id].volume_backup_dir, self.users_config.ids[user_id].volume_work_dir]:
            if os.path.exists(path) is False:
                self.msg.info(f"{path} is not exists.")
                isNotExist = True
        if isNotExist:
            return True

        backup_size = round(get_dir_size_unix(self.users_config.ids[user_id].volume_backup_dir) / (1024**2), 2)  # GB
        work_size = round(get_dir_size_unix(path=self.users_config.ids[user_id].volume_work_dir) / (1024**2), 2)  # GB

        backup_over_used = backup_size - user_backup_capacity
        work_over_used = work_size - user_work_capacity

        msg_ls = []
        if backup_over_used > 0:
            msg_ls.append(f"backup_dir {backup_over_used}GB")
        if work_over_used > 0:
            msg_ls.append(f"work_dir {work_over_used}GB")

        if len(msg_ls) != 0:
            print(f"ys-huang is over-use the {', and the '.join(msg_ls)}.")

        if len(msg_ls) != 0:
            self.msg.warning(sign=SpaceWarning.__name__, msg=f"{user_id} is over-use the {', and the '.join(msg_ls)}.")
            return False

        return True

    def close_containers(self, user_ids: List) -> List:
        result_ls = []
        for id in user_ids:  # user_ids is a list which contains ids need to be remove
            id = id.lower()
            os.system(f'docker exec {id} python3 /root/Backup/.container_backup.py')
            os.system(f'docker container stop {id}')
            cmdInfo = os.system(f'docker container rm {id}')
            if cmdInfo == 0:  # success
                self.msg.info(msg=f"Container {id} have been closed successfully")
                result_ls.append(True)

            else:
                self.msg.error(sign="ContainerError", msg=f"Fail to close container {id}")
                result_ls.append(False)

        return result_ls

    def run_containers(self, run_df: pd.DataFrame) -> List:
        result_ls: List
        task: NamedTuple
        result_ls = []
        for task in run_df.itertuples(index=False, name=None):
            user_id, cpus, memory, gpus, forward_port, image, extra_command = task[2:]
            user_id = user_id.lower()
            try:
                result = run_container(
                    user_id=user_id,
                    cpus=cpus,
                    memory=memory,
                    gpus=gpus,
                    forward_port=forward_port,
                    image=image,
                    extra_command=extra_command,
                    cap_max=self.cap_config.max,
                    user_config=self.users_config.ids[user_id],
                )
                result_ls.append(True)
                self.msg.info(msg=f"Container {user_id} have been run successfully")
            except Exception as e:
                self.msg.error(sign="ContainerError", msg=f"Fail to run container {user_id}, {e}")
                result_ls.append(False)
        return result_ls

    def update_tasks(self) -> List[str] and pd.DataFrame:
        remove_ids = []
        sorted_using = self.using.df.sort_values(by='end', ascending=False)  # sort by the ending time from big to small
        sorted_using.reset_index(drop=True, inplace=True)  # reset the index
        using_end_dates = sorted_using['end']
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
                    remove_ids = move_to_used['user_id'].tolist()
                    self.msg.info(msg=f"Successfully update {remove_ids} from using to used")
                    break
        except:
            self.msg.error(
                sign="UpdateError",
                msg=f"Fail to update {remove_ids} from using to used",
            )
        move_to_using = pd.DataFrame(columns=self.used.df.columns)
        sorted_booking = self.booking.df.sort_values(by='start', ascending=False)  # sort by the starting time from big to small
        sorted_booking.reset_index(drop=True, inplace=True)  # reset the index
        booking_start_dates = sorted_booking['start']
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
                    move_to_using_ids = move_to_using['user_id'].to_list()
                    self.msg.info(msg=f"Successfully update {move_to_using_ids} from booking to using")
                    break
        except:
            self.msg.error(
                sign="UpdateError",
                msg=f"Fail to update {move_to_using_ids} from booking to using",
            )

        return (remove_ids, move_to_using)

    def exec(self) -> None:
        close_ls: List[str]
        check_ls: List[bool]
        task_df: pd.DataFrame
        run_df: pd.DataFrame
        run_df = pd.DataFrame(columns=self.using.df.columns)

        close_ls, task_df = self.update_tasks()
        self.close_containers(close_ls)
        check_ls = [self.check_space(user_id) for user_id in task_df[ScheduleColumnNames.user_id]]
        for i in range(len(task_df)):
            if check_ls[i] == True:
                run_df.loc[len(run_df.index)] = task_df.iloc[i]
        self.run_containers(run_df)
        # os.system(f'docker exec {user_id} echo 'info' > N/run_echo')
        self.check_gpus_duplicate(run_df)


if __name__ == '__main__':
    monitor = Monitor(
        deploy_yaml=PROJECT_DIR / 'cfg/host_deploy.yaml',
        booking_csv=PROJECT_DIR / 'jobs/booking.csv',
        using_csv=PROJECT_DIR / 'jobs/using.csv',
        used_csv=PROJECT_DIR / 'jobs/used.csv',
        log_path=PROJECT_DIR / 'jobs/monitor.log',
    )
    monitor.exec()
