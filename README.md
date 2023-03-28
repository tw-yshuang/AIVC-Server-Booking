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

**Please see [USER_GUIDE.md](docs/USER_GUIDE.md)**

### For Host Maintainer and MLOps

1. Setting the maximum to compute capability for general users.
2. Setting the white list to custom compute capability for specific users.
3. Setting volume directory: Dataset, Work, and Backup
4. Easy to maintain the user config via yaml file.

**Please see [MAINTAINER_GUIDE.md](docs/MAINTAINER_GUIDE.md)**
