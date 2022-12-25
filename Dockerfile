FROM nvidia/cuda:11.4.2-cudnn8-runtime-ubuntu20.04

LABEL author="tw-yshuang" version="1.0" description="I'm writing server image!"

# Localtime
ENV TZ=Asia/Taipei
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# apt PPA source
RUN echo 'export LANG="C.UTF-8"' >> /etc/profile \
    && mkdir -p /.script \
    && cp /etc/apt/sources.list /etc/apt/sources.list.bak \
    # && echo "deb http://ftp.tku.edu.tw/ubuntu/ focal main restricted universe multiverse\n \
    # deb http://ftp.tku.edu.tw/ubuntu/ focal-updates main restricted universe multiverse\n \
    # deb http://ftp.tku.edu.tw/ubuntu/ focal-backports main restricted universe multiverse\n \
    # deb http://ftp.tku.edu.tw/ubuntu/ focal-security main restricted universe multiverse" > /etc/apt/sources.list
    && echo "deb http://free.nchc.org.tw/ubuntu/ focal main restricted universe multiverse\n \
    deb http://free.nchc.org.tw/ubuntu/ focal-updates main restricted universe multiverse\n \
    deb http://free.nchc.org.tw/ubuntu/ focal-backports main restricted universe multiverse\n \
    deb http://free.nchc.org.tw/ubuntu/ focal-security main restricted universe multiverse" > /etc/apt/sources.list

RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install apt-utils locales vim wget curl git-all htop tmux -y

# ssh-server & allow X11 forwarding use.
RUN apt-get install openssh-server iputils-ping -y \
    && sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/g' /etc/ssh/sshd_config \
    && sed -i 's/#X11UseLocalhost yes/X11UseLocalhost no/g' /etc/ssh/sshd_config \
    && echo "root:ys-huang" | chpasswd
ADD container_run/ssh_start.sh /.script/
RUN chmod +x /.script/*

# shell setup
ADD imgae_setup/ ~/imgae_setup
WORKDIR ~/imgae_setup
RUN chmod +x ./*.sh \
    && ./zsh_ohmyzsh_setup.sh \
    && ./ohmyzsh_config.sh -y \
    &&  sed -i 's/# export LANG=en_US.UTF-8/export LANG=C.UTF-8/g' ~/.zshrc

# shell history buckup mechanism
RUN bash ./zsh_buckup_machanism.sh

# welcome message
ADD ttf/*.flf /usr/share/figlet/
ADD imgae_setup/11-logo.sh /etc/profile.d/11-logo.sh
RUN apt-get install figlet lolcat -y \
    && chmod +x /etc/profile.d/11-logo.sh \
    && cat /etc/profile.d/11-logo.sh | sed '1d' >> ~/.zlogin

# install python env tool & some dotfile
RUN ./language_package.sh -y \
    && ./custom_function.sh -no_nvm \
    && cp ./config/.tmux.conf ~/.tmux.conf \
    && cp ./config/.vimrc ~/.vimrc

# cuda setting
RUN ./cuda_path.sh

# git-acc tool
RUN git clone https://github.com/tw-yshuang/Git_SSH-Account_Switch.git
WORKDIR Git_SSH-Account_Switch
RUN chmod +x ./*.sh && ./setup.sh

# volume work directory
# VOLUME ~/Work
# VOLUME ~/Dataset
# VOLUME ~/.pyenv/versions
# VOLUME ~/.local/share/virtualenvs

