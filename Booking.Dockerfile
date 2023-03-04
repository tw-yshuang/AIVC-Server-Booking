FROM python:3.10.10-slim

LABEL author="tw-yshuang" version="1.1" description="I'm writing server image!"

# Localtime
ENV TZ=Asia/Taipei
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# user
ENV ACCOUNT=booking
ENV ACCOUNT_HOME=/home/${ACCOUNT}
RUN useradd -ms /bin/bash ${ACCOUNT}

# ssh-server & allow X11 forwarding use.
RUN apt-get update \
    && apt-get install sudo openssh-server iputils-ping -y \
    && sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/g' /etc/ssh/sshd_config \
    && echo "${ACCOUNT}:ys-huang" | chpasswd

# https://www.baeldung.com/linux/control-variable-access-sudo-environment
# TODO: is there has a way to use env in /etc/sudoers ?
RUN echo "${ACCOUNT}" 'ALL=(ALL) NOPASSWD: /usr/bin/booking_sudo' >> /etc/sudoers

ADD image_setup/booking_exec /.script/
RUN chmod +x /.script/*

WORKDIR ${ACCOUNT_HOME}
# USER ${ACCOUNT}
ADD requirements.txt ${ACCOUNT_HOME}/requirements.txt
RUN pip3 install -r requirements.txt

USER root

ENTRYPOINT ["/.script/entrypoint.sh"]