import ast
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from dataclasses import dataclass, asdict

import yaml
import pandas as pd

# https://github.com/yaml/pyyaml/issues/127#issuecomment-525800484
class CustomDumper(yaml.SafeDumper):
    def write_line_break(self, data=None):
        super().write_line_break(data)

        if len(self.indents) == 1:
            super().write_line_break()


def load_yaml(filename: str) -> dict:
    with open(filename, 'r') as f:
        return yaml.load(f, Loader=yaml.SafeLoader)


def dump_yaml(info_dict: dict, filename: str):
    with open(filename, 'w') as f:
        yaml.dump(info_dict, f, Dumper=CustomDumper, sort_keys=False)
    return True


@dataclass
class BookingTime:
    '''
    The time to book in the schedule.
    '''

    start: datetime = datetime.now()
    end: datetime = datetime.now() + timedelta(hours=1)

    def to_dict(self):
        if hasattr(self, 'dict'):
            del self.dict

        self.dict = asdict(self)
        return self.dict


@dataclass
class UserConfig:
    password: str = None
    forward_port: int = None  # which forward port you want to connect to port: 22(SSH).
    image: Path = None  # which image you want to use, default is use "rober5566a/aivc-server:latest"
    extra_command: str = None  # the extra command you want to execute when the docker runs.
    volume_work_dir: Path = None
    volume_dataset_dir: Path = None
    volume_backup_dir: Path = None

    def to_dict(self):
        if hasattr(self, 'dict'):
            del self.dict

        self.dict = asdict(self)
        return self.dict


class UsersConfig:
    ids: Dict[str, UserConfig]

    def __init__(self, yaml_file='cfg/users_config.yaml') -> None:
        self.ids = self.get_users_config(yaml_file)

    @staticmethod
    def get_users_config(yaml_file='cfg/users_config.yaml') -> Dict[str, UserConfig]:
        users_dict = load_yaml(yaml_file)
        users_config = {}
        for k, v in users_dict.items():
            users_config[k] = UserConfig(**v)

        return users_config

    def to_dict(self):
        self.dict = {}
        for k in self.ids.keys():
            self.dict[k] = self.ids[k].to_dict()
        return self.dict


class MaxCapability:
    cpus: float
    ram: int
    swap_size: int
    gpus: int

    shm_rate: int
    memory: int

    def __init__(self, max_dict: dict) -> None:
        for k, v in max_dict.items():
            if k == 'shm_rate' or k == 'memory':
                setattr(self, k, eval(v, {'ram': self.ram, 'swap_size': self.swap_size}))
            else:
                setattr(self, k, v)


class BasicCapability:
    cpus: float
    memory: int
    gpus: int

    backup_space: int
    work_space: int

    def __init__(
        self,
        cpus: float or str = None,
        memory: int or str = None,
        gpus: int or str = None,
        backup_space: int or str = None,
        work_space: int or str = None,
        defaultCap: object = None,
        maxCap: MaxCapability = None,
    ) -> None:
        cap_str_ls = ['cpus', 'memory', 'gpus', 'backup_space', 'work_space']
        for cap_str in cap_str_ls:
            cap_value = locals()[cap_str]
            cap_value_type = type(cap_value)
            if cap_value_type is int or cap_value_type is float:
                setattr(self, cap_str, cap_value)
            elif cap_value_type is str:
                setattr(self, cap_str, getattr(maxCap, cap_str))
            else:
                setattr(self, cap_str, getattr(defaultCap, cap_str))


class CapabilityConfig:
    max: MaxCapability
    allow_userID: List[str]
    max_default_capability: BasicCapability
    max_custom_capability: Dict[str, BasicCapability]

    def __init__(self, yaml='cfg/capability_config.yaml') -> None:
        for k, v in load_yaml(yaml).items():
            if k == 'max':
                setattr(self, k, MaxCapability(v))
            elif k == 'max_default_capability':
                setattr(self, k, BasicCapability(**v))
            elif k == 'max_custom_capability':
                custom_dict = {}
                for k_sub, v_sub in v.items():
                    custom_dict[k_sub] = BasicCapability(**v_sub, defaultCap=self.max_default_capability, maxCap=self.max)
                setattr(self, k, custom_dict)
            else:
                setattr(self, k, v)


class HostDeployInfo:
    volume_work_dir: Path
    volume_dataset_dir: Path
    volume_backup_dir: Path

    capability_config_yaml: Path
    users_config_yaml: Path
    images: List[str]

    def __init__(self, yaml_file='host_deploy.yaml') -> None:
        for k, v in load_yaml(yaml_file).items():
            setattr(self, k, v)


@dataclass
class ScheduleColumnNames:
    start = 'start'
    end = 'end'
    user_id = 'user_id'
    cpus = 'cpus'
    memory = 'memory'
    gpus = 'gpus'
    forward_port = 'forward_port'
    image = 'image'
    extra_command = 'extra_command'


class ScheduleDF:
    path: Path
    df: pd.DataFrame

    def __init__(self, csv_path: Path) -> None:
        self.path = csv_path
        self.df = pd.read_csv(self.path)

        self.df[[ScheduleColumnNames.start, ScheduleColumnNames.end]] = self.df[
            [ScheduleColumnNames.start, ScheduleColumnNames.end]
        ].astype('datetime64[ns]')
        self.df[ScheduleColumnNames.gpus] = self.df[ScheduleColumnNames.gpus].apply(ast.literal_eval)

    def update_csv(self) -> None:
        self.df.to_csv(self.path, index=False)

    @staticmethod
    def concat(df1: pd.DataFrame, df2: pd.DataFrame, *args):
        cat_ls = [df1, df2, *args] if tuple(args) == Tuple[pd.DataFrame] else [df1, df2]
        return pd.concat(cat_ls)


class HostInfo:
    deploy_info: HostDeployInfo
    cap_config: CapabilityConfig
    users_config: UsersConfig

    booking: ScheduleDF
    using: ScheduleDF
    used: ScheduleDF

    def __init__(
        self,
        deploy_yaml: Path = Path('cfg/host_deploy.yaml'),
        booking_csv: Path = Path('jobs/booking.csv'),
        using_csv: Path = Path('jobs/using.csv'),
        used_csv: Path = Path('jobs/used.csv'),
        *args,
        **kwargs
    ) -> None:
        # super(HostInfo, self).__init__(deploy_yaml, booking_csv, using_csv, used_csv, *args, **kwargs)

        self.deploy_info = HostDeployInfo(deploy_yaml)
        self.cap_config = CapabilityConfig(self.deploy_info.capability_config_yaml)
        self.users_config = UsersConfig(self.deploy_info.users_config_yaml)

        self.booking = ScheduleDF(booking_csv)
        self.using = ScheduleDF(using_csv)
        self.used = ScheduleDF(used_csv)


if __name__ == '__main__':
    import sys

    host_info = HostDeployInfo('./cfg/test_host_deploy.yaml')
    # print(HostInfo.deploy_info)
    # CapCfg = CapabilityConfig(
    #     host_info.capability_config_yaml,
    # )

    # print(dir(host_info))
    # print(host_info)

    # userCig = UserConfig()
    # print(userCig.to_dict())
    # print(userCig.dict)

    # import copy

    # users_config = UsersConfig('./cfg/test_users_config.yaml')
    # user_config = copy.deepcopy(users_config.ids['m11007s05'])
    # print(id(user_config), id(users_config))
    # print(users_config.ids['m11007s05'] == user_config)

    # sch_df = ScheduleDF('./cfg/template/test_schedule.csv')
    # print(sch_df[ScheduleColumnNames])
    # print('aa')
