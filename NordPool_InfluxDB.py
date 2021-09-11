# Created by Daniel Nilsson
# Please support me with a coffee https://www.buymeacoffee.com/flopp999
# Version 1.0
# Script to fetch hourly prices from Nord Pool and store the data into InfluxDB
from nordpool import elspot
from datetime import datetime
from influxdb import InfluxDBClient, exceptions

prices_spot = elspot.Prices("SEK")
price=prices_spot.hourly(end_date=datetime.now().date(),areas=["SE4"])

# InfluxDB variables
database = "Tibber"
measurement = "El"
field = "Pris"

# database information
client = InfluxDBClient('localhost', 8086) # IP, port, user, password

jsondata = []
hour = 0
for each,b in price["areas"]["SE4"].items():
    if each == "values":
        for each in price["areas"]["SE4"]["values"]:
            time = int(each["start"].timestamp()) # store the datetime
            hour += 1
            jsondata.append({"measurement": measurement, "time": time, "fields": {field: float(each["value"]/10.0)}})

try:
    client.write_points(jsondata, database=database, time_precision='s', batch_size=10000, protocol='json')  # skriver data till Influx
except exceptions.InfluxDBClientError:
    print("Couldn\'t save data to InfluxDB database: ")
