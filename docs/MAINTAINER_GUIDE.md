# **AIVC-Server-Booking Maintainer Manual**

For Host Maintainer & MLOps

## **1. Pre-required**

There has 3 things you must install before start it:
`nvidia-linux-driver`, `docker` and `nvidia-container-toolkit`

### Nvidia-Linux-Driver

Here is suggest to use apt to install the driver, use this [Nvidia Linux Driver Installation Guide](https://docs.nvidia.com/datacenter/tesla/tesla-installation-notes/index.html#ubuntu-lts) to install the latest version of GPU driver.

**Note**: If you are using others methods to install, make sure the **NVIDIA Linux Driver >= 418.81.07**, after install, please reboot the OS.

### Docker

Here is suggest to use apt to install the Docker, follow the [Install Docker Engine on Ubuntu](https://docs.docker.com/engine/install/ubuntu/#install-using-the-repository) to install the Docker.

After that, you need to create a Unix group called docker and add users to it. So the you don't need to use `docker` command with `sudo`, and it is **must for this system**. see [Manage Docker as a non-root user](https://docs.docker.com/engine/install/linux-postinstall/#manage-docker-as-a-non-root-user) to setup.

**Note:** Docker >= 19.03

### Nvidia-Container-Toolkit

The NVIDIA Container Toolkit is available on a variety of Linux distributions and supports different container engines.

- [Platform Requirements](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html#platform-requirements)
- [Platform Requirements](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html#platform-requirements)

- [Setting up NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html#setting-up-nvidia-container-toolkit)

---

## **2. Installation of AIVC-Server-Booking System**

```bash
# To the project directory location
bash setup.sh
```

### Main Funciton

The setup.sh is a file that needs to be executed during system **installation** and **updates**. It fully and automatically sets up the necessary files and packages. It performs the following tasks sequentially:

- Checks if there are any `job/monitor` files; if not, it creates them using the 'touch' command.
- Checks if the files `booking.csv`, `use.csv`, and `used.csv` exist; if not, it creates copies based on a template.
- Checks if the files `capability_config.yaml`, `host_deploy.yaml`, and `users_config.yaml` exist; if not, it creates copies based on a template.
- Utilize the `crontab` command to schedule the operating system to execute the program at specific times, achieving the goal of monitoring.
- Install required packages.
- Pull all the images from [tw-yshuang's Docker Hub](https://hub.docker.com/repository/docker/rober5566a/aivc-server/general)
- Stop and remove the old container, then run the booking container on port 10000.

---
---

# Config File

## **`host_deploy.yaml`**

### Main function

<!-- TODO: -->

### Variables

1. **`volume_work_dir`**: `str`,
The path contains folders with student IDs, and each folder stores user-specific data such as code and datasets.
   - ***Example:*** Folders within this path might store individualized information for each user, including code and datasets.
   - The default parent volume work directory. Usually, user's volume work direct will be: `volume_work_dir/userID`, please see [users_config.yaml](#users_configyaml) for more detail.
2. **`volume_dataset_dir`**: `str`,
This path includes publicly accessible datasets for all users to access.
   - ***Example:*** The path might contain datasets like the COCO dataset, available for use by all users.
3. **`volume_backup_dir`**: `str`,
This path also stores folders identified by student IDs, each holding backup files specific to that user.
   - ***Example:*** Folders within this path could store user-specific backup files, such as .pyenv and .zshrc.
4. **`users_config_yaml`**: `str`,
Points to the path of the users_config.yaml file.
5. **`capability_config_yaml`**: `str`,
Points to the path of the capability.yaml file.
6. **`images`**: `List[str]`,
Points to image files for different CUDA versions, allowing users to choose the corresponding version based on their needs.
   - ***Example:*** This could be used for selecting different CUDA versions of images according to the user's requirements.

---

## **`users_config.yaml`**

### Main function

<!-- TODO: -->

### Variables

1. **`password`**: `str`,
Represents the user's password, displayed in plaintext for easy management.
2. **`forward_port`**: `int`,
Indicates the port number assigned to the user.
3. **`image`**: `str`,
Represents the image used for the user's container.
4. **`extra_command`**: `str`,
Refers to additional commands inputted by the user.
5. **`volume_work_dir`**: `str`,
The user's exclusive working directory.
6. **`volume_dataset_dir`**: `str`,
The directory for publicly accessible datasets.
7. **`volume_backup_dir`**: `str`,
The backup directory exclusively designated for the user.

---

## **`capability_config.yaml`**

### Main function

<!-- TODO: -->

### Variables

1. **`max`**: `Dict`, the maximum resource of this server can afford.
   1. **`cpus`**: `int`, Maximum CPU utilization.
   2. **`ram`**: `int`, Maximum RAM utilization.
   3. **`swap_size`**: `int`, Maximum swap space utilization.
   4. **`gpus`**: `int`, Maximum GPU utilization.
   5. **`shm_rate`**: The ratio of swap space to RAM.
   6. **`memory`**: `int`, Available storage capacity.
   7. **`backup_space`**: `int`, Maximum allowable user backup space.
   8. **`work_space`**: `int`, Maximum allowable user workspace.

2. **`allow_userIDs`**: `List[str]`, User IDs with access to resources.

3. **`max_default_capability`**: `Dict`, Default usage for users accessing the server.
   1. **`cpus`**: `int`, Maximum default CPU usage.
   2. **`gpus`**: `int`, Maximum default GPU usage.
   3. **`memory`**: `int`, Maximum default memory usage.
   4. **`backup_space`**: `int`, Maximum default backup space usage.
   5. **`work_space`**: `int`, Maximum default workspace usage.

4. **`max_custom_capability`**: `Dict`, same with `max_default_capability`, if there is not parameter, follow by max_default_capability.

### Custom setting example

```bash
'''Example 1'''
max_default_capability:
  cpus: 8
  memory: 32
  gpus: 1

  backup_space: 50
  work_space: 200
```

In this example, for all non-customized users:

- Default maximum CPU is **8**.
- Default maximum memory is **32GB**.
- Default maximum GPU is **1**.
- Default maximum backup space is **50GB**.
- Default maximum work space is **200GB**.

```bash
'''Example 2'''
max_custom_capability:
   m111xxxxx:
      cpus: max
      memory: 64
      backup_space: max
```

In this example, for the m111xxxxx:

- The available cpus are labeled as "max" corresponding to a maximum CPU usage of **62** as indicated by the "max" label.
- The maximum allowable memory usage is **64GB**.
- The backup_space is labeled as "max," and corresponding to the "max" label. the maximum allowable backup space is **200GB**.

---

# CSV File

## **`booking.csv`**

### Main Function

The **`booking.csv`** records upcoming scheduled activities.

### Example

For instance, if "m112xxxxx" is scheduled to activate a container for work one day later, the booking.csv file will document this reservation.

---

## **`use.csv`**

### Main Function

The **`use.csv`** file logs currently active records.

### Example

For example, if "m111xxxxx" has its container opened and is in an operational phase, the use.csv file will capture this information.

---

## **`used`**.csv

### Main Function

The **`used.csv`** file maintains records of completed activities.

### Example

For instance, when "m110xxxxx" finishes its work, and the container is closed, the used.csv file will document this information.

---

---

## Run Booking Container

### Main Function

Receiving user input. If it is `-h` or `--help`, it will display the **help message**. If not `-h` or `--help`, it will prompt the user to enter a password. Finally, it will execute the command to open a Docker container.

### Variables

   1. **`show_script_help()`**:
   The purpose of `show_script_help()` is to display the help message.
   2. **`-dit`**: Indicates running the container in the background.
   3. **`--cpus="0.5"`**: Allocates the number of CPU cores for the container.
   4. **`--memory="50"M`**: Allocates the amount of memory for the container.
   5. **`--restart=always`**: The container always restarts after exiting.
   6. **`-p 10000:22`**: Maps the host's port 10000 to port 22 of the container.
   7. **`--name=booking`**: Specifies the name of the container as "booking".
   8. **`-v parameter`**: Maps directories on the host to corresponding directories inside the container.
   9. **`rober5566a/aivc-server:booking-v1.1.1`**: Specifies the Docker image to run.
   10. **`/bin/bash -c "( ln -s $DOCKER_PATH/src/booking/booking.py /usr/sbin/booking || true ) && /.script/ssh_start.sh $password"`**: The command executed inside the container, including creating a symbolic link and starting the ssh service.

## Run Container without booking(for test used)
>>>>>>>
>>>>>>> develop
