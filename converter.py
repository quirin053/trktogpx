import re
from time import time
import pandas as pd
import gpxpy.gpx
import datetime
import math

# 1988/8/5  4:1:49
# 48,221282
# 12,902967
# 402,5
# 0

# regex
# (?P<date>(?P<year>\d{4})\/(?P<month>\d{1,2})\/(?P<day>\d{1,2})  (?P<hour>\d{1,2}):(?P<minute>\d{1,2}):(?P<second>\d{1,2}))\n(?P<latitude>\d*,\d*)\n(?P<longitude>\d*,\d*)\n(?P<altitude>\d*,\d*)\n(?P<speed>\d*(,\d*)?)

ifile = open("01.trk",'r')
ifile.seek(4239) #skip unreadable content
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

max_distance = 0.1
max_time_delta = datetime.timedelta(0,0,0,0,5)

gpx_segment = gpxpy.gpx.GPXTrackSegment()
prev_tp_time = data[0]['time']
prev_tp_pos = [data[0]['latitude'], data[0]['longitude']]

actual_start_time = datetime.datetime(2022, 8, 18, 16, 13, 28)
timeshift = actual_start_time - data[0]['time']

camsync_camera_time = datetime.datetime(2022, 8, 18, 16, 14, 28)
camsync_gps_time = datetime.datetime(2022, 8, 18, 16, 13, 28)
timeshift += camsync_camera_time - camsync_gps_time

# Create points:
# gpx_segment.points.append(gpxpy.gpx.GPXTrackPoint(2.1234, 5.1234, elevation=1234))
# gpx_segment.points.append(gpxpy.gpx.GPXTrackPoint(2.1235, 5.1235, elevation=1235))
# gpx_segment.points.append(gpxpy.gpx.GPXTrackPoint(2.1236, 5.1236, elevation=1236))
for trackpoint in data:
    if trackpoint['time'] - prev_tp_time > max_time_delta or math.sqrt((trackpoint['latitude']-prev_tp_pos[0])**2+(trackpoint['longitude']-prev_tp_pos[1])**2) > max_distance:
        gpx_track.segments.append(gpx_segment)
        gpx_segment = gpxpy.gpx.GPXTrackSegment()
    gpx_segment.points.append(gpxpy.gpx.GPXTrackPoint(trackpoint['latitude'], trackpoint['longitude'], elevation=trackpoint['altitude'], time= trackpoint['time']+timeshift))
    prev_tp_time = trackpoint['time']
    prev_tp_pos = [trackpoint['latitude'], trackpoint['longitude']]


# Create first segment in our GPX track:

gpx_track.segments.append(gpx_segment)
# You can add routes and waypoints, too...

# print('Created GPX:', gpx.to_xml())

f = open("3207498739.gpx", "w")
f.write(gpx.to_xml())
f.close()