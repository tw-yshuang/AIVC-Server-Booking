# AIVC-Server-Booking

A server booking system for the Advanced Intelligent Image and Vision Technology Research Center at the National Taiwan University of Science and Technology, we call it NTUST-AIVC.

We create a custom docker image for this system, and you can click this [docker-hub-link](https://hub.docker.com/repository/docker/rober5566a/aivc-server/general) to check the latest version of the image.

## Introduction

For this custom image, we design this booking system to help users and host maintainer(MLOps).

### For Users

1. Booking the server used time.
2. Setting the server to compute capability for each container (CPUs, RAM+SWAP, GPUs).
3. Back up the file users want when the container is removed.
4. Setting the password and forward port for the container via SSH makes the container more secure.
5. Custom image and the initial command to make the user more flexible to use.

### For Host Maintainer and MLOps

1. Setting the maximum to compute capability for general users.
2. Setting the white list to custom compute capability for specific users.
3. Setting volume directory: Dataset, Work, and Backup
4. Easy to maintain the user config via json file.

## Structure

```
.
├── Dockerfile
├── LICENSE
├── Pipfile
├── Pipfile.lock
├── README.md
├── cfg
│   ├── host_deploy.yaml
│   └── users_config.json
├── container_run
│   ├── HostDeployInfo.py
│   └── ssh_start.sh
├── docs
│   ├── DEV_DOCUMENT.md
│   ├── USER_GUIDE.md
│   └── tips
│       └── Error 804: forward compatibility was attempted on non supported HW.md
├── fonts
│   ├── 3-D.flf
│   ├── 3D-ASCII.flf
│   ├── 3d.flf
│   ├── ANSI Regular.flf
│   ├── ANSI Shadow.flf
│   ├── Big Money-ne.flf
│   ├── Big Money-nw.flf
│   ├── Broadway.flf
│   ├── DOS Rebel.flf
│   ├── Delta Corps Priest 1.flf
│   ├── Electronic.flf
│   ├── Isometric1.flf
│   ├── Sauce Code Pro Medium Nerd Font Complete.ttf
│   ├── SourceCodePro.zip
│   └── msjh.ttf
├── imgae_setup
│   ├── 11-logo.sh
│   ├── config
│   ├── cuda_path.sh
│   ├── custom_function.sh
│   ├── language_package.sh
│   ├── ohmyzsh_config.sh
│   ├── zsh_buckup_machanism.sh
│   └── zsh_ohmyzsh_setup.sh
├── lib
│   └── WordOperator.py
├── requirements.txt
└── run_container.py.
├── 123.txt
├── Dockerfile
├── LICENSE
├── Pipfile
├── Pipfile.lock
├── README.md
├── cfg
│   ├── capability_config.yaml
│   ├── host_deploy.yaml
│   ├── users_config.json
│   └── users_config.yaml
├── container_run
│   ├── HostInfo.py
│   ├── __pycache__
│   │   ├── HostDeployInfo.cpython-38.pyc
│   │   └── HostInfo.cpython-39.pyc
│   └── ssh_start.sh
├── docs
│   ├── DEV_DOCUMENT.md
│   ├── USER_GUIDE.md
│   └── tips
│       └── Error 804: forward compatibility was attempted on non supported HW.md
├── fonts
│   ├── 3-D.flf
│   ├── 3D-ASCII.flf
│   ├── 3d.flf
│   ├── ANSI Regular.flf
│   ├── ANSI Shadow.flf
│   ├── Big Money-ne.flf
│   ├── Big Money-nw.flf
│   ├── Broadway.flf
│   ├── DOS Rebel.flf
│   ├── Delta Corps Priest 1.flf
│   ├── Electronic.flf
│   ├── Isometric1.flf
│   ├── Sauce Code Pro Medium Nerd Font Complete.ttf
│   ├── SourceCodePro.zip
│   └── msjh.ttf
├── imgae_setup
│   ├── 11-logo.sh
│   ├── config
│   ├── cuda_path.sh
│   ├── custom_function.sh
│   ├── language_package.sh
│   ├── ohmyzsh_config.sh
│   ├── zsh_buckup_machanism.sh
│   └── zsh_ohmyzsh_setup.sh
├── lib
│   ├── WordOperator.py
│   └── __pycache__
│       └── WordOperator.cpython-38.pyc
├── requirements.txt
└── run_container.py
```

<!-- ## Installation

```bash
bash setup.sh
``` -->
