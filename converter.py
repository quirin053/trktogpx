import re
import pandas as pd

# 1988/8/5  4:1:49
# 48,221282
# 12,902967
# 402,5
# 0

# regex
# (?P<date>(?P<year>\d{4})\/(?P<month>\d{1,2})\/(?P<day>\d{1,2})  (?P<hour>\d{1,2}):(?P<minute>\d{1,2}):(?P<second>\d{1,2}))\n(?P<latitude>\d*,\d*)\n(?P<longitude>\d*,\d*)\n(?P<altitude>\d*,\d*)\n(?P<speed>\d*(,\d*)?)

ifile = open("01.txt",'r')
text = ifile.read()
ifile.close()

waypoint = re.compile(r'(?P<date>(?P<year>\d{4})\/(?P<month>\d{1,2})\/(?P<day>\d{1,2})  (?P<hour>\d{1,2}):(?P<minute>\d{1,2}):(?P<second>\d{1,2}))\n(?P<latitude>\d*,\d*)\n(?P<longitude>\d*,\d*)\n(?P<altitude>\d*,\d*)\n(?P<speed>\d*(,\d*)?)')

for match in waypoint.finditer(text):
    print(match.group('year'))