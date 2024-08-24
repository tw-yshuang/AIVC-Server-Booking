FROM nvidia/cuda:12.4.1-cudnn-devel-ubuntu22.04

LABEL author="tw-yshuang" version="1.3" description="The user password & weclome logo can be change via environment variable `PASSWORD` & `LOGO`."

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
    && echo "deb http://free.nchc.org.tw/ubuntu/ jammy main restricted universe multiverse\n \
    deb http://free.nchc.org.tw/ubuntu/ jammy-updates main restricted universe multiverse\n \
    deb http://free.nchc.org.tw/ubuntu/ jammy-backports main restricted universe multiverse\n \
    deb http://free.nchc.org.tw/ubuntu/ jammy-security main restricted universe multiverse" > /etc/apt/sources.list

RUN apt update \
    && apt upgrade -y \
    && apt install apt-utils locales vim wget curl git-all htop tmux -y

# ssh-server & allow X11 forwarding use.
RUN apt install openssh-server iputils-ping -y \
    && sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/g' /etc/ssh/sshd_config \
    && sed -i 's/#X11UseLocalhost yes/X11UseLocalhost no/g' /etc/ssh/sshd_config \
    && echo "root:ys-huang" | chpasswd
ADD image_setup/run_exec /.script/
RUN chmod +x /.script/*

# shell setup
ADD image_setup/ /image_setup
WORKDIR /image_setup
RUN chmod +x ./*.sh \
    && ./zsh_ohmyzsh_setup.sh \
    && ./ohmyzsh_config.sh -y \
    &&  sed -i 's/# export LANG=en_US.UTF-8/export LANG=C.UTF-8/g' ~/.zshrc

# welcome message
ADD fonts/*.flf /usr/share/figlet/
ADD image_setup/11-logo.sh /etc/profile.d/11-logo.sh
RUN apt install figlet lolcat -y \
    && chmod +x /etc/profile.d/11-logo.sh \
    && echo 'bash /etc/profile.d/11-logo.sh' >> ~/.zlogin\
    && echo "LOGO='Go Go'" >> /etc/environment

# install python env tool & some dotfile
RUN ./language_package.sh -y \
    && ./custom_function.sh -no_nvm \
    && cp ./config/.tmux.conf ~/.tmux.conf \
    && cp ./config/.vimrc ~/.vimrc

# cuda setting
RUN ./cuda_path.sh

# git-acc tool
RUN git clone https://github.com/tw-yshuang/Git_SSH-Account_Switch.git
WORKDIR /image_setup/Git_SSH-Account_Switch
RUN chmod +x ./*.sh && ./setup.sh

WORKDIR /root
RUN rm -rf /image_setup

# install package for AIVC-Server-Booking used.
RUN pip3 install pyyaml --no-cache-dir

ENTRYPOINT ["/.script/entrypoint.sh"]

# volume work directory
# VOLUME ~/Work
# VOLUME ~/Dataset
# VOLUME ~/Backup

