FROM python:3.8-slim

RUN apt-get update && apt-get install -y \
    mininet \
    openvswitch-switch \
    openvswitch-testcontroller \
    graphviz \
    sudo \
 && rm -rf /var/lib/apt/lists/*

RUN pip install \
    mininet \
    graphviz

WORKDIR /app

CMD ["python start_network.py"]
