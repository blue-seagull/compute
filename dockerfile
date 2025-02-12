FROM ubuntu:latest

ENV DEVIAN_FRONTEND=noninteractive

RUN apt updata && apt install -y \
    openssh-server \
    sudo \
    curl \
    vim \
    tmux \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir /var/run/sshd
RUN echo 'root:password' | chpasswd
RUN sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config
RUN sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config

EXPOSE 22

VOLUME /bodega-storage

CMD ["/usr/sbin/sshd", "-D"]