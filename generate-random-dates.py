import json
import dateutil.parser
import datetime
from random import randrange

dates = []

for i in range(1, 25):
    day = i
    hour = randrange(24)
    minute = randrange(60)
    dates.append(datetime.datetime(2025, 12, day, hour, minute, 0, 0))

for date in dates:
    print(date.isoformat())
