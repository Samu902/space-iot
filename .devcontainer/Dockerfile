FROM python:3.8-slim

RUN apt-get update && apt-get install -y \
    iproute2 \
    iputils-ping \
    mininet \
    openvswitch-switch \
    openvswitch-testcontroller \
    graphviz \
    git \
    sudo \
 && rm -rf /var/lib/apt/lists/*

RUN pip install \
    eventlet==0.30.2 \
    ryu==4.34 \
    mininet \
    graphviz \
    networkx

CMD ["/bin/bash"]
