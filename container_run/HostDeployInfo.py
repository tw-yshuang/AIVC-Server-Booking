import yaml


class HostDeployInfo:
    volume_work_dir: str
    volume_dataset_dir: str
    user_config_json: str
    total_ram: int
    total_swap_size: int
    shm_rate: int

    def __init__(self, yaml='host_deploy.yaml') -> None:
        for k, v in self.load_yaml(yaml).items():
            setattr(self, k, v)

        self.shm_rate = self.total_ram / self.total_swap_size if self.total_swap_size != 0 else 1

    @staticmethod
    def load_yaml(filename: str) -> dict:
        with open(filename, 'r') as f:
            return yaml.load(f, Loader=yaml.SafeLoader)


if __name__ == '__main__':
    host_info = HostDeployInfo('host_deploy-test.yaml')
    print(dir(host_info))
