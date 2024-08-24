#!/usr/bin/env bash

# update from v2.15.0 to v2.16.0

# What's New:
#   1. security: the password will not show on the process monitor's command section, e.g.(top, htop)
#   2. feature: contianer logo is now changeable
#   3. optimize: the process of building the custom image updated to make the image thinner

# Add Image:
#   rober5566a/aivc-server:booking-v1.2.0
#   rober5566a/aivc-server:cuda12.4.1-cudnn-devel-ubuntu22.04

# Update Images:
#   rober5566a/aivc-server:latest (rober5566a/aivc-server:cuda12.1.1-cudnn8-devel-ubuntu22.04)
#   rober5566a/aivc-server:cuda12.1.1-cudnn8-devel-ubuntu22.04
#   rober5566a/aivc-server:cuda12.0.1-cudnn8-devel-ubuntu22.04
#   rober5566a/aivc-server:cuda11.8.0-cudnn8-devel-ubuntu22.04
#   rober5566a/aivc-server:cuda11.7.1-cudnn8-devel-ubuntu22.04
#   rober5566a/aivc-server:cuda12.1.1-cudnn8-devel-ubuntu20.04
#   rober5566a/aivc-server:cuda12.0.1-cudnn8-devel-ubuntu20.04
#   rober5566a/aivc-server:cuda11.8.0-cudnn8-devel-ubuntu20.04
#   rober5566a/aivc-server:cuda11.7.1-cudnn8-devel-ubuntu20.04
#   rober5566a/aivc-server:cuda11.4.3-cudnn8-devel-ubuntu20.04

docker rmi \
    7c3e4778db2f \
    0342ef0a319e \
    4b6ec30d78e5 \
    0e374a8aac06 \
    59de3fef86f7 \
    d02a57110df7 \
    3ef905f029bc \
    86d348a4bbc3 \
    7d9297f10366 

bash "$(pwd)"/setup.sh