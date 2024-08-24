import os, time, subprocess
from pathlib import Path
from datetime import datetime
from typing import List, NamedTuple, Union

import numpy as np
import pandas as pd
from numpy.typing import NDArray

PROJECT_DIR = Path(__file__).resolve().parents[2]
if __name__ == '__main__':
    import sys

    sys.path.append(str(PROJECT_DIR))

from lib.WordOperator import str_format
from lib.FileOperator import get_dir_size_unix
from src.HostInfo import HostInfo, ScheduleDF
from src.HostInfo import ScheduleColumnNames as SC
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
    def __init__(self) -> None:
        super().__init__()

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        return 'SpaceWarning'


class GPUDuplicateWarning(Warning):
    def __init__(self) -> None:
        super().__init__()

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        return 'GPUDuplicateWarning'


class ContainerWarning(Warning):
    def __init__(self) -> None:
        super().__init__()

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        return 'ContainerWarning'


class ContainerError(Exception):
    def __init__(self) -> None:
        super().__init__()

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        return 'ContainerError'


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
            count.extend(run_df[SC.gpus].iloc[i])
        u, c = np.unique(count, return_counts=True)
        dup = u[c > 1]
        dup_ids = []
        for k in range(len(run_df)):
            for ele in dup:
                if ele in run_df[SC.gpus].iloc[k]:
                    dup_ids.append(run_df[SC.user_id].iloc[k])
        dup_ids = list(set(dup_ids))
        if dup_ids != []:
            self.msg.warning(
                sign=GPUDuplicateWarning.__name__,
                msg=f"{dup_ids} containers encounter GPU duplicate",
            )

    def check_space(self, user_id: str) -> bool:
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

        backup_size = round(get_dir_size_unix(self.users_config.ids[user_id].volume_backup_dir) / (2**20), 2)  # GB
        work_size = round(get_dir_size_unix(path=self.users_config.ids[user_id].volume_work_dir, timeout=600.0) / (2**20), 2)  # GB

        backup_over_used = backup_size - user_backup_capacity
        work_over_used = work_size - user_work_capacity

        msg_ls = []
        if backup_over_used > 0:
            msg_ls.append(f"backup_dir {backup_over_used}GB")
        if work_over_used > 0:
            msg_ls.append(f"work_dir {work_over_used}GB")

        if len(msg_ls) != 0:
            self.msg.warning(sign=SpaceWarning.__name__, msg=f"{user_id} is over-use the {', and the '.join(msg_ls)}.")
            return False

        return True

    def close_containers(self, user_ids: List[str]) -> List[bool]:
        result_ls = []
        for id in user_ids:  # user_ids is a list which contains ids need to be remove
            id = id.lower()

            exec_str_ls = [
                f'docker exec {id} python3 /root/Backup/.container_backup.py',  # Execute backup
                f'docker container stop {id}',  # Container stop
                f'docker container rm {id}',  # Container remove
            ]

            for exec_str, stage in zip(exec_str_ls[:-1], ['Exec', 'Stop']):
                result = subprocess.run(
                    exec_str.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8'
                ).stderr.split('\n')[0]
                if result != '':
                    self.msg.warning(sign=ContainerWarning(), msg=f"Close-{stage} {id}, {result}")

            result = subprocess.run(
                exec_str_ls[-1].split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8'
            ).stderr.split('\n')[0]

            if result != '':
                self.msg.error(sign=ContainerError(), msg=f"Close-Remove {id}, {result}")
                result_ls.append(False)
            else:
                self.msg.info(msg=f"Container {id} have been closed successfully")
                result_ls.append(True)

        return result_ls

    def run_containers(self, run_df: pd.DataFrame) -> List[bool]:
        result_ls: List
        task: NamedTuple
        result_ls = []
        for task in run_df.itertuples(index=False, name=None):
            user_id, cpus, memory, gpus, forward_port, image, extra_command = task[2:]
            user_id = user_id.lower()
            result = run_container(
                user_id=user_id,
                user_config=self.users_config.ids[user_id],
                cpus=cpus,
                memory=memory,
                gpus=gpus,
                forward_port=forward_port,
                image=image,
                extra_command=extra_command,
                cap_max=self.cap_config.max,
            )
            if result == '':
                result_ls.append(True)
                self.msg.info(msg=f"Container {user_id} have been run successfully")
            else:
                result_ls.append(False)
                self.msg.error(sign=ContainerError(), msg=f"Run {user_id}, {result}")

        return result_ls

    def update_tasks(self) -> List[Union[pd.DataFrame, None]]:
        t_now = datetime.now()

        move2used, now_using, move2using, now_booking = [None] * 4

        sorted_using = self.using.df.sort_values(by=SC.end, ascending=False)  # sort by the ending time from big to small
        sorted_using.reset_index(drop=True, inplace=True)  # reset the index
        using_end_dates = sorted_using[SC.end]
        for i in range(len(using_end_dates)):  # find the
            if pd.Timedelta.total_seconds(t_now - using_end_dates[i]) >= 0:
                move2used = sorted_using[i:]
                now_using = sorted_using.loc[sorted_using[:i].index].copy()
                break

        sorted_booking = self.booking.df.sort_values(by=SC.start, ascending=False)  # sort by the starting time from big to small
        sorted_booking.reset_index(drop=True, inplace=True)  # reset the index
        booking_start_dates = sorted_booking[SC.start]
        for i in range(len(booking_start_dates)):  # find the
            if pd.Timedelta.total_seconds(t_now - booking_start_dates[i]) >= 0:
                move2using = sorted_booking[i:]
                now_booking = sorted_booking.loc[sorted_booking[:i].index].copy()
                break

        return move2used, now_using, move2using, now_booking

    def update_sdf(
        self,
        from_sdf: ScheduleDF,
        to_sdf: ScheduleDF,
        now_df: pd.DataFrame,
        move2next_df: pd.DataFrame,
        status_arr: NDArray[np.bool_],
        msg: str,
    ) -> None:
        from_sdf.df = ScheduleDF.concat(now_df, move2next_df[np.invert(status_arr)])
        to_sdf.df = ScheduleDF.concat(to_sdf.df, move2next_df[status_arr])
        from_sdf.update_csv()
        to_sdf.update_csv()
        if status_arr.any() == True:
            self.msg.info(msg=f"Successfully update {move2next_df.loc[status_arr, SC.user_id].tolist()} from {msg}")
        if status_arr.any() == False:
            self.msg.error(
                sign="UpdateError",
                msg=f"Fail to update {move2next_df.loc[np.invert(status_arr), SC.user_id].tolist()} from {msg}",
            )

    def exec(self) -> None:
        move2used, now_using, move2using, now_booking = self.update_tasks()

        if not (move2used is None or move2used.empty):
            close_results = np.array(self.close_containers(move2used[SC.user_id].tolist()), dtype=np.bool_)
            self.update_sdf(self.using, self.used, now_using, move2used, close_results, msg="using to used")

        if not (move2using is None or move2using.empty):
            run_results = np.array([self.check_space(user_id) for user_id in move2using[SC.user_id]], dtype=np.bool_)
            run_results[run_results] = self.run_containers(move2using[run_results])
            self.update_sdf(self.booking, self.using, now_booking, move2using, run_results, msg="booking to using")

        self.check_gpus_duplicate(self.using.df)


if __name__ == '__main__':
    monitor = Monitor(
        deploy_yaml=PROJECT_DIR / 'cfg/host_deploy.yaml',
        booking_csv=PROJECT_DIR / 'jobs/booking.csv',
        using_csv=PROJECT_DIR / 'jobs/using.csv',
        used_csv=PROJECT_DIR / 'jobs/used.csv',
        log_path=PROJECT_DIR / 'jobs/monitor.log',
    )
    monitor.exec()
