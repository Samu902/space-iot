FROM python:3.8-slim

RUN pip install \
    eventlet==0.30.2 \
    ryu==4.34

WORKDIR /app

CMD ["python start_sdn_controller.py"]
