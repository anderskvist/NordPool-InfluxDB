# Created by Daniel Nilsson
# Please support me with a coffee https://www.buymeacoffee.com/flopp999
# Version 1.1
# Script to fetch hourly prices from Nord Pool and store the data into InfluxDB

from pprint import pprint

import os
from nordpool import elspot
from datetime import datetime
from influxdb import InfluxDBClient, exceptions

# InfluxDB variables
database = os.getenv("INFLUXDB_DATABASE", "NordPool")
measurement = os.getenv("INFLUXDB_MEASUREMENT", "spot")
field = os.getenv("INFLUXDB_FIELD","price")

# NordPool variables
area = os.getenv("NORDPOOL_AREA")
currency = os.getenv("NORDPOOL_CURRENCY")

# database information
host = os.getenv("INFLUXDB_HOST", "localhost")
port = os.getenv("INFLUXDB_PORT", "8086")
username = os.getenv("INFLUXDB_USERNAME", "")
password = os.getenv("INFLUXDB_PASSWORD", "")
ssl = os.getenv("INFLUXDB_SSL", "False").lower() in ("true", "1", "t")
verify_ssl = os.getenv("INFLUXDB_VERIFY_SSL", "True").lower() in ("true", "1", "t")

client = InfluxDBClient(host=host, port=port, username=username, password=password, ssl=ssl, verify_ssl=verify_ssl) # IP, port, user, password

prices_spot = elspot.Prices(currency)
jsondata = []

tags = {"currency": currency, "area": area}

#Today
hour = 0
price=prices_spot.hourly(end_date=datetime.now().date(),areas=[area])
for each,b in price["areas"][area].items():
    if each == "values":
        for each in price["areas"][area]["values"]:
            time = int(each["start"].timestamp()) # store the datetime
            hour += 1
            jsondata.append({"measurement": measurement, "time": time, "tags": tags, "fields": {field: float(round(each["value"]/10.0,1))}})
#Tomorrow
hour = 0
price=prices_spot.hourly(areas=[area])
for each,b in price["areas"][area].items():
    if each == "values":
        for each in price["areas"][area]["values"]:
            if str(each["value"]) == "inf":
                continue
            time = int(each["start"].timestamp()) # store the datetime
            hour += 1
            jsondata.append({"measurement": measurement, "time": time, "tags": tags, "fields": {field: float(round(each["value"]/10.0,1))}})

#Store to InfluxDB
try:
    client.write_points(jsondata, database=database, time_precision='s', batch_size=10000, protocol='json')  # skriver data till Influx
except exceptions.InfluxDBClientError:
    print("Couldn\'t save data to InfluxDB database: ")
