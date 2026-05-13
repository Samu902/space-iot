FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    mininet \
    openvswitch-switch \
    openvswitch-testcontroller \
    # iproute2 \
    # iputils-ping \
    # net-tools \
    # tcpdump \
    # vim \
    # curl \
    python3-dev \
    python3-pip \
    git \
    sudo \
    && apt-get clean

RUN pip3 install \
    ryu==4.34 \
    eventlet==0.33.3 \
    dnspython==2.2.1 \
    "setuptools<81"

CMD ["/bin/bash"]