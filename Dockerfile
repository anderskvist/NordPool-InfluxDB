FROM python:3

WORKDIR /data
COPY . /data/

RUN pip3 install -r requirements.txt
CMD python3 NordPool_InfluxDB.py
