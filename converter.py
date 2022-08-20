import re
from time import time
import pandas as pd
import gpxpy.gpx
import datetime

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

trackpoint_pattern = re.compile(r'(?P<date>(?P<year>\d{4})\/(?P<month>\d{1,2})\/(?P<day>\d{1,2})  (?P<hour>\d{1,2}):(?P<minute>\d{1,2}):(?P<second>\d{1,2}))\n(?P<latitude>\d*,\d*)\n(?P<longitude>\d*,\d*)\n(?P<altitude>\d*,\d*)\n(?P<speed>\d*(,\d*)?)')

data = []

for match in trackpoint_pattern.finditer(text):
    # print(match.group(0))
    pointtime = datetime.datetime(int(match.group('year')), int(match.group('month')), int(match.group('day')), int(match.group('hour')), int(match.group('minute')), int(match.group('second')));
    trackpoint = {
        'time': pointtime,
        'latitude': float(match.group('latitude').replace(',','.')),
        'longitude': float(match.group('longitude').replace(',','.')),
        'altitude': float(match.group('altitude').replace(',','.')),
        'speed': float(match.group('speed').replace(',','.'))
    }
    data.append(trackpoint)

gpx = gpxpy.gpx.GPX()

# Create first track in our GPX:
gpx_track = gpxpy.gpx.GPXTrack()
gpx.tracks.append(gpx_track)

# Create first segment in our GPX track:
gpx_segment = gpxpy.gpx.GPXTrackSegment()
gpx_track.segments.append(gpx_segment)

# Create points:
# gpx_segment.points.append(gpxpy.gpx.GPXTrackPoint(2.1234, 5.1234, elevation=1234))
# gpx_segment.points.append(gpxpy.gpx.GPXTrackPoint(2.1235, 5.1235, elevation=1235))
# gpx_segment.points.append(gpxpy.gpx.GPXTrackPoint(2.1236, 5.1236, elevation=1236))
for trackpoint in data:
    gpx_segment.points.append(gpxpy.gpx.GPXTrackPoint(trackpoint['latitude'], trackpoint['longitude'], elevation=trackpoint['altitude'], time= trackpoint['time']))

# You can add routes and waypoints, too...

# print('Created GPX:', gpx.to_xml())

f = open("3207498739.gpx", "w")
f.write(gpx.to_xml())
f.close()