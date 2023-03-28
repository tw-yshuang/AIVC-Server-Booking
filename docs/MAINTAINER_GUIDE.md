# **AIVC-Server-Booking Maintainer Manual**

For Host Maintainer & MLOps

## **Pre-required**

There has 3 things you must install before start it:
`nvidia-linux-driver`, `docker` and `nvidia-container-toolkit`

### Nvidia-Linux-Driver

Here is suggest to use apt to install the driver, use this [Nvidia Linux Driver Installation Guide](https://docs.nvidia.com/datacenter/tesla/tesla-installation-notes/index.html#ubuntu-lts) to install the latest version of GPU driver.

**Note**: If you are using others methods to install, make sure the **NVIDIA Linux Driver >= 418.81.07**

### Docker

Here is suggest to use apt to install the Docker, follow the [Install Docker Engine on Ubuntu](https://docs.docker.com/engine/install/ubuntu/#install-using-the-repository) to install the Docker.

After that, you need to create a Unix group called docker and add users to it. So the you don't need to use `docker` command with `sudo`, and it is **must for this system**. see [Manage Docker as a non-root user](https://docs.docker.com/engine/install/linux-postinstall/#manage-docker-as-a-non-root-user) to setup.

**Note:** Docker >= 19.03

### Nvidia-Container-Toolkit

The NVIDIA Container Toolkit is available on a variety of Linux distributions and supports different container engines.

* [Platform Requirements](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html#platform-requirements)

* [Setting up NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html#setting-up-nvidia-container-toolkit)

## **Installation of AIVC-Server-Booking System**

```bash
# To the project directory location
bash setup.sh
```

It will be automatic to do the things below:

* Generate some system files.
* Setting some configurations to the OS.
* Install some packages.
* Pull all the images from [tw-yshuang's Docker Hub](https://hub.docker.com/repository/docker/rober5566a/aivc-server/general)
* Run booking container on port: 10000

## Config File

<!-- TODO: -->
*.yaml

### cfg/example

### cfg/templates
<!-- TODO: -->
## Run Booking Container

## Run Container without booking(for test used)
