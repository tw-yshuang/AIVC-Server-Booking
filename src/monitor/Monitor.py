import os

# import warnings
import time
import sys
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Tuple, Dict, NamedTuple, List

if __name__ == "__main__":
    sys.path.extend("../../")
    # print(sys.path)

from lib.WordOperator import str_format
from src.HostInfo import HostInfo, BookingTime, BasicCapability, UserConfig, ScheduleDF, ScheduleColumnNames
from run_container import run_container


class SpaceWarning(Warning):
    pass


class GPUDuplicateWarning(Warning):
    pass


class MonitorMassage():
    '''
    Control the `Monitor` massage
    '''

    # STATUS
    ERROR: str = "[ERROR]"
    WARING: str = "[WARNING]"
    DONE: str = "[DONE]"
    INFO: str = "[INFO]"

    def __init__(self, path: Path = Path("src/jobs/t_monitor.log")) -> None:
        self.log_path = path

    def update_log(self, status: str, msg: str, sign) -> bool:
        with open(self.log_path, 'a') as f:
            timeStr = time.strftime("%Y%m%d %H:%M", time.localtime())
            if sign == None:  # INFO
                history = f"{timeStr} {status} {msg}\n"
            else:  # WARNING
                history = f"{timeStr} {status} {sign}, {msg}\n"
            f.write(history)

    # TODO
    def warning(self, msg) -> None:
        self.update_log(self.WARING, msg, sign=self.__name__)
        timeStr = time.strftime("%Y%m%d %H:%M", time.localtime())
        send_msg = f"{timeStr} {self.WARING} {SpaceWarning.__name__}, {msg}\n"
        send_msg = str_format(send_msg, fore="y")
        print(send_msg)

    def info(self, msg: str) -> None:
        self.update_log(self.INFO, msg, sign=None)
        timeStr = time.strftime("%Y%m%d %H:%M", time.localtime())
        send_msg = f"{timeStr} {self.INFO} {msg}\n"
        send_msg = str_format(send_msg, fore="g")
        print(send_msg)


class Monitor(HostInfo):
    '''
    `deploy_info`: the deploy information that from yaml file.
    `cap_config`: the capability config that from yaml file.
    `users_config`: the users config that from yaml file.
    `booking`: the booking schedule frame that from csv file.
    `using`: the using data schedule frame that from csv file.
    `used`: the used data schedule frame that from csv file.
    `msg`: control the massage and record it to the log file.
    '''

    deploy_info: HostInfo.deploy_info
    cap_config: HostInfo.cap_config
    users_config: HostInfo.users_config

    booking: HostInfo.booking
    using: HostInfo.using
    used: HostInfo.used

    msg: MonitorMassage
    Error = "[ERROR]"
    def __init__(
        self,
        deploy_yaml: Path = Path('cfg/host_deploy.yaml'),
        booking_csv: Path = Path('jobs/booking.csv'),
        using_csv: Path = Path('jobs/using.csv'),
        used_csv: Path = Path('jobs/used.csv'),
        log_path: Path = Path('jobs/monitor.log'),
    ) -> None:
        super(HostInfo, self).__init__(deploy_yaml, booking_csv, using_csv, used_csv)

        self.msg = MonitorMassage(log_path)

        self.exec()

    def update_tasks(self) -> (List[str], pd.DataFrame):
        pass
        
    def check_space(self, user_id: str) -> bool:
        pass

    def close_containers(self, user_ids: List[str]) -> List[bool or Error]:
        result_ls: List[bool or Error]
        ...
        for user_id in user_ids:
            try:
                print(os.system(f"docker container stop {user_id}"))
                print(os.system(f"docker container remove {user_id}"))
                self.msg.info(...)
                result_ls.append(True)

            except ...:
                ...
                result_ls.append(Error)
            ...
        return result_ls

    def run_containers(self, run_df: pd.DataFrame) -> List[bool or Error]:
        result_ls: List[bool or Error]
        ...
        task: NamedTuple
        for task in run_df.itertuples(index=False, name=None):
            ...
        result = run_container(..., **task._asdict())
        self.msg.info(...)
        ...
        return result_ls

    def exec(self) -> None:

        close_ls: List[str]
        check_ls: List[bool]
        task_df: pd.DataFrame
        run_df: pd.DataFrame

        close_ls, task_df = self.update_tasks()
        self.close_containers(close_ls)

        ...
        check_ls = [self.check_space() for user_id in task_df[ScheduleColumnNames.user_id]]

        run_df = ...  # use check_ls to select it.

        self.run_containers(run_df)
        ...
